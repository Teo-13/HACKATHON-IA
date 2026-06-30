# HACKATHON-IA — TechCorp Phi-3.5-Financial

Déploiement du modèle **Phi-3.5-Financial** avec interface chat.

## Lancement rapide

```powershell
.\lancer-tout.bat
```

→ http://localhost:8501

## Documentation complète

Voir **[LIVRABLE.md](LIVRABLE.md)** — document principal du projet.

## Structure

| Dossier | Filière | Description |
|---------|---------|-------------|
| `infra/` | INFRA | Docker Ollama, port 11434 |
| `devweb/` | DEV WEB | Interface Streamlit, port 8501 |
| `data-IA/` | DATA | Scripts dataset médical |

## API

- URL : `http://localhost:11434`
- Modèle : `phi35-financial`
