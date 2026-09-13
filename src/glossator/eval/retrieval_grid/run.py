"""Running the grid and writing the run directory as it goes."""

import asyncio
import hashlib
import json
import time
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import structlog

from glossator.eval.datasets import EvalQuestion
from glossator.eval.retrieval_grid.metrics import summarize
from glossator.eval.retrieval_grid.models import (
    DEFAULT_REQUEST_INTERVAL,
    RUN_KIND,
    GridEntry,
    GridRecord,
    GridSpec,
    HitRecord,
)
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import Hit, SearchEngine, SearchTrace
from glossator.retrieval.reranker import RERANK_PROMPT_VERSION, SYSTEM_PROMPT

logger = structlog.get_logger(__name__)


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
