"""Ask the documentation a question from the command line.

Usage:
    python -m glossator.answer "how do I stream a chat completion" --strategy single_pass
"""

import argparse
import asyncio

from dotenv import load_dotenv

from glossator.answer.citations import Answer
from glossator.answer.config import DEFAULT_VARIANT, AnswerConfig
from glossator.answer.llm import JsonlCallRecorder
from glossator.answer.service import STRATEGIES, ask
from glossator.index.variants import VARIANTS


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Answer a question from Mistral's documentation.")
    parser.add_argument("question", help="The question to answer")
    parser.add_argument(
        "--strategy",
        default="single_pass",
        choices=sorted(STRATEGIES),
        help="How to gather evidence before answering",
    )
    parser.add_argument(
        "--variant",
        default=DEFAULT_VARIANT,
        choices=sorted(VARIANTS),
        help="Index variant to search",
    )
    parser.add_argument(
        "--model",
        help="Generation model id; defaults to the one in AnswerConfig",
    )
    parser.add_argument(
        "--rewrite",
        action="store_true",
        help="Reword the question into the documentation's vocabulary before retrieval",
    )
    parser.add_argument(
        "--record",
        help="Write every model call, verbatim, as JSON lines to this path",
    )
    return parser.parse_args()


def _print(answer: Answer) -> None:
    print(answer.answer_markdown)
    print()
    if answer.insufficient_evidence:
        print("insufficient evidence")
    print(f"Citations ({len(answer.citations)} verified):")
    for citation in answer.citations:
        # A citation that only matched after normalization is still verified, but
        # the eval counts it apart, so the CLI says so too.
        note = f"  ({citation.reason})" if citation.reason else ""
        print(f"  [{citation.n}] verified  {citation.citation_url}{note}")
        print(f'      "{citation.quote}"')
    for citation in answer.trace.unverified_citations:
        print(f"  [{citation.n}] REJECTED  {citation.reason}")
        print(f'      "{citation.quote}"')
    print()
    print(f"Trace: {answer.trace.summary()}")
    for event in answer.trace.events:
        detail = event.note or ""
        print(
            f"  {event.step:>2}. r{event.round} {event.kind}/{event.name} "
            f"-> {len(event.result_ids)} ids {detail}".rstrip()
        )
    print()
    print(
        f"Tokens: {answer.usage.prompt_tokens} in / {answer.usage.completion_tokens} out"
        f" | {answer.latency_ms / 1000:.1f}s | ${answer.cost_usd:.4f}"
    )


async def main() -> None:
    load_dotenv(override=True)
    args = _parse_args()
    recorder = JsonlCallRecorder(args.record) if args.record else None
    try:
        answer = await ask(
            args.question,
            strategy=args.strategy,
            variant=args.variant,
            model=args.model,
            config=AnswerConfig(rewrite_for_retrieval=args.rewrite),
            recorder=recorder,
        )
    finally:
        if recorder is not None:
            recorder.close()
    _print(answer)


if __name__ == "__main__":
    asyncio.run(main())
