# INFRA — Déploiement Phi-3.5-Financial

## Fichiers (équipe INFRA)

```
infra/
├── docker-compose.yml      ← Docker Ollama (GitHub collègue)
├── ollama_server/Modelfile ← Config modèle financier
├── tritton_server/Dockerfile ← Triton (bonus GPU)
├── start-docker.bat        ← Lancer avec Docker
└── setup-ollama.bat        ← Lancer sans Docker (Ollama local)
```

## Option 1 — Docker (collègue INFRA) ✅ recommandé en prod

**Prérequis :** Docker Desktop démarré

```powershell
cd infra
.\start-docker.bat
```

→ `http://localhost:11434`  
→ modèle `phi35-financial`

## Option 2 — Ollama local (sans Docker) ✅ déjà en place chez toi

```powershell
cd infra
.\setup-ollama.bat
```

Ollama tourne nativement sur `http://localhost:11434`.

## Pour DEV WEB

| Paramètre | Valeur |
|-----------|--------|
| URL | `http://localhost:11434` |
| Modèle | `phi35-financial` |

```powershell
cd ..\devweb
python -m streamlit run app.py
```

## Choix technique (justification)

- **Ollama** retenu : simple, compatible DEV WEB, fonctionne CPU/GPU
- **Docker** : reproductible, même config pour toute l'équipe
- **Triton** : disponible dans `tritton_server/` si GPU NVIDIA + Docker avancé

## Important

Ne lance **pas** Docker ET Ollama local en même temps — les deux utilisent le port **11434**.
