"""
TechCorp - Mission DATA
Etape 8 : Generer l'echantillon de validation avant suppression
des cas classes PRIORITE_HAUTE.

Le script concatene les fichiers *_priorite_haute.json de tous les splits,
tire un echantillon reproductible de 25 lignes (seed=42), puis exporte
un fichier de revue manuelle a completer.
"""

import argparse
import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
TRI_DIR = BASE_DIR / "dataset" / "revue_securite" / "tri"
OUTPUT_PATH = TRI_DIR / "echantillon_validation_suppression.json"
N_ECHANTILLON = 25
SEED = 42


def charger_priorite_haute():
    frames = []

    for split_name in ["train", "validation", "test"]:
        chemin = TRI_DIR / f"{split_name}_priorite_haute.json"
        if not chemin.exists():
            print(f"[{split_name}] introuvable, ignore.")
            continue

        df = pd.read_json(chemin)
        df["split"] = split_name
        df["source_index"] = df.index
        frames.append(df)

    if not frames:
        raise FileNotFoundError("Aucun fichier *_priorite_haute.json trouve.")

    return pd.concat(frames, ignore_index=True)


def contient_annotations_manuelles(path):
    if not path.exists():
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            donnees = json.load(f)
    except json.JSONDecodeError:
        return False

    for ligne in donnees:
        verdict = str(ligne.get("verdict", "")).strip()
        commentaire = str(ligne.get("commentaire", "")).strip()
        if verdict or commentaire:
            return True
    return False


def construire_echantillon(df):
    echantillon = df.sample(n=N_ECHANTILLON, random_state=SEED).reset_index(drop=True)

    registres = []
    for i, row in echantillon.iterrows():
        registres.append(
            {
                "id": i + 1,
                "split": row["split"],
                "source_index": int(row["source_index"]),
                "mots_cles_detectes": row.get("mots_cles_detectes", []),
                "question_patient": row["input"],
                "reponse_medecin": row["output"],
                "verdict": "",
                "commentaire": "",
            }
        )
    return registres


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        action="store_true",
        help="ecrase le fichier de sortie meme s'il contient deja des annotations",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="chemin du fichier JSON de sortie",
    )
    args = parser.parse_args()

    output_path = args.output

    if contient_annotations_manuelles(output_path) and not args.force:
        print(
            f"{output_path} contient deja des annotations manuelles. "
            "Relancez avec --force pour le regenerer."
        )
        raise SystemExit(1)

    df_priorite = charger_priorite_haute()
    registres = construire_echantillon(df_priorite)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(registres, f, ensure_ascii=False, indent=2)

    print(f"{N_ECHANTILLON} lignes extraites -> {output_path}")
    print("Remplir ensuite 'verdict' et 'commentaire' pour chaque cas.")
