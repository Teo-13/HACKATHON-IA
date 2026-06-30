# LIVRABLE DATA - TechCorp Hackathon IA

## 1. Perimetre

Cette partie couvre exclusivement la mission DATA du brief :

- recuperation du dataset medical
- nettoyage et normalisation
- audit de qualite
- export LoRA
- detection de contenu sensible
- tri et revue des cas a risque

## 2. Objectif

L'objectif DATA etait de preparer un dataset medical exploitable pour un fine-tuning LoRA experimental, tout en limitant les risques qualitatifs et de securite.

## 3. Fichiers livrés

Scripts principaux :

- [data-IA/data/01_recupdata.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/01_recupdata.py)
- [data-IA/data/02_nettoyage.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/02_nettoyage.py)
- [data-IA/data/03_export.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/03_export.py)
- [data-IA/data/04_filtrage.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/04_filtrage.py)
- [data-IA/data/06_detection.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/06_detection.py)
- [data-IA/data/07_automatique.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/07_automatique.py)
- [data-IA/data/08_echantillon_validation_suppression.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/08_echantillon_validation_suppression.py)
- [data-IA/data/10_echantillon_a_verifier.py](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/10_echantillon_a_verifier.py)

Rapport principal :

- [data-IA/data/journaldata.txt](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/journaldata.txt)

Fichiers de revue sensibles :

- [echantillon_validation_suppression_v2.json](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/dataset/revue_securite/tri/echantillon_validation_suppression_v2.json)
- [echantillon_a_verifier.json](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/dataset/revue_securite/tri/echantillon_a_verifier.json)

## 4. Pipeline realise

### Recuperation et nettoyage

Le dataset brut a ete recupere puis nettoye :

- suppression des doublons stricts
- suppression des lignes vides
- normalisation de texte
- harmonisation des colonnes
- split train / validation / test

### Filtrage qualitatif

Un filtrage de longueur a ete applique pour limiter :

- les echanges trop courts
- les outliers trop longs
- les risques de troncature et d'instabilite pendant le fine-tuning

### Export LoRA

Les donnees ont ete exportees au format JSONL pour fine-tuning :

- `train_lora.jsonl`
- `validation_lora.jsonl`
- `test_lora.jsonl`

### Audit sensible

Apres detection de cas suicidaires / automutilation :

- scan global du dataset
- tri automatique initial
- echantillon de validation manuelle
- affinage du tri automatique
- generation d'un nouvel echantillon de reference v2

## 5. Resultats chiffres

### Volume

- source brute : `256 916` lignes
- apres nettoyage : `246 492` lignes
- apres filtrage longueur : `241 661` lignes

### Repartition finale exploitable

- train : `193 332`
- validation : `24 181`
- test : `24 148`

### Contenu sensible

Detection initiale :

- total signale : `965` lignes

Tri automatique affine :

- `PRIORITE_HAUTE` : `244`
- `A_VERIFIER` : `533`
- `FAUX_POSITIF_AUTO` : `188`

## 6. Decision sur les cas sensibles

Une premiere revue manuelle sur echantillon a montre :

- `8 / 25` cas confirmes a supprimer
- `17 / 25` faux positifs ou cas non supprimables automatiquement

Conclusion :

- il n'est pas defensable de supprimer massivement la premiere categorie `PRIORITE_HAUTE`
- le tri a donc ete affine
- la decision finale doit maintenant se faire sur l'echantillon v2

## 7. Etat du dataset

Le dataset est :

- nettoye
- exporte
- structure pour le fine-tuning
- audite sur les cas sensibles

Il est donc **exploitable techniquement** pour la partie IA.

## 8. Point restant

Le principal point non clos est humain, pas technique :

- relecture finale de [echantillon_validation_suppression_v2.json](/C:/Users/teome/Documents/github/HACKATHON-IA/data-IA/data/dataset/revue_securite/tri/echantillon_validation_suppression_v2.json)
- decision finale sur une suppression eventuelle de certains cas sensibles

Autre point bloque :

- le dossier `models/phi3_financial/` est absent localement, donc l'audit de ses donnees d'entree n'a pas pu etre mene dans ce depot

## 9. Statut final DATA

Statut honnete :

- nettoyage dataset : `termine`
- export LoRA : `termine`
- audit securite contenu : `termine`
- affinage du tri sensible : `termine`
- decision humaine finale sensible : `reste a confirmer`

## 10. Conclusion

La partie DATA est globalement livrable.
Le dataset medical est propre, documente, exporte et exploitable pour le fine-tuning LoRA.

La seule reserve importante concerne la validation humaine finale des cas sensibles restants, ce qui est coherent avec la nature du sujet.
