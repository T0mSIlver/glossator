"""Command line: analyse answer-evaluation runs and optionally judge flagged references."""

from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import structlog
from dotenv import load_dotenv

from glossator.eval.failures.analyse import analyse_run
from glossator.eval.failures.judge import judge_flagged, parse_judge_model
from glossator.eval.failures.models import FAILURES_KIND, AnalysedRun, SkippedRun
from glossator.eval.failures.run_dir import RUNS_ROOT, resolve_run_directory, write_run

logger = structlog.get_logger(__name__)

DEFAULT_CORPUS = Path("corpus/mistral-docs")
DEFAULT_LABELS = Path("eval/labels/dev60-rerank-human.jsonl")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify the failed answers of one or more answer-evaluation runs"
    )
    parser.add_argument(
        "--run",
        action="append",
        default=[],
        dest="runs",
        type=Path,
        required=True,
        help="An answer-evaluation run directory to read; repeatable",
    )
    parser.add_argument("--name", required=True, help="Run name for the output directory")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument(
        "--labels",
        type=Path,
        default=DEFAULT_LABELS,
        help="Human correctness labels as JSONL; missing files are ignored",
    )
    parser.add_argument(
        "--judge-model",
        help=(
            "Ask this provider:model whether each flagged reference answer is "
            "supported by its gold section text; off by default, one call per flag"
        ),
    )
    parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    return parser.parse_args(argv)


async def _run(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    analysed: list[AnalysedRun] = []
    skipped: list[SkippedRun] = []
    for run_dir in args.runs:
        result = analyse_run(run_dir, corpus_dir=args.corpus, labels_path=args.labels)
        if isinstance(result, SkippedRun):
            logger.warning("Skipping a directory", run=str(run_dir), reason=result.reason)
            skipped.append(result)
        else:
            analysed.append(result)
    if not analysed:
        raise SystemExit("no answer-evaluation run was given")

    run_dir = resolve_run_directory(args.name, root=args.runs_root)
    run_dir.mkdir(parents=True, exist_ok=False)
    judge = parse_judge_model(args.judge_model) if args.judge_model else None
    if judge is not None:
        load_dotenv()
        analysed = await judge_flagged(
            analysed,
            judge=judge,
            calls_path=run_dir / "calls.jsonl",
            corpus_dir=args.corpus,
        )
    config = {
        "kind": FAILURES_KIND,
        "runs": [str(path) for path in args.runs],
        "corpus": str(args.corpus),
        "labels": str(args.labels) if args.labels and args.labels.exists() else None,
        "judge_model": f"{judge[0]}:{judge[1]}" if judge else None,
        "name": args.name,
        "run_dir": str(run_dir),
    }
    return run_dir, write_run(run_dir, analysed, skipped, config)


def main() -> None:
    args = _parse_args()
    run_dir, metrics = asyncio.run(_run(args))
    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "runs": metrics["runs"],
                "answers": metrics["totals"]["answers"],
                "failures": metrics["totals"]["failures"],
                "by_class": metrics["totals"]["by_class"],
            }
        )
    )
