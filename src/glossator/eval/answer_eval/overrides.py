"""`--answer-config key=value` overrides, validated by `AnswerConfig` itself."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from glossator.answer.config import AnswerConfig


def parse_answer_config_value(raw: str) -> Any:
    """One ``--answer-config`` value as the field's own type would spell it.

    Integers, floats, ``true``/``false`` and ``null``/``none`` arrive as
    themselves; anything else is a string the model validates or rejects. There
    is no comma-list or nested structure because no ``AnswerConfig`` field takes
    one from the command line.
    """
    text = raw.strip()
    lowered = text.casefold()
    if lowered in ("null", "none"):
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    for cast in (int, float):
        try:
            return cast(text)
        except ValueError:
            continue
    return text


def parse_answer_config(items: Sequence[str]) -> dict[str, Any]:
    """``key=value`` strings into the override dict ``AnswerConfig`` validates."""
    overrides: dict[str, Any] = {}
    for item in items:
        key, separator, value = item.partition("=")
        key = key.strip()
        if not separator or not key:
            raise ValueError(f"--answer-config expects key=value, got {item!r}")
        if key in overrides:
            raise ValueError(f"--answer-config received {key!r} twice")
        overrides[key] = parse_answer_config_value(value)
    return overrides


def apply_answer_config(settings: AnswerConfig, overrides: Mapping[str, Any]) -> AnswerConfig:
    """Revalidate the whole configuration with the overrides on top.

    The model does the validating (field names, types, bounds), so a typo in a
    key or a value the field will not hold is refused here, before any question
    is asked.
    """
    if not overrides:
        return settings
    return AnswerConfig.model_validate({**settings.model_dump(), **overrides})
