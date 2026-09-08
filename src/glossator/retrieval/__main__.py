"""Search the index from the command line.

Usage:
    python -m glossator.retrieval "how do I stream a chat completion" --variant sec1024 --top-k 10
"""

import argparse
import asyncio

from dotenv import load_dotenv

from glossator.index.variants import VARIANTS
from glossator.retrieval.config import DEFAULT_TOP_K, KINDS, RetrievalConfig
from glossator.retrieval.engine import SearchEngine


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
    return parser.parse_args()


async def main() -> None:
    load_dotenv(override=True)
    args = _parse_args()
    config = RetrievalConfig(
        variant=args.variant,
        top_k=args.top_k,
        kinds=frozenset(args.kind or ()),
        locales=frozenset(args.locale or ()),
    )
    hits = await SearchEngine(config).search(args.query)

    print(f"{args.query!r} on {config.index_variant.schema_name} ({len(hits)} hits)")
    for rank, hit in enumerate(hits, 1):
        print(f"\n{rank}. {hit.citation_url}  score={hit.score:.4f}")
        print(f"   {hit.heading_line}")
        print(f"   {hit.preview()}")


if __name__ == "__main__":
    asyncio.run(main())
