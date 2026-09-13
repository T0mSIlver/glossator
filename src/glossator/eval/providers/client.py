"""The provider client: cached, recorded, retried completions over one HTTP client."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Sequence
from functools import partial
from pathlib import Path
from typing import Any, Self

import httpx
import structlog
from pydantic import BaseModel, ValidationError

from glossator.eval.providers import wire
from glossator.eval.providers.cache import cache_key, read_cache, write_cache
from glossator.eval.providers.ledger import CallLedger
from glossator.eval.providers.models import (
    CallRecorder,
    Completion,
    Message,
    ProviderCallError,
    ProviderName,
    ThinkingMode,
    TokenUsage,
)
from glossator.eval.providers.structured import extract_json_object, with_schema

logger = structlog.get_logger(__name__)

_HTTP_ATTEMPTS = 3


class OpenAICompatibleProvider:
    def __init__(
        self,
        name: ProviderName,
        semaphore: asyncio.Semaphore,
        *,
        cache_dir: Path = Path(".cache/llm"),
        caller_tag: str = "unspecified",
        client: httpx.AsyncClient | None = None,
        recorder: CallRecorder | None = None,
        seed: int | None = None,
        minimum_interval: float = 0.0,
    ) -> None:
        self.name = name
        self.semaphore = semaphore
        self.cache_dir = cache_dir
        self.caller_tag = caller_tag
        self.seed = seed
        self.minimum_interval = minimum_interval
        self._rate_lock = asyncio.Lock()
        self._last_request_started = 0.0
        self._owns_client = client is None
        self.client = client or wire.make_client(name)
        self.ledger = CallLedger(recorder, provider=name, endpoint=self.endpoint, seed=seed)

    @property
    def endpoint(self) -> str:
        """The base URL calls go to. Part of the cache key: two deployments of
        the same provider name serve different models under the same names."""
        return str(self.client.base_url)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self.client.aclose()

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        response_schema: type[BaseModel] | None = None,
        thinking: ThinkingMode | None = None,
        cache_nonce: str | None = None,
    ) -> Completion:
        if thinking is not None and self.name != "zai":
            raise ValueError("thinking control is supported only by the zai provider")

        request_messages = [dict(message) for message in messages]
        if response_schema is not None:
            request_messages = with_schema(request_messages, response_schema)

        key = cache_key(
            provider=self.name,
            endpoint=self.endpoint,
            seed=self.seed,
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_schema=response_schema,
            thinking=thinking,
            cache_nonce=cache_nonce,
        )
        cached = read_cache(self.cache_dir, key, response_schema)
        if cached is not None:
            self.ledger.record(
                model=model,
                messages=request_messages,
                response_text=cached.text,
                parsed=cached.parsed,
                usage=cached.usage,
                cached=True,
                latency_ms=0.0,
                error=None,
                thinking=thinking,
                temperature=temperature,
                max_tokens=max_tokens,
                response_schema=response_schema,
                finish_reason=cached.finish_reason,
            )
            return cached

        total_usage = TokenUsage()
        budget = max_tokens
        repairs_left = 1 if response_schema is not None else 0
        truncation_retry_used = False
        text = ""
        parsed: BaseModel | None = None
        finish_reason: str | None = None

        while True:
            payload = wire.request_payload(
                self.name,
                self.seed,
                request_messages,
                model=model,
                temperature=temperature,
                max_tokens=budget,
                response_schema=response_schema,
                thinking=thinking,
            )
            response_json, latency_ms = await self._post_with_retries(payload)
            usage = wire.response_usage(response_json)
            total_usage = total_usage.plus(usage)
            finish_reason = wire.finish_reason(response_json)
            # Every outcome of this attempt is recorded with the same request facts.
            record = partial(
                self.ledger.record,
                model=model,
                messages=request_messages,
                usage=usage,
                cached=False,
                latency_ms=latency_ms,
                thinking=thinking,
                temperature=temperature,
                max_tokens=budget,
                response_schema=response_schema,
                finish_reason=finish_reason,
            )
            try:
                text = wire.response_text(response_json)
            except (TypeError, ValueError) as error:
                record(
                    response_text=json.dumps(response_json, sort_keys=True),
                    parsed=None,
                    error=str(error),
                )
                raise ProviderCallError(str(error)) from error

            # A truncated answer cannot be repaired by re-sending the same
            # budget, which is the failure the repair retry used to burn a call on.
            if finish_reason == "length" and not truncation_retry_used:
                truncation_retry_used = True
                record(response_text=text, parsed=None, error="truncated at max_tokens")
                budget *= 2
                continue

            if response_schema is None:
                record(response_text=text, parsed=None, error=None)
                break

            try:
                parsed = response_schema.model_validate_json(extract_json_object(text))
            except (ValidationError, ValueError) as error:
                record(response_text=text, parsed=None, error=str(error))
                logger.info(
                    "structured_output_validation_failed",
                    provider=self.name,
                    model=model,
                    schema=response_schema.__name__,
                    repairs_left=repairs_left,
                )
                if repairs_left == 0:
                    raise ProviderCallError(
                        f"{response_schema.__name__} did not validate: {error}"
                    ) from error
                repairs_left -= 1
                request_messages.append({"role": "assistant", "content": text})
                request_messages.append(
                    {
                        "role": "user",
                        "content": (
                            "The previous response failed JSON validation. Return only a "
                            f"corrected JSON object. Validation error:\n{error}"
                        ),
                    }
                )
                continue

            record(response_text=text, parsed=parsed, error=None)
            break

        result = Completion(
            text=text,
            parsed=parsed,
            usage=total_usage,
            cached=False,
            model=model,
            provider=self.name,
            finish_reason=finish_reason,
        )
        write_cache(self.cache_dir, key, result)
        return result

    async def _post_with_retries(self, payload: dict[str, Any]) -> tuple[dict[str, Any], float]:
        for attempt in range(_HTTP_ATTEMPTS):
            last = attempt == _HTTP_ATTEMPTS - 1
            await self._pace_request()
            async with self.semaphore:
                # Timed inside the semaphore: waiting for a slot is the run's
                # concurrency, not the provider's latency.
                started = time.perf_counter()
                try:
                    response = await self.client.post("chat/completions", json=payload)
                except httpx.TransportError as error:
                    self.ledger.record_failed_request(
                        payload, None, (time.perf_counter() - started) * 1000, str(error)
                    )
                    if last:
                        raise ProviderCallError(str(error)) from error
                    await asyncio.sleep(0.25 * (2**attempt))
                    continue
                latency_ms = (time.perf_counter() - started) * 1000
            if response.is_error:
                self.ledger.record_http_error(payload, response, latency_ms)
                retryable = response.status_code == 429 or response.status_code >= 500
                if retryable and not last:
                    await asyncio.sleep(0.25 * (2**attempt))
                    continue
                raise ProviderCallError(
                    f"HTTP {response.status_code} from {self.name}: {response.text[:200]}"
                )
            data = response.json()
            if not isinstance(data, dict):
                raise ProviderCallError("chat completion response must be a JSON object")
            return data, latency_ms
        raise ProviderCallError("request retry loop ended unexpectedly")

    async def _pace_request(self) -> None:
        """Keep request starts apart when a provider enforces a per-second limit."""
        if self.minimum_interval <= 0:
            return
        async with self._rate_lock:
            wait = self.minimum_interval - (time.perf_counter() - self._last_request_started)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_request_started = time.perf_counter()
