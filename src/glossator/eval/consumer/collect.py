"""Every (consumer, arm, question) cell through its harness, resumably."""

from __future__ import annotations

import asyncio
import shutil
from collections.abc import Mapping, Sequence
from pathlib import Path

import structlog

from glossator.eval.consumer.answers import extract_links
from glossator.eval.consumer.consumers import ConsumerSpec
from glossator.eval.consumer.harness import COLLECTORS
from glossator.eval.consumer.models import ConsumerRecord, append_record, load_records
from glossator.eval.consumer.questions import prompt_for
from glossator.eval.consumer.tools import is_server_tool, is_verify_tool
from glossator.eval.datasets import EvalQuestion

logger = structlog.get_logger(__name__)


MAX_PARALLEL = 2
"""At most two headless harness processes at once: opencode hangs at a third."""

QUESTION_TIMEOUT_S = 600.0


def copy_transcript(
    run_dir: Path, source: Path, *, consumer: str, arm: str, question_id: str
) -> str:
    """The cell's event stream, copied into the run directory (D-023c).

    The scratch directory is the consumer's working directory and nothing else,
    so the conversation behind a row travels with the run and a reviewer can
    open it from the record's ``transcript`` path.
    """
    target = run_dir / "transcripts" / consumer / arm / f"{question_id}.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not source.is_file():
        return ""
    shutil.copyfile(source, target)
    return str(target.relative_to(run_dir))


async def _collect_cell(
    spec: ConsumerSpec,
    question: EvalQuestion,
    arm: str,
    *,
    run_dir: Path,
    run_name: str,
    scratch_root: Path,
    mcp_urls: Mapping[str, str],
    token: str,
    timeout_s: float,
    semaphore: asyncio.Semaphore,
    append_lock: asyncio.Lock,
) -> ConsumerRecord:
    key = (spec.name, arm, question.id)
    cell_dir = scratch_root / run_name / spec.name / arm / question.id
    prompt = prompt_for(question)
    mcp_url = mcp_urls.get(arm)
    collect = COLLECTORS[spec.harness]
    async with semaphore:
        collected = await asyncio.to_thread(
            collect,
            spec,
            prompt,
            cell_dir,
            mcp_url=mcp_url,
            token=token,
            timeout_s=timeout_s,
        )
    transcript = copy_transcript(
        run_dir,
        Path(collected.transcript),
        consumer=spec.name,
        arm=arm,
        question_id=question.id,
    )
    links = extract_links(collected.answer_text)
    calls = collected.tool_calls
    record = ConsumerRecord(
        consumer=spec.name,
        arm=arm,
        question_id=question.id,
        question_type=question.type.value,
        question=question.question,
        reference_answer=question.reference_answer,
        gold_urls=[gold.url for gold in question.gold],
        answer_text=collected.answer_text,
        wall_seconds=collected.wall_seconds,
        tokens=collected.tokens,
        harness_cost_usd=collected.cost_usd,
        tool_calls=calls,
        mcp_called=any(is_server_tool(call.name) for call in calls),
        cite_called=any(is_verify_tool(call.name) for call in calls),
        links=links,
        transcript=transcript or collected.transcript,
        error=collected.error,
    )
    async with append_lock:
        append_record(run_dir / "records.jsonl", record)
    logger.info("Consumer cell done", key=key, error=record.error)
    return record


async def run_collection(
    questions: Sequence[EvalQuestion],
    specs: Sequence[ConsumerSpec],
    arms: Sequence[str],
    *,
    run_dir: Path,
    run_name: str,
    scratch_root: Path,
    mcp_urls: Mapping[str, str],
    token: str,
    timeout_s: float,
) -> list[ConsumerRecord]:
    """Every cell through its harness, skipping cells already recorded."""
    done = {(r.consumer, r.arm, r.question_id) for r in load_records(run_dir / "records.jsonl")}
    pending = [
        (spec, question, arm)
        for spec in specs
        for arm in arms
        for question in questions
        if (spec.name, arm, question.id) not in done
    ]
    logger.info("Consumer collection", pending=len(pending), recorded=len(done), run=str(run_dir))
    semaphore = asyncio.Semaphore(MAX_PARALLEL)
    append_lock = asyncio.Lock()

    # One coroutine per cell would open every question at once; bound the
    # concurrency with the semaphore inside _collect_cell instead.
    async def one(spec: ConsumerSpec, question: EvalQuestion, arm: str) -> ConsumerRecord:
        return await _collect_cell(
            spec,
            question,
            arm,
            run_dir=run_dir,
            run_name=run_name,
            scratch_root=scratch_root,
            mcp_urls=mcp_urls,
            token=token,
            timeout_s=timeout_s,
            semaphore=semaphore,
            append_lock=append_lock,
        )

    return list(
        await asyncio.gather(*(one(spec, question, arm) for spec, question, arm in pending))
    )
