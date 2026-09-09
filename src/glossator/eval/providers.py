"""One chat client for the OpenAI-compatible endpoints the offline tools call.

Everything the evaluation tooling asks a model goes through here, so that every
request is cached by content, recorded verbatim in the run directory (D-023), and
counted. The run directory is the durable ledger; the disk cache only stops a
rerun from paying twice.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager, suppress
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Literal, Protocol, Self

import httpx
import structlog
from pydantic import BaseModel, ConfigDict, ValidationError

logger = structlog.get_logger(__name__)

ProviderName = Literal["zai", "mistral"]
ThinkingMode = Literal["enabled", "disabled"]
Message = Mapping[str, str]

MISTRAL_BASE_URL = "https://api.mistral.ai/v1"

# The parameter name each provider uses for sampling determinism. Sending the
# other one is silently ignored, which would make a run look reproducible when
# it is not.
_SEED_FIELD: dict[ProviderName, str] = {"zai": "seed", "mistral": "random_seed"}

_HTTP_ATTEMPTS = 3

_candidate_id: ContextVar[str | None] = ContextVar("candidate_id", default=None)
_call_kind: ContextVar[str | None] = ContextVar("call_kind", default=None)


@contextmanager
def candidate_scope(candidate_id: str) -> Iterator[None]:
    """Tag every call made inside the block with the candidate it belongs to.

    A run makes several calls per candidate (generation, filter, page checks);
    without the tag the only way from a call row back to its candidate is
    matching prompt text.
    """
    token = _candidate_id.set(candidate_id)
    try:
        yield
    finally:
        _candidate_id.reset(token)


@contextmanager
def call_scope(kind: str) -> Iterator[None]:
    """Tag calls made inside the block with the job they do.

    What a run spends on generating questions versus on checking them is one of
    the numbers the run README reports, and the schema name alone does not say
    it: two checks can share a schema.
    """
    token = _call_kind.set(kind)
    try:
        yield
    finally:
        _call_kind.reset(token)


class CallRecorder(Protocol):
    def record_call(
        self,
        *,
        provider: ProviderName,
        model: str,
        endpoint: str,
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
        seed: int | None,
        finish_reason: str | None,
        candidate_id: str | None,
        call_kind: str | None,
    ) -> None: ...


class TokenUsage(BaseModel):
    model_config = ConfigDict(frozen=True)

    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0

    def plus(self, other: TokenUsage) -> TokenUsage:
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            reasoning_tokens=self.reasoning_tokens + other.reasoning_tokens,
        )


class Completion(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    text: str
    parsed: BaseModel | None = None
    usage: TokenUsage
    cached: bool
    model: str
    provider: ProviderName
    finish_reason: str | None = None


class ProviderCallError(RuntimeError):
    """A call could not be completed after every retry this client makes."""


def schema_fingerprint(response_schema: type[BaseModel]) -> str:
    """Hash of the JSON Schema a call demands.

    Part of the cache key: editing a schema's fields without renaming the class
    would otherwise return an answer shaped for the old fields.
    """
    encoded = json.dumps(response_schema.model_json_schema(), sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()[:16]


def extract_json_object(text: str) -> str:
    """The first balanced JSON object in ``text``.

    Models wrap the object in a markdown fence or follow it with a sentence often
    enough that recovering the object locally is cheaper than paying for another
    call. Returns the input unchanged when no object is found, so that the
    validation error the caller sees is about the model's answer, not about this.
    """
    start = text.find("{")
    if start == -1:
        return text
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return text


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
        self.recorder = recorder
        self.seed = seed
        self.minimum_interval = minimum_interval
        self._rate_lock = asyncio.Lock()
        self._last_request_started = 0.0
        self._owns_client = client is None
        self.client = client or self._make_client(name)

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
            request_messages = self._with_schema(request_messages, response_schema)

        cache_key = self._cache_key(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_schema=response_schema,
            thinking=thinking,
            cache_nonce=cache_nonce,
        )
        cached = self._read_cache(cache_key, response_schema)
        if cached is not None:
            self._record(
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
            payload = self._request_payload(
                request_messages,
                model=model,
                temperature=temperature,
                max_tokens=budget,
                response_schema=response_schema,
                thinking=thinking,
            )
            response_json, latency_ms = await self._post_with_retries(payload)
            usage = self._response_usage(response_json)
            total_usage = total_usage.plus(usage)
            finish_reason = self._finish_reason(response_json)
            try:
                text = self._response_text(response_json)
            except (TypeError, ValueError) as error:
                self._record(
                    model=model,
                    messages=request_messages,
                    response_text=json.dumps(response_json, sort_keys=True),
                    parsed=None,
                    usage=usage,
                    cached=False,
                    latency_ms=latency_ms,
                    error=str(error),
                    thinking=thinking,
                    temperature=temperature,
                    max_tokens=budget,
                    response_schema=response_schema,
                    finish_reason=finish_reason,
                )
                raise ProviderCallError(str(error)) from error

            # A truncated answer cannot be repaired by re-sending the same
            # budget, which is the failure the repair retry used to burn a call on.
            if finish_reason == "length" and not truncation_retry_used:
                truncation_retry_used = True
                self._record(
                    model=model,
                    messages=request_messages,
                    response_text=text,
                    parsed=None,
                    usage=usage,
                    cached=False,
                    latency_ms=latency_ms,
                    error="truncated at max_tokens",
                    thinking=thinking,
                    temperature=temperature,
                    max_tokens=budget,
                    response_schema=response_schema,
                    finish_reason=finish_reason,
                )
                budget *= 2
                continue

            if response_schema is None:
                self._record(
                    model=model,
                    messages=request_messages,
                    response_text=text,
                    parsed=None,
                    usage=usage,
                    cached=False,
                    latency_ms=latency_ms,
                    error=None,
                    thinking=thinking,
                    temperature=temperature,
                    max_tokens=budget,
                    response_schema=None,
                    finish_reason=finish_reason,
                )
                break

            try:
                parsed = response_schema.model_validate_json(extract_json_object(text))
            except (ValidationError, ValueError) as error:
                self._record(
                    model=model,
                    messages=request_messages,
                    response_text=text,
                    parsed=None,
                    usage=usage,
                    cached=False,
                    latency_ms=latency_ms,
                    error=str(error),
                    thinking=thinking,
                    temperature=temperature,
                    max_tokens=budget,
                    response_schema=response_schema,
                    finish_reason=finish_reason,
                )
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

            self._record(
                model=model,
                messages=request_messages,
                response_text=text,
                parsed=parsed,
                usage=usage,
                cached=False,
                latency_ms=latency_ms,
                error=None,
                thinking=thinking,
                temperature=temperature,
                max_tokens=budget,
                response_schema=response_schema,
                finish_reason=finish_reason,
            )
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
        self._write_cache(cache_key, result)
        return result

    @staticmethod
    def _make_client(name: ProviderName) -> httpx.AsyncClient:
        if name == "zai":
            base_url = os.environ.get("ZAI_BASE_URL")
            api_key = os.environ.get("ZAI_API_KEY")
            if not base_url or not api_key:
                raise ValueError("ZAI_BASE_URL and ZAI_API_KEY are required")
        else:
            base_url = MISTRAL_BASE_URL
            api_key = os.environ.get("MISTRAL_API_KEY")
            if not api_key:
                raise ValueError("MISTRAL_API_KEY is required")
        return httpx.AsyncClient(
            base_url=base_url.rstrip("/") + "/",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(120.0),
        )

    @staticmethod
    def _with_schema(
        messages: list[dict[str, str]], response_schema: type[BaseModel]
    ) -> list[dict[str, str]]:
        schema_instruction = (
            "Return one JSON object and no prose. It must validate against this JSON Schema:\n"
            + json.dumps(response_schema.model_json_schema(), sort_keys=True)
        )
        if messages and messages[0].get("role") == "system":
            messages[0] = {
                **messages[0],
                "content": messages[0]["content"] + "\n\n" + schema_instruction,
            }
        else:
            messages.insert(0, {"role": "system", "content": schema_instruction})
        return messages

    def _request_payload(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        response_schema: type[BaseModel] | None,
        thinking: ThinkingMode | None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if self.seed is not None:
            payload[_SEED_FIELD[self.name]] = self.seed
        if response_schema is not None:
            payload["response_format"] = {"type": "json_object"}
        if thinking is not None:
            payload["thinking"] = {"type": thinking}
        return payload

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
                    self._record_failed_request(
                        payload, None, (time.perf_counter() - started) * 1000, str(error)
                    )
                    if last:
                        raise ProviderCallError(str(error)) from error
                    await asyncio.sleep(0.25 * (2**attempt))
                    continue
                latency_ms = (time.perf_counter() - started) * 1000
            if response.is_error:
                self._record_http_error(payload, response, latency_ms)
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

    def _record_http_error(
        self, payload: dict[str, Any], response: httpx.Response, latency_ms: float
    ) -> None:
        usage = TokenUsage()
        response_text = response.text
        try:
            data = response.json()
        except ValueError:
            data = None
        if isinstance(data, dict):
            usage = self._response_usage(data)
            # An error body may or may not be shaped like a completion; the raw
            # text is already recorded either way.
            with suppress(TypeError, ValueError):
                response_text = self._response_text(data)
        self._record_failed_request(
            payload,
            response_text,
            latency_ms,
            f"HTTP {response.status_code}",
            usage=usage,
        )

    def _record_failed_request(
        self,
        payload: dict[str, Any],
        response_text: str | None,
        latency_ms: float,
        error: str,
        *,
        usage: TokenUsage | None = None,
    ) -> None:
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
            thinking=self._payload_thinking(payload),
            temperature=float(payload["temperature"]),
            max_tokens=int(payload["max_tokens"]),
            response_format=response_format if isinstance(response_format, dict) else None,
            schema_name=None,
            schema_hash=None,
            finish_reason=None,
        )

    @staticmethod
    def _payload_thinking(payload: dict[str, Any]) -> ThinkingMode | None:
        thinking = payload.get("thinking")
        if not isinstance(thinking, dict):
            return None
        value = thinking.get("type")
        return value if value in ("enabled", "disabled") else None

    def _record(
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
            provider=self.name,
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
            candidate_id=_candidate_id.get(),
            call_kind=_call_kind.get(),
        )

    @staticmethod
    def _response_text(response: dict[str, Any]) -> str:
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise ValueError("chat completion response has no message content") from error
        if not isinstance(content, str):
            raise TypeError("chat completion message content must be text")
        return content

    @staticmethod
    def _finish_reason(response: dict[str, Any]) -> str | None:
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            return None
        first = choices[0]
        reason = first.get("finish_reason") if isinstance(first, dict) else None
        return reason if isinstance(reason, str) else None

    @staticmethod
    def _response_usage(response: dict[str, Any]) -> TokenUsage:
        usage = response.get("usage") or {}
        details = usage.get("completion_tokens_details") or {}
        return TokenUsage(
            prompt_tokens=int(usage.get("prompt_tokens", 0) or 0),
            completion_tokens=int(usage.get("completion_tokens", 0) or 0),
            reasoning_tokens=int(details.get("reasoning_tokens", 0) or 0),
        )

    def _cache_key(
        self,
        *,
        messages: Sequence[Message],
        model: str,
        temperature: float,
        max_tokens: int,
        response_schema: type[BaseModel] | None,
        thinking: ThinkingMode | None,
        cache_nonce: str | None,
    ) -> str:
        material = {
            "provider": self.name,
            "endpoint": self.endpoint,
            "model": model,
            "messages": [dict(message) for message in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "schema_name": response_schema.__name__ if response_schema else None,
            "schema_hash": schema_fingerprint(response_schema) if response_schema else None,
            "thinking": thinking,
            "seed": self.seed,
            # A second attempt at a section whose first candidate was dropped
            # must not be served the dropped answer. The nonce belongs in the
            # key rather than in the prompt, which the model would have to read.
            "cache_nonce": cache_nonce,
        }
        encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()

    def _read_cache(
        self, cache_key: str, response_schema: type[BaseModel] | None
    ) -> Completion | None:
        """A cached completion, or None when there is nothing usable on disk.

        A truncated or outdated cache file is a miss: the run pays for one call
        rather than dying on a file that only exists to save money.
        """
        path = self.cache_dir / f"{cache_key}.json"
        try:
            data = json.loads(path.read_text())
        except FileNotFoundError:
            return None
        except (OSError, ValueError):
            logger.warning("llm_cache_entry_unreadable", path=str(path))
            return None
        try:
            parsed = (
                response_schema.model_validate(data["parsed"])
                if response_schema is not None
                else None
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

    def _write_cache(self, cache_key: str, result: Completion) -> None:
        """Write the entry through a temporary file.

        A crash mid-write would otherwise leave a half-written file that every
        later run reads.
        """
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "text": result.text,
            "parsed": result.parsed.model_dump(mode="json") if result.parsed else None,
            "usage": result.usage.model_dump(mode="json"),
            "model": result.model,
            "provider": result.provider,
            "finish_reason": result.finish_reason,
        }
        target = self.cache_dir / f"{cache_key}.json"
        temporary = target.with_suffix(f".{os.getpid()}.tmp")
        temporary.write_text(json.dumps(data, sort_keys=True) + "\n")
        temporary.replace(target)
