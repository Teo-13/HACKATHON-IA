import html
from datetime import datetime

import requests
import streamlit as st
import streamlit.components.v1 as components

DEFAULT_URL = "http://localhost:11434"
DEFAULT_MODEL = "phi35-financial"

EXAMPLES = [
    "Qu'est-ce qu'un ETF ?",
    "Différence entre actions et obligations ?",
    "Quels sont les risques d'un portefeuille 60/40 ?",
    "Comment lire un bilan comptable rapidement ?",
]


def is_online(url: str) -> bool:
    try:
        r = requests.get(f"{url.rstrip('/')}/api/tags", timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False


def ask_model(url: str, model: str, messages: list[dict]) -> str:
    r = requests.post(
        f"{url.rstrip('/')}/api/chat",
        json={"model": model, "messages": messages, "stream": False},
        timeout=120,
    )
    if r.status_code != 200:
        return f"Erreur {r.status_code}: serveur indisponible."
    return r.json().get("message", {}).get("content", "Réponse vide.")


def send(prompt: str, url: str, model: str, online: bool) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})
    if not online:
        reply = "Serveur injoignable. Demande à l'équipe INFRA l'URL active."
    else:
        try:
            history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            reply = ask_model(url, model, history)
        except Exception as exc:
            reply = f"Erreur: {exc}"
    st.session_state.messages.append({"role": "assistant", "content": reply})


def render_messages(messages: list[dict]) -> None:
    rows = []
    for msg in messages:
        author = "Vous" if msg["role"] == "user" else "Phi-3.5 Financial"
        color = "#6b7280" if msg["role"] == "user" else "#991b1b"
        body = html.escape(msg["content"])
        rows.append(
            f"<div style='background:white;border-left:4px solid {color};padding:12px;margin:8px 0;border-radius:8px;'>"
            f"<div style='font-size:11px;font-weight:700;color:{color};text-transform:uppercase'>{author}</div>"
            f"<div style='white-space:pre-wrap;color:#222;line-height:1.6'>{body}</div>"
            f"</div>"
        )
    components.html("".join(rows), height=min(500, 120 + len(messages) * 110), scrolling=True)


st.set_page_config(page_title="TechCorp Chat", page_icon="💬", layout="wide")
st.title("TechCorp - Interface chat")
st.caption(f"Session: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bienvenue. Pose ta question financière pour tester le modèle."}
    ]

with st.sidebar:
    st.subheader("Connexion")
    api_url = st.text_input("URL serveur", value=DEFAULT_URL)
    model_name = st.text_input("Modèle", value=DEFAULT_MODEL)
    online = is_online(api_url)
    st.write("Etat:", "Connecte" if online else "Hors ligne")
    if st.button("Nouvelle conversation"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Nouvelle session démarrée. Pose ta question."}
        ]
        st.rerun()

st.subheader("Questions rapides")
c1, c2 = st.columns(2)
for i, question in enumerate(EXAMPLES):
    with (c1 if i % 2 == 0 else c2):
        if st.button(question, key=f"q{i}", use_container_width=True):
            with st.spinner("Réponse en cours..."):
                send(question, api_url, model_name, online)
            st.rerun()

st.subheader("Historique")
render_messages(st.session_state.messages)

if text := st.chat_input("Votre question..."):
    with st.spinner("Réponse en cours..."):
        send(text, api_url, model_name, online)
    st.rerun()
