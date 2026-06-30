"""
TechCorp - Mission DATA
Etape 7 : Tri automatique des lignes sensibles detectees a l'etape 6,
pour reduire le volume avant relecture manuelle.

Logique en 2 niveaux :
1. Distinguer les vraies mentions de risque suicidaire/automutilation
   des faux positifs evidents (expressions figees sans rapport avec le risque
   reel : "die of embarrassment", "dying my hair", "died laughing", etc.)
2. Parmi les vrais cas, verifier si la REPONSE du medecin oriente vers
   une ressource d'aide (urgence, hotline, professionnel de sante).
   Si non -> priorite haute pour la relecture manuelle.

Prerequis : avoir execute 06_detection_contenu_sensible.py

Usage :
    pip install pandas --break-system-packages
    python 07_tri_automatique_securite.py
"""

import json
import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "dataset" / "revue_securite"
SORTIE_DIR = SOURCE_DIR / "tri"
SORTIE_DIR.mkdir(parents=True, exist_ok=True)

MOTS_CLES_SENSIBLES = [
    "suicide", "suicidal", "kill myself", "killing myself",
    "end my life", "ending my life", "want to die", "wanna die",
    "self harm", "self-harm", "cutting myself", "hurt myself",
    "no reason to live", "better off dead",
]

# Expressions qui indiquent presque toujours un faux positif
# (mot-cle present mais sans lien avec un risque reel)
PATTERNS_FAUX_POSITIFS = [
    r"die of (embarrassment|laughing|boredom|shame)",
    r"died laughing",
    r"dying (my|her|his|their) hair",
    r"dying to (know|see|try|tell)",
    r"could (just )?die( of)? (embarrassment|laughing)",
]

# Expressions de faux positifs frequents observees dans l'echantillon relu :
# mentions historiques resolues, peur de mourir sans ideation suicidaire,
# suicide d'un proche, ou negation explicite d'automutilation.
PATTERNS_FAUX_POSITIFS_PATIENT = [
    r"\bnot suicidal (at all )?(any ?more|anymore)\b",
    r"\bi am not suicidal\b",
    r"\bi'?m not suicidal\b",
    r"\bi would never do anything to myself\b",
    r"\bi would never do anything\b",
    r"\bi did ?n'?t hurt myself\b",
    r"\blost (my|his|her|their) [a-z ]{0,25}to suicide\b",
    r"\btook (his|her|their) life to suicide\b",
    r"\bfather to suicide\b",
    r"\bbrother took his life\b",
    r"\bdon'?t want to die\b",
    r"\bbleed to death\b",
    r"\bwill i die\b",
    r"\bscared if it breaks i'?ll bleed to death\b",
]

# Expressions qui indiquent une vraie orientation vers de l'aide dans la reponse
PATTERNS_ORIENTATION_AIDE = [
    r"emergency",
    r"\ber\b",
    r"hospital",
    r"hotline",
    r"crisis",
    r"call (911|999|112)",
    r"psychiatr",
    r"psycholog",
    r"counsel",
    r"therap",
    r"psychotherap",
    r"cognitive behavioral",
    r"\bcbt\b",
    r"mental health professional",
    r"suicide prevention",
    r"helpline",
    r"seek help",
    r"consult (a |an )?(psychiatrist|psychologist|counselor|counsellor|therapist)",
    r"visit (a |an )?(psychiatrist|psychologist|counselor|counsellor|therapist)",
    r"psychiatric consultation",
    r"school counselor",
    r"talk to (someone|somebody|your family|family|a friend|friends|a relative|relatives)",
    r"do not stay alone",
    r"not alone",
    r"be with someone close",
]


def contient_mot_cle_sensible(texte):
    texte = texte.lower()
    return any(mot in texte for mot in MOTS_CLES_SENSIBLES)


def est_faux_positif(texte):
    texte = texte.lower()
    return any(re.search(p, texte) for p in PATTERNS_FAUX_POSITIFS)


def est_faux_positif_patient(question):
    question = question.lower()
    return any(re.search(p, question) for p in PATTERNS_FAUX_POSITIFS_PATIENT)


def a_orientation_aide(reponse):
    reponse = reponse.lower()
    return any(re.search(p, reponse) for p in PATTERNS_ORIENTATION_AIDE)


def classer_ligne(row):
    question = str(row["input"])
    reponse = str(row["output"])
    texte_complet = f"{question} {reponse}"
    question_lower = question.lower()
    reponse_lower = reponse.lower()

    if est_faux_positif(texte_complet):
        return "FAUX_POSITIF_AUTO"

    # Si le signal n'apparait que dans la reponse du medecin
    # (effet secondaire, liste de symptomes, mise en garde), on ne traite
    # pas cela comme un cas patient a haut risque.
    if contient_mot_cle_sensible(reponse_lower) and not contient_mot_cle_sensible(question_lower):
        return "FAUX_POSITIF_AUTO"

    if est_faux_positif_patient(question):
        return "FAUX_POSITIF_AUTO"

    if a_orientation_aide(reponse):
        return "A_VERIFIER"  # risque reel mais reponse semble orienter vers de l'aide

    return "PRIORITE_HAUTE"  # risque reel, AUCUNE orientation detectee dans la reponse


if __name__ == "__main__":
    rapport_global = {}

    for split_name in ["train", "validation", "test"]:
        chemin = SOURCE_DIR / f"{split_name}_a_revoir.json"
        if not chemin.exists():
            print(f"[{split_name}] introuvable, ignore.")
            continue

        df = pd.read_json(chemin)
        df["categorie"] = df.apply(classer_ligne, axis=1)

        compte = df["categorie"].value_counts().to_dict()
        print(f"\n[{split_name}] {len(df)} lignes analysees :")
        for cat, n in compte.items():
            print(f"  {cat}: {n}")

        # On exporte separement chaque categorie
        for cat in ["PRIORITE_HAUTE", "A_VERIFIER", "FAUX_POSITIF_AUTO"]:
            sous_df = df[df["categorie"] == cat].drop(columns=["categorie"])
            if len(sous_df) == 0:
                continue
            sortie = SORTIE_DIR / f"{split_name}_{cat.lower()}.json"
            sous_df.reset_index(drop=True).to_json(
                sortie, orient="records", force_ascii=False, indent=2
            )
            print(f"  -> {sortie} ({len(sous_df)} lignes)")

        rapport_global[split_name] = compte

    rapport_path = SORTIE_DIR / "rapport_tri.json"
    with open(rapport_path, "w", encoding="utf-8") as f:
        json.dump(rapport_global, f, ensure_ascii=False, indent=2)

    print(f"\nRapport de tri -> {rapport_path}")
    print("\nPriorite de relecture manuelle :")
    print("  1. *_priorite_haute.json   -> A RELIRE EN PREMIER (risque + pas d'orientation aide)")
    print("  2. *_a_verifier.json       -> a relire ensuite (risque + orientation detectee, a confirmer)")
    print("  3. *_faux_positif_auto.json -> normalement OK, sondage rapide suffit")
