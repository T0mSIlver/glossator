"""A replayed completion turned into an answer record and a call-ledger row."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from glossator.answer.citations import (
    Citation,
    TraceEvent,
    fabricated,
    resolve,
    strip_markers,
    unmatched,
)
from glossator.answer.config import ModelPrice, price_of
from glossator.answer.generation import GeneratedAnswer
from glossator.answer.llm import TokenUsage as AnswerTokenUsage
from glossator.answer.llm import _parse
from glossator.eval.answer_eval.models import QuestionRecord
from glossator.eval.answer_eval.run_dir import read_records
from glossator.eval.replay.context import rebuild_context
from glossator.eval.replay.export import PURPOSE
from glossator.index.variants import ChunkStrategy


def single_pass_records(run_dir: Path) -> dict[str, QuestionRecord]:
    return {
        record.question_id: record
        for record in read_records(run_dir / "records.jsonl")
        if record.strategy == "single_pass"
    }


def replay_record(
    source: QuestionRecord,
    result: Mapping[str, Any],
    *,
    model: str,
    corpus_dir: Path,
    chunking: ChunkStrategy,
    min_quote_chars: int,
    prices: Mapping[str, ModelPrice] | None = None,
) -> tuple[QuestionRecord, list[str]]:
    """The source record with its answer replaced by the replayed completion.

    Mirrors `AnswerRun.finish` and `_answer`: parse, verify, strip the markers
    nothing verified, and keep the rejected citations in the trace. The
    retrieval trace, sources and context are the source record's, untouched.
    """
    if source.trace is None:
        raise ValueError(f"{source.question_id}: the source record has no trace")
    context, notes = rebuild_context(source.trace, corpus_dir=corpus_dir, chunking=chunking)
    usage_row = result.get("usage") or {}
    usage = AnswerTokenUsage(
        prompt_tokens=int(usage_row.get("prompt_tokens") or 0),
        completion_tokens=int(usage_row.get("completion_tokens") or 0),
    )
    cost = price_of(model, usage.prompt_tokens, usage.completion_tokens, prices) or 0.0
    events = list(source.trace.events)
    step = max((event.step for event in events), default=0) + 1
    if result.get("error"):
        events.append(
            TraceEvent(
                step=step, kind="generation", name="replay_error", note=result["error"][:500]
            )
        )
        record = source.model_copy(
            update={
                "model": model,
                "answer_markdown": "",
                "citations": [],
                "unverified_citations": [],
                "insufficient_evidence": True,
                "trace": source.trace.model_copy(
                    update={"events": events, "unverified_citations": [], "unmatched_markers": []}
                ),
                "usage": usage,
                "latency_ms": float(result.get("latency_ms") or 0.0),
                "cost_usd": cost,
                "cost_usd_v1": None,
                "error": str(result["error"]),
                "judge": None,
                "judges": {},
                "judges_v1": {},
            }
        )
        return record, notes

    parsed, parse_error = _parse(str(result.get("text") or ""), GeneratedAnswer)
    if parsed is None:
        events.append(TraceEvent(step=step, kind="generation", name="unparsed", note=parse_error))
        markdown = str(result.get("text") or "")
        verified: list[Citation] = []
        rejected: list[Citation] = []
        insufficient = True
    else:
        generated = GeneratedAnswer.model_validate(parsed)
        events.append(TraceEvent(step=step, kind="generation", name="replayed", note=model))
        verified, rejected = resolve(
            [(citation.n, citation.quote) for citation in generated.citations],
            context,
            min_quote_chars=min_quote_chars,
        )
        markdown = generated.answer_markdown
        insufficient = generated.insufficient_evidence or not verified

    unmatched_markers = unmatched(markdown, verified + rejected)
    verified_numbers = {citation.n for citation in verified}
    rejected_fabricated = {
        citation.n for citation in fabricated(rejected) if citation.n not in verified_numbers
    }
    rendered = strip_markers(markdown, set(unmatched_markers) | rejected_fabricated)
    trace = source.trace.model_copy(
        update={
            "events": events,
            "unverified_citations": rejected,
            "unmatched_markers": unmatched_markers,
        }
    )
    record = source.model_copy(
        update={
            "model": model,
            "answer_markdown": rendered,
            "citations": verified,
            "unverified_citations": rejected,
            "insufficient_evidence": insufficient,
            "trace": trace,
            "usage": usage,
            "latency_ms": float(result.get("latency_ms") or 0.0),
            "cost_usd": cost,
            "cost_usd_v1": None,
            "error": None,
            "judge": None,
            "judges": {},
            "judges_v1": {},
        }
    )
    return record, notes


def call_row(
    result: Mapping[str, Any], prompt: Mapping[str, Any], record: QuestionRecord
) -> dict[str, Any]:
    """One `calls.jsonl` line in the answer layer's shape (D-023)."""
    parsed, _ = _parse(str(result.get("text") or ""), GeneratedAnswer)
    return {
        "call_id": f"replay:{result['id']}",
        "purpose": PURPOSE,
        "question_id": record.question_id,
        "strategy": record.strategy,
        "started_at": result.get("started_at"),
        "model": result.get("model"),
        "temperature": result.get("temperature"),
        "max_tokens": result.get("max_tokens"),
        "attempt": result.get("attempt"),
        "messages": prompt["messages"],
        "response_schema": "GeneratedAnswer",
        "response_format": result.get("response_format"),
        "response": result.get("response"),
        "text": result.get("text") or "",
        "parsed": parsed,
        "finish_reason": result.get("finish_reason"),
        "usage": {
            "prompt_tokens": record.usage.prompt_tokens,
            "completion_tokens": record.usage.completion_tokens,
        },
        "latency_ms": record.latency_ms,
        "cost_usd": record.cost_usd,
        "error": result.get("error"),
        "source_call_id": result.get("source_call_id"),
    }
