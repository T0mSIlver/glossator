"""Deterministic per-record numbers and their per-cell aggregates."""

from __future__ import annotations

import statistics
from collections.abc import Sequence
from typing import Any

from glossator.eval.answer_eval.models import CORRECTNESS_SCORE
from glossator.eval.consumer.answers import cite_verdicts, refused
from glossator.eval.consumer.links import page_of
from glossator.eval.consumer.models import ConsumerRecord
from glossator.eval.consumer.tools import asked_for_rerank
from glossator.eval.percentiles import nearest_rank_percentile

BAD_PARAM = "error: E_BAD_PARAM"
CLAMP = "clamped server-side"


def record_metrics(record: ConsumerRecord, corpus_urls: set[str]) -> dict[str, float | None]:
    answerable = record.question_type != "unanswerable"
    page_links = [page_of(url) for url in record.links]
    resolved = [url for url in page_links if url in corpus_urls]
    gold = [url for url in page_links if url in set(record.gold_urls)]
    bad_param = sum(1 for call in record.tool_calls if BAD_PARAM in (call.error or ""))
    clamps = sum(1 for call in record.tool_calls for note in call.notes if CLAMP in note)
    verified, rejected = cite_verdicts(record.tool_calls)
    verdict = record.judge.verdict if record.judge else None
    return {
        "correctness": CORRECTNESS_SCORE[verdict.correctness] if verdict else None,
        "correct": float(verdict.correctness == "correct") if verdict else None,
        "refusal_correct": float(refused(record.answer_text) == (not answerable)),
        "refused": float(refused(record.answer_text)),
        "links": float(len(record.links)),
        "links_resolve": float(len(resolved) / len(page_links)) if page_links else None,
        "links_on_gold": float(bool(gold)) if answerable else None,
        "mcp_called": float(record.mcp_called),
        "rerank_asked": float(any(asked_for_rerank(call) for call in record.tool_calls)),
        "cite_called": float(record.cite_called),
        "cite_verified": float(verified),
        "cite_rejected": float(rejected),
        "tool_calls": float(len(record.tool_calls)),
        "bad_param_errors": float(bad_param),
        "clamps": float(clamps),
        "tokens_total": float(record.tokens.total),
        "wall_seconds": record.wall_seconds,
        "errors": float(record.error is not None),
    }


def _mean(values: Sequence[float | None]) -> float | None:
    kept = [v for v in values if v is not None]
    return statistics.fmean(kept) if kept else None


CELL_METRICS = (
    "correctness",
    "refusal_correct",
    "links_resolve",
    "links_on_gold",
    "mcp_called",
    "rerank_asked",
    "cite_called",
    "cite_verified",
    "cite_rejected",
    "tool_calls",
    "bad_param_errors",
    "clamps",
    "tokens_total",
)


def aggregate(records: Sequence[ConsumerRecord], corpus_urls: set[str]) -> dict[str, Any]:
    """One metrics object for the run: per (consumer, arm) cells plus totals."""
    per_row = [record_metrics(record, corpus_urls) for record in records]
    grouped: dict[str, list[dict[str, float | None]]] = {}
    for record, metrics in zip(records, per_row, strict=True):
        grouped.setdefault(f"{record.consumer} / {record.arm}", []).append(metrics)
    by_cell: dict[str, dict[str, Any]] = {}
    for name, rows in grouped.items():
        by_cell[name] = {
            "n": len(rows),
            "errors": int(sum(r["errors"] or 0 for r in rows)),
            **{metric: _mean([r[metric] for r in rows]) for metric in CELL_METRICS},
            "latency_p50": nearest_rank_percentile(
                [float(r["wall_seconds"] or 0) for r in rows],
                0.5,
            ),
        }
    return {"cells": by_cell, "records": len(records)}


def cost_per_correct(records: Sequence[ConsumerRecord]) -> dict[str, float | None]:
    """Harness tokens per correct answer, per cell (judge-dependent)."""
    out: dict[str, float | None] = {}
    cells: dict[str, list[ConsumerRecord]] = {}
    for record in records:
        cells.setdefault(f"{record.consumer} / {record.arm}", []).append(record)
    for name, rows in cells.items():
        correct = sum(
            1
            for row in rows
            if row.judge and row.judge.verdict and row.judge.verdict.correctness == "correct"
        )
        tokens = sum(row.tokens.total for row in rows)
        out[name] = tokens / correct if correct else None
    return out
