"""Ingest a corpus directory into one index variant.

Usage:
    python -m glossator.ingest --corpus corpus/mistral-docs --variant sec1024
"""

import argparse
import asyncio
from pathlib import Path

from dotenv import load_dotenv

from glossator.index.variants import VARIANTS
from glossator.ingest.pipeline import (
    DEFAULT_CONCURRENCY,
    IngestReport,
    PartialIngestError,
    ingest_corpus,
)
from glossator.retrieval.probe import EmbeddingProbeError, probe_embedding


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
    parser.add_argument(
        "--skip-probe",
        action="store_true",
        help="Index without checking the embedding model first (D-031)",
    )
    return parser.parse_args()


def _summary(report: IngestReport) -> str:
    return (
        f"{report.variant}: indexed {report.chunks} chunks from {report.pages} page(s); "
        f"{report.embedding_tokens} embedding tokens (~${report.estimated_usd:.4f})"
    )


async def main() -> None:
    load_dotenv(override=True)
    args = _parse_args()
    if not args.skip_probe:
        # Before anything is embedded, not after: a corpus indexed with a broken
        # embedding model looks exactly like a corpus indexed correctly, and the
        # only cheap moment to find out is before the spend (D-031).
        try:
            print(f"embedding probe: {(await probe_embedding(args.variant)).summary()}")
        except EmbeddingProbeError as exc:
            raise SystemExit(str(exc)) from None
    try:
        report = await ingest_corpus(args.corpus, args.variant, concurrency=args.concurrency)
    except PartialIngestError as exc:
        # Report what did land before failing: a partial index is still worth
        # knowing the size of, and the exit code is what a script reads.
        print(_summary(exc.report))
        raise SystemExit(str(exc)) from None
    print(_summary(report))


if __name__ == "__main__":
    asyncio.run(main())
