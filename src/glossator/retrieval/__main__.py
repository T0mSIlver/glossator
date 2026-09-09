"""Search the index from the command line.

Usage:
    python -m glossator.retrieval "how do I stream a chat completion" --variant sec1024 --top-k 10
"""

import argparse
import asyncio

from dotenv import load_dotenv

from glossator.index.variants import VARIANTS
from glossator.retrieval.config import (
    DEFAULT_RERANK_CANDIDATES,
    DEFAULT_TOP_K,
    KINDS,
    RetrievalConfig,
)
from glossator.retrieval.engine import SearchEngine
from glossator.retrieval.probe import EmbeddingProbeError, check_embedding_once


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search the glossator documentation index.")
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--variant",
        default="sec1024",
        choices=sorted(VARIANTS),
        help="Index variant to search",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help=f"Hits to return (default: {DEFAULT_TOP_K})",
    )
    parser.add_argument(
        "--kind",
        action="append",
        choices=sorted(KINDS),
        help="Restrict to a page kind (repeatable)",
    )
    parser.add_argument("--locale", action="append", help="Restrict to a locale (repeatable)")
    parser.add_argument(
        "--rerank",
        action="store_true",
        help="Reorder the candidates with one listwise model call",
    )
    parser.add_argument(
        "--rerank-candidates",
        type=int,
        default=DEFAULT_RERANK_CANDIDATES,
        help=f"Hits the reranker reads (default: {DEFAULT_RERANK_CANDIDATES})",
    )
    parser.add_argument(
        "--footing",
        action="store_true",
        help="Report whether the query has any word in common with the corpus",
    )
    parser.add_argument(
        "--skip-probe",
        action="store_true",
        help="Search without checking the embedding model first (D-031)",
    )
    return parser.parse_args()


async def main() -> None:
    load_dotenv()
    args = _parse_args()
    config = RetrievalConfig(
        variant=args.variant,
        top_k=args.top_k,
        kinds=frozenset(args.kind or ()),
        locales=frozenset(args.locale or ()),
        rerank=args.rerank,
        rerank_candidates=max(args.rerank_candidates, args.top_k),
        check_lexical_footing=args.footing,
    )
    if not args.skip_probe:
        try:
            await check_embedding_once(config.variant)
        except EmbeddingProbeError as exc:
            raise SystemExit(str(exc)) from None

    hits, trace = await SearchEngine(config).search_with_trace(args.query)

    print(
        f"{args.query!r} on {config.index_variant.schema_name} "
        f"({trace.kept}/{trace.considered} hits, {trace.latency_ms:.0f} ms)"
    )
    if trace.lexical_footing is False:
        print(f"note: no lexical footing; the corpus contains none of {list(trace.missing_terms)}")
    if trace.rerank is not None:
        if trace.rerank.applied:
            print(
                f"note: reranked {trace.rerank.candidates} candidates on "
                f"{trace.rerank.model} for ${trace.rerank.cost_usd:.6f}"
            )
        else:
            print(f"note: rerank fell back to retrieval order ({trace.rerank.error})")
    for rank, hit in enumerate(hits, 1):
        score = f"score={hit.score:.4f}"
        if hit.retrieval_score is not None:
            score += f" retrieval={hit.retrieval_score:.4f}"
        if hit.similarity is not None:
            score += f" cosine={hit.similarity:.4f}"
        print(f"\n{rank}. {hit.citation_url}  {score}")
        print(f"   {hit.heading_line}")
        print(f"   {hit.preview()}")


if __name__ == "__main__":
    asyncio.run(main())
