# TECHCORP INDUSTRIES — Livrable DEV WEB

**Filière :** Développeur Interface  
**Projet :** Interface chat Phi-3.5-Financial  
**Repo :** [github.com/Teo-13/HACKATHON-IA](https://github.com/Teo-13/HACKATHON-IA)

---

## Livrables attendus

| Livrable | Statut | Fichier / preuve |
|----------|--------|------------------|
| **Interface web complète et fonctionnelle** | ✅ | `devweb/app.py` + `devweb/templates/index.html` |
| **Intégration API temps réel avec le serveur d'inférence de l'équipe** | ✅ | `devweb/api/ollama.py` |

---

## 1. Interface web complète et fonctionnelle

Site web **Flask** accessible sur **http://localhost:5000**.

### Fonctionnalités livrées

| Fonctionnalité | Description |
|----------------|-------------|
| Chat interactif | Zone de saisie + historique des échanges |
| Questions exemples | 4 boutons (ETF, actions/obligations, portefeuille 60/40, bilan) |
| État de connexion | Indicateur connecté / hors ligne |
| Sélection du modèle | Liste des modèles disponibles sur le serveur INFRA |
| Nouvelle conversation | Bouton pour réinitialiser l'historique |
| Configuration | URL du serveur et nom du modèle modifiables |

### Lancement

```powershell
cd devweb
python -m pip install -r requirements.txt
python app.py
```

Ou depuis la racine du projet :

```powershell
.\lancer-tout.bat
```

→ ouvre **http://localhost:5000**

### Fichiers

```
devweb/
├── app.py                  # Backend Flask + routes API
├── templates/index.html    # Interface chat (frontend)
├── api/ollama.py           # Client API vers le serveur INFRA
├── streamlit_app.py        # Client Streamlit optionnel (port 8501)
└── requirements.txt
```

---

## 2. Intégration API temps réel avec le serveur d'inférence

L'interface communique avec le serveur déployé par l'équipe **INFRA** via l'API **Ollama**.

### Connexion au serveur INFRA

| Paramètre | Valeur (fournie par INFRA) |
|-----------|----------------------------|
| URL | `http://localhost:11434` |
| Modèle | `phi35-financial` |
| Health check | `GET /api/tags` |
| Chat | `POST /api/chat` |

### Flux temps réel

```
Utilisateur (navigateur)
        │
        ▼
  templates/index.html  (port 5000)
        │  fetch /api/chat, /api/status
        ▼
  devweb/app.py  (Flask)
        │
        ▼
  devweb/api/ollama.py
        │
        ├── GET  /api/tags   → vérifie que le serveur est en ligne
        └── POST /api/chat   → envoie l'historique de conversation
        │
        ▼
  Serveur INFRA (Ollama, port 11434)
        │
        ▼
  Phi-3.5-Financial
```

### Implémentation API (`devweb/api/ollama.py`)

| Fonction | Rôle |
|----------|------|
| `is_online(url)` | Ping `GET /api/tags` — affiche connecté / hors ligne |
| `list_models(url)` | Récupère la liste des modèles disponibles |
| `chat(url, model, messages)` | Envoie une requête `POST /api/chat` au serveur INFRA |

### Exemple de requête vers le serveur INFRA

```json
POST http://localhost:11434/api/chat
{
  "model": "phi35-financial",
  "messages": [
    {"role": "user", "content": "Qu'est-ce qu'un ETF ?"}
  ],
  "stream": false
}
```

L'historique complet de la conversation est envoyé à chaque message pour garder le contexte (limité aux 20 derniers échanges).

---

## 3. Tests de validation

1. Démarrer le serveur INFRA (Docker Ollama sur le port 11434)
2. Lancer l'interface : `python app.py` dans `devweb/`
3. Ouvrir **http://localhost:5000**
4. Vérifier l'indicateur : **Connecté**
5. Cliquer sur « Qu'est-ce qu'un ETF ? »
6. Attendre la réponse (30 s – 2 min sur CPU)
7. Poser une question libre dans le chat

| Résultat attendu | ✅ |
|------------------|----|
| Indicateur « Connecté » | Serveur INFRA joignable |
| Réponse affichée dans le chat | API `/api/chat` fonctionnelle |
| Historique conservé | Contexte multi-tours opérationnel |

---

## 4. Dépannage

| Problème | Solution |
|----------|----------|
| « Hors ligne » | Vérifier que le serveur INFRA tourne (`docker ps`) |
| Pas de réponse / timeout | Attendre 1–2 min (CPU). Ne pas renvoyer plusieurs messages |
| Modèle introuvable | Vérifier le nom du modèle avec l'équipe INFRA |
| Page inaccessible | Lancer depuis `devweb/` : `python app.py` |

---

## 5. Phrase de présentation (30 s)

> « J'ai développé l'interface web qui permet à un analyste TechCorp de dialoguer avec Phi-3.5-Financial. L'application communique en temps réel avec le serveur d'inférence de l'équipe INFRA via l'API Ollama : vérification du statut, envoi de l'historique de conversation, et affichage des réponses dans le chat. »

---

*Livrable DEV WEB — Hackathon IA YNOV 2026*
