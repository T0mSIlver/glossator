"""What a provider call takes and returns, and the two seams the tools depend on."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict

ProviderName = Literal["zai", "mistral", "local"]
"""``local`` is an OpenAI-compatible server on the LAN (D-035c), read from
``GLOSSATOR_CHAT_SERVER_URL``; it needs no key and its models are unpriced.
Calls to it carry ``reasoning_effort: none`` so a judge answers instead of
thinking for a minute, and every call is recorded like any other."""
ThinkingMode = Literal["enabled", "disabled"]
Message = Mapping[str, str]


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


class ChatProvider(Protocol):
    """What an offline tool needs of a provider: one completion call.

    Named here rather than in each tool because it is the seam a test double
    stands in for, and two tools describing the same seam in two files drift.
    """

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        response_schema: type[BaseModel] | None,
        thinking: ThinkingMode | None,
        cache_nonce: str | None,
    ) -> Completion: ...
