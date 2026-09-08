"""Re-run this smoke: five questions through each of the three answer strategies.

    uv run python eval/runs/2026-09-09-answer-smoke/replay.py --out eval/runs/<new-run>

Writes `config.json`, `calls.jsonl`, `records.jsonl` and `metrics.json` into the
output directory, appending as it goes so an interrupted run keeps what it paid
for. Needs `MISTRAL_API_KEY` and a running Vespa with the `sec1024` variant
ingested (`make setup-vespa && make ingest corpus=corpus/mistral-docs
variant=sec1024`).
"""

import argparse
import asyncio
import collections
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from glossator.answer.config import AnswerConfig
from glossator.answer.llm import JsonlCallRecorder, MistralLLM
from glossator.answer.outline import DEFAULT_MANIFEST
from glossator.answer.prompts import (
    GROUNDED_ANSWER_SYSTEM,
    GROUNDED_ANSWER_VERSION,
    OUTLINE_SYSTEM,
    OUTLINE_VERSION,
    SEARCH_LOOP_SYSTEM,
    SEARCH_LOOP_VERSION,
    prompt_hash,
)
from glossator.answer.service import ask, build_client
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import SearchEngine

QUESTIONS = [
    "How do I create a conversational workflow?",
    "What models support function calling?",
    "How do I configure a reranker in the Search Toolkit?",
    "What is the maximum number of tool calls in one response?",
    "Comment fonctionne le mode JSON avec l'API chat ?",
]

VARIANT = "sec1024"
RUN_DIR = Path(__file__).parent


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(RUN_DIR), help="Directory to write the run into")
    parser.add_argument(
        "--strategies",
        default="single_pass,search_loop,outline",
        help="Comma-separated strategy names",
    )
    parser.add_argument(
        "--questions", default="", help="Comma-separated indices into the question list"
    )
    parser.add_argument("--model", default="", help="Generation model id; default is Medium 3.5")
    return parser.parse_args()


def write_config(out: Path, config: AnswerConfig, strategies: list[str], questions: list[str]) -> None:
    """Every parameter of the run, including what the outline numbering depends on."""
    manifest = DEFAULT_MANIFEST.read_bytes() if DEFAULT_MANIFEST.exists() else b""
    (out / "config.json").write_text(
        json.dumps(
            {
                "variant": VARIANT,
                "strategies": strategies,
                "questions": questions,
                "answer_config": config.model_dump(mode="json"),
                # The outline strategy numbers pages by their order in the
                # manifest, so a different manifest means different page numbers
                # in `calls.jsonl` for the same question.
                "corpus_manifest_sha256": hashlib.sha256(manifest).hexdigest(),
                "prompts": {
                    GROUNDED_ANSWER_VERSION: prompt_hash(GROUNDED_ANSWER_SYSTEM),
                    SEARCH_LOOP_VERSION: prompt_hash(SEARCH_LOOP_SYSTEM),
                    OUTLINE_VERSION: prompt_hash(OUTLINE_SYSTEM),
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_metrics(out: Path) -> dict[str, Any]:
    """Aggregate the records into the table the README prints."""
    records = [json.loads(line) for line in (out / "records.jsonl").read_text().splitlines()]
    calls = [json.loads(line) for line in (out / "calls.jsonl").read_text().splitlines()]

    def blank() -> dict[str, float]:
        return dict.fromkeys(
            (
                "questions",
                "prompt_tokens",
                "completion_tokens",
                "cost_usd",
                "latency_s",
                "verified_citations",
                "rejected_citations",
                "distinct_sources_cited",
                "insufficient_evidence",
            ),
            0.0,
        )

    by_strategy: dict[str, dict[str, float]] = collections.defaultdict(blank)
    for record in records:
        if "error" in record:
            continue
        row = by_strategy[record["strategy"]]
        row["questions"] += 1
        row["prompt_tokens"] += record["usage"]["prompt_tokens"]
        row["completion_tokens"] += record["usage"]["completion_tokens"]
        row["cost_usd"] += record["cost_usd"]
        row["latency_s"] += record["latency_ms"] / 1000
        row["verified_citations"] += len(record["citations"])
        row["rejected_citations"] += len(record["trace"]["unverified_citations"])
        row["distinct_sources_cited"] += len({c["n"] for c in record["citations"]})
        row["insufficient_evidence"] += int(record["insufficient_evidence"])

    for row in by_strategy.values():
        total = row["verified_citations"] + row["rejected_citations"]
        row["quote_verification_rate"] = round(row["verified_citations"] / total, 3) if total else 0.0
        row["cost_usd"] = round(row["cost_usd"], 6)
        row["latency_s"] = round(row["latency_s"], 1)

    metrics = {
        "model": calls[0]["model"] if calls else "",
        "variant": VARIANT,
        "questions": len({record["question"] for record in records}),
        "llm_calls": len(calls),
        "prompt_tokens": sum(call["usage"]["prompt_tokens"] for call in calls),
        "completion_tokens": sum(call["usage"]["completion_tokens"] for call in calls),
        "cost_usd": round(sum(call["cost_usd"] for call in calls), 6),
        "errors": sum(1 for call in calls if call["error"]),
        "by_strategy": dict(by_strategy),
    }
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return metrics


async def main() -> None:
    load_dotenv(override=True)
    args = _parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    strategies = args.strategies.split(",")
    indices = (
        [int(index) for index in args.questions.split(",")]
        if args.questions
        else range(len(QUESTIONS))
    )
    questions = [QUESTIONS[index] for index in indices]

    config = AnswerConfig(model=args.model) if args.model else AnswerConfig()
    write_config(out, config, strategies, questions)

    engine = SearchEngine(RetrievalConfig(variant=VARIANT, top_k=config.top_k))
    recorder = JsonlCallRecorder(out / "calls.jsonl")
    llm = MistralLLM(config, client=build_client(), recorder=recorder)
    records = (out / "records.jsonl").open("a", encoding="utf-8")

    spent = 0.0
    for strategy in strategies:
        for question in questions:
            started = time.perf_counter()
            try:
                answer = await ask(
                    question,
                    strategy=strategy,
                    variant=VARIANT,
                    config=config,
                    engine=engine,
                    llm=llm,
                )
            except Exception as error:  # noqa: BLE001 - a run records its own failures
                records.write(
                    json.dumps(
                        {
                            "question": question,
                            "strategy": strategy,
                            "error": f"{type(error).__name__}: {error}",
                            "latency_ms": (time.perf_counter() - started) * 1000,
                        }
                    )
                    + "\n"
                )
                records.flush()
                print(f"FAILED {strategy} | {question} | {error}", file=sys.stderr, flush=True)
                continue
            spent += answer.cost_usd
            records.write(json.dumps({"variant": VARIANT, **answer.model_dump(mode="json")}) + "\n")
            records.flush()
            print(
                f"{strategy:12} | ${answer.cost_usd:.4f} | "
                f"{answer.usage.prompt_tokens}in/{answer.usage.completion_tokens}out | "
                f"{answer.latency_ms / 1000:.1f}s | "
                f"{len(answer.citations)} cited, "
                f"{len(answer.trace.unverified_citations)} rejected | "
                f"insufficient={answer.insufficient_evidence} | {question}",
                flush=True,
            )
        print(f"--- {strategy} done, running total ${spent:.4f}", flush=True)

    records.close()
    recorder.close()
    metrics = write_metrics(out)
    print(f"TOTAL ${metrics['cost_usd']:.4f} over {metrics['llm_calls']} calls")


if __name__ == "__main__":
    asyncio.run(main())
