"""Command line: run the loop-cap grid."""

from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Sequence
from pathlib import Path

from dotenv import load_dotenv

from glossator.answer.config import AnswerConfig
from glossator.eval.answer_eval.models import DEFAULT_GENERATION_MODEL, DEFAULT_JUDGE_MODEL
from glossator.eval.loop_grid.run import run_grid

RUNS_ROOT = Path("eval/runs")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Vary the search loop's caps one axis at a time (D-035c)"
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument(
        "--name", default="loop-grid", help="Grid name; rows are <name>-<axis>-<value>"
    )
    parser.add_argument("--model", default=DEFAULT_GENERATION_MODEL)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--variant", default="sec1024")
    parser.add_argument(
        "--response-format",
        choices=("json_schema", "json_object"),
        default=AnswerConfig().response_format,
        help=(
            "How structured requests are sent; json_object is the fallback for a "
            "server that does not honour a JSON schema"
        ),
    )
    parser.add_argument("--limit", type=int, help="Stratified subset of this many questions")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--quota-ceiling", type=int, default=80)
    parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    parser.add_argument(
        "--retry-errors",
        action="store_true",
        help="On resume, regenerate the rows whose record carries an error",
    )
    parser.add_argument(
        "--note",
        action="append",
        default=[],
        dest="note",
        help="A sentence of context rendered into the summary README; repeatable",
    )
    return parser.parse_args(argv)


def main() -> None:
    load_dotenv()
    metrics = asyncio.run(run_grid(_parse_args()))
    print(
        json.dumps(
            {
                "summary_dir": metrics["run_dir"],
                "configurations": len(metrics["configurations"]),
                "failed_rows": metrics["failed_rows"],
                "model": metrics["model"],
                "generation_server": metrics["generation_server"],
            },
            indent=2,
        )
    )
