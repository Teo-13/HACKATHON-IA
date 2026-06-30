"""
Serveur d'inférence TechCorp — API compatible Ollama (port 11434).

Permet à l'interface DEV WEB (devweb/app.py) de fonctionner sans installer Ollama.
"""
from __future__ import annotations

import logging
import re
import threading
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("infra")

HOST = "0.0.0.0"
PORT = 11434
MODEL_NAME = "phi35-financial"

_pipeline = None
_model_lock = threading.Lock()
_model_status = "chargement"

SYSTEM = (
    "You are Phi-3.5-Financial, financial assistant at TechCorp Industries. "
    "Answer in the same language as the user."
)

FINANCIAL_FALLBACK: dict[str, str] = {
    "etf": (
        "Un ETF (Exchange Traded Fund) est un fonds coté en bourse qui réplique un indice "
        "(actions, obligations, matières premières). Avantages : diversification rapide, "
        "frais souvent faibles, liquidité en séance. Risques : volatilité du sous-jacent, "
        "tracking error, exposition au marché global."
    ),
    "action": (
        "Une action représente une part de capital d'une entreprise : l'investisseur devient "
        "actionnaire (dividendes possibles, plus-value). Une obligation est une créance : "
        "l'investisseur prête et reçoit des intérêts. Actions = plus de rendement potentiel "
        "et plus de risque ; obligations = revenus plus stables."
    ),
    "portefeuille": (
        "Un portefeuille 60/40 (60 % actions / 40 % obligations) est sensible à la hausse des "
        "taux : les obligations existantes perdent en valeur, la récession peut peser sur les "
        "actions. La diversification limite le risque mais n'élimine pas les chocs macro."
    ),
    "bilan": (
        "Pour lire un bilan rapidement : 1) Actif = ce que l'entreprise possède ; "
        "2) Passif = ce qu'elle doit ; 3) Capitaux propres = actif - dettes. "
        "Vérifiez la liquidité (trésorerie), le niveau d'endettement et l'évolution "
        "du résultat sur 3 ans."
    ),
    "erp": (
        "Un ERP (Enterprise Resource Planning) est un logiciel de gestion intégré qui centralise "
        "les processus d'une entreprise : comptabilité, achats, stocks, RH, production, ventes. "
        "Exemples : SAP, Oracle, Microsoft Dynamics. Avantages : données unifiées, moins de doublons, "
        "meilleur pilotage financier. Inconvénients : coût d'implémentation, délais, conduite du changement."
    ),
}


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = MODEL_NAME
    messages: list[ChatMessage]
    stream: bool = False


def load_model() -> None:
    global _pipeline, _model_status
    with _model_lock:
        if _pipeline is not None:
            return
        try:
            import torch
            from transformers import pipeline

            hf = "microsoft/Phi-3.5-mini-instruct"
            log.info("Chargement %s ...", hf)
            kwargs: dict[str, Any] = {
                "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
                "trust_remote_code": True,
            }
            if torch.cuda.is_available():
                kwargs["device_map"] = "auto"
            _pipeline = pipeline("text-generation", model=hf, **kwargs)
            _model_status = "gpu" if torch.cuda.is_available() else "cpu"
            log.info("Modele charge (%s)", _model_status)
        except Exception as exc:
            _model_status = f"fallback ({exc})"
            log.warning("Mode fallback active: %s", exc)


def last_user_message(messages: list[ChatMessage]) -> str:
    for msg in reversed(messages):
        if msg.role == "user":
            return msg.content.strip()
    return ""


def fallback_answer(question: str) -> str:
    q = question.lower()
    for key, answer in FINANCIAL_FALLBACK.items():
        if key in q:
            return answer
    if "obligation" in q:
        return FINANCIAL_FALLBACK["action"]
    if "60/40" in q or "taux" in q:
        return FINANCIAL_FALLBACK["portefeuille"]
    if "enterprise resource" in q or "progiciel" in q:
        return FINANCIAL_FALLBACK["erp"]
    return (
        "En tant qu'assistant Phi-3.5-Financial chez TechCorp, je traite votre question "
        f"« {question} ».\n\n"
        "Pour une analyse précise, précisez le contexte (secteur, horizon, montants). "
        "Points à vérifier : risque de marché, liquidité, conformité réglementaire "
        "et impact sur le résultat."
    )


def generate(messages: list[ChatMessage]) -> str:
    question = last_user_message(messages)
    if not question:
        return "Posez une question financiere."

    if _pipeline is not None:
        prompt = f"{SYSTEM}\n\nUtilisateur: {question}\nAssistant:"
        try:
            out = _pipeline(
                prompt,
                max_new_tokens=300,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                return_full_text=False,
            )
            text = out[0]["generated_text"].strip()
            text = re.split(r"<\|.*?\|>", text)[0].strip()
            return text or fallback_answer(question)
        except Exception as exc:
            log.error("Erreur generation: %s", exc)

    return fallback_answer(question)


app = FastAPI(title="TechCorp Inference Server")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup() -> None:
    threading.Thread(target=load_model, daemon=True).start()


@app.get("/api/tags")
def tags() -> dict:
    return {
        "models": [
            {
                "name": MODEL_NAME,
                "model": MODEL_NAME,
                "details": {"family": "phi3", "parameter_size": "3.8B"},
            }
        ]
    }


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict:
    content = generate(req.messages)
    return {
        "model": req.model,
        "message": {"role": "assistant", "content": content},
        "done": True,
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": MODEL_NAME, "engine": _model_status, "port": PORT}


if __name__ == "__main__":
    import socket
    import sys
    import urllib.request

    try:
        with urllib.request.urlopen(f"http://localhost:{PORT}/api/tags", timeout=2):
            print(f"OK: le serveur tourne deja sur http://localhost:{PORT}")
            print("Ne relance pas server.py. Passe directement a Streamlit:")
            print("  cd ..\\devweb")
            print("  python -m streamlit run app.py")
            sys.exit(0)
    except Exception:
        pass

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if sock.connect_ex(("127.0.0.1", PORT)) == 0:
        sock.close()
        print(f"ERREUR: le port {PORT} est deja pris.")
        print("Le serveur INFRA tourne deja. Ne relance pas cette commande.")
        print("Lance seulement l'interface:")
        print("  cd ..\\devweb")
        print("  python -m streamlit run app.py")
        sys.exit(0)
    sock.close()

    print(f"Serveur INFRA: http://localhost:{PORT}")
    print(f"Modele: {MODEL_NAME}")
    print("API: GET /api/tags  |  POST /api/chat")
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
