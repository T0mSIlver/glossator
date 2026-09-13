"""Command line: export, import, check."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from glossator.eval.answer_eval.models import parse_judge_models
from glossator.eval.answer_eval.rejudge import rejudge
from glossator.eval.replay.check import check_rebuild
from glossator.eval.replay.export import export_prompts
from glossator.eval.replay.importing import import_results


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Replay recorded generation prompts on another model, off the pipeline."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    exp = sub.add_parser("export", help="write the recorded generation prompts of one or more runs")
    exp.add_argument("run_dirs", nargs="+", type=Path)
    exp.add_argument("--output", type=Path, required=True)
    exp.add_argument(
        "--temperature", type=float, default=None, help="override the recorded sampling"
    )
    exp.add_argument(
        "--max-tokens", type=int, default=None, help="override the recorded completion cap"
    )
    imp = sub.add_parser("import", help="score replayed completions as new run directories")
    imp.add_argument("results", type=Path)
    imp.add_argument("--prompts", type=Path, required=True)
    imp.add_argument("--name", required=True, help="run name prefix, e.g. medium35-replay")
    imp.add_argument("--model", required=True, help="the model id the completions came from")
    imp.add_argument("--corpus", type=Path, default=Path("corpus/mistral-docs"))
    imp.add_argument("--runs-root", type=Path, default=Path("eval/runs"))
    imp.add_argument(
        "--judge-models", default=None, help="provider:model list; omit to import unjudged"
    )
    imp.add_argument("--note", action="append", default=[], dest="notes")
    chk = sub.add_parser("check", help="prove the rebuilt sources reproduce a run's own verdicts")
    chk.add_argument("run_dirs", nargs="+", type=Path)
    chk.add_argument("--corpus", type=Path, default=Path("corpus/mistral-docs"))
    args = parser.parse_args(argv)
    if args.command == "export":
        summary = export_prompts(
            args.run_dirs, args.output, temperature=args.temperature, max_tokens=args.max_tokens
        )
        print(json.dumps(summary, indent=2))
    elif args.command == "check":
        for run_dir in args.run_dirs:
            print(json.dumps(check_rebuild(run_dir, corpus_dir=args.corpus), indent=2))
    elif args.command == "import":
        written = import_results(
            args.results,
            args.prompts,
            name=args.name,
            model=args.model,
            corpus_dir=args.corpus,
            runs_root=args.runs_root,
            notes=args.notes,
        )
        for run_path in written:
            print(run_path)
        if args.judge_models:
            judges = parse_judge_models(args.judge_models)
            for run_path in written:
                asyncio.run(rejudge(run_path, judge_models=judges))
                print(f"judged {run_path}")
