"""Command line: run the grid, or a named subset of its rows."""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from glossator.eval.datasets import read_jsonl
from glossator.eval.retrieval_grid.grid import expand, select
from glossator.eval.retrieval_grid.models import DEFAULT_REQUEST_INTERVAL, GridSpec
from glossator.eval.retrieval_grid.run import GridRun
from glossator.eval.run_records import create_run_directory


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
