"""
TechCorp - Mission DATA
Etape 6 : Detection des conversations sensibles (idees suicidaires / automutilation)
sur l'ensemble du dataset, suite a la relecture manuelle de l'echantillon (cas #29).

Objectif : ne pas se contenter de l'echantillon de 30 lignes, scanner les
241 661 lignes finales pour quantifier et isoler les cas a traiter avant
le fine-tuning.

Prerequis : avoir execute 04_filtrage_longueur.py

Usage :
    pip install pandas --break-system-packages
    python 06_detection_contenu_sensible.py
"""

import json
from pathlib import Path

import pandas as pd

EXPORT_DIR = Path("dataset/export_lora")
SORTIE_DIR = Path("dataset/revue_securite")
SORTIE_DIR.mkdir(parents=True, exist_ok=True)

# Mots-cles indicatifs (pas exhaustifs) d'un contenu lie au suicide /
# automutilation, cote question (input) ET reponse (output).
# But : isoler pour revue manuelle, pas une suppression automatique aveugle.
MOTS_CLES_SENSIBLES = [
    "suicide", "suicidal", "kill myself", "killing myself",
    "end my life", "ending my life", "want to die", "wanna die",
    "self harm", "self-harm", "cutting myself", "hurt myself",
    "no reason to live", "better off dead",
]


def charger_jsonl(chemin):
    lignes = []
    with open(chemin, "r", encoding="utf-8") as f:
        for ligne in f:
            lignes.append(json.loads(ligne))
    return pd.DataFrame(lignes)


def detecter_contenu_sensible(df):
    """Repere les lignes contenant un mot-cle sensible, cote input ou output."""
    texte_complet = (df["input"].fillna("") + " " + df["output"].fillna("")).str.lower()

    masque = pd.Series(False, index=df.index)
    mots_trouves = pd.Series([[] for _ in range(len(df))], index=df.index)

    for mot in MOTS_CLES_SENSIBLES:
        contient = texte_complet.str.contains(mot, regex=False)
        masque = masque | contient
        for idx in df.index[contient]:
            mots_trouves[idx].append(mot)

    return masque, mots_trouves


if __name__ == "__main__":
    rapport_global = {}

    for split_name in ["train", "validation", "test"]:
        chemin = EXPORT_DIR / f"{split_name}_lora.jsonl"
        if not chemin.exists():
            print(f"[{split_name}] introuvable, ignore.")
            continue

        df = charger_jsonl(chemin)
        masque, mots_trouves = detecter_contenu_sensible(df)

        nb_total = len(df)
        nb_sensibles = int(masque.sum())

        print(f"[{split_name}] {nb_sensibles} / {nb_total} lignes contiennent "
              f"un mot-cle sensible ({nb_sensibles / nb_total * 100:.2f}%)")

        # Export des lignes sensibles pour revue manuelle (toute l'equipe,
        # notamment CYBER pour la validation des biais/risques)
        df_sensible = df[masque].copy()
        df_sensible["mots_cles_detectes"] = mots_trouves[masque]
        df_sensible["verdict"] = ""       # a remplir : GARDER / RETIRER / A_REECRIRE
        df_sensible["commentaire"] = ""

        sortie = SORTIE_DIR / f"{split_name}_a_revoir.json"
        df_sensible.reset_index(drop=True).to_json(
            sortie, orient="records", force_ascii=False, indent=2
        )
        print(f"  -> {sortie}")

        rapport_global[split_name] = {
            "nb_total": nb_total,
            "nb_sensibles": nb_sensibles,
            "pourcentage": round(nb_sensibles / nb_total * 100, 2),
        }

    rapport_path = SORTIE_DIR / "rapport_contenu_sensible.json"
    with open(rapport_path, "w", encoding="utf-8") as f:
        json.dump(rapport_global, f, ensure_ascii=False, indent=2)

    print(f"\nRapport global -> {rapport_path}")
    print("\nProchaine etape : relire manuellement les fichiers *_a_revoir.json")
    print("et decider pour chaque ligne : GARDER (reponse adequate, oriente")
    print("vers de l'aide) / RETIRER (reponse inadequate) / A_REECRIRE.")
    print("\nRecommandation : ne jamais laisser dans le dataset de fine-tuning")
    print("une reponse a une ideation suicidaire qui minimise le risque sans")
    print("orienter vers une ressource d'urgence.")