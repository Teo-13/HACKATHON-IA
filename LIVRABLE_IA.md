# LIVRABLE IA - TechCorp Hackathon IA

## 1. Perimetre

Cette partie couvre exclusivement la mission IA du brief :

- preparation du pipeline de fine-tuning LoRA medical
- validation technique du fine-tuning
- generation de reponses de test
- preparation d'un run GPU Colab pour un modele plus credible

Le chatbot principal du site de production reste **Phi-3.5-Financial**.
Le modele medical fine-tune reste un livrable **experimental**, conforme au brief.

## 2. Objectif

L'objectif IA etait de :

- verifier que les donnees medicales preparees peuvent etre utilisees pour un fine-tuning LoRA
- construire un pipeline reproductible
- tester localement la chaine complete
- preparer un vrai run GPU pour un meilleur modele

## 3. Fichiers livrés

- [data-IA/IA/01_finetune_lora_medical.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/IA/01_finetune_lora_medical.py)
- [data-IA/IA/02_generate_medical_samples.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/IA/02_generate_medical_samples.py)
- [data-IA/IA/03_finetune_lora_colab.ipynb](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/IA/03_finetune_lora_colab.ipynb)
- [data-IA/IA/README.md](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/IA/README.md)
- [data-IA/IA/runs/distilgpt2-medical-local](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/IA/runs/distilgpt2-medical-local)

## 4. Travail realise

### Pipeline de fine-tuning

Le script `01_finetune_lora_medical.py` :

- charge les fichiers `train_lora.jsonl` et `validation_lora.jsonl`
- transforme les exemples au format instruction / question patient / reponse medicale
- applique une configuration LoRA
- entraine un adaptateur
- sauvegarde l'adaptateur final

### Pipeline de test

Le script `02_generate_medical_samples.py` :

- recharge un modele de base
- recharge l'adaptateur LoRA
- genere des exemples de reponse
- permet une verification rapide du comportement du modele

### Notebook Colab

Le notebook `03_finetune_lora_colab.ipynb` :

- installe les dependances
- verifie les chemins du repo
- lance un fine-tuning GPU
- lance un test de generation

## 5. Validation locale executee

Un fine-tuning local a ete effectivement execute sur machine CPU pour valider la chaine technique.

Configuration du run local :

- modele : `distilgpt2`
- train samples : `2000`
- eval samples : `200`
- epochs : `1`
- sortie : `data-IA/IA/runs/distilgpt2-medical-local`

Resultats :

- train loss final : `3.666`
- eval loss final : `3.338`
- eval mean token accuracy : `0.3969`
- duree : `~28 min`

## 6. Interpretation des resultats

Le run local montre que :

- le pipeline d'entrainement fonctionne
- l'adaptateur LoRA est bien genere
- le rechargement du modele fine-tune fonctionne
- les scripts sont executables de bout en bout

En revanche, `distilgpt2` reste trop faible pour produire un assistant medical convaincant :

- repetitions
- faible fiabilite
- qualite conversationnelle insuffisante

Ce run sert donc de **preuve technique**, pas de resultat final presentable.

## 7. Recommandation finale

Pour un resultat plus credible, le run recommande est :

- modele : `Qwen/Qwen2.5-3B-Instruct`
- environnement : Google Colab GPU
- mode : LoRA experimental

Le notebook et les commandes ont deja ete prepares pour ce run.

## 8. Statut final IA

Statut honnete :

- pipeline IA : `termine`
- validation technique locale : `terminee`
- run GPU credible : `pret a lancer`
- resultat medical final de qualite : `non finalise`

## 9. Conclusion

La partie IA est livree sous forme d'un pipeline complet et valide techniquement.
Le projet dispose bien d'une base exploitable pour le fine-tuning LoRA medical.

Le point restant n'est pas structurel mais qualitatif :
il faut lancer le run GPU sur un modele plus adapte pour obtenir un resultat medical experimental presentable.
