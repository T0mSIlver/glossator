"""Every question through every retrieval configuration, with the record to prove it.

A grid row is a ``RetrievalConfig`` and nothing else, so what the evaluation
measures is exactly what a caller could set. Each row runs the whole dataset, and
each question keeps its ranked hits -- ids, urls, anchors, scores -- so any number
in the report can be traced back to the hits it was computed from (D-023).

Usage:
    python -m glossator.eval.retrieval_grid --dataset eval/dev.jsonl \\
        --grid eval/configs/retrieval-grid.yaml --name dev
"""

import argparse
import asyncio
import hashlib
import json
import time
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, Self

import structlog
import yaml
from dotenv import load_dotenv
from mistralai.search.toolkit.document import ChunkType
from mistralai.search.toolkit.search import SearchResult, SearchResultChunk
from pydantic import BaseModel, ConfigDict, Field, model_validator

from glossator.answer.llm import TokenUsage
from glossator.eval.datasets import (
    EvalQuestion,
    GoldSource,
    QuestionSource,
    QuestionType,
    read_jsonl,
)
from glossator.eval.retrieval_metrics import (
    Matching,
    aggregate,
    as_row,
    evaluate,
    scoreable,
)
from glossator.eval.run_records import create_run_directory
from glossator.retrieval.config import (
    DEFAULT_RERANK_CANDIDATES,
    DEFAULT_TOP_K,
    RERANK_MODEL,
    RetrievalConfig,
)
from glossator.retrieval.engine import Hit, SearchEngine, SearchTrace
from glossator.retrieval.reranker import RERANK_PROMPT_VERSION, SYSTEM_PROMPT

logger = structlog.get_logger(__name__)

RUN_KIND = "retrieval-grid"
"""Written into config.json so `make eval-report` knows which README to render."""

DEFAULT_REQUEST_INTERVAL = 1.1
"""Seconds between model calls. The Mistral account is on the free tier and is
governed to about one request a second with retries rather than concurrency
(D-028); Vespa itself is local and is not the constraint."""


class GridSpec(BaseModel):
    """The grid as it is written in YAML."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = "retrieval-grid"
    top_k: int = DEFAULT_TOP_K
    weight_sets: dict[str, dict[str, float]] = Field(default_factory=dict)
    axes: dict[str, list[str]] = Field(default_factory=dict)
    exclude: list[dict[str, str]] = Field(default_factory=list)
    rerank: "RerankSpec" = Field(default_factory=lambda: RerankSpec())

    @model_validator(mode="after")
    def _validate(self) -> Self:
        unknown_axes = sorted(set(self.axes) - {"variant", "weights"})
        if unknown_axes:
            raise ValueError(f"unknown grid axis/axes {unknown_axes}; available: variant, weights")
        unknown_weights = sorted(set(self.axes.get("weights", [])) - set(self.weight_sets))
        if unknown_weights:
            raise ValueError(
                f"axes name weight set(s) with no definition: {unknown_weights}; "
                f"defined: {sorted(self.weight_sets)}"
            )
        return self

    @classmethod
    def load(cls, path: Path) -> "GridSpec":
        return cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})


class RerankSpec(BaseModel):
    """Which rows get a reranker, on which model, and how many calls they may make."""

    model_config = ConfigDict(frozen=True, extra="forbid", protected_namespaces=())

    model: str = RERANK_MODEL
    temperature: float = 0.0
    candidates: int = DEFAULT_RERANK_CANDIDATES
    max_calls: int = 400
    configurations: list[str] = Field(default_factory=list)


class GridEntry(BaseModel):
    """One row of the grid: a name and the configuration it stands for."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    variant: str
    weights: str
    """The weight set's name, kept so a table can group rows by it."""

    config: RetrievalConfig

    @property
    def reranked(self) -> bool:
        return self.config.rerank

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "variant": self.variant,
            "weights": self.weights,
            "rerank": self.reranked,
            "config": self.config.model_dump(mode="json"),
        }


def expand(spec: GridSpec) -> list[GridEntry]:
    """The grid's rows, in a stable order: the cross product, then the reranked rows.

    A reranked row is a copy of the row it names rather than a row of its own, so
    "reranking is worth this much" is a comparison between two rows that differ in
    one field and share everything else.
    """
    entries: list[GridEntry] = []
    excluded = {tuple(sorted(rule.items())) for rule in spec.exclude}
    for variant in spec.axes.get("variant", []):
        for weights in spec.axes.get("weights", []):
            if tuple(sorted({"variant": variant, "weights": weights}.items())) in excluded:
                continue
            entries.append(
                GridEntry(
                    name=f"{variant}-{weights}",
                    variant=variant,
                    weights=weights,
                    config=RetrievalConfig(
                        variant=variant,
                        top_k=spec.top_k,
                        ranking_weights=spec.weight_sets[weights],
                    ),
                )
            )

    by_name = {entry.name: entry for entry in entries}
    for name in spec.rerank.configurations:
        base = by_name.get(name)
        if base is None:
            raise ValueError(
                f"rerank names configuration {name!r}, which the grid does not contain; "
                f"available: {sorted(by_name)}"
            )
        entries.append(
            GridEntry(
                name=f"{name}+rerank",
                variant=base.variant,
                weights=base.weights,
                config=base.config.model_copy(
                    update={
                        "rerank": True,
                        "rerank_candidates": spec.rerank.candidates,
                        "rerank_model": spec.rerank.model,
                        "rerank_temperature": spec.rerank.temperature,
                    }
                ),
            )
        )
    return entries


class HitRecord(BaseModel):
    """One ranked hit, complete enough to recompute any metric from."""

    model_config = ConfigDict(frozen=True)

    rank: int
    chunk_id: str
    url: str
    anchor: str | None
    heading_path: list[str]
    score: float
    retrieval_score: float | None = None
    rerank_score: float | None = None
    similarity: float | None = None


class GridRecord(BaseModel):
    """One question through one configuration."""

    model_config = ConfigDict(frozen=True)

    question_id: str
    question: str
    question_type: str
    language: str
    question_source: str
    reference_answer: str
    gold: list[dict[str, str | None]]
    configuration: str
    variant: str
    weights: str
    rerank: bool

    hits: list[HitRecord] = Field(default_factory=list)
    latency_ms: float = 0.0
    lexical_footing: bool | None = None
    considered: int = 0
    kept: int = 0
    rerank_attempted: bool = False
    """Whether a rerank call was actually made and paid for. A row of a reranked
    configuration has ``rerank`` set and this false when the call budget was
    already spent, and those rows are not fallbacks: nothing was sent."""

    reranked: bool = False
    """Whether the model's ranking was applied. Attempted and not reranked is a
    fallback -- the call happened and its answer could not be used."""

    rerank_error: str | None = None
    rerank_cost_usd: float = 0.0
    rerank_usage: dict[str, int] = Field(default_factory=dict)
    metrics: dict[str, dict[str, float | int | None]] = Field(default_factory=dict)
    error: str | None = None


class GridRun:
    """Runs the grid and writes the run directory as it goes."""

    def __init__(
        self,
        entries: Sequence[GridEntry],
        questions: Sequence[EvalQuestion],
        run_dir: Path,
        *,
        spec: GridSpec,
        dataset_path: Path,
        request_interval: float = DEFAULT_REQUEST_INTERVAL,
        engine_factory: Any = None,
    ) -> None:
        self.entries = list(entries)
        self.questions = list(questions)
        self.run_dir = run_dir
        self.spec = spec
        self.dataset_path = dataset_path
        self.request_interval = request_interval
        self._engine_factory = engine_factory or _build_engine
        self.records: list[GridRecord] = []
        self.rerank_calls = 0
        self.embedding_calls = 0
        self._last_call = 0.0
        # A query's vector depends on the embedding model, not on the ranking
        # weights, so thirteen configurations over three variants embed each
        # question twice (1024 and 128 dimensions) instead of thirteen times.
        # On a rate-limited account that is the difference between a run that
        # finishes and a run pocked with 429s.
        self._embeddings: dict[tuple[str, str], list[float]] = {}

    async def run(self) -> dict[str, Any]:
        self.run_dir.mkdir(parents=True, exist_ok=False)
        (self.run_dir / "figures").mkdir()
        (self.run_dir / "config.json").write_text(
            json.dumps(self.config, indent=2, sort_keys=True) + "\n"
        )
        records_path = self.run_dir / "records.jsonl"
        calls_path = self.run_dir / "calls.jsonl"
        records_path.touch()
        calls_path.touch()

        for entry in self.entries:
            recorder = _JsonlRecorder(calls_path, entry.name)
            engine = self._engine_factory(entry.config, recorder)
            for question in self.questions:
                record = await self._one(entry, question, engine)
                self.records.append(record)
                with records_path.open("a") as handle:
                    handle.write(record.model_dump_json() + "\n")
            logger.info(
                "Configuration done", configuration=entry.name, questions=len(self.questions)
            )

        metrics = await summarize(self.entries, self.questions, self.records, self.config)
        (self.run_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2, sort_keys=True) + "\n"
        )
        return metrics

    async def _one(self, entry: GridEntry, question: EvalQuestion, engine: Any) -> GridRecord:
        base = GridRecord(
            question_id=question.id,
            question=question.question,
            question_type=str(question.type),
            language=question.language,
            question_source=str(question.source),
            reference_answer=question.reference_answer,
            gold=[{"url": gold.url, "anchor": gold.anchor} for gold in question.gold],
            configuration=entry.name,
            variant=entry.variant,
            weights=entry.weights,
            rerank=entry.reranked,
        )
        budget_left = self.rerank_calls < self.spec.rerank.max_calls
        use_rerank = entry.reranked and budget_left
        if entry.reranked and not budget_left:
            base = base.model_copy(
                update={
                    "rerank_error": (
                        f"reranker budget of {self.spec.rerank.max_calls} calls was spent"
                    )
                }
            )
        try:
            embedding = await self._embedding(entry, question, engine)
            if use_rerank:
                await self._throttle()
            hits, trace = await engine.search_with_trace(
                question.question, rerank=use_rerank, embedding=embedding
            )
        except Exception as error:  # noqa: BLE001 - one question's failure is not the run's
            logger.warning(
                "Search failed",
                configuration=entry.name,
                question_id=question.id,
                error=str(error),
            )
            return base.model_copy(update={"error": str(error)})

        if use_rerank:
            self.rerank_calls += 1
        return _fill(base, hits, trace, attempted=use_rerank)

    async def _embedding(
        self, entry: GridEntry, question: EvalQuestion, engine: Any
    ) -> list[float]:
        key = (entry.config.index_variant.embedding_model_name, question.id)
        cached = self._embeddings.get(key)
        if cached is None:
            await self._throttle()
            cached = await engine.retriever.embed_query(question.question, context=engine.context)
            self._embeddings[key] = cached
            self.embedding_calls += 1
        return cached

    async def _throttle(self) -> None:
        """One API call at a time, spaced. The free tier limits requests, not
        tokens, so waiting is cheaper than retrying through a 429 (D-028)."""
        elapsed = time.monotonic() - self._last_call
        if self._last_call and elapsed < self.request_interval:
            await asyncio.sleep(self.request_interval - elapsed)
        self._last_call = time.monotonic()

    @property
    def config(self) -> dict[str, Any]:
        """Every parameter of the run, as it is written to ``config.json`` (D-023)."""
        return {
            "kind": RUN_KIND,
            "name": self.spec.name,
            "dataset": str(self.dataset_path),
            "dataset_sha256": _sha256(self.dataset_path),
            "questions": len(self.questions),
            "questions_by_type": dict(
                sorted(Counter(str(question.type) for question in self.questions).items())
            ),
            "top_k": self.spec.top_k,
            "grid": [entry.as_dict() for entry in self.entries],
            "rerank": {
                **self.spec.rerank.model_dump(mode="json"),
                "prompt_version": RERANK_PROMPT_VERSION,
                "prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()[:12],
            },
            "request_interval_seconds": self.request_interval,
        }


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
        "p90_latency_ms": round(_percentile(latencies, 0.9), 1) if latencies else None,
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


def _fill(
    record: GridRecord, hits: Sequence[Hit], trace: SearchTrace, *, attempted: bool
) -> GridRecord:
    rerank = trace.rerank
    return record.model_copy(
        update={
            "rerank_attempted": attempted,
            "hits": [
                HitRecord(
                    rank=rank,
                    chunk_id=hit.chunk_id,
                    url=hit.url,
                    anchor=hit.anchor,
                    heading_path=list(hit.heading_path),
                    score=hit.score,
                    retrieval_score=hit.retrieval_score,
                    rerank_score=hit.rerank_score,
                    similarity=hit.similarity,
                )
                for rank, hit in enumerate(hits, start=1)
            ],
            "latency_ms": round(trace.latency_ms, 3),
            "lexical_footing": trace.lexical_footing,
            "considered": trace.considered,
            "kept": trace.kept,
            "reranked": bool(rerank and rerank.applied),
            "rerank_error": rerank.error if rerank else record.rerank_error,
            "rerank_cost_usd": rerank.cost_usd if rerank else 0.0,
            "rerank_usage": rerank.usage.model_dump(mode="json") if rerank else {},
        }
    )


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


class _JsonlRecorder:
    """Appends every rerank call to the run's ``calls.jsonl``, verbatim (D-023)."""

    def __init__(self, path: Path, configuration: str) -> None:
        self.path = path
        self.configuration = configuration

    def record(self, call: Any) -> None:
        row = {"configuration": self.configuration, **call.model_dump(mode="json")}
        with self.path.open("a") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            handle.flush()


def _build_engine(config: RetrievalConfig, recorder: Any) -> SearchEngine:
    return SearchEngine(config, recorder=recorder)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _median(values: Sequence[float]) -> float:
    return _percentile(values, 0.5)


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, max(0, round(fraction * (len(values) - 1))))
    return values[index]


def select(entries: Sequence[GridEntry], names: Iterable[str] | None) -> list[GridEntry]:
    """The named rows, in the grid's own order. ``None`` means every row."""
    if names is None:
        return list(entries)
    wanted = {name.strip() for name in names if name.strip()}
    unknown = sorted(wanted - {entry.name for entry in entries})
    if unknown:
        raise ValueError(
            f"unknown configuration(s) {unknown}; the grid holds "
            f"{sorted(entry.name for entry in entries)}"
        )
    return [entry for entry in entries if entry.name in wanted]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the retrieval evaluation grid.")
    parser.add_argument("--dataset", type=Path, required=True, help="Question set, one per line")
    parser.add_argument(
        "--grid",
        type=Path,
        default=Path("eval/configs/retrieval-grid.yaml"),
        help="Grid definition (default: eval/configs/retrieval-grid.yaml)",
    )
    parser.add_argument("--name", required=True, help="Name for the run directory")
    parser.add_argument("--configs", help="Comma-separated configuration names to run")
    parser.add_argument("--limit", type=int, help="Run only the first N questions")
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=Path("eval/runs"),
        help="Where the run directory is created (default: eval/runs)",
    )
    parser.add_argument(
        "--request-interval",
        type=float,
        default=DEFAULT_REQUEST_INTERVAL,
        help=f"Seconds between reranker calls (default: {DEFAULT_REQUEST_INTERVAL})",
    )
    return parser.parse_args()


async def main() -> None:
    load_dotenv()
    args = _parse_args()
    spec = GridSpec.load(args.grid)
    entries = select(expand(spec), args.configs.split(",") if args.configs else None)
    questions = read_jsonl(args.dataset)[: args.limit]
    if not entries:
        raise SystemExit("no configurations selected")
    if not questions:
        raise SystemExit(f"{args.dataset}: no questions")

    run_dir = create_run_directory(args.name, root=args.runs_root)
    run = GridRun(
        entries,
        questions,
        run_dir,
        spec=spec,
        dataset_path=args.dataset,
        request_interval=args.request_interval,
    )
    metrics = await run.run()

    from glossator.eval.retrieval_report import write_report

    write_report(run_dir, run.config, metrics)
    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "configurations": len(entries),
                "questions": len(questions),
                "rerank_calls": metrics["rerank_calls"],
                "rerank_cost_usd": metrics["rerank_cost_usd"],
                "best": {
                    matching: metrics["best"].get(matching, {}).get("configuration")
                    for matching in ("page", "section")
                },
            },
            indent=2,
        )
    )


__all__ = [
    "DEFAULT_REQUEST_INTERVAL",
    "RUN_KIND",
    "GridEntry",
    "GridRecord",
    "GridRun",
    "GridSpec",
    "HitRecord",
    "RerankSpec",
    "expand",
    "select",
    "summarize",
]

if __name__ == "__main__":
    asyncio.run(main())
