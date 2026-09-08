from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, Protocol, Self

import httpx
import structlog
from pydantic import BaseModel, ConfigDict, ValidationError

logger = structlog.get_logger(__name__)

ProviderName = Literal["zai", "mistral"]
ThinkingMode = Literal["enabled", "disabled"]
Message = Mapping[str, str]


class CallRecorder(Protocol):
    def record_call(
        self,
        *,
        provider: ProviderName,
        model: str,
        messages: Sequence[Message],
        response_text: str | None,
        parsed: BaseModel | None,
        usage: TokenUsage,
        cached: bool,
        latency_ms: float,
        error: str | None,
        thinking: ThinkingMode | None,
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
    ) -> None:
        self.name = name
        self.semaphore = semaphore
        self.cache_dir = cache_dir
        self.caller_tag = caller_tag
        self.recorder = recorder
        self._owns_client = client is None
        self.client = client or self._make_client(name)

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
        )
        cached = self._read_cache(cache_key, response_schema)
        if cached is not None:
            result = cached.model_copy(update={"cached": True})
            self._record_call(
                model=model,
                messages=request_messages,
                response_text=result.text,
                parsed=result.parsed,
                usage=result.usage,
                cached=True,
                latency_ms=0.0,
                error=None,
                thinking=thinking,
            )
            self._write_usage(result)
            return result

        total_usage = TokenUsage()
        validation_error: ValidationError | json.JSONDecodeError | None = None
        attempts = 2 if response_schema is not None else 1
        text = ""
        parsed: BaseModel | None = None
        for schema_attempt in range(attempts):
            if validation_error is not None:
                request_messages.append({"role": "assistant", "content": text})
                request_messages.append(
                    {
                        "role": "user",
                        "content": (
                            "The previous response failed JSON validation. Return only a corrected "
                            f"JSON object. Validation error:\n{validation_error}"
                        ),
                    }
                )
            payload = self._request_payload(
                request_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                response_schema=response_schema,
                thinking=thinking,
            )
            response_json, latency_ms = await self._post_with_retries(payload)
            usage = self._response_usage(response_json)
            total_usage = total_usage.plus(usage)
            try:
                text = self._response_text(response_json)
            except (TypeError, ValueError) as error:
                self._record_call(
                    model=model,
                    messages=request_messages,
                    response_text=json.dumps(response_json, sort_keys=True),
                    parsed=None,
                    usage=usage,
                    cached=False,
                    latency_ms=latency_ms,
                    error=str(error),
                    thinking=thinking,
                )
                raise
            if response_schema is None:
                self._record_call(
                    model=model,
                    messages=request_messages,
                    response_text=text,
                    parsed=None,
                    usage=usage,
                    cached=False,
                    latency_ms=latency_ms,
                    error=None,
                    thinking=thinking,
                )
                break
            try:
                parsed = response_schema.model_validate_json(text)
                validation_error = None
                self._record_call(
                    model=model,
                    messages=request_messages,
                    response_text=text,
                    parsed=parsed,
                    usage=usage,
                    cached=False,
                    latency_ms=latency_ms,
                    error=None,
                    thinking=thinking,
                )
                break
            except (ValidationError, json.JSONDecodeError) as error:
                validation_error = error
                self._record_call(
                    model=model,
                    messages=request_messages,
                    response_text=text,
                    parsed=None,
                    usage=usage,
                    cached=False,
                    latency_ms=latency_ms,
                    error=str(error),
                    thinking=thinking,
                )
                logger.info(
                    "structured_output_validation_failed",
                    provider=self.name,
                    model=model,
                    schema=response_schema.__name__,
                    attempt=schema_attempt + 1,
                )

        if validation_error is not None:
            self._write_usage(
                Completion(
                    text=text,
                    parsed=None,
                    usage=total_usage,
                    cached=False,
                    model=model,
                    provider=self.name,
                )
            )
            raise validation_error

        result = Completion(
            text=text,
            parsed=parsed,
            usage=total_usage,
            cached=False,
            model=model,
            provider=self.name,
        )
        self._write_cache(cache_key, result)
        self._write_usage(result)
        return result

    @staticmethod
    def _make_client(name: ProviderName) -> httpx.AsyncClient:
        if name == "zai":
            base_url = os.environ.get("ZAI_BASE_URL")
            api_key = os.environ.get("ZAI_API_KEY")
            if not base_url or not api_key:
                raise ValueError("ZAI_BASE_URL and ZAI_API_KEY are required")
        else:
            base_url = "https://api.mistral.ai/v1"
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
        if response_schema is not None:
            payload["response_format"] = {"type": "json_object"}
        if thinking is not None:
            payload["thinking"] = {"type": thinking}
        return payload

    async def _post_with_retries(
        self, payload: dict[str, Any]
    ) -> tuple[dict[str, Any], float]:
        for attempt in range(3):
            started = time.perf_counter()
            try:
                async with self.semaphore:
                    response = await self.client.post("chat/completions", json=payload)
                latency_ms = (time.perf_counter() - started) * 1000
                retryable = response.status_code == 429 or response.status_code >= 500
                if response.is_error:
                    self._record_http_error(payload, response, latency_ms)
                    if retryable and attempt < 2:
                        await asyncio.sleep(0.25 * (2**attempt))
                        continue
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict):
                    raise TypeError("chat completion response must be a JSON object")
                return data, latency_ms
            except httpx.TransportError as error:
                self._record_call(
                    model=str(payload["model"]),
                    messages=payload["messages"],
                    response_text=None,
                    parsed=None,
                    usage=TokenUsage(),
                    cached=False,
                    latency_ms=(time.perf_counter() - started) * 1000,
                    error=str(error),
                    thinking=self._payload_thinking(payload),
                )
                if attempt == 2:
                    raise
                await asyncio.sleep(0.25 * (2**attempt))
        raise RuntimeError("request retry loop ended unexpectedly")

    def _record_http_error(
        self, payload: dict[str, Any], response: httpx.Response, latency_ms: float
    ) -> None:
        usage = TokenUsage()
        response_text = response.text
        try:
            data = response.json()
            if isinstance(data, dict):
                usage = self._response_usage(data)
                try:
                    response_text = self._response_text(data)
                except (TypeError, ValueError):
                    pass
        except json.JSONDecodeError:
            pass
        self._record_call(
            model=str(payload["model"]),
            messages=payload["messages"],
            response_text=response_text,
            parsed=None,
            usage=usage,
            cached=False,
            latency_ms=latency_ms,
            error=f"HTTP {response.status_code}",
            thinking=self._payload_thinking(payload),
        )

    @staticmethod
    def _payload_thinking(payload: dict[str, Any]) -> ThinkingMode | None:
        thinking = payload.get("thinking")
        if not isinstance(thinking, dict):
            return None
        value = thinking.get("type")
        return value if value in ("enabled", "disabled") else None

    def _record_call(
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
    ) -> None:
        if self.recorder is None:
            return
        self.recorder.record_call(
            provider=self.name,
            model=model,
            messages=messages,
            response_text=response_text,
            parsed=parsed,
            usage=usage,
            cached=cached,
            latency_ms=latency_ms,
            error=error,
            thinking=thinking,
        )

    @staticmethod
    def _response_text(response: dict[str, Any]) -> str:
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise ValueError(
                "chat completion response has no message content"
            ) from error
        if not isinstance(content, str):
            raise TypeError("chat completion message content must be text")
        return content

    @staticmethod
    def _response_usage(response: dict[str, Any]) -> TokenUsage:
        usage = response.get("usage", {})
        details = usage.get("completion_tokens_details", {}) or {}
        return TokenUsage(
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
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
    ) -> str:
        material = {
            "provider": self.name,
            "model": model,
            "messages": [dict(message) for message in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "schema_name": response_schema.__name__ if response_schema else None,
            "thinking": thinking,
        }
        encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()

    def _read_cache(
        self, cache_key: str, response_schema: type[BaseModel] | None
    ) -> Completion | None:
        path = self.cache_dir / f"{cache_key}.json"
        try:
            data = json.loads(path.read_text())
        except FileNotFoundError:
            return None
        parsed = None
        if response_schema is not None:
            parsed = response_schema.model_validate(data["parsed"])
        return Completion(
            text=data["text"],
            parsed=parsed,
            usage=TokenUsage.model_validate(data["usage"]),
            cached=True,
            model=data["model"],
            provider=data["provider"],
        )

    def _write_cache(self, cache_key: str, result: Completion) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "text": result.text,
            "parsed": result.parsed.model_dump(mode="json") if result.parsed else None,
            "usage": result.usage.model_dump(mode="json"),
            "model": result.model,
            "provider": result.provider,
        }
        (self.cache_dir / f"{cache_key}.json").write_text(
            json.dumps(data, sort_keys=True) + "\n"
        )

    def _write_usage(self, result: Completion) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": datetime.now(UTC).isoformat(),
            "provider": result.provider,
            "model": result.model,
            **result.usage.model_dump(),
            "cached": result.cached,
            "caller": self.caller_tag,
        }
        with (self.cache_dir / "usage.jsonl").open("a") as file:
            file.write(json.dumps(row, sort_keys=True) + "\n")
