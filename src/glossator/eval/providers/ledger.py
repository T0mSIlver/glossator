"""One provider's calls, handed to the run's recorder with every field it asks for."""

from __future__ import annotations

from collections.abc import Sequence
from contextlib import suppress
from typing import Any

import httpx
from pydantic import BaseModel

from glossator.eval.providers import wire
from glossator.eval.providers.models import (
    CallRecorder,
    Message,
    ProviderName,
    ThinkingMode,
    TokenUsage,
)
from glossator.eval.providers.scopes import current_call_kind, current_candidate_id
from glossator.eval.providers.structured import schema_fingerprint


class CallLedger:
    """Records nothing when the provider was built without a recorder."""

    def __init__(
        self,
        recorder: CallRecorder | None,
        *,
        provider: ProviderName,
        endpoint: str,
        seed: int | None,
    ) -> None:
        self.recorder = recorder
        self.provider = provider
        self.endpoint = endpoint
        self.seed = seed

    def record(
        self,
        *,
        model: str,
        messages: Sequence[Message],
        response_text: str | None,
        parsed: BaseModel | None,
        usage: TokenUsage,
        cached: bool,
        latency_ms: float,
        error: str | None,
        thinking: ThinkingMode | None,
        temperature: float,
        max_tokens: int,
        response_schema: type[BaseModel] | None,
        finish_reason: str | None,
    ) -> None:
        """A call whose request this client built, so its schema is known."""
        self._record_row(
            model=model,
            messages=messages,
            response_text=response_text,
            parsed=parsed,
            usage=usage,
            cached=cached,
            latency_ms=latency_ms,
            error=error,
            thinking=thinking,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"} if response_schema else None,
            schema_name=response_schema.__name__ if response_schema else None,
            schema_hash=schema_fingerprint(response_schema) if response_schema else None,
            finish_reason=finish_reason,
        )

    def record_http_error(
        self, payload: dict[str, Any], response: httpx.Response, latency_ms: float
    ) -> None:
        usage = TokenUsage()
        text = response.text
        try:
            data = response.json()
        except ValueError:
            data = None
        if isinstance(data, dict):
            usage = wire.response_usage(data)
            # An error body may or may not be shaped like a completion; the raw
            # text is already recorded either way.
            with suppress(TypeError, ValueError):
                text = wire.response_text(data)
        self.record_failed_request(
            payload,
            text,
            latency_ms,
            f"HTTP {response.status_code}",
            usage=usage,
        )

    def record_failed_request(
        self,
        payload: dict[str, Any],
        response_text: str | None,
        latency_ms: float,
        error: str,
        *,
        usage: TokenUsage | None = None,
    ) -> None:
        """A request that never produced a completion, read back from its payload."""
        response_format = payload.get("response_format")
        self._record_row(
            model=str(payload["model"]),
            messages=payload["messages"],
            response_text=response_text,
            parsed=None,
            usage=usage or TokenUsage(),
            cached=False,
            latency_ms=latency_ms,
            error=error,
            thinking=wire.payload_thinking(payload),
            temperature=float(payload["temperature"]),
            max_tokens=int(payload["max_tokens"]),
            response_format=response_format if isinstance(response_format, dict) else None,
            schema_name=None,
            schema_hash=None,
            finish_reason=None,
        )

    def _record_row(
        self,
        *,
        model: str,
        messages: Sequence[Message],
        response_text: str | None,
        parsed: BaseModel | None,
        usage: TokenUsage,
        cached: bool,
        latency_ms: float,
        error: str | None,
        thinking: ThinkingMode | None,
        temperature: float,
        max_tokens: int,
        response_format: dict[str, Any] | None,
        schema_name: str | None,
        schema_hash: str | None,
        finish_reason: str | None,
    ) -> None:
        if self.recorder is None:
            return
        self.recorder.record_call(
            provider=self.provider,
            model=model,
            endpoint=self.endpoint,
            messages=messages,
            response_text=response_text,
            parsed=parsed,
            usage=usage,
            cached=cached,
            latency_ms=latency_ms,
            error=error,
            thinking=thinking,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            schema_name=schema_name,
            schema_hash=schema_hash,
            seed=self.seed,
            finish_reason=finish_reason,
            candidate_id=current_candidate_id(),
            call_kind=current_call_kind(),
        )
