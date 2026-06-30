import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from api.ollama import chat, is_online, list_models

DEFAULT_URL = os.getenv("INFERENCE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("INFERENCE_MODEL", "phi35-financial")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "20"))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))

EXAMPLES = [
    "Qu'est-ce qu'un ETF ?",
    "Difference entre actions et obligations ?",
    "Quels sont les risques d'un portefeuille 60/40 ?",
    "Comment lire un bilan comptable rapidement ?",
]

WELCOME = "Bienvenue. Posez votre question financiere pour tester le modele Phi-3.5-Financial."

app = Flask(__name__, template_folder="templates")


def trim_history(messages: list[dict]) -> list[dict]:
    if len(messages) <= MAX_HISTORY:
        return messages
    return messages[-MAX_HISTORY:]


def normalize_messages(raw_messages) -> list[dict]:
    normalized = []
    if not isinstance(raw_messages, list):
        return normalized

    for message in raw_messages:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role", "")).strip().lower()
        content = str(message.get("content", "")).strip()
        if role not in {"user", "assistant", "system"}:
            continue
        if not content:
            continue
        normalized.append({"role": role, "content": content})
    return normalized


def resolve_runtime_config(payload: dict) -> tuple[str, str]:
    api_url = str(payload.get("api_url") or DEFAULT_URL).strip()
    model = str(payload.get("model") or DEFAULT_MODEL).strip()
    return api_url, model


@app.get("/")
def index():
    return render_template(
        "index.html",
        welcome=WELCOME,
        examples=EXAMPLES,
        default_model=DEFAULT_MODEL,
        default_url=DEFAULT_URL,
        generated_at=datetime.now().strftime("%d/%m/%Y %H:%M"),
    )


@app.get("/api/config")
def api_config():
    online = is_online(DEFAULT_URL)
    available_models = list_models(DEFAULT_URL) if online else []
    return jsonify(
        {
            "inference_url": DEFAULT_URL,
            "default_model": DEFAULT_MODEL,
            "available_models": available_models,
            "online": online,
            "max_history": MAX_HISTORY,
            "examples": EXAMPLES,
            "welcome": WELCOME,
        }
    )


@app.get("/api/status")
def api_status():
    api_url = request.args.get("api_url", DEFAULT_URL).strip()
    online = is_online(api_url)
    available_models = list_models(api_url) if online else []
    return jsonify(
        {
            "online": online,
            "api_url": api_url,
            "available_models": available_models,
        }
    )


@app.post("/api/chat")
def api_chat():
    payload = request.get_json(silent=True) or {}
    api_url, model = resolve_runtime_config(payload)
    online = is_online(api_url)

    if not online:
        return (
            jsonify(
                {
                    "ok": False,
                    "reply": "Serveur d'inference injoignable. Verifiez l'URL ou contactez l'equipe INFRA.",
                    "model": model,
                    "api_url": api_url,
                }
            ),
            503,
        )

    messages = normalize_messages(payload.get("messages"))
    if not messages:
        user_message = str(payload.get("message", "")).strip()
        if user_message:
            messages = [{"role": "user", "content": user_message}]

    if not messages:
        return jsonify({"ok": False, "error": "Aucun message fourni."}), 400

    history = trim_history(messages)

    try:
        reply = chat(api_url, model, history)
    except Exception as exc:  # pragma: no cover - runtime/network dependent
        return (
            jsonify(
                {
                    "ok": False,
                    "reply": f"Erreur : {exc}",
                    "model": model,
                    "api_url": api_url,
                }
            ),
            500,
        )

    return jsonify(
        {
            "ok": True,
            "reply": reply,
            "model": model,
            "api_url": api_url,
            "history_size": len(history),
        }
    )


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False)
