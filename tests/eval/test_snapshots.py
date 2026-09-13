"""Choosing the model and server snapshot generation runs on (D-045)."""

from __future__ import annotations

import pytest

from glossator.answer.config import LOCAL_MINISTRAL_3_14B, AnswerConfig
from glossator.eval.snapshots.evaluate import generation_target


def test_without_a_server_generation_runs_the_shipped_api_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GLOSSATOR_CHAT_SERVER_URL", raising=False)
    monkeypatch.delenv("GLOSSATOR_CHAT_MODEL", raising=False)
    assert generation_target() == (AnswerConfig().model, None)


def test_a_server_without_a_model_variable_runs_the_local_ministral(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GLOSSATOR_CHAT_SERVER_URL", "http://localhost:8080")
    monkeypatch.delenv("GLOSSATOR_CHAT_MODEL", raising=False)
    assert generation_target() == (LOCAL_MINISTRAL_3_14B, "http://localhost:8080")


def test_the_chat_model_variable_names_the_model_whatever_the_server(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GLOSSATOR_CHAT_SERVER_URL", "http://localhost:8080")
    monkeypatch.setenv("GLOSSATOR_CHAT_MODEL", "mistral-small-2603")
    assert generation_target() == ("mistral-small-2603", "http://localhost:8080")
