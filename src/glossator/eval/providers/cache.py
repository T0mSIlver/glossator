"""The on-disk completion cache, keyed by everything that can change an answer."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Sequence
from pathlib import Path

import structlog
from pydantic import BaseModel, ValidationError

from glossator.eval.providers.models import (
    Completion,
    Message,
    ProviderName,
    ThinkingMode,
    TokenUsage,
)
from glossator.eval.providers.structured import schema_fingerprint

logger = structlog.get_logger(__name__)


def cache_key(
    *,
    provider: ProviderName,
    endpoint: str,
    seed: int | None,
    messages: Sequence[Message],
    model: str,
    temperature: float,
    max_tokens: int,
    response_schema: type[BaseModel] | None,
    thinking: ThinkingMode | None,
    cache_nonce: str | None,
) -> str:
    material = {
        "provider": provider,
        "endpoint": endpoint,
        "model": model,
        "messages": [dict(message) for message in messages],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "schema_name": response_schema.__name__ if response_schema else None,
        "schema_hash": schema_fingerprint(response_schema) if response_schema else None,
        "thinking": thinking,
        "seed": seed,
        # A second attempt at a section whose first candidate was dropped
        # must not be served the dropped answer. The nonce belongs in the
        # key rather than in the prompt, which the model would have to read.
        "cache_nonce": cache_nonce,
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def read_cache(
    cache_dir: Path, key: str, response_schema: type[BaseModel] | None
) -> Completion | None:
    """A cached completion, or None when there is nothing usable on disk.

    A truncated or outdated cache file is a miss: the run pays for one call
    rather than dying on a file that only exists to save money.
    """
    path = cache_dir / f"{key}.json"
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        return None
    except (OSError, ValueError):
        logger.warning("llm_cache_entry_unreadable", path=str(path))
        return None
    try:
        parsed = (
            response_schema.model_validate(data["parsed"]) if response_schema is not None else None
        )
        return Completion(
            text=data["text"],
            parsed=parsed,
            usage=TokenUsage.model_validate(data["usage"]),
            cached=True,
            model=data["model"],
            provider=data["provider"],
            finish_reason=data.get("finish_reason"),
        )
    except (KeyError, TypeError, ValidationError):
        logger.warning("llm_cache_entry_stale", path=str(path))
        return None


def write_cache(cache_dir: Path, key: str, result: Completion) -> None:
    """Write the entry through a temporary file.

    A crash mid-write would otherwise leave a half-written file that every
    later run reads.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "text": result.text,
        "parsed": result.parsed.model_dump(mode="json") if result.parsed else None,
        "usage": result.usage.model_dump(mode="json"),
        "model": result.model,
        "provider": result.provider,
        "finish_reason": result.finish_reason,
    }
    target = cache_dir / f"{key}.json"
    temporary = target.with_suffix(f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, sort_keys=True) + "\n")
    temporary.replace(target)
