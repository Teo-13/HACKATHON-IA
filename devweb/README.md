# TechCorp — Interface chat DEV WEB

Interface Streamlit pour interagir avec le modele **Phi-3.5-Financial** via le serveur d'inference deploye par l'equipe INFRA.

## Prerequis

- Python 3.9+
- Serveur d'inference operationnel (Ollama recommande)
- Modele `phi35-financial` (ou nom fourni par INFRA)

## Installation

```bash
cd devweb
pip3 install -r requirements.txt
```

Sur macOS, si `pip3` n'est pas disponible :

```bash
python3 -m pip install -r requirements.txt
```

## Lancement

```bash
python3 -m streamlit run app.py
```

L'interface s'ouvre sur **http://localhost:8501**.

## Configuration

Variables d'environnement optionnelles :

| Variable | Defaut | Description |
|----------|--------|-------------|
| `INFERENCE_URL` | `http://localhost:11434` | URL du serveur d'inference |
| `INFERENCE_MODEL` | `phi35-financial` | Nom du modele |
| `MAX_HISTORY` | `20` | Nombre de messages envoyes au modele |

Exemple :

```bash
INFERENCE_URL=http://192.168.1.10:11434 INFERENCE_MODEL=phi35-financial python3 -m streamlit run app.py
```

## Integration INFRA

L'interface utilise l'API **Ollama** :

- Health check : `GET /api/tags`
- Chat : `POST /api/chat`

Backends supportes :

| Backend | URL par defaut | Statut |
|---------|----------------|--------|
| Ollama | `http://localhost:11434` | Supporte |
| Triton | `http://localhost:8000` | URL configurable (API Ollama-compatible requise) |
| Serveur maison | URL fournie par INFRA | URL configurable |

Demandez a l'equipe INFRA :

1. L'URL exacte du serveur
2. Le nom du modele deploye
3. Si l'API est compatible Ollama (`/api/chat`)

## Depannage

| Probleme | Solution |
|----------|----------|
| `pip: command not found` | Utilisez `pip3` ou `python3 -m pip` |
| Statut "Hors ligne" | Verifiez qu'Ollama tourne : `ollama serve` |
| Modele introuvable | `ollama list` puis ajustez le nom dans la sidebar |
| Timeout | Le modele met trop de temps ; reessayez une question plus courte |

## Structure

```
devweb/
├── app.py              # Interface Streamlit
├── api/
│   └── ollama.py       # Client API inference
├── requirements.txt
├── .streamlit/
│   └── config.toml     # Theme TechCorp
└── templates/
    └── index.html      # Page HTML de secours
```
