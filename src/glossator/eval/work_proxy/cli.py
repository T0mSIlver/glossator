"""Command line: run a question set through the proxy, or rewrite a run's README."""

from __future__ import annotations

import argparse
import asyncio
from collections.abc import Sequence
from pathlib import Path

from dotenv import load_dotenv

from glossator.eval.consumer.run_dir import RUNS_ROOT
from glossator.eval.datasets import EvalQuestion, read_jsonl
from glossator.eval.work_proxy.collect import DEFAULT_CONCURRENCY, run_work_proxy
from glossator.eval.work_proxy.models import QUESTION_TIMEOUT_S, WorkProxyConfig
from glossator.eval.work_proxy.report import write_readme
from glossator.eval.work_proxy.run_dir import (
    merge_existing_config,
    resolve_run_directory,
    write_config,
)

DEFAULT_MODEL = "mistral-medium-3-5"
DEFAULT_REASONING_EFFORT = "high"
DEFAULT_CONNECTOR = "mistral_docs_ca30"
"""The workspace's Connector for the deployed server, the one Work sessions use.
The platform suffixes a Connector's requested name with four hex characters, so
the name to pass is the suffixed one, or the UUID (D-049)."""


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Conversations-API work proxy over a question set"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Collect answers through the proxy agent")
    run_parser.add_argument("--dataset", type=Path, required=True)
    run_parser.add_argument("--name", required=True, help="Run stem; re-running it resumes")
    run_parser.add_argument("--model", default=DEFAULT_MODEL)
    run_parser.add_argument(
        "--reasoning-effort", choices=["high", "none"], default=DEFAULT_REASONING_EFFORT
    )
    run_parser.add_argument("--connector", default=DEFAULT_CONNECTOR, help="Connector name or UUID")
    run_parser.add_argument("--limit", type=int, help="How many questions to run")
    run_parser.add_argument("--ids", help="Comma-separated question ids to run")
    run_parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    run_parser.add_argument("--timeout", type=float, default=QUESTION_TIMEOUT_S)
    run_parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)

    readme_parser = sub.add_parser("readme", help="Re-render a run's README from its records")
    readme_parser.add_argument("--run", type=Path, required=True)
    return parser.parse_args(argv)


def _select_questions(
    dataset: Path, *, ids: Sequence[str], limit: int | None
) -> list[EvalQuestion]:
    questions = read_jsonl(dataset)
    if ids:
        wanted = set(ids)
        questions = [question for question in questions if question.id in wanted]
        missing = wanted - {question.id for question in questions}
        if missing:
            raise SystemExit(f"question ids not in {dataset}: {sorted(missing)}")
    if limit is not None:
        questions = questions[:limit]
    return questions


async def _run(args: argparse.Namespace) -> None:
    questions = _select_questions(
        args.dataset,
        ids=[piece.strip() for piece in args.ids.split(",")] if args.ids else [],
        limit=args.limit,
    )
    if not questions:
        raise SystemExit("no questions selected")
    run_dir = resolve_run_directory(args.name, root=args.runs_root)
    config = WorkProxyConfig(
        name=args.name,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        connector=args.connector,
        dataset=args.dataset,
        run_dir=run_dir,
        timeout_s=args.timeout,
    )
    (run_dir / "records.jsonl").touch()
    (run_dir / "calls.jsonl").touch()
    write_config(
        run_dir,
        merge_existing_config(
            run_dir, config.as_dict(agent_id=None, question_count=len(questions))
        ),
    )
    try:
        await run_work_proxy(questions, config=config, concurrency=args.concurrency)
    finally:
        write_readme(run_dir)


def main() -> None:
    load_dotenv()
    args = _parse_args()
    if args.command == "run":
        asyncio.run(_run(args))
    elif args.command == "readme":
        write_readme(args.run)
    else:
        raise SystemExit(f"unknown command {args.command!r}")
