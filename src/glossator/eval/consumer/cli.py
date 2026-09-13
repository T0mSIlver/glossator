"""Command line: collect, judge and score, as three resumable subcommands."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from glossator.eval.answer_eval.models import parse_judge_models
from glossator.eval.answer_eval.prompts import JUDGE_PROMPT_HASHES, JUDGE_VERSION
from glossator.eval.consumer.collect import QUESTION_TIMEOUT_S, run_collection
from glossator.eval.consumer.consumers import ARM_TOOLS, ARMS, consumer_spec
from glossator.eval.consumer.defects import collect_defects, render_defects
from glossator.eval.consumer.judge import run_judge
from glossator.eval.consumer.links import DEFAULT_CORPUS, check_fragments, corpus_page_urls
from glossator.eval.consumer.metrics import aggregate, cost_per_correct
from glossator.eval.consumer.models import load_records
from glossator.eval.consumer.prompts import PROMPT_LEAD
from glossator.eval.consumer.questions import (
    FRESH_COUNT,
    FRESH_DATASET,
    MINED_COUNT,
    MINED_DATASET,
    build_question_set,
)
from glossator.eval.consumer.report import render_figures, render_readme, render_samples
from glossator.eval.consumer.run_dir import (
    QUARANTINE_FILE,
    RUNS_ROOT,
    merge_config,
    resolve_run_directory,
)
from glossator.eval.consumer.tools import MCP_SERVER_NAME


def _read_config(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "config.json"
    if not path.is_file():
        return {}
    loaded = json.loads(path.read_text())
    return loaded if isinstance(loaded, dict) else {}


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Blind consumer evaluation over the MCP server")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Collect consumer answers")
    run_parser.add_argument("--name", help="Run name; re-running it resumes the run")
    run_parser.add_argument(
        "--consumers",
        default="opencode-muse-minimal",
        help="Comma-separated consumer names",
    )
    run_parser.add_argument("--arms", default="A0,A1", help="Comma-separated arms")
    run_parser.add_argument("--scratch-root", type=Path, required=True)
    run_parser.add_argument("--mcp-url-a1", default="http://127.0.0.1:8000/mcp")
    run_parser.add_argument("--mcp-url-a2", default="http://127.0.0.1:8001/mcp")
    run_parser.add_argument("--token-env", default="GLOSSATOR_MCP_TOKEN")
    run_parser.add_argument("--timeout-s", type=float, default=QUESTION_TIMEOUT_S)
    run_parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    run_parser.add_argument(
        "--mined", type=int, default=MINED_COUNT, help="How many mined questions (seed 0)"
    )
    run_parser.add_argument(
        "--fresh", type=int, default=FRESH_COUNT, help="How many fresh questions (seed 0)"
    )
    run_parser.add_argument(
        "--note",
        action="append",
        default=[],
        dest="notes",
        help=(
            "One line about the machine this run reached, kept in the run's "
            "config and printed in its README (repeatable)"
        ),
    )
    run_parser.add_argument("--mined-path", type=Path, default=MINED_DATASET)
    run_parser.add_argument("--fresh-path", type=Path, default=FRESH_DATASET)

    judge_parser = sub.add_parser("judge", help="Grade stored answers (resumable)")
    judge_parser.add_argument("--run", type=Path, required=True)
    judge_parser.add_argument("--judge-models", default="zai:glm-5.3")
    judge_parser.add_argument("--rejudge", action="store_true")
    judge_parser.add_argument("--quota-ceiling", type=int, default=80)

    score_parser = sub.add_parser("score", help="Score a run deterministically")
    score_parser.add_argument("--run", type=Path, required=True)
    score_parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    score_parser.add_argument("--sample-consumer", default="opencode-muse-minimal")
    return parser.parse_args(argv)


async def _run(args: argparse.Namespace) -> None:
    specs = [consumer_spec(name.strip()) for name in args.consumers.split(",")]
    arms = [arm.strip() for arm in args.arms.split(",")]
    unknown_arms = sorted(set(arms) - set(ARMS))
    if unknown_arms:
        raise SystemExit(f"unknown arms {unknown_arms}; available: {list(ARMS)}")
    name = args.name or (datetime.now(UTC).strftime("%Y-%m-%d-%H%M") + "-consumer-eval")
    run_dir = resolve_run_directory(name, root=args.runs_root)
    questions = build_question_set(args.mined, args.fresh, args.mined_path, args.fresh_path)
    token = os.environ.get(args.token_env, "")
    if any(arm in ("A1", "A2") for arm in arms) and not token:
        raise SystemExit(f"{args.token_env} is not set; the MCP arms need it")
    mcp_urls = {"A1": args.mcp_url_a1, "A2": args.mcp_url_a2}
    config = {
        "kind": "consumer_eval",
        "name": name,
        "run_dir": str(run_dir),
        "consumers": [spec.name for spec in specs],
        "consumer_models": {spec.name: spec.model for spec in specs},
        "consumer_harnesses": {spec.name: spec.harness for spec in specs},
        "consumer_variants": {spec.name: spec.variant for spec in specs},
        "arms": arms,
        "arm_tools": {arm: ARM_TOOLS[arm] for arm in arms},
        "mcp_urls": {arm: mcp_urls[arm] for arm in arms if arm in mcp_urls},
        "mcp_server_name": MCP_SERVER_NAME,
        "scratch_root": str(args.scratch_root),
        "question_count": len(questions),
        "mined_count": args.mined,
        "fresh_count": args.fresh,
        "unanswerable_count": sum(1 for q in questions if q.type.value == "unanswerable"),
        "questions": [question.id for question in questions],
        "prompt_lead": PROMPT_LEAD,
        "notes": list(args.notes),
        "judge_model": None,
        "judge_prompt_version": JUDGE_VERSION,
        "judge_prompt_hashes": JUDGE_PROMPT_HASHES,
    }
    config = merge_config(_read_config(run_dir), config)
    (run_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    (run_dir / "questions.jsonl").write_text("".join(q.model_dump_json() + "\n" for q in questions))
    _start_run_directory(run_dir)
    await run_collection(
        questions,
        specs,
        arms,
        run_dir=run_dir,
        run_name=name,
        scratch_root=args.scratch_root,
        mcp_urls=mcp_urls,
        token=token,
        timeout_s=args.timeout_s,
    )


async def _judge(args: argparse.Namespace) -> None:
    try:
        judge_models = parse_judge_models(args.judge_models)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    counts = await run_judge(
        args.run, judge_models, rejudge=args.rejudge, quota_ceiling=args.quota_ceiling
    )
    config_path = args.run / "config.json"
    if config_path.is_file():
        config = json.loads(config_path.read_text())
        config["judge_model"] = judge_models[0].identifier
        config["judge_models"] = [judge.identifier for judge in judge_models]
        config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    print(json.dumps(counts, indent=2, sort_keys=True))


def _score(args: argparse.Namespace) -> None:
    run_dir: Path = args.run
    records = load_records(run_dir / "records.jsonl")
    corpus_urls = corpus_page_urls(args.corpus)
    metrics = aggregate(records, corpus_urls)
    fragments = check_fragments(run_dir, records)
    metrics["fragments"] = fragments
    judged = sum(1 for r in records if r.judge and r.judge.verdict)
    metrics["judged"] = judged
    config = json.loads((run_dir / "config.json").read_text())
    metrics["correctness_cost"] = cost_per_correct(records)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    extra_files = (
        [
            f"- `{QUARANTINE_FILE}`: answer-arm rows this run does not report,",
            "  collected while the server could not reach its model or against a",
            "  model since replaced. Their cells were collected again.",
        ]
        if (run_dir / QUARANTINE_FILE).is_file()
        else []
    )
    (run_dir / "README.md").write_text(render_readme(config, metrics, fragments, extra_files))
    (run_dir / "defects.md").write_text(render_defects(collect_defects(records)))
    (run_dir / "samples.md").write_text(render_samples(records, consumer=args.sample_consumer))
    figures = render_figures(metrics, run_dir / "figures")
    print(json.dumps({"records": len(records), "figures": figures}, indent=2))


def _start_run_directory(run_dir: Path) -> None:
    """Give a collection run the shape D-023 asks for before it collects anything.

    Collection, judging and scoring are three commands, and a run interrupted
    between them used to sit in the repository as a bare `records.jsonl`: no
    ledger, no figures directory, and no README saying what it was or which of
    the three steps still owed it numbers. The placeholder is overwritten by
    `score`.
    """
    (run_dir / "figures").mkdir(parents=True, exist_ok=True)
    (run_dir / "calls.jsonl").touch()
    (run_dir / "records.jsonl").touch()
    readme = run_dir / "README.md"
    if not readme.is_file():
        readme.write_text(
            "# Blind consumer evaluation (collecting)\n\n"
            "Answers are being collected; no judge has run and no metrics exist yet.\n"
            "`config.json` holds the consumers, arms and question set. Run\n"
            "`python -m glossator.eval.consumer judge --run <dir>` and then `score`\n"
            "to fill in `metrics.json`, `figures/` and this file.\n"
        )


def main() -> None:
    load_dotenv()
    args = _parse_args()
    if args.command == "run":
        asyncio.run(_run(args))
    elif args.command == "judge":
        asyncio.run(_judge(args))
    elif args.command == "score":
        _score(args)
    else:
        raise SystemExit(f"unknown command {args.command!r}")
