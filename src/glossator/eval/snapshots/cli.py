"""Command line: label, evaluate, rescore, rejudge."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv

from glossator.corpus.snapshots import DEFAULT_MANIFEST
from glossator.eval.answer_eval.models import parse_judge_models
from glossator.eval.snapshots.evaluate import (
    rejudge_snapshot_eval,
    rescore_snapshot_eval,
    run_snapshot_eval,
)
from glossator.eval.snapshots.label import label
from glossator.eval.snapshots.models import LABEL_SEED
from glossator.eval.snapshots.run_files import RUNS_ROOT


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="glossator.eval.snapshots")
    subparsers = parser.add_subparsers(dest="command", required=True)
    label_parser = subparsers.add_parser("label")
    label_parser.add_argument("--dataset", type=Path, action="append", required=True)
    label_parser.add_argument("--name", required=True)
    label_parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    label_parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    label_parser.add_argument("--seed", type=int, default=LABEL_SEED)
    label_parser.add_argument(
        "--deterministic-only",
        action="store_true",
        help="Run only the exact-span step; cells needing a judge are stored as "
        "pending_judges for a later judged pass.",
    )
    rescore_parser = subparsers.add_parser("rescore")
    rescore_parser.add_argument("--run", type=Path, required=True)
    rescore_parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    rescore_parser.add_argument(
        "--labels", type=Path, help="Labels file, when the run predates the config key"
    )
    rejudge_parser = subparsers.add_parser("rejudge")
    rejudge_parser.add_argument("--run", type=Path, required=True)
    rejudge_parser.add_argument("--judge-models", required=True)
    rejudge_parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--dataset", type=Path, required=True)
    run_parser.add_argument("--name", required=True)
    run_parser.add_argument("--labels", type=Path, required=True)
    run_parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    run_parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    run_parser.add_argument(
        "--skip-judge",
        action="store_true",
        help="Record answers without judge verdicts; correctness and refusal stay "
        "empty until judges run later.",
    )
    return parser


async def _main(args: argparse.Namespace) -> None:
    if args.command == "label":
        path, metrics = await label(
            args.dataset,
            name=args.name,
            manifest_path=args.manifest,
            runs_root=args.runs_root,
            seed=args.seed,
            deterministic_only=args.deterministic_only,
        )
    elif args.command == "rescore":
        metrics = rescore_snapshot_eval(
            args.run, manifest_path=args.manifest, labels_path=args.labels
        )
        path = args.run
    elif args.command == "rejudge":
        metrics = await rejudge_snapshot_eval(
            args.run, parse_judge_models(args.judge_models), manifest_path=args.manifest
        )
        path = args.run
    else:
        path, metrics = await run_snapshot_eval(
            args.dataset,
            name=args.name,
            labels_path=args.labels,
            manifest_path=args.manifest,
            runs_root=args.runs_root,
            skip_judge=args.skip_judge,
        )
    print(json.dumps({"run_dir": str(path), **metrics}, indent=2))


def main() -> None:
    load_dotenv()
    asyncio.run(_main(_parser().parse_args()))
