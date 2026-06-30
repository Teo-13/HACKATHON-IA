"""
TechCorp - Mission DATA
Etape 4 : Filtrage des outliers de longueur (trop courts / trop longs)
avant fine-tuning LoRA.

Prerequis : avoir execute 02_nettoyage.py (genere data/clean/*.json)

Usage :
    pip install pandas --break-system-packages
    python 04_filtrage_longueur.py
"""

import json
from pathlib import Path

import pandas as pd

CLEAN_DIR = Path("data/clean")
EXPORT_DIR = Path("data/export_lora")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

MIN_MOTS = 4          # en dessous, l'echange n'est pas exploitable
PERCENTILE_MAX = 0.99  # on coupe les 1% les plus longs (instruction OU output)


def charger_split(nom):
    return pd.read_json(CLEAN_DIR / f"{nom}.json")


def filtrer_longueur(df, seuil_instr_max, seuil_output_max):
    df["len_instruction"] = df["instruction"].str.split().str.len()
    df["len_output"] = df["output"].str.split().str.len()

    avant = len(df)

    masque = (
        (df["len_instruction"] >= MIN_MOTS)
        & (df["len_output"] >= MIN_MOTS)
        & (df["len_instruction"] <= seuil_instr_max)
        & (df["len_output"] <= seuil_output_max)
    )
    df_filtre = df[masque].drop(columns=["len_instruction", "len_output"]).reset_index(drop=True)

    apres = len(df_filtre)
    print(f"  {avant} -> {apres} lignes ({avant - apres} supprimees)")
    return df_filtre


def vers_format_lora(df):
    registres = []
    for _, row in df.iterrows():
        registres.append({
            "instruction": "Tu es un assistant medical. Reponds a la question du patient.",
            "input": row["instruction"],
            "output": row["output"],
        })
    return registres


def exporter_jsonl(donnees, chemin):
    with open(chemin, "w", encoding="utf-8") as f:
        for ligne in donnees:
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    print(f"  -> {chemin} ({len(donnees)} lignes)")


if __name__ == "__main__":
    # On calcule les seuils sur le train uniquement, puis on les applique
    # aux 3 splits pour rester coherent (meme regle partout).
    df_train = charger_split("train")
    df_train["len_instruction"] = df_train["instruction"].str.split().str.len()
    df_train["len_output"] = df_train["output"].str.split().str.len()

    seuil_instr_max = int(df_train["len_instruction"].quantile(PERCENTILE_MAX))
    seuil_output_max = int(df_train["len_output"].quantile(PERCENTILE_MAX))

    print(f"Seuils calcules sur train (percentile {int(PERCENTILE_MAX*100)}) :")
    print(f"  instruction <= {seuil_instr_max} mots")
    print(f"  output      <= {seuil_output_max} mots")
    print(f"  min commun  >= {MIN_MOTS} mots\n")

    stats_finales = {"seuils": {
        "min_mots": MIN_MOTS,
        "instruction_max_mots": seuil_instr_max,
        "output_max_mots": seuil_output_max,
    }}

    for split_name in ["train", "validation", "test"]:
        chemin_split = CLEAN_DIR / f"{split_name}.json"
        if not chemin_split.exists():
            print(f"[{split_name}] introuvable, ignore.")
            continue

        print(f"[{split_name}]")
        df = charger_split(split_name)
        df_filtre = filtrer_longueur(df, seuil_instr_max, seuil_output_max)

        # Stats apres filtrage
        len_instr = df_filtre["instruction"].str.split().str.len()
        len_out = df_filtre["output"].str.split().str.len()
        stats_finales[split_name] = {
            "nb_lignes": len(df_filtre),
            "instruction_mots_moyenne": round(len_instr.mean(), 1),
            "instruction_mots_max": int(len_instr.max()) if len(df_filtre) else 0,
            "output_mots_moyenne": round(len_out.mean(), 1),
            "output_mots_max": int(len_out.max()) if len(df_filtre) else 0,
        }

        donnees_lora = vers_format_lora(df_filtre)
        exporter_jsonl(donnees_lora, EXPORT_DIR / f"{split_name}_lora.jsonl")

    rapport_path = EXPORT_DIR / "stats_finales.json"
    with open(rapport_path, "w", encoding="utf-8") as f:
        json.dump(stats_finales, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nStatistiques finales -> {rapport_path}")
    print("Fichiers LoRA finaux prets dans data/export_lora/")