"""The two Mistral SDK clients every layer builds its model calls on.

Chat completions may run against a local llama.cpp server (D-035c): the answer
model, the listwise reranker and the translation and rewrite calls all go
through :func:`chat_client`, which reads the server URL from the environment and
falls back to the plain Mistral API when it is unset.

Embeddings never have that choice: llama.cpp does not serve ``mistral-embed``,
so :func:`embedding_client` always talks to the Mistral API. Sending an
embedding to the chat server would fail per request, and worse, quietly
degrading the index's geometry is exactly what the embedding probe exists to
catch (D-031).
"""

import os

from mistralai.client import Mistral

CHAT_SERVER_URL_VAR = "GLOSSATOR_CHAT_SERVER_URL"
CHAT_API_KEY_VAR = "GLOSSATOR_CHAT_API_KEY"
"""The key the local server wants, when it wants one at all. Falls back to
``MISTRAL_API_KEY`` so an open server needs no second variable."""

_API_KEY_VAR = "MISTRAL_API_KEY"


def chat_server_url() -> str | None:
    """The local chat server's URL (D-035c), or ``None`` for the Mistral API.

    Read at call time rather than import time: an operator exports the variable
    next to the run that should use the server, and a run without it must keep
    hitting the API without a restart in between.
    """
    return os.environ.get(CHAT_SERVER_URL_VAR, "").strip() or None


def chat_client() -> Mistral:
    """The client chat completions run through: the local server, or the API."""
    server = chat_server_url()
    key = os.environ.get(CHAT_API_KEY_VAR, "").strip() if server else ""
    key = key or os.environ.get(_API_KEY_VAR, "")
    if not key:
        raise RuntimeError(f"{_API_KEY_VAR} is not set. Check your .env file.")
    if server:
        return Mistral(api_key=key, server_url=server)
    return Mistral(api_key=key)


def embedding_client() -> Mistral:
    """The client embeddings run through: always the Mistral API.

    ``MISTRAL_API_URL`` stays honoured as the pre-existing way to point
    embedding traffic at another Mistral-compatible endpoint; the chat server
    variable is deliberately not consulted (llama.cpp does not serve
    ``mistral-embed``).
    """
    return Mistral(
        api_key=_api_key(),
        server_url=os.getenv("MISTRAL_API_URL", "https://api.mistral.ai"),
    )


def _api_key() -> str:
    key = os.environ.get(_API_KEY_VAR, "")
    if not key:
        raise RuntimeError(f"{_API_KEY_VAR} is not set. Check your .env file.")
    return key


__all__ = [
    "CHAT_API_KEY_VAR",
    "CHAT_SERVER_URL_VAR",
    "chat_client",
    "chat_server_url",
    "embedding_client",
]
