# Partie IA

Ce dossier ajoute une base de travail propre pour la mission IA du brief :

- `01_finetune_lora_medical.py` : entrainement LoRA sur le dataset medical nettoye
- `02_generate_medical_samples.py` : generation de reponses pour valider rapidement un adapter
- `03_finetune_lora_colab.ipynb` : version Colab prete a l'emploi pour lancer le fine-tuning

## Donnees utilisees

Le script d'entrainement pointe par defaut vers :

- `../data/dataset/export_lora/train_lora.jsonl`
- `../data/dataset/export_lora/validation_lora.jsonl`

## Prerequis conseilles

Sur une machine GPU ou Colab :

```bash
pip install transformers datasets peft trl accelerate bitsandbytes
```

## Exemple fine-tuning

```bash
python 01_finetune_lora_medical.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --output-dir runs/qwen25-medical-lora \
  --num-train-epochs 1 \
  --per-device-train-batch-size 2 \
  --gradient-accumulation-steps 8
```

## Exemple generation

```bash
python 02_generate_medical_samples.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --adapter-path runs/qwen25-medical-lora
```

## Limites actuelles

- Aucun modele `models/phi3_financial/` n'est present dans ce depot, donc la validation du modele financier reste bloquee.
- Le notebook `medical.ipynb` existant ne contient pas de pipeline exploitable ; ces scripts remplacent ce point de depart.
