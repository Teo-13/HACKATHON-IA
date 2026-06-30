"""
TechCorp - Mission DATA
Etape 1 : Recuperation et premier etat des lieux du dataset medical
Source : huggingface.co/datasets/ruslanmv/ai-medical-chatbot

Usage :
    pip install datasets pandas --break-system-packages
    python 01_recuperation_donnees.py
"""

import json
from pathlib import Path

import pandas as pd
from datasets import load_dataset

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)


def recuperer_dataset():
    """Telecharge le dataset depuis le Hub HuggingFace."""
    print("Telechargement du dataset 'ruslanmv/ai-medical-chatbot'...")
    dataset = load_dataset("ruslanmv/ai-medical-chatbot")
    print("Splits disponibles :", list(dataset.keys()))
    return dataset


def sauvegarder_bruts(dataset):
    """Sauvegarde une copie brute locale (JSON + CSV) pour traçabilite."""
    for split_name, split_data in dataset.items():
        df = split_data.to_pandas()

        json_path = OUTPUT_DIR / f"raw_{split_name}.json"
        csv_path = OUTPUT_DIR / f"raw_{split_name}.csv"

        df.to_json(json_path, orient="records", force_ascii=False, indent=2)
        df.to_csv(csv_path, index=False)

        print(f"[{split_name}] {len(df)} lignes -> {json_path.name}, {csv_path.name}")


def etat_des_lieux(dataset):
    """Premier audit rapide : structure, colonnes, valeurs manquantes, doublons."""
    rapport = {}

    for split_name, split_data in dataset.items():
        df = split_data.to_pandas()

        rapport[split_name] = {
            "nb_lignes": len(df),
            "colonnes": list(df.columns),
            "valeurs_manquantes": df.isna().sum().to_dict(),
            "doublons": int(df.duplicated().sum()),
            "exemple": df.iloc[0].to_dict() if len(df) > 0 else None,
        }

    rapport_path = OUTPUT_DIR / "etat_des_lieux.json"
    with open(rapport_path, "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2, default=str)

    print(f"\nRapport d'etat des lieux sauvegarde -> {rapport_path}")
    return rapport


def afficher_resume(rapport):
    print("\n===== RESUME =====")
    for split_name, infos in rapport.items():
        print(f"\nSplit : {split_name}")
        print(f"  Lignes      : {infos['nb_lignes']}")
        print(f"  Colonnes    : {infos['colonnes']}")
        print(f"  Doublons    : {infos['doublons']}")
        print(f"  Manquants   : {infos['valeurs_manquantes']}")


if __name__ == "__main__":
    dataset = recuperer_dataset()
    sauvegarder_bruts(dataset)
    rapport = etat_des_lieux(dataset)
    afficher_resume(rapport)

    print("\nProchaine etape : nettoyage + detection d'anomalies (script 02_nettoyage.py)")