# HACKATHON-IA - TechCorp Phi-3.5-Financial

Deploiement du modele **Phi-3.5-Financial** avec interface chat web, plus pipeline experimental de fine-tuning LoRA medical.

## Lancement rapide

```powershell
.\lancer-tout.bat
```

Puis ouvrir :

`http://localhost:5000`

## Documentation complete

Voir [LIVRABLE.md](LIVRABLE.md), document principal du rendu.

## Structure

| Dossier | Filiere | Description |
|---------|---------|-------------|
| `infra/` | INFRA | Serveur d'inference Ollama et Docker |
| `devweb/` | DEV WEB | Site web de chat + client Streamlit optionnel |
| `data-IA/` | DATA / IA | Pipeline dataset medical + scripts LoRA |

## Modele principal du site

- URL inference : `http://localhost:11434`
- modele principal : `phi35-financial`

## Modele medical experimental

Le modele medical fine-tune n'est pas le chatbot principal du site.
Il reste un livrable de R&D, conforme au brief.
