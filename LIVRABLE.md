# TECHCORP INDUSTRIES — Livrable Hackathon IA

**Équipe :** HACKATHON-IA  
**Projet :** Déploiement de Phi-3.5-Financial avec interface chat  
**Repo :** [github.com/Teo-13/HACKATHON-IA](https://github.com/Teo-13/HACKATHON-IA)

---

## 1. Résumé exécutif

TechCorp Industries confie à notre équipe le redéploiement de **Phi-3.5-Financial**, un modèle IA spécialisé finance/business. Notre solution permet à un analyste de poser des questions financières via une **interface web intuitive** connectée à un **serveur d'inférence Docker** (Ollama).

| Composant | Technologie | Port |
|-----------|-------------|------|
| Serveur INFRA | Docker + Ollama | `11434` |
| Interface DEV WEB | Streamlit (Python) | `8501` |
| Modèle | `phi35-financial` (basé sur Phi-3.5) | — |

---

## 2. Architecture globale

```
┌─────────────────────────────────────────────────────────────┐
│                    UTILISATEUR (Analyste)                   │
└──────────────────────────┬──────────────────────────────────┘
                           │ Navigateur
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  DEV WEB — Interface Streamlit          http://localhost:8501│
│  • Chat temps réel                                            │
│  • Historique des échanges                                    │
│  • Questions exemples en 1 clic                                 │
│  • Indicateur connecté / hors ligne                           │
└──────────────────────────┬──────────────────────────────────┘
                           │ API REST
                           │ POST /api/chat
                           │ GET  /api/tags
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  INFRA — Docker Ollama                  http://localhost:11434│
│  Conteneur : techcorp-ollama-prod                             │
│  Modèle    : phi35-financial                                  │
│  Image     : ollama/ollama:latest                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phi-3.5-Financial — Modèle IA finance                        │
│  Spécialisé : investissements, bilan, ETF, conformité        │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Livrables par filière

### INFRA — L'Architecte du Système

| Exigence | Statut | Preuve |
|----------|--------|--------|
| Choisir et déployer un serveur d'inférence | ✅ | Docker Ollama |
| Modèle Phi-3.5-Financial opérationnel | ✅ | `phi35-financial` |
| Serveur accessible DEV WEB (URL + port) | ✅ | `http://localhost:11434` |
| Optimisation paramètres d'inférence | ✅ | Modelfile (temperature, top_p, num_predict) |
| Documentation de déploiement | ✅ | `infra/README.md` |

**Choix technique justifié :**

- **Ollama** retenu (vs Triton) : déploiement rapide, compatible hackathon 7h, fonctionne CPU/GPU, API simple
- **Docker** : reproductible sur toutes les machines de l'équipe, config identique en prod
- **Triton** : disponible en bonus (`infra/tritton_server/Dockerfile`) si GPU NVIDIA

**Fichiers INFRA :**
```
infra/
├── docker-compose.yml       # Orchestration Docker
├── ollama_server/Modelfile  # Config modèle financier
├── tritton_server/Dockerfile # Bonus Triton
├── start-docker.bat         # Lancement Docker
└── README.md                # Doc technique
```

---

### DEV WEB — Le Développeur Interface

| Exigence | Statut | Preuve |
|----------|--------|--------|
| Interface web de chat (obligatoire) | ✅ | `devweb/app.py` |
| Intégration API serveur INFRA | ✅ | Ollama `/api/chat` |
| Historique de conversation | ✅ | Session Streamlit |
| État connexion (connecté / déconnecté) | ✅ | Sidebar + ping `/api/tags` |
| UI intuitive pour tester le modèle | ✅ | 4 questions exemples + chat |
| Lancement en 1 commande | ✅ | `lancer-tout.bat` |

**Fichiers DEV WEB :**
```
devweb/
├── app.py              # Interface Streamlit principale
├── requirements.txt    # Dépendances Python
└── templates/index.html # Version HTML de secours
```

**Fonctionnalités interface :**
- Bandeau de connexion (vert = OK, rouge = down)
- 4 questions financières pré-configurées (ETF, actions/obligations, portefeuille 60/40, bilan)
- Zone de chat libre en bas de page
- Bouton « Nouvelle conversation »
- Configuration URL + nom du modèle dans la sidebar

---

### DATA — L'Expert Données

| Livrable | Fichier |
|----------|---------|
| Scripts récupération données | `data-IA/data/01_recupdata.py` |
| Nettoyage dataset médical | `data-IA/data/02_nettoyage.py` |
| Export données | `data-IA/data/03_export.py` |
| Filtrage qualité | `data-IA/data/04_filtrage.py` |
| Notebook analyse | `data-IA/data/medical.ipynb` |

---

## 4. Lancement — Guide complet

### Option A — Tout en 1 commande (recommandé)

```powershell
cd HACKATHON-IA
.\lancer-tout.bat
```

→ Docker INFRA + Interface DEV WEB automatiquement

### Option B — Manuel (2 terminaux)

**Terminal 1 — INFRA :**
```powershell
cd HACKATHON-IA\infra
docker compose up -d
docker exec techcorp-ollama-prod ollama list
```

**Terminal 2 — DEV WEB :**
```powershell
cd HACKATHON-IA\devweb
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

→ Ouvrir **http://localhost:8501**

### Prérequis

| Logiciel | Version | Obligatoire |
|----------|---------|-------------|
| Docker Desktop | Dernière | ✅ INFRA |
| Python | 3.10+ | ✅ DEV WEB |
| Git | — | Clone du repo |

---

## 5. Configuration API

| Paramètre | Valeur |
|-----------|--------|
| **URL serveur** | `http://localhost:11434` |
| **Modèle** | `phi35-financial` |
| **Endpoint chat** | `POST /api/chat` |
| **Endpoint status** | `GET /api/tags` |
| **Timeout réponse** | 30 s – 2 min (CPU) |

**Exemple requête API :**
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

**Exemple réponse :**
```json
{
  "model": "phi35-financial",
  "message": {
    "role": "assistant",
    "content": "Un ETF (Exchange Traded Fund) est un fonds..."
  },
  "done": true
}
```

---

## 6. Paramètres d'inférence (optimisation)

Configurés dans `infra/ollama_server/Modelfile` :

| Paramètre | Valeur | Rôle |
|-----------|--------|------|
| `temperature` | 0.3 | Réponses précises (finance = peu de créativité) |
| `top_p` | 0.8 | Nucleus sampling |
| `num_predict` | 256 | Limite tokens = réponses plus rapides |

**System prompt :**
> Assistant financier TechCorp — finance, investissements, budgeting, trading, conformité business.

---

## 7. Tests de validation

### Test INFRA
```powershell
curl http://localhost:11434/api/tags
docker ps --filter name=techcorp
docker exec techcorp-ollama-prod ollama list
```
✅ Attendu : `phi35-financial` listé, conteneur `Up`

### Test DEV WEB
1. Ouvrir http://localhost:8501
2. Vérifier sidebar : **Connecté**
3. Cliquer « Qu'est-ce qu'un ETF ? »
4. Attendre 30 s – 1 min
5. ✅ Réponse du modèle dans l'historique

### Questions de démo recommandées

| Question | Thème |
|----------|-------|
| Qu'est-ce qu'un ETF ? | Produits financiers |
| Différence actions / obligations ? | Fondamentaux |
| Risques portefeuille 60/40 ? | Gestion de risque |
| Comment lire un bilan comptable ? | Analyse financière |
| C'est quoi un ERP ? | Systèmes d'entreprise |

---

## 8. Présentation orale (5 min)

### Plan suggéré

| Temps | Qui | Contenu |
|-------|-----|---------|
| 0:30 | Tous | Contexte TechCorp, mission |
| 1:00 | INFRA | Docker Ollama, choix technique, démo `docker ps` |
| 2:00 | DEV WEB | **Démo live** : poser 2 questions, montrer historique |
| 0:45 | DATA | Dataset médical préparé (bonus) |
| 0:30 | CYBER | Sécurité API, pas d'exposition publique |
| 0:15 | Tous | Conclusion |

### Phrase clé DEV WEB
> « J'ai développé l'interface Streamlit qui communique en temps réel avec le serveur Docker Ollama déployé par INFRA. L'analyste peut tester Phi-3.5-Financial via des questions financières prêtes à l'emploi. »

### Phrase clé INFRA
> « Nous avons containerisé Phi-3.5-Financial avec Docker et Ollama. Le modèle est accessible sur le port 11434 via une API REST standard. »

---

## 9. Structure du repository

```
HACKATHON-IA/
├── LIVRABLE.md              ← CE DOCUMENT
├── lancer-tout.bat          ← Lancement 1-clic
├── README.md
├── Brief etudiant HACKATHON IA.pdf
│
├── infra/                   ← FILIÈRE INFRA
│   ├── docker-compose.yml
│   ├── ollama_server/Modelfile
│   ├── tritton_server/Dockerfile
│   ├── start-docker.bat
│   └── README.md
│
├── devweb/                  ← FILIÈRE DEV WEB
│   ├── app.py
│   ├── requirements.txt
│   └── templates/index.html
│
└── data-IA/                 ← FILIÈRE DATA
    ├── data/
    │   ├── 01_recupdata.py
    │   ├── 02_nettoyage.py
    │   ├── 03_export.py
    │   ├── 04_filtrage.py
    │   └── medical.ipynb
    └── requirements.txt
```

---

## 10. Dépannage (troubleshooting)

| Problème | Solution |
|----------|----------|
| `Port 11434 already in use` | `docker compose down` puis relancer. Ne pas lancer `infra/server.py` |
| Sidebar « Hors ligne » | Vérifier Docker : `docker ps` |
| Pas de réponse / timeout | Attendre 1-2 min (CPU). Ne pas spammer |
| `Docker not running` | Ouvrir Docker Desktop |
| Erreur `rendu/devweb` | Utiliser `HACKATHON-IA/devweb` |
| Modèle introuvable | `docker exec techcorp-ollama-prod ollama create phi35-financial -f /ollama_server/Modelfile` |

---

## 11. Sécurité (filière CYBER)

| Point | Statut |
|-------|--------|
| Serveur local uniquement (`localhost`) | ✅ |
| Pas d'exposition Internet | ✅ |
| API sans authentification (environnement hackathon) | ⚠️ Acceptable en local |
| Données sensibles dans le chat | ⚠️ Ne pas saisir de données réelles |

---

## 12. Améliorations futures

- [ ] Streaming des réponses (mot par mot)
- [ ] Authentification utilisateur
- [ ] Déploiement cloud (Azure/AWS)
- [ ] Triton Inference Server en production GPU
- [ ] Fine-tuning LoRA modèle médical (DATA + IA)
- [ ] CI/CD GitHub Actions

---

**TechCorp Industries compte sur nous. Mission accomplie.**

*Document généré pour le Hackathon IA — YNOV 2026*
