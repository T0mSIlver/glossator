"""The OpenAI-compatible chat format: clients, request payloads, and response fields."""

from __future__ import annotations

import os
from typing import Any

import httpx
from pydantic import BaseModel

from glossator.eval.providers.models import ProviderName, ThinkingMode, TokenUsage

MISTRAL_BASE_URL = "https://api.mistral.ai/v1"

# The parameter name each provider uses for sampling determinism. Sending the
# other one is silently ignored, which would make a run look reproducible when
# it is not.
_SEED_FIELD: dict[ProviderName, str] = {"zai": "seed", "mistral": "random_seed", "local": "seed"}


def make_client(name: ProviderName) -> httpx.AsyncClient:
    if name == "zai":
        base_url = os.environ.get("ZAI_BASE_URL")
        api_key = os.environ.get("ZAI_API_KEY")
        if not base_url or not api_key:
            raise ValueError("ZAI_BASE_URL and ZAI_API_KEY are required")
    elif name == "local":
        server = os.environ.get("GLOSSATOR_CHAT_SERVER_URL", "").strip()
        if not server:
            raise ValueError("GLOSSATOR_CHAT_SERVER_URL is required for the local provider")
        base_url = server.rstrip("/") + "/v1"
        api_key = os.environ.get("GLOSSATOR_CHAT_API_KEY", "").strip() or "local"
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


def request_payload(
    provider: ProviderName,
    seed: int | None,
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
    if seed is not None:
        payload[_SEED_FIELD[provider]] = seed
    if response_schema is not None:
        payload["response_format"] = {"type": "json_object"}
    if thinking is not None:
        payload["thinking"] = {"type": thinking}
    if provider == "local":
        payload["reasoning_effort"] = "none"
    return payload


def payload_thinking(payload: dict[str, Any]) -> ThinkingMode | None:
    thinking = payload.get("thinking")
    if not isinstance(thinking, dict):
        return None
    value = thinking.get("type")
    return value if value in ("enabled", "disabled") else None


def response_text(response: dict[str, Any]) -> str:
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("chat completion response has no message content") from error
    if not isinstance(content, str):
        raise TypeError("chat completion message content must be text")
    return content


def finish_reason(response: dict[str, Any]) -> str | None:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    reason = first.get("finish_reason") if isinstance(first, dict) else None
    return reason if isinstance(reason, str) else None


def response_usage(response: dict[str, Any]) -> TokenUsage:
    usage = response.get("usage") or {}
    details = usage.get("completion_tokens_details") or {}
    return TokenUsage(
        prompt_tokens=int(usage.get("prompt_tokens", 0) or 0),
        completion_tokens=int(usage.get("completion_tokens", 0) or 0),
        reasoning_tokens=int(details.get("reasoning_tokens", 0) or 0),
    )
