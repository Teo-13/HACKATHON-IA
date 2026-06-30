"""
TechCorp - Mission DATA
Etape 3 : Statistiques descriptives + export final pour le fine-tuning LoRA

Prerequis : avoir execute 02_nettoyage.py (genere data/clean/train.json etc.)

Usage :
    pip install pandas matplotlib --break-system-packages
    python 03_stats_et_export.py
"""

import json
from pathlib import Path

import pandas as pd

CLEAN_DIR = Path("data/clean")
EXPORT_DIR = Path("data/export_lora")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Si le script de fine-tuning herite attend un autre format,
# il suffit d'adapter la fonction vers_format_lora() ci-dessous.


def charger_split(nom):
    return pd.read_json(CLEAN_DIR / f"{nom}.json")


def stats_longueur(df):
    df["len_instruction"] = df["instruction"].str.split().str.len()
    df["len_output"] = df["output"].str.split().str.len()

    return {
        "nb_lignes": len(df),
        "instruction_mots_moyenne": round(df["len_instruction"].mean(), 1),
        "instruction_mots_min": int(df["len_instruction"].min()),
        "instruction_mots_max": int(df["len_instruction"].max()),
        "output_mots_moyenne": round(df["len_output"].mean(), 1),
        "output_mots_min": int(df["len_output"].min()),
        "output_mots_max": int(df["len_output"].max()),
    }


def themes_frequents(df, n=15):
    """Mots les plus frequents dans les questions patients (hors mots vides courants)."""
    mots_vides = {
        "the", "a", "i", "is", "of", "to", "and", "my", "in", "have", "it",
        "for", "what", "this", "me", "am", "on", "with", "that", "are", "be",
        "do", "you", "as", "but", "not", "can", "has", "from", "an",
    }

    tous_mots = " ".join(df["instruction"].str.lower()).split()
    tous_mots = [m.strip(".,!?;:") for m in tous_mots if m.strip(".,!?;:") not in mots_vides]

    freq = pd.Series(tous_mots).value_counts().head(n)
    return freq.to_dict()


def vers_format_lora(df):
    """
    Convertit vers le format Alpaca-style, standard pour la plupart
    des scripts de fine-tuning LoRA (peft / transformers / axolotl) :
    {"instruction": ..., "input": ..., "output": ...}
    """
    registres = []
    for _, row in df.iterrows():
        registres.append({
            "instruction": "Tu es un assistant medical. Reponds a la question du patient.",
            "input": row["instruction"],      # la question du patient
            "output": row["output"],          # la reponse du medecin
        })
    return registres


def exporter_jsonl(donnees, chemin):
    with open(chemin, "w", encoding="utf-8") as f:
        for ligne in donnees:
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    print(f"  -> {chemin} ({len(donnees)} lignes)")


if __name__ == "__main__":
    rapport_stats = {}

    for split_name in ["train", "validation", "test"]:
        chemin_split = CLEAN_DIR / f"{split_name}.json"
        if not chemin_split.exists():
            print(f"[{split_name}] introuvable, ignore.")
            continue

        df = charger_split(split_name)
        print(f"\n[{split_name}] {len(df)} lignes")

        # Stats descriptives
        stats = stats_longueur(df)
        rapport_stats[split_name] = stats
        print(f"  Longueur instruction (mots) : moy={stats['instruction_mots_moyenne']} "
              f"min={stats['instruction_mots_min']} max={stats['instruction_mots_max']}")
        print(f"  Longueur output (mots)      : moy={stats['output_mots_moyenne']} "
              f"min={stats['output_mots_min']} max={stats['output_mots_max']}")

        # Themes frequents (seulement sur train, pour limiter le temps de calcul)
        if split_name == "train":
            themes = themes_frequents(df)
            rapport_stats["themes_frequents_train"] = themes
            print(f"  Themes frequents : {list(themes.keys())[:8]}...")

        # Export au format LoRA
        donnees_lora = vers_format_lora(df)
        exporter_jsonl(donnees_lora, EXPORT_DIR / f"{split_name}_lora.jsonl")

    rapport_path = EXPORT_DIR / "stats_finales.json"
    with open(rapport_path, "w", encoding="utf-8") as f:
        json.dump(rapport_stats, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nStatistiques finales -> {rapport_path}")

    print("\nFichiers prets pour le fine-tuning LoRA dans data/export_lora/")
    print("Si le script herite attend un format different (chat template, etc.),")
    print("adapter la fonction vers_format_lora().")