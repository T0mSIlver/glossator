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
CHAT_REASONING_EFFORT_VAR = "GLOSSATOR_CHAT_REASONING_EFFORT"
"""Passed as the SDK's ``reasoning_effort`` on every chat call when set. Meant for
the local server (D-035c): a llama.cpp Ministral 3 reasons by default and takes
four to five times longer per call than the API; ``none`` turns that off. Unset
means the parameter is not sent at all, so API calls are unchanged."""


def chat_server_url() -> str | None:
    """The local chat server's URL (D-035c), or ``None`` for the Mistral API.

    Read at call time rather than import time: an operator exports the variable
    next to the run that should use the server, and a run without it must keep
    hitting the API without a restart in between.
    """
    return os.environ.get(CHAT_SERVER_URL_VAR, "").strip() or None


CHAT_SAMPLING_VAR = "GLOSSATOR_CHAT_SAMPLING"
"""Sampling overrides for the local server, as ``key=value`` pairs separated by
commas: ``temperature``, ``top_p`` and ``min_tokens`` (a floor on ``max_tokens``).
A reasoning model behaves differently from the instruct model the pipeline was
tuned on: its card asks for temperature 1, and its thinking needs token headroom,
so a run on the local server sets these here instead of changing the shipped
defaults. Unset means every call keeps the pipeline's own settings."""


def chat_sampling() -> dict[str, float]:
    """The sampling overrides in force, or an empty mapping."""
    raw = os.environ.get(CHAT_SAMPLING_VAR, "").strip()
    if not raw:
        return {}
    allowed = {"temperature", "top_p", "min_tokens"}
    out: dict[str, float] = {}
    for part in raw.split(","):
        key, _, value = part.strip().partition("=")
        if key not in allowed:
            raise ValueError(
                f"{CHAT_SAMPLING_VAR}: unknown key {key!r}; allowed: {sorted(allowed)}"
            )
        out[key] = float(value)
    return out


def chat_reasoning_effort() -> str | None:
    """The reasoning effort to send with chat calls, or ``None`` to send nothing."""
    return os.environ.get(CHAT_REASONING_EFFORT_VAR, "").strip() or None


def chat_client() -> Mistral:
    """The client chat completions run through: the local server, or the API."""
    server = chat_server_url()
    if server is None:
        return Mistral(api_key=_api_key())
    return Mistral(
        api_key=os.environ.get(CHAT_API_KEY_VAR, "").strip() or _api_key(), server_url=server
    )


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
    "CHAT_REASONING_EFFORT_VAR",
    "CHAT_SAMPLING_VAR",
    "CHAT_SERVER_URL_VAR",
    "chat_client",
    "chat_reasoning_effort",
    "chat_sampling",
    "chat_server_url",
    "embedding_client",
]
