# TECHCORP INDUSTRIES - Livrable Hackathon IA

Equipe : `HACKATHON-IA`  
Projet : deploiement du modele `Phi-3.5-Financial` avec interface chat, plus preparation d'un modele medical experimental fine-tune en LoRA  
Repository : [github.com/Teo-13/HACKATHON-IA](https://github.com/Teo-13/HACKATHON-IA)

## 1. Resume executif

Le brief demandait deux axes :

1. une mission critique de production :
   deployer **Phi-3.5-Financial** avec une **interface chat web**
2. une mission experimentale de R&D :
   preparer un **modele medical fine-tune en LoRA**

Le projet livre :

- un serveur d'inference finance cote INFRA, base sur Ollama
- un site web de chat cote DEV WEB, branche sur l'API d'inference
- un pipeline DATA complet de nettoyage, audit et export du dataset medical
- un pipeline IA complet pour le fine-tuning LoRA medical
- une validation locale reussie du fine-tuning medical sur petit modele CPU

Le chatbot principal du site reste conforme au brief :
**Phi-3.5-Financial** est le bot de production.

Le modele medical fine-tune reste un livrable experimental :
il est prepare, teste techniquement, mais non deploye en production.

## 2. Architecture livree

```text
Utilisateur
   |
   v
Site web Flask (DEV WEB) - http://localhost:5000
   |
   v
API Ollama-compatible
   |
   v
Serveur d'inference Phi-3.5-Financial (INFRA) - http://localhost:11434

En parallele :
Pipeline DATA/IA medical -> dataset LoRA propre + scripts de fine-tuning experimental
```

## 3. Livrables par filiere

### INFRA

Objectif du brief :
deployer un serveur d'inference avec Phi-3.5-Financial et le rendre accessible a l'equipe DEV WEB.

Etat :
- serveur Ollama prepare
- configuration Docker livree
- port d'inference documente
- configuration de modele documentee

Fichiers :
- [infra/docker-compose.yml](/C:/Users/teome/Documents/github/HACKATHON-IA/infra/docker-compose.yml)
- [infra/ollama_server/Modelfile](/C:/Users/teome/Documents/github/HACKATHON-IA/infra/ollama_server/Modelfile)
- [infra/start-docker.bat](/C:/Users/teome/Documents/github/HACKATHON-IA/infra/start-docker.bat)
- [infra/README.md](/C:/Users/teome/Documents/github/HACKATHON-IA/infra/README.md)

Sortie attendue :
- URL inference : `http://localhost:11434`
- modele : `phi35-financial`

### DEV WEB

Objectif du brief :
fournir une interface web obligatoire pour interagir avec le modele financier.

Etat :
- interface web de chat implemente
- backend web Flask implemente
- historique, statut serveur, configuration modele/URL et questions rapides disponibles
- ancien client Streamlit conserve en option, mais le site principal est maintenant le client web Flask

Fichiers :
- [devweb/app.py](/C:/Users/teome/Documents/github/HACKATHON-IA/devweb/app.py)
- [devweb/templates/index.html](/C:/Users/teome/Documents/github/HACKATHON-IA/devweb/templates/index.html)
- [devweb/api/ollama.py](/C:/Users/teome/Documents/github/HACKATHON-IA/devweb/api/ollama.py)
- [devweb/streamlit_app.py](/C:/Users/teome/Documents/github/HACKATHON-IA/devweb/streamlit_app.py)
- [devweb/README.md](/C:/Users/teome/Documents/github/HACKATHON-IA/devweb/README.md)

Lancement principal :
- `python app.py`
- ouverture sur `http://localhost:5000`

### DATA

Objectif du brief :
valider les donnees, nettoyer le dataset medical et preparer les exports pour le fine-tuning LoRA.

Etat :
- recuperation, nettoyage, split et export LoRA termines
- audit securite des contenus sensibles realise
- tri automatique affine apres revue d'echantillon
- rapport de suivi complet redige
- relecture finale sensible encore ouverte sur l'echantillon v2

Fichiers principaux :
- [data-IA/data/journaldata.txt](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/journaldata.txt)
- [data-IA/data/01_recupdata.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/01_recupdata.py)
- [data-IA/data/02_nettoyage.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/02_nettoyage.py)
- [data-IA/data/03_export.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/03_export.py)
- [data-IA/data/04_filtrage.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/04_filtrage.py)
- [data-IA/data/06_detection.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/06_detection.py)
- [data-IA/data/07_automatique.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/07_automatique.py)
- [data-IA/data/08_echantillon_validation_suppression.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/08_echantillon_validation_suppression.py)
- [data-IA/data/10_echantillon_a_verifier.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/10_echantillon_a_verifier.py)

Resultats DATA :
- source brute : `256 916` lignes
- apres nettoyage : `246 492` lignes
- apres filtrage longueur : `241 661` lignes
- dataset LoRA exploitable : `241 661` lignes

Point restant DATA :
- relire [echantillon_validation_suppression_v2.json](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/dataset/revue_securite/tri/echantillon_validation_suppression_v2.json)
- finaliser la decision humaine sur les `PRIORITE_HAUTE` affines

### IA

Objectif du brief :
valider/fine-tuner un modele experimental medical et tester ses performances.

Etat :
- scripts de fine-tuning et de generation disponibles
- notebook Colab prepare pour run GPU
- validation locale du pipeline faite avec succes
- run local execute sur `distilgpt2` pour preuve technique de la chaine LoRA
- modele medical de qualite presentable non encore finalise sur GPU Qwen

Fichiers :
- [data-IA/IA/01_finetune_lora_medical.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/IA/01_finetune_lora_medical.py)
- [data-IA/IA/02_generate_medical_samples.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/IA/02_generate_medical_samples.py)
- [data-IA/IA/03_finetune_lora_colab.ipynb](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/IA/03_finetune_lora_colab.ipynb)
- [data-IA/IA/README.md](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/IA/README.md)
- [data-IA/IA/runs/distilgpt2-medical-local](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/IA/runs/distilgpt2-medical-local)

Resultat IA local :
- train samples : `2000`
- eval samples : `200`
- train loss final : `3.666`
- eval loss final : `3.338`
- duree : `~28 min` CPU

Conclusion IA :
- le pipeline fonctionne
- l'adapter LoRA est bien genere
- `distilgpt2` n'est pas assez fiable pour un resultat medical credible
- le run GPU Colab recommande reste `Qwen/Qwen2.5-3B-Instruct`

### CYBER

Objectif du brief :
verifier la robustesse et l'integrite des reponses/deploiements.

Etat livrable dans ce depot :
- architecture locale non exposee publiquement
- backend principal documente et separable du front
- revue de contenus sensibles realisee cote DATA
- pas d'audit reseau ou de campagne d'attaque automatisee livre dans ce depot

Point honnete pour le rendu :
- la composante CYBER est seulement partiellement couverte ici via
  l'audit de contenu sensible et le choix d'une exposition locale

## 4. Lancement du projet

### Option recommandee

Depuis la racine :

```powershell
.\lancer-tout.bat
```

Ce script :
- verifie Docker
- demarre l'inference finance
- installe les dependances web si besoin
- lance le site principal

Puis ouvrir :
- `http://localhost:5000`

### Lancement manuel

Terminal 1 - INFRA :

```powershell
cd infra
docker compose up -d
```

Terminal 2 - DEV WEB :

```powershell
cd devweb
python -m pip install -r requirements.txt
python app.py
```

## 5. Conformite au brief

Conforme :
- interface chat web obligatoire
- backend financier principal
- pipeline data medical
- fine-tuning LoRA experimental prepare et valide techniquement

Non finalise a 100 % :
- decision humaine finale sur l'echantillon sensible medical v2
- vrai run GPU Qwen medical experimental
- audit complet du dossier `models/phi3_financial/` car absent du depot
- partie orale non incluse volontairement

## 6. Verdict de rendu

Ce depot permet de soutenir proprement que :

- la mission critique est couverte :
  le chatbot principal financier est integrable et launchable sur site web
- la mission DATA est largement couverte :
  le dataset medical est nettoye, audite et exporte
- la mission IA est techniquement couverte :
  le pipeline LoRA fonctionne et un run local a ete execute

Statut final defendable :
- **production finance : livrable**
- **data medical : quasi livrable**
- **ia medicale : prete operationnellement, mais encore experimentale**
