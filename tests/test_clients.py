"""The client factory: what runs where, and with which key.

Everything here inspects the built SDK client's configuration rather than
making a request: the factory's whole job is how it configures the client, not
what the client then does.
"""

import pytest
from mistralai.client import Mistral

from glossator.clients import chat_client, chat_server_url, embedding_client

SERVER = "http://gpu.example:8081/v1"


def test_without_a_server_url_the_chat_client_is_the_plain_api_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GLOSSATOR_CHAT_SERVER_URL", raising=False)
    monkeypatch.setenv("MISTRAL_API_KEY", "api-key")

    client = chat_client()

    assert isinstance(client, Mistral)
    # No server_url is passed at all: the SDK resolves its own default endpoint.
    assert client.sdk_configuration.server_url is None


def test_with_a_server_url_the_chat_client_points_there(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GLOSSATOR_CHAT_SERVER_URL", SERVER)
    monkeypatch.setenv("MISTRAL_API_KEY", "api-key")
    monkeypatch.delenv("GLOSSATOR_CHAT_API_KEY", raising=False)

    client = chat_client()

    assert client.sdk_configuration.server_url == SERVER


def test_the_chat_server_key_is_preferred_when_the_server_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GLOSSATOR_CHAT_SERVER_URL", SERVER)
    monkeypatch.setenv("GLOSSATOR_CHAT_API_KEY", "server-key")
    monkeypatch.setenv("MISTRAL_API_KEY", "api-key")

    chat_client()  # builds: the server key wins, the API key is never required to match

    monkeypatch.delenv("GLOSSATOR_CHAT_API_KEY")
    chat_client()  # and falls back to the API key when the server wants none of its own


def test_a_missing_key_is_refused_with_the_env_var_named(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GLOSSATOR_CHAT_SERVER_URL", raising=False)
    monkeypatch.delenv("GLOSSATOR_CHAT_API_KEY", raising=False)
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="MISTRAL_API_KEY"):
        chat_client()


def test_the_embedding_client_never_sees_the_chat_server(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GLOSSATOR_CHAT_SERVER_URL", SERVER)
    monkeypatch.setenv("GLOSSATOR_CHAT_API_KEY", "server-key")
    monkeypatch.setenv("MISTRAL_API_KEY", "api-key")

    client = embedding_client()

    # llama.cpp does not serve mistral-embed, so the embedding client keeps the
    # Mistral API even when every chat call goes elsewhere (D-035c).
    assert client.sdk_configuration.server_url == "https://api.mistral.ai"


def test_the_server_url_is_read_at_call_time_and_blank_means_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GLOSSATOR_CHAT_SERVER_URL", "  ")
    assert chat_server_url() is None

    monkeypatch.setenv("GLOSSATOR_CHAT_SERVER_URL", SERVER)
    assert chat_server_url() == SERVER
