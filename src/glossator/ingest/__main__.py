"""Ingest a corpus directory into one index variant.

Usage:
    python -m glossator.ingest --corpus corpus/mistral-docs --variant sec1024
"""

import argparse
import asyncio
from pathlib import Path

from dotenv import load_dotenv

from glossator.index.variants import VARIANTS
from glossator.ingest.pipeline import DEFAULT_CONCURRENCY, ingest_corpus


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest a corpus directory into a Vespa index variant."
    )
    parser.add_argument(
        "--corpus", type=Path, required=True, help="Corpus directory of markdown pages"
    )
    parser.add_argument(
        "--variant",
        required=True,
        choices=sorted(VARIANTS),
        help="Index variant to write",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Pages processed at once (default: {DEFAULT_CONCURRENCY})",
    )
    return parser.parse_args()


async def main() -> None:
    load_dotenv(override=True)
    args = _parse_args()
    report = await ingest_corpus(
        args.corpus, args.variant, concurrency=args.concurrency
    )
    print(
        f"{report.variant}: indexed {report.chunks} chunks from {report.pages} page(s); "
        f"{report.embedding_tokens} embedding tokens (~${report.estimated_usd:.4f})"
    )
    if report.failures:
        raise SystemExit(
            f"{len(report.failures)} page(s) failed: {', '.join(report.failures)}"
        )


if __name__ == "__main__":
    asyncio.run(main())
