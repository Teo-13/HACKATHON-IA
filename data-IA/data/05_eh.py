"""
TechCorp - Mission DATA
Etape 5 : Echantillon aleatoire pour relecture manuelle qualitative

Genere un sous-ensemble de paires question/reponse a relire a la main,
pour confirmer que le filtrage automatique n'a pas laisse passer
des reponses incoherentes, hors-sujet ou problematiques.

Prerequis : avoir execute 04_filtrage_longueur.py

Usage :
    pip install pandas --break-system-packages
    python 05_echantillon_relecture.py
"""

import json
from pathlib import Path

import pandas as pd

EXPORT_DIR = Path("dataset/export_lora")
ECHANTILLON_PATH = EXPORT_DIR / "echantillon_relecture.json"
N_ECHANTILLON = 30
SEED = 42


def charger_jsonl(chemin):
    lignes = []
    with open(chemin, "r", encoding="utf-8") as f:
        for ligne in f:
            lignes.append(json.loads(ligne))
    return pd.DataFrame(lignes)


if __name__ == "__main__":
    df = charger_jsonl(EXPORT_DIR / "train_lora.jsonl")

    echantillon = df.sample(n=N_ECHANTILLON, random_state=SEED).reset_index(drop=True)

    # On ajoute un champ vide a remplir a la main pour chaque ligne
    registres = []
    for i, row in echantillon.iterrows():
        registres.append({
            "id": i + 1,
            "question_patient": row["input"],
            "reponse_medecin": row["output"],
            "verdict": "",          # a remplir : OK / A_REVOIR / PROBLEME
            "commentaire": "",      # a remplir : pourquoi
        })

    with open(ECHANTILLON_PATH, "w", encoding="utf-8") as f:
        json.dump(registres, f, ensure_ascii=False, indent=2)

    print(f"{N_ECHANTILLON} paires extraites -> {ECHANTILLON_PATH}")
    print("\nOuvrez ce fichier et remplissez 'verdict' (OK / A_REVOIR / PROBLEME)")
    print("et 'commentaire' pour chaque ligne, en lisant la question et la reponse.")
    print("\nGrille de lecture suggeree :")
    print("  OK        -> reponse coherente, pertinente, pas de contenu choquant")
    print("  A_REVOIR  -> reponse incomplete, vague, ou hors-sujet")
    print("  PROBLEME  -> reponse dangereuse, fausse, ou contenu inapproprie")