"""Command line: measure both populations and write the run directory."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import structlog
from dotenv import load_dotenv

from glossator.eval.calibrate_floors.measure import measure
from glossator.eval.calibrate_floors.models import (
    DEPTHS,
    JUNK_QUESTIONS,
    RUN_KIND,
    TOP_K,
    QuerySimilarities,
)
from glossator.eval.calibrate_floors.proposal import summarize
from glossator.eval.calibrate_floors.report import write_report
from glossator.eval.datasets import QuestionType, read_jsonl
from glossator.eval.run_records import create_run_directory
from glossator.retrieval.config import DEFAULT_CORPUS_DIR, RetrievalConfig
from glossator.retrieval.engine import SearchEngine

logger = structlog.get_logger(__name__)


async def run(
    dataset: Path,
    run_dir: Path,
    *,
    variant: str,
    corpus_dir: Path,
    limit: int | None = None,
) -> dict[str, Any]:
    questions = read_jsonl(dataset)[:limit]
    config = {
        "kind": RUN_KIND,
        "variant": variant,
        "top_k": TOP_K,
        "depths": list(DEPTHS),
        "dataset": str(dataset),
        "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
        "real_questions": len(questions),
        "junk_questions": len(JUNK_QUESTIONS),
        "corpus_dir": str(corpus_dir),
    }
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "figures").mkdir()
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    # No model calls are made here, so calls.jsonl exists and stays empty rather
    # than being absent: a run directory has the same shape whatever produced it.
    (run_dir / "calls.jsonl").touch()
    records_path = run_dir / "records.jsonl"
    records_path.touch()

    engine = SearchEngine(
        RetrievalConfig(
            variant=variant, top_k=TOP_K, check_lexical_footing=True, corpus_dir=corpus_dir
        )
    )
    if engine.vocabulary is None:
        logger.warning(
            "No corpus vocabulary; lexical footing will be unknown", corpus_dir=str(corpus_dir)
        )

    rows: list[QuerySimilarities] = []
    for question in questions:
        rows.append(
            await measure(
                engine,
                question.question,
                "unanswerable" if question.type is QuestionType.UNANSWERABLE else "real",
                question_id=question.id,
                question_type=str(question.type),
            )
        )
    for junk in JUNK_QUESTIONS:
        rows.append(await measure(engine, junk, "junk"))

    with records_path.open("a") as handle:
        for row in rows:
            handle.write(row.model_dump_json() + "\n")

    metrics = summarize(rows, config)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    write_report(run_dir, config, metrics)
    return metrics


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure the similarity corridor between real and junk questions."
    )
    parser.add_argument("--dataset", type=Path, required=True, help="Question set, one per line")
    parser.add_argument("--name", required=True, help="Name for the run directory")
    parser.add_argument("--variant", default="sec1024", help="Index variant to measure")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_DIR)
    parser.add_argument("--limit", type=int, help="Use only the first N real questions")
    parser.add_argument("--runs-root", type=Path, default=Path("eval/runs"))
    return parser.parse_args()


async def main() -> None:
    load_dotenv()
    args = _parse_args()
    run_dir = create_run_directory(args.name, root=args.runs_root)
    metrics = await run(
        args.dataset, run_dir, variant=args.variant, corpus_dir=args.corpus, limit=args.limit
    )
    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "queries": metrics["queries"],
                "proposal": metrics["proposal"],
            },
            indent=2,
        )
    )
