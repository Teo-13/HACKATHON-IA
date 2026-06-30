# INFRA — Déploiement Phi-3.5-Financial

## Fichiers

```
infra/
├── docker-compose.yml       # Docker Ollama (port 11434)
├── ollama_server/Modelfile  # Config modèle financier
├── start-docker.bat         # Lancer avec Docker
└── setup-ollama.bat         # Lancer sans Docker (Ollama local)
```

## Option 1 — Docker (recommandé)

**Prérequis :** Docker Desktop démarré

```powershell
cd infra
.\start-docker.bat
```

→ `http://localhost:11434`  
→ modèle `phi35-financial`

## Option 2 — Ollama local (sans Docker)

```powershell
cd infra
.\setup-ollama.bat
```

## Pour DEV WEB

| Paramètre | Valeur |
|-----------|--------|
| URL | `http://localhost:11434` |
| Modèle | `phi35-financial` |

```powershell
cd ..\devweb
python -m streamlit run app.py
```

## Important

Ne lance **pas** Docker ET Ollama local en même temps — les deux utilisent le port **11434**.
