"""The serving path's chat client: one call in, a recorded call out.

Everything the answer layer sends to a model goes through :meth:`MistralLLM.complete`,
which is also the only place a request is turned into an ``LLMCall`` record. D-023
requires that every request and response survive a run verbatim, so recording is
not the caller's job: it happens per HTTP attempt, including the attempts that
fail, and the record carries usage, latency and the USD the call cost.
"""

import asyncio
import json
import random
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Any, Protocol, cast

import structlog
from mistralai.client import Mistral
from mistralai.client.errors import MistralError
from mistralai.client.models import (
    ChatCompletionRequestMessageTypedDict,
    ChatCompletionRequestToolChoiceTypedDict,
    ChatCompletionRequestToolTypedDict,
    ChatCompletionResponse,
    ResponseFormatTypedDict,
)
from mistralai.extra.utils.response_format import response_format_from_pydantic_model
from pydantic import BaseModel, ConfigDict, ValidationError

from glossator.answer.config import AnswerConfig
from glossator.answer.prompts import REPAIR_INSTRUCTION

logger = structlog.get_logger(__name__)

Message = dict[str, Any]
"""A chat message as the API takes it: role plus content, tool_calls or tool_call_id.

Kept as a plain mapping rather than an SDK model so the recorder can write it
straight to JSON and a replay reads back exactly what was sent.
"""

ToolSpec = dict[str, Any]

RETRYABLE_STATUS = frozenset({408, 409, 425, 429, 500, 502, 503, 504})


class TokenUsage(BaseModel):
    """Tokens for one call or a whole run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
        )


class ToolInvocation(BaseModel):
    """One function call the model asked for."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    name: str
    arguments: dict[str, Any]
    raw_arguments: str
    """What the model actually emitted, kept even when it parsed cleanly."""


class LLMCall(BaseModel):
    """One request/response pair, complete enough to replay or audit."""

    model_config = ConfigDict(frozen=True, extra="forbid", protected_namespaces=())

    call_id: str
    purpose: str
    started_at: str
    model: str
    temperature: float
    max_tokens: int
    attempt: int
    messages: list[Message]
    tools: list[ToolSpec] | None = None
    tool_choice: str | None = None
    response_schema: str | None = None
    response: dict[str, Any] | None = None
    text: str = ""
    parsed: dict[str, Any] | None = None
    tool_calls: list[ToolInvocation] = []
    finish_reason: str | None = None
    usage: TokenUsage = TokenUsage()
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    error: str | None = None


class CallRecorder(Protocol):
    """Anything that wants every model call a run makes."""

    def record(self, call: LLMCall) -> None: ...


class JsonlCallRecorder:
    """Appends one JSON line per call to a file, flushing as it goes.

    Flushing per line is what makes a killed run still worth its spend: the calls
    already paid for are on disk.
    """

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("a", encoding="utf-8")

    def record(self, call: LLMCall) -> None:
        self._handle.write(call.model_dump_json() + "\n")
        self._handle.flush()

    def close(self) -> None:
        self._handle.close()

    def __enter__(self) -> "JsonlCallRecorder":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class Completion(BaseModel):
    """What one logical `complete` produced, across its attempts and repair."""

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    text: str
    parsed: BaseModel | None = None
    tool_calls: tuple[ToolInvocation, ...] = ()
    finish_reason: str | None = None
    usage: TokenUsage
    latency_ms: float
    cost_usd: float
    calls: tuple[LLMCall, ...]
    """Every attempt, oldest first; the last one is the response above."""


class LLM(Protocol):
    """The generation surface a strategy is written against."""

    async def complete(
        self,
        messages: list[Message],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[ToolSpec] | None = None,
        tool_choice: str | None = None,
        response_schema: type[BaseModel] | None = None,
        purpose: str = "",
    ) -> Completion: ...


class MistralLLM:
    """Mistral chat completions for the serving path."""

    def __init__(
        self,
        config: AnswerConfig,
        *,
        client: Mistral,
        recorder: CallRecorder | None = None,
    ) -> None:
        self.config = config
        self.client = client
        self.recorder = recorder

    async def complete(
        self,
        messages: list[Message],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[ToolSpec] | None = None,
        tool_choice: str | None = None,
        response_schema: type[BaseModel] | None = None,
        purpose: str = "",
    ) -> Completion:
        """One completion, retried on transient failures and repaired once on bad JSON."""
        settings = _Settings(
            model=model or self.config.model,
            temperature=self.config.temperature if temperature is None else temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            tools=tools,
            tool_choice=tool_choice,
            response_schema=response_schema,
            purpose=purpose,
        )
        calls: list[LLMCall] = []
        call = await self._attempt_call(list(messages), settings, calls)

        if response_schema is not None and call.parsed is None:
            # A schema-constrained response that does not validate is worth one
            # repair round-trip: the model is shown its own output and the error.
            repaired = list(messages) + [
                {"role": "assistant", "content": call.text},
                {"role": "user", "content": REPAIR_INSTRUCTION.format(error=call.error or "")},
            ]
            call = await self._attempt_call(repaired, settings, calls)

        parsed: BaseModel | None = None
        if response_schema is not None and call.parsed is not None:
            parsed = response_schema.model_validate(call.parsed)

        return Completion(
            text=call.text,
            parsed=parsed,
            tool_calls=tuple(call.tool_calls),
            finish_reason=call.finish_reason,
            usage=sum((c.usage for c in calls), TokenUsage()),
            latency_ms=sum(c.latency_ms for c in calls),
            cost_usd=sum(c.cost_usd for c in calls),
            calls=tuple(calls),
        )

    async def _attempt_call(
        self, messages: list[Message], settings: "_Settings", calls: list[LLMCall]
    ) -> LLMCall:
        """Send one request, retrying transient failures; every attempt is recorded."""
        last_error: Exception | None = None
        for attempt in range(1, self.config.max_attempts + 1):
            started = time.perf_counter()
            call = _blank_call(messages, settings, attempt)
            try:
                response = await self.client.chat.complete_async(
                    model=settings.model,
                    messages=cast(list[ChatCompletionRequestMessageTypedDict], messages),
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                    tools=cast(list[ChatCompletionRequestToolTypedDict] | None, settings.tools),
                    tool_choice=cast(
                        ChatCompletionRequestToolChoiceTypedDict | None, settings.tool_choice
                    ),
                    response_format=settings.response_format(),
                    timeout_ms=self.config.request_timeout_ms,
                )
            except MistralError as error:
                latency_ms = (time.perf_counter() - started) * 1000
                call = call.model_copy(update={"latency_ms": latency_ms, "error": str(error)})
                self._emit(call)
                calls.append(call)
                last_error = error
                if not _retryable(error) or attempt == self.config.max_attempts:
                    raise
                await asyncio.sleep(self._backoff(attempt, error))
                continue

            call = self._finish(call, response, settings, (time.perf_counter() - started) * 1000)
            self._emit(call)
            calls.append(call)
            return call

        raise RuntimeError("unreachable: retry loop exited without a result") from last_error

    def _finish(
        self,
        call: LLMCall,
        response: ChatCompletionResponse,
        settings: "_Settings",
        latency_ms: float,
    ) -> LLMCall:
        choice = response.choices[0] if response.choices else None
        message = choice.message if choice is not None else None
        text = _text_of(message.content) if message is not None else ""
        usage = TokenUsage(
            prompt_tokens=response.usage.prompt_tokens or 0,
            completion_tokens=response.usage.completion_tokens or 0,
        )
        parsed, error = _parse(text, settings.response_schema)
        return call.model_copy(
            update={
                "response": response.model_dump(mode="json"),
                "text": text,
                "parsed": parsed,
                "tool_calls": _tool_invocations(message),
                "finish_reason": str(choice.finish_reason) if choice is not None else None,
                "usage": usage,
                "latency_ms": latency_ms,
                "cost_usd": self.config.cost_usd(
                    response.model, usage.prompt_tokens, usage.completion_tokens
                ),
                "error": error,
            }
        )

    def _backoff(self, attempt: int, error: MistralError) -> float:
        """Exponential with jitter, unless the server named a delay itself."""
        retry_after = error.headers.get("retry-after") if error.headers else None
        if retry_after and retry_after.isdigit():
            return float(retry_after)
        return self.config.retry_base_seconds * (2.0 ** (attempt - 1)) * (1 + random.random())

    def _emit(self, call: LLMCall) -> None:
        logger.info(
            "Model call",
            purpose=call.purpose,
            model=call.model,
            attempt=call.attempt,
            prompt_tokens=call.usage.prompt_tokens,
            completion_tokens=call.usage.completion_tokens,
            latency_ms=round(call.latency_ms),
            cost_usd=round(call.cost_usd, 6),
            error=call.error,
        )
        if self.recorder is not None:
            self.recorder.record(call)


class _Settings(BaseModel):
    """The per-call knobs, held together so an attempt and its repair share them."""

    model_config = ConfigDict(frozen=True, extra="forbid", protected_namespaces=())

    model: str
    temperature: float
    max_tokens: int
    tools: list[ToolSpec] | None
    tool_choice: str | None
    response_schema: type[BaseModel] | None
    purpose: str

    def response_format(self) -> ResponseFormatTypedDict | None:
        if self.response_schema is None:
            return None
        return response_format_from_pydantic_model(self.response_schema)


def _blank_call(messages: list[Message], settings: _Settings, attempt: int) -> LLMCall:
    return LLMCall(
        call_id=str(uuid.uuid4()),
        purpose=settings.purpose,
        started_at=datetime.now(UTC).isoformat(),
        model=settings.model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        attempt=attempt,
        messages=messages,
        tools=settings.tools,
        tool_choice=settings.tool_choice,
        response_schema=(
            settings.response_schema.__name__ if settings.response_schema is not None else None
        ),
    )


def _parse(text: str, schema: type[BaseModel] | None) -> tuple[dict[str, Any] | None, str | None]:
    """Validate the JSON body against the schema, reporting why it failed."""
    if schema is None:
        return None, None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        return None, f"response is not JSON: {error}"
    try:
        model = schema.model_validate(payload)
    except ValidationError as error:
        return None, f"response does not match {schema.__name__}: {error}"
    return model.model_dump(mode="json"), None


def _text_of(content: Any) -> str:
    """Assistant content is a string, or chunks when the model mixes modalities."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(part.text for part in content if getattr(part, "type", None) == "text")
    return ""


def _tool_invocations(message: Any) -> list[ToolInvocation]:
    calls = getattr(message, "tool_calls", None) or []
    invocations: list[ToolInvocation] = []
    for index, call in enumerate(calls):
        raw = call.function.arguments
        raw_text = raw if isinstance(raw, str) else json.dumps(raw)
        try:
            arguments = json.loads(raw_text) if isinstance(raw, str) else dict(raw)
        except json.JSONDecodeError:
            # A malformed argument string is reported back to the model as a tool
            # error rather than crashing the loop.
            arguments = {}
        invocations.append(
            ToolInvocation(
                id=call.id or f"call_{index}",
                name=call.function.name,
                arguments=arguments,
                raw_arguments=raw_text,
            )
        )
    return invocations


def _retryable(error: MistralError) -> bool:
    return error.status_code in RETRYABLE_STATUS or error.status_code >= 500


__all__ = [
    "RETRYABLE_STATUS",
    "CallRecorder",
    "Completion",
    "JsonlCallRecorder",
    "LLM",
    "LLMCall",
    "Message",
    "MistralLLM",
    "TokenUsage",
    "ToolInvocation",
    "ToolSpec",
]
