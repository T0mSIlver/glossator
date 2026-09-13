"""Every number the grid report is built from, recomputable from the records."""

import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from mistralai.search.toolkit.document import ChunkType
from mistralai.search.toolkit.search import SearchResult, SearchResultChunk

from glossator.answer.llm import TokenUsage
from glossator.eval.datasets import EvalQuestion, GoldSource, QuestionSource, QuestionType
from glossator.eval.percentiles import rounded_index_percentile
from glossator.eval.retrieval_grid.models import RUN_KIND, GridEntry, GridRecord
from glossator.eval.retrieval_metrics import Matching, aggregate, as_row, evaluate, scoreable
from glossator.retrieval.config import RetrievalConfig


async def recompute(run_dir: Path) -> dict[str, Any]:
    """Rebuild ``metrics.json`` from the run's own records.

    Every question a metric is computed over is reconstructed from the rows in
    ``records.jsonl``, not read back out of ``metrics.json``, so a regenerated
    report can never drift from the hits under it and does not depend on the
    dataset file still being where the run found it (D-023).
    """
    config = json.loads((run_dir / "config.json").read_text())
    records = [
        GridRecord.model_validate_json(line)
        for line in (run_dir / "records.jsonl").read_text().splitlines()
        if line.strip()
    ]
    questions: dict[str, EvalQuestion] = {}
    for record in records:
        questions.setdefault(record.question_id, _question(record))
    # ``rerank`` is written into the row for a reader's benefit and is derived from
    # the configuration, so it is not passed back in.
    entries = [
        GridEntry(
            name=row["name"],
            variant=row["variant"],
            weights=row["weights"],
            config=RetrievalConfig.model_validate(row["config"]),
        )
        for row in config["grid"]
    ]
    metrics = await summarize(entries, list(questions.values()), records, config)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    return metrics


def _question(record: GridRecord) -> EvalQuestion:
    return EvalQuestion(
        id=record.question_id,
        question=record.question,
        type=QuestionType(record.question_type),
        gold=[GoldSource(url=str(gold["url"]), anchor=gold.get("anchor")) for gold in record.gold],
        reference_answer=record.reference_answer,
        language="fr" if record.language == "fr" else "en",
        source=QuestionSource(record.question_source),
    )


async def summarize(
    entries: Sequence[GridEntry],
    questions: Sequence[EvalQuestion],
    records: Sequence[GridRecord],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Every number the README and the figures are built from.

    Metrics are reported twice. ``all`` scores each configuration over the
    questions it actually ran; ``common`` scores every configuration over the
    questions *all* of them ran, which is the only comparison that is fair when a
    reranker budget stopped one row short of the others.
    """
    by_id = {question.id: question for question in questions}
    by_config: dict[str, list[GridRecord]] = defaultdict(list)
    for record in records:
        by_config[record.configuration].append(record)

    answered: dict[str, set[str]] = {
        name: {record.question_id for record in rows if record.error is None}
        for name, rows in by_config.items()
    }
    common_ids = set.intersection(*answered.values()) if answered else set()

    per_config: dict[str, Any] = {}
    for entry in entries:
        rows = by_config.get(entry.name, [])
        results = {
            record.question_id: _as_search_results(record)
            for record in rows
            if record.error is None
        }
        entry_metrics: dict[str, Any] = {}
        for matching in Matching:
            per_question = await evaluate(questions, results, matching, config["top_k"])
            entry_metrics[str(matching)] = {
                "all": _grouped(per_question, by_id, set(per_question)),
                "common": _grouped(per_question, by_id, set(per_question) & common_ids),
            }
        per_config[entry.name] = {
            **entry.as_dict(),
            "metrics": entry_metrics,
            **_operational(rows),
        }

    unanswerable = _unanswerable(records, by_id)
    return {
        "kind": RUN_KIND,
        "status": "complete",
        "configurations": per_config,
        "configuration_order": [entry.name for entry in entries],
        "question_types": sorted({str(question.type) for question in questions}),
        "questions": len(questions),
        "common_questions": len(common_ids),
        "section_scoreable": len(scoreable(questions, Matching.SECTION)),
        "page_scoreable": len(scoreable(questions, Matching.PAGE)),
        "unanswerable": unanswerable,
        # Three different numbers, and conflating them makes a report lie: calls
        # that were made and paid for, the subset whose ranking was applied, and
        # the rows of a reranked configuration that never sent anything because
        # the budget was gone.
        "rerank_billed_calls": sum(1 for record in records if record.rerank_attempted),
        "rerank_calls": sum(1 for record in records if record.reranked),
        "rerank_fallbacks": sum(
            1 for record in records if record.rerank_attempted and not record.reranked
        ),
        "rerank_skipped": sum(
            1
            for record in records
            if record.rerank and not record.rerank_attempted and not record.error
        ),
        "rerank_cost_usd": round(sum(record.rerank_cost_usd for record in records), 6),
        "errors": [
            {
                "configuration": record.configuration,
                "question_id": record.question_id,
                "error": record.error,
            }
            for record in records
            if record.error
        ],
        "best": _best(per_config),
    }


def _grouped(
    per_question: Mapping[str, Any],
    by_id: Mapping[str, EvalQuestion],
    keep: set[str],
) -> dict[str, dict[str, float | int | None]]:
    """One aggregate for everything, plus one per question type."""
    selected = {qid: metrics for qid, metrics in per_question.items() if qid in keep}
    grouped: dict[str, list[Any]] = defaultdict(list)
    for qid, metrics in selected.items():
        grouped["overall"].append(metrics)
        grouped[str(by_id[qid].type)].append(metrics)
    return {name: as_row(aggregate(rows), len(rows)) for name, rows in sorted(grouped.items())}


def _operational(records: Sequence[GridRecord]) -> dict[str, Any]:
    """Latency, cost and the counts that say whether a row ran cleanly."""
    latencies = sorted(record.latency_ms for record in records if record.error is None)
    usage = TokenUsage()
    for record in records:
        usage = usage + TokenUsage.model_validate(record.rerank_usage or {})
    reranked = sum(1 for record in records if record.reranked)
    return {
        "questions_run": len(records),
        "errors": sum(1 for record in records if record.error),
        "median_latency_ms": round(_median(latencies), 1) if latencies else None,
        "p90_latency_ms": (
            round(rounded_index_percentile(latencies, 0.9), 1) if latencies else None
        ),
        "rerank_applied": reranked,
        "rerank_billed_calls": sum(1 for record in records if record.rerank_attempted),
        "rerank_fallbacks": sum(
            1 for record in records if record.rerank_attempted and not record.reranked
        ),
        "rerank_skipped": sum(
            1
            for record in records
            if record.rerank and not record.rerank_attempted and not record.error
        ),
        "rerank_cost_usd": round(sum(record.rerank_cost_usd for record in records), 6),
        "rerank_usage": usage.model_dump(mode="json"),
        "no_lexical_footing": sum(1 for record in records if record.lexical_footing is False),
    }


def _unanswerable(
    records: Sequence[GridRecord], by_id: Mapping[str, EvalQuestion]
) -> dict[str, Any]:
    """What the unanswerable questions returned, reported rather than scored.

    They have no gold, so recall is undefined for them; what matters is whether
    the engine returned something confident anyway, which is what the score floors
    are meant to stop (D-030).
    """
    rows = [
        {
            "configuration": record.configuration,
            "question_id": record.question_id,
            "question": record.question,
            "lexical_footing": record.lexical_footing,
            "top_hit": record.hits[0].model_dump(mode="json") if record.hits else None,
        }
        for record in records
        if by_id[record.question_id].type is QuestionType.UNANSWERABLE and record.error is None
    ]
    return {
        "questions": len({row["question_id"] for row in rows}),
        "with_a_top_hit": sum(1 for row in rows if row["top_hit"] is not None),
        "no_lexical_footing": sum(1 for row in rows if row["lexical_footing"] is False),
        "rows": rows,
    }


def _best(per_config: Mapping[str, Any]) -> dict[str, Any]:
    """The winning configuration per matching, and by how much.

    Ranked on recall@5 over the questions that matching could score: recall@1 is
    the noisiest column on a dataset this size, and recall@10 is close to saturated
    once the right page is anywhere in the results. Each matching carries its own
    question count, because the section level scores fewer questions than the page
    level and a report that printed the dataset's size here would overstate both.
    """
    winners: dict[str, Any] = {}
    for matching in Matching:
        overall = [
            (name, row["metrics"][str(matching)]["common"].get("overall") or {})
            for name, row in per_config.items()
        ]
        ranked = sorted(
            ((name, row["recall@5"]) for name, row in overall if row.get("recall@5") is not None),
            key=lambda item: (-item[1], item[0]),
        )
        if not ranked:
            continue
        counted = {row.get("questions", 0) for _name, row in overall if row}
        winners[str(matching)] = {
            "configuration": ranked[0][0],
            "recall@5": ranked[0][1],
            "questions": max(counted) if counted else 0,
            "runner_up": ranked[1][0] if len(ranked) > 1 else None,
            "margin": round(ranked[0][1] - ranked[1][1], 4) if len(ranked) > 1 else None,
            "ranking": [{"configuration": name, "recall@5": value} for name, value in ranked],
        }
    winners["ranked_on"] = "recall@5 over the questions each matching can score"
    return winners


def _as_search_results(record: GridRecord) -> list[SearchResult]:
    """The recorded hits back in the shape the harness scores.

    Only the id and the metadata are read by the proxy matcher, but the whole
    chunk is rebuilt so a reader of this function does not have to know that.
    """
    return [
        SearchResult(
            chunk=SearchResultChunk(
                id=hit.chunk_id,
                source_id=hit.url,
                locator=f"rank:{hit.rank}",
                start_offset=None,
                end_offset=None,
                chunk_type=ChunkType.CONTENT,
                content="",
                metadata={"url": hit.url, "anchor": hit.anchor},
            ),
            score=hit.score,
        )
        for hit in record.hits
    ]


def _median(values: Sequence[float]) -> float:
    return rounded_index_percentile(values, 0.5)
