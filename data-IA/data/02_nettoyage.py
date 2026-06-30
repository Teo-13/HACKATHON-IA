"""
TechCorp - Mission DATA
Etape 2 : Nettoyage, detection d'anomalies et preparation pour le fine-tuning LoRA

Prerequis : avoir execute 01_recuperation_donnees.py (genere data/raw_*.json)

Usage :
    pip install pandas --break-system-packages
    python 02_nettoyage.py
"""

import json
import re
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
OUTPUT_DIR = Path("data/clean")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Le dataset ruslanmv/ai-medical-chatbot utilise typiquement les colonnes
# "Description", "Patient", "Doctor". On les detecte automatiquement
# pour ne pas planter si la structure differe legerement.
COLONNES_CANDIDATES = {
    "input": ["Patient", "patient", "question", "input", "instruction"],
    "output": ["Doctor", "doctor", "answer", "output", "response"],
    "contexte": ["Description", "description", "context"],
}

# Mots-cles grossiers pour un premier filtrage de securite / pertinence.
# A completer selon ce que vous trouvez reellement dans le dataset.
MOTS_SUSPECTS = [
    "ignore previous instructions",
    "system prompt",
    "jailbreak",
    "<script",
    "http://",
    "https://",
]


def charger_donnees():
    fichiers = sorted(DATA_DIR.glob("raw_*.json"))
    if not fichiers:
        raise FileNotFoundError(
            "Aucun fichier raw_*.json trouve dans data/. "
            "Lancez d'abord 01_recuperation_donnees.py"
        )

    frames = {}
    for f in fichiers:
        split_name = f.stem.replace("raw_", "")
        frames[split_name] = pd.read_json(f)
        print(f"Charge : {f.name} ({len(frames[split_name])} lignes)")
    return frames


def detecter_colonnes(df):
    mapping = {}
    for cible, candidats in COLONNES_CANDIDATES.items():
        for c in candidats:
            if c in df.columns:
                mapping[cible] = c
                break
    return mapping


def nettoyer_texte(texte):
    if not isinstance(texte, str):
        return ""
    texte = texte.strip()
    texte = re.sub(r"\s+", " ", texte)          # espaces multiples -> un seul
    texte = re.sub(r"<.*?>", "", texte)          # balises HTML residuelles
    return texte


def detecter_anomalies(df, col_input, col_output):
    """Repere les lignes suspectes a verifier manuellement (pas de suppression automatique)."""
    anomalies = []

    for idx, row in df.iterrows():
        texte_complet = f"{row.get(col_input, '')} {row.get(col_output, '')}".lower()
        raisons = []

        for mot in MOTS_SUSPECTS:
            if mot in texte_complet:
                raisons.append(f"mot suspect: '{mot}'")

        if len(str(row.get(col_input, ""))) < 5:
            raisons.append("input trop court")
        if len(str(row.get(col_output, ""))) < 5:
            raisons.append("output trop court")

        if raisons:
            anomalies.append({"index": int(idx), "raisons": raisons})

    return anomalies


def nettoyer_split(split_name, df):
    mapping = detecter_colonnes(df)
    print(f"\n[{split_name}] Colonnes detectees : {mapping}")

    if "input" not in mapping or "output" not in mapping:
        print(f"[{split_name}] Colonnes input/output introuvables, split ignore.")
        return None, []

    col_in, col_out = mapping["input"], mapping["output"]

    avant = len(df)

    # 1. Normalisation du texte
    df[col_in] = df[col_in].apply(nettoyer_texte)
    df[col_out] = df[col_out].apply(nettoyer_texte)

    # 2. Detection d'anomalies AVANT suppression (pour le rapport)
    anomalies = detecter_anomalies(df, col_in, col_out)

    # 3. Suppression des doublons stricts
    df = df.drop_duplicates(subset=[col_in, col_out])

    # 4. Suppression des lignes vides ou trop courtes (bruit, pas exploitable)
    df = df[df[col_in].str.len() >= 5]
    df = df[df[col_out].str.len() >= 5]

    # 5. Renommage standard pour le fine-tuning LoRA (format instruction/output)
    df = df.rename(columns={col_in: "instruction", col_out: "output"})
    colonnes_finales = ["instruction", "output"]
    if "contexte" in mapping:
        df = df.rename(columns={mapping["contexte"]: "contexte"})
        colonnes_finales.append("contexte")
    df = df[colonnes_finales].reset_index(drop=True)

    apres = len(df)
    print(f"[{split_name}] {avant} -> {apres} lignes apres nettoyage "
          f"({avant - apres} supprimees, {len(anomalies)} anomalies signalees)")

    return df, anomalies


def split_train_val_test(df, train=0.8, val=0.1, seed=42):
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    n = len(df)
    n_train = int(n * train)
    n_val = int(n * val)

    return {
        "train": df.iloc[:n_train],
        "validation": df.iloc[n_train:n_train + n_val],
        "test": df.iloc[n_train + n_val:],
    }


def sauvegarder(df, nom):
    json_path = OUTPUT_DIR / f"{nom}.json"
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)
    print(f"  -> {json_path}")


def generer_rapport_qualite(rapport):
    chemin = OUTPUT_DIR / "rapport_qualite.json"
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nRapport de qualite -> {chemin}")


if __name__ == "__main__":
    frames = charger_donnees()
    rapport_global = {}

    df_propre_total = []

    for split_name, df in frames.items():
        df_nettoye, anomalies = nettoyer_split(split_name, df)
        if df_nettoye is None:
            continue

        rapport_global[split_name] = {
            "lignes_avant": len(df),
            "lignes_apres": len(df_nettoye),
            "nb_anomalies_signalees": len(anomalies),
            "exemples_anomalies": anomalies[:10],  # echantillon pour revue manuelle
        }
        df_propre_total.append(df_nettoye)

    if not df_propre_total:
        raise RuntimeError("Aucun split n'a pu etre nettoye, verifiez le format des donnees.")

    df_final = pd.concat(df_propre_total, ignore_index=True)
    print(f"\nTotal apres nettoyage et fusion : {len(df_final)} lignes")

    # Si le dataset source n'avait qu'un seul split, on cree nous-memes train/val/test
    splits = split_train_val_test(df_final)

    print("\nSauvegarde des splits finaux :")
    for nom, df_split in splits.items():
        print(f"  {nom}: {len(df_split)} lignes")
        sauvegarder(df_split, nom)

    rapport_global["splits_finaux"] = {nom: len(d) for nom, d in splits.items()}
    generer_rapport_qualite(rapport_global)

    print("\n/!\\ A faire manuellement : relire l'echantillon 'exemples_anomalies' du "
          "rapport_qualite.json pour confirmer/ecarter les faux positifs avant le fine-tuning.")