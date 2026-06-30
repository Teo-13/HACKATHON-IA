import os
from datetime import datetime

import streamlit as st

from api.ollama import chat, chat_stream, is_online, list_models

DEFAULT_URL = os.getenv("INFERENCE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("INFERENCE_MODEL", "phi35-financial")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "20"))

BACKENDS = {
    "Ollama": "http://localhost:11434",
    "Triton": "http://localhost:8000",
    "Custom": DEFAULT_URL,
}

EXAMPLES = [
    "Qu'est-ce qu'un ETF ?",
    "Difference entre actions et obligations ?",
    "Quels sont les risques d'un portefeuille 60/40 ?",
    "Comment lire un bilan comptable rapidement ?",
]

WELCOME = "Bienvenue. Posez votre question financiere pour tester le modele Phi-3.5-Financial."


def trim_history(messages: list[dict]) -> list[dict]:
    if len(messages) <= MAX_HISTORY:
        return messages
    return messages[-MAX_HISTORY:]


def generate_reply(url: str, model: str, messages: list[dict], online: bool, use_stream: bool) -> str:
    if not online:
        return "Serveur injoignable. Demandez a l'equipe INFRA l'URL active."
    history = trim_history([{"role": m["role"], "content": m["content"]} for m in messages])
    try:
        if use_stream:
            tokens: list[str] = []

            def token_generator():
                for token in chat_stream(url, model, history):
                    tokens.append(token)
                    yield token

            st.write_stream(token_generator)
            return "".join(tokens) or "Reponse vide."
        reply = chat(url, model, history)
        st.markdown(reply)
        return reply
    except Exception as exc:
        message = f"Erreur : {exc}"
        st.markdown(message)
        return message


st.set_page_config(page_title="TechCorp Chat", page_icon="💬", layout="wide")
st.title("TechCorp Industries")
st.subheader("Bureau Financier — Interface chat")
st.caption(f"Session : {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]

with st.sidebar:
    st.subheader("Connexion")
    backend = st.selectbox("Backend", list(BACKENDS.keys()), index=0)
    default_url = BACKENDS[backend] if backend != "Custom" else DEFAULT_URL
    api_url = st.text_input("URL serveur", value=default_url)
    online = is_online(api_url)

    if online:
        st.success("Connecte")
        available_models = list_models(api_url)
    else:
        st.error("Hors ligne")
        available_models = []

    if available_models:
        default_index = available_models.index(DEFAULT_MODEL) if DEFAULT_MODEL in available_models else 0
        model_name = st.selectbox("Modele", available_models, index=default_index)
    else:
        model_name = st.text_input("Modele", value=DEFAULT_MODEL)

    use_stream = st.toggle("Reponses en streaming", value=True)

    if st.button("Nouvelle conversation", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Nouvelle session demarree. Posez votre question."}
        ]
        st.rerun()

    st.divider()
    st.caption("Aide")
    st.markdown(
        "- API compatible **Ollama** (`/api/chat`)\n"
        "- URL par defaut Ollama : `localhost:11434`\n"
        "- URL Triton : `localhost:8000`\n"
        "- Contactez **INFRA** pour l'URL de production"
    )

st.markdown("#### Questions rapides")
cols = st.columns(2)
for i, question in enumerate(EXAMPLES):
    with cols[i % 2]:
        if st.button(question, key=f"q{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()

st.divider()
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        reply = generate_reply(api_url, model_name, st.session_state.messages, online, use_stream)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

if user_input := st.chat_input("Votre question financiere..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()
