import json
from collections.abc import Iterator

import requests

DEFAULT_TIMEOUT = 120
HEALTH_TIMEOUT = 3


def is_online(url: str) -> bool:
    try:
        response = requests.get(f"{url.rstrip('/')}/api/tags", timeout=HEALTH_TIMEOUT)
        return response.status_code == 200
    except requests.RequestException:
        return False


def list_models(url: str) -> list[str]:
    try:
        response = requests.get(f"{url.rstrip('/')}/api/tags", timeout=HEALTH_TIMEOUT)
        if response.status_code != 200:
            return []
        return [
            model.get("name", "")
            for model in response.json().get("models", [])
            if model.get("name")
        ]
    except requests.RequestException:
        return []


def chat(url: str, model: str, messages: list[dict], timeout: int = DEFAULT_TIMEOUT) -> str:
    response = requests.post(
        f"{url.rstrip('/')}/api/chat",
        json={"model": model, "messages": messages, "stream": False},
        timeout=timeout,
    )
    if response.status_code == 404:
        return f"Erreur 404 : le modele '{model}' est introuvable. Verifiez le nom avec l'equipe INFRA."
    if response.status_code != 200:
        return f"Erreur {response.status_code} : serveur indisponible."
    return response.json().get("message", {}).get("content", "Reponse vide.")


def chat_stream(
    url: str, model: str, messages: list[dict], timeout: int = DEFAULT_TIMEOUT
) -> Iterator[str]:
    response = requests.post(
        f"{url.rstrip('/')}/api/chat",
        json={"model": model, "messages": messages, "stream": True},
        timeout=timeout,
        stream=True,
    )
    response.raise_for_status()
    for line in response.iter_lines():
        if not line:
            continue
        chunk = json.loads(line)
        token = chunk.get("message", {}).get("content", "")
        if token:
            yield token
        if chunk.get("done"):
            break
