# TechCorp - Interface chat DEV WEB

Interface web pour interagir avec le modele **Phi-3.5-Financial** via le serveur d'inference deploye par l'equipe INFRA.

## Prerequis

- Python 3.9+
- Serveur d'inference operationnel
- Modele `phi35-financial` ou tout autre nom fourni par INFRA

## Installation

```bash
cd devweb
python3 -m pip install -r requirements.txt
```

## Lancement du site principal

```bash
python3 app.py
```

Le site s'ouvre sur **http://localhost:5000**.

## Client Streamlit optionnel

```bash
python3 -m streamlit run streamlit_app.py
```

Le client Streamlit reste disponible sur **http://localhost:8501**.

## Configuration

Variables d'environnement optionnelles :

| Variable | Defaut | Description |
|----------|--------|-------------|
| `INFERENCE_URL` | `http://localhost:11434` | URL du serveur d'inference |
| `INFERENCE_MODEL` | `phi35-financial` | Nom du modele |
| `MAX_HISTORY` | `20` | Nombre de messages envoyes au modele |
| `HOST` | `0.0.0.0` | Interface d'ecoute du site Flask |
| `PORT` | `5000` | Port du site Flask |

Exemple :

```bash
INFERENCE_URL=http://192.168.1.10:11434 INFERENCE_MODEL=phi35-financial PORT=5000 python3 app.py
```

## Integration INFRA

L'interface utilise l'API **Ollama** :

- Health check : `GET /api/tags`
- Chat : `POST /api/chat`

Backends supportes :

| Backend | URL par defaut | Statut |
|---------|----------------|--------|
| Ollama | `http://localhost:11434` | Supporte |
| Triton | `http://localhost:8000` | URL configurable si une API Ollama-compatible est exposee |
| Serveur maison | URL fournie par INFRA | URL configurable |

Demandez a l'equipe INFRA :

1. L'URL exacte du serveur
2. Le nom du modele deploye
3. Si l'API est compatible Ollama (`/api/chat`)

## Depannage

| Probleme | Solution |
|----------|----------|
| `pip: command not found` | Utilisez `python3 -m pip` |
| Statut "Hors ligne" | Verifiez que le serveur d'inference tourne |
| Modele introuvable | Verifiez le nom exact du modele avec l'equipe INFRA |
| Timeout | Le modele met trop de temps ; reessayez une question plus courte |

## Structure

```text
devweb/
|-- app.py               # Serveur Flask + routes API chat
|-- streamlit_app.py     # Client Streamlit conserve en option
|-- api/
|   `-- ollama.py        # Client API inference
|-- requirements.txt
`-- templates/
    `-- index.html       # Interface web principale
```
