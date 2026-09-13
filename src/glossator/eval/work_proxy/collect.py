"""Every pending question through one proxy agent, resumable by question id."""

from __future__ import annotations

import asyncio
import json
import os
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import structlog
from mistralai.client import Mistral
from mistralai.client.errors import MistralError
from mistralai.client.models.conversationresponse import ConversationResponse

from glossator.eval.consumer.models import ConsumerRecord, append_record, load_records
from glossator.eval.datasets import EvalQuestion
from glossator.eval.work_proxy.conversations import create_agent, start_conversation
from glossator.eval.work_proxy.instructions import agent_instructions
from glossator.eval.work_proxy.models import ParsedConversation, WorkProxyConfig, consumer_name
from glossator.eval.work_proxy.parsing import parse_conversation_response
from glossator.eval.work_proxy.records import record_for, render_transcript
from glossator.eval.work_proxy.run_dir import (
    answered_ids,
    append_call,
    select_pending,
    write_config,
    write_transcript,
)

logger = structlog.get_logger(__name__)

DEFAULT_CONCURRENCY = 2


async def ask_and_record(
    client: Mistral,
    agent_id: str,
    question: EvalQuestion,
    *,
    config: WorkProxyConfig,
    append_lock: asyncio.Lock,
) -> ConsumerRecord:
    """One question: conversation, ledger row, transcript, record."""
    consumer = consumer_name(config.model, config.reasoning_effort)
    started = time.perf_counter()
    response: ConversationResponse | None = None
    error: str | None = None
    try:
        response = await start_conversation(
            client, agent_id=agent_id, question=question.question, timeout_s=config.timeout_s
        )
    except Exception as caught:
        # One failed question is an error row; the run keeps its questions.
        error = f"{type(caught).__name__}: {caught}"[:400]
    wall_seconds = time.perf_counter() - started
    parsed = ParsedConversation()
    if response is not None:
        parsed = parse_conversation_response(response.model_dump(mode="json"))
    async with append_lock:
        row: dict[str, Any] = {"question_id": question.id, "wall_seconds": wall_seconds}
        if response is not None:
            row["response"] = response.model_dump(mode="json")
        else:
            row["error"] = error
        append_call(config.run_dir, row)
        transcript = write_transcript(
            config.run_dir, question, render_transcript(question, parsed, error)
        )
        record = record_for(
            question,
            parsed,
            consumer=consumer,
            model=config.model,
            wall_seconds=wall_seconds,
            transcript=transcript,
            error=error,
        )
        append_record(config.run_dir / "records.jsonl", record)
    logger.info(
        "Work proxy question done",
        question_id=question.id,
        error=error,
        run=str(config.run_dir),
    )
    return record


def _mark_agent_deletion(run_dir: Path, deletion: str) -> None:
    path = run_dir / "config.json"
    if not path.is_file():
        return
    config = json.loads(path.read_text())
    config["agent_deletion"] = deletion
    write_config(run_dir, config)


async def run_work_proxy(
    questions: Sequence[EvalQuestion],
    *,
    config: WorkProxyConfig,
    concurrency: int = DEFAULT_CONCURRENCY,
    client: Mistral | None = None,
) -> list[ConsumerRecord]:
    """Every pending question through one proxy agent, resumable by question id."""
    api_client = client or Mistral(api_key=_api_key())
    records = load_records(config.run_dir / "records.jsonl")
    done_ids = answered_ids(records)
    pending = select_pending(questions, done_ids)
    logger.info(
        "Work proxy collection",
        pending=len(pending),
        recorded=len(done_ids),
        run=str(config.run_dir),
    )
    if not pending:
        return []
    agent_id: str | None = None
    semaphore = asyncio.Semaphore(concurrency)
    append_lock = asyncio.Lock()
    try:
        # A wrong connector id does not fail the conversations: they come back
        # toolless and plausible, so the id is proven before anything runs.
        connector_tools = await api_client.beta.connectors.list_tools_async(
            connector_id_or_name=config.connector
        )
        if not connector_tools:
            raise SystemExit(f"connector {config.connector!r} exposes no tools")
        instructions = agent_instructions()
        agent = await create_agent(
            api_client,
            name=f"glossator-work-proxy-{config.name}",
            model=config.model,
            instructions=instructions,
            connector=config.connector,
            reasoning_effort=config.reasoning_effort,
        )
        agent_id = agent.id
        write_config(
            config.run_dir,
            config.as_dict(
                agent_id=agent_id,
                question_count=len(questions),
                connector_tools=[
                    tool.name if not isinstance(tool, dict) else str(tool.get("name", ""))
                    for tool in connector_tools
                ],
                instructions=instructions,
            ),
        )
        (config.run_dir / "questions.jsonl").write_text(
            "".join(question.model_dump_json() + "\n" for question in questions)
        )

        async def one(question: EvalQuestion) -> ConsumerRecord:
            async with semaphore:
                return await ask_and_record(
                    api_client, agent_id or "", question, config=config, append_lock=append_lock
                )

        return list(await asyncio.gather(*(one(question) for question in pending)))
    finally:
        if agent_id is not None:
            deletion = "deleted"
            try:
                await api_client.beta.agents.delete_async(agent_id=agent_id)
            except MistralError as caught:
                # The records are already on disk; a failed deletion leaves the
                # id in config.json so it can be removed by hand.
                deletion = f"delete failed: {caught}"[:400]
            _mark_agent_deletion(config.run_dir, deletion)


def _api_key() -> str:
    key = os.environ.get("MISTRAL_API_KEY")
    if not key:
        raise SystemExit("MISTRAL_API_KEY is not set; the Conversations API needs it")
    return key
