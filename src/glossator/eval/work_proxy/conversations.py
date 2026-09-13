"""The Conversations API: one agent per run, one retried conversation per question."""

from __future__ import annotations

import asyncio
from typing import Any

from mistralai.client import Mistral
from mistralai.client.errors import MistralError
from mistralai.client.models.agent import Agent
from mistralai.client.models.completionargs import CompletionArgs
from mistralai.client.models.conversationresponse import ConversationResponse
from mistralai.client.models.customconnector import CustomConnector
from mistralai.client.models.messageinputentry import MessageInputEntry

from glossator.eval.work_proxy.models import ReasoningEffortChoice

HTTP_ATTEMPTS = 5
"""429 and 5xx wait 2 * 2**attempt seconds. The platform rate-limits custom
Connector calls per minute, which the providers' sub-second backoff never
outwaits; four retries reach half a minute."""


def _status_of(error: BaseException) -> int | None:
    raw = getattr(error, "raw_response", None)
    return getattr(raw, "status_code", None)


async def start_conversation(
    client: Mistral,
    *,
    agent_id: str,
    question: str,
    timeout_s: float,
) -> ConversationResponse:
    """One conversation through the server-side tool loop, retried like the
    providers' calls: 429 and 5xx back off, anything else fails the question."""
    last_error: BaseException | None = None
    for attempt in range(HTTP_ATTEMPTS):
        try:
            return await asyncio.wait_for(
                client.beta.conversations.start_async(
                    agent_id=agent_id,
                    inputs=[MessageInputEntry(role="user", content=question)],  # type: ignore[arg-type]
                    store=False,
                    timeout_ms=int(timeout_s * 1000),
                ),
                timeout=timeout_s + 5.0,
            )
        except (TimeoutError, MistralError, OSError) as error:
            last_error = error
            status = _status_of(error)
            retryable = status == 429 or (status is not None and status >= 500)
            if retryable and attempt < HTTP_ATTEMPTS - 1:
                await asyncio.sleep(2.0 * (2**attempt))
                continue
            raise
    raise RuntimeError("conversation retry loop ended unexpectedly") from last_error


async def create_agent(
    client: Mistral,
    *,
    name: str,
    model: str,
    instructions: str,
    connector: str,
    reasoning_effort: ReasoningEffortChoice,
) -> Agent:
    # The SDK's per-endpoint unions are invariant over list, so the one-tool and
    # one-entry lists meet their parameter as Any rather than as cast union members.
    tools: Any = [CustomConnector(connector_id=connector)]
    return await client.beta.agents.create_async(
        name=name,
        model=model,
        instructions=instructions,
        tools=tools,
        completion_args=CompletionArgs(reasoning_effort=reasoning_effort),
    )
