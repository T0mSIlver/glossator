"""Every page's sizes, and the distributions and budget fits computed from them."""

from __future__ import annotations

import math
import statistics
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict

from glossator.eval.corpus_stats.tokens import TokenCounter
from glossator.index.variants import ChunkStrategy
from glossator.ingest.chunker import CorpusChunker, PageFacts, build_chunker
from glossator.ingest.pages import CorpusPage

RUN_KIND = "corpus-stats"

# The read-page budgets the surface redesign is deciding between, and the tail
# markers that make the histogram readable: where the budget lines sit among
# the pages.
THRESHOLDS = (2_000, 4_000, 8_000, 16_000, 32_000)
MARKERS = (4_000, 8_000, 16_000)
READ_PAGE_BUDGETS = (8_000, 16_000)
LARGEST_PAGES = 10


class PageStats(BaseModel):
    """One measured page: a row of ``pages.jsonl``."""

    model_config = ConfigDict(frozen=True)

    url: str
    kind: str
    locale: str
    tokens: int
    characters: int
    chunks: int


def measure_page(
    page: CorpusPage, *, count_tokens: TokenCounter, chunker: CorpusChunker | None = None
) -> PageStats:
    """One page's sizes. The token counter is injected so tests never download."""
    chunker = chunker or build_chunker(ChunkStrategy.SECTION)
    facts = PageFacts(url=page.url, title=page.title, kind=page.kind, locale=page.locale)
    chunks = chunker.plan(page.body, facts)
    return PageStats(
        url=page.url,
        kind=page.kind,
        locale=page.locale,
        tokens=count_tokens(page.body),
        characters=len(page.body),
        chunks=len(chunks),
    )


def percentile(values: Sequence[int], fraction: float) -> float:
    """Linear-interpolation percentile, the inclusive method: the value at
    ``fraction`` of the way through the sorted values, so p50 of an even count
    is the mean of the middle pair and p0/p1 are the min/max."""
    if not values:
        raise ValueError("percentile of no values")
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def distribution(values: Sequence[int]) -> dict[str, Any]:
    """The distribution rows the README and metrics carry, rounded to whole
    tokens: a fraction of a token has no meaning for a budget decision."""
    return {
        "n": len(values),
        "min": min(values),
        "p50": round(percentile(values, 0.50)),
        "p75": round(percentile(values, 0.75)),
        "p90": round(percentile(values, 0.90)),
        "p95": round(percentile(values, 0.95)),
        "p99": round(percentile(values, 0.99)),
        "max": max(values),
        "mean": round(statistics.fmean(values)),
    }


def shares_under(values: Sequence[int], thresholds: Sequence[int] = THRESHOLDS) -> dict[str, Any]:
    """How much of the corpus each budget holds whole, keyed by threshold."""
    total = len(values) or 1
    return {
        str(threshold): {
            "threshold": threshold,
            "pages": sum(1 for value in values if value < threshold),
            "share": round(sum(1 for value in values if value < threshold) / total, 4),
        }
        for threshold in thresholds
    }


def read_page_fits(
    values: Sequence[int], budgets: Sequence[int] = READ_PAGE_BUDGETS
) -> dict[str, Any]:
    """What each budget means for one ``read_page`` call: how many pages fit
    whole, and how many median-sized pages the budget holds."""
    median = percentile(values, 0.50) or 1.0
    shares = shares_under(values, budgets)
    return {
        str(budget): {
            "budget": budget,
            "pages_fitting_whole": shares[str(budget)]["pages"],
            "share_fitting_whole": shares[str(budget)]["share"],
            "median_sized_pages_per_call": max(1, math.floor(budget / median)),
        }
        for budget in budgets
    }


def totals_by_kind(rows: Sequence[PageStats]) -> dict[str, Any]:
    tokens = sum(row.tokens for row in rows) or 1
    kinds = sorted({row.kind for row in rows})
    return {
        kind: {
            "pages": sum(1 for row in rows if row.kind == kind),
            "tokens": sum(row.tokens for row in rows if row.kind == kind),
            "token_share": round(sum(row.tokens for row in rows if row.kind == kind) / tokens, 4),
            "characters": sum(row.characters for row in rows if row.kind == kind),
            "chunks": sum(row.chunks for row in rows if row.kind == kind),
        }
        for kind in kinds
    }


def largest_pages(rows: Sequence[PageStats], count: int = LARGEST_PAGES) -> list[PageStats]:
    """The biggest pages by token count; ties keep the corpus's path order."""
    return sorted(rows, key=lambda row: -row.tokens)[:count]


def summarize(rows: Sequence[PageStats], config: dict[str, Any]) -> dict[str, Any]:
    tokens = [row.tokens for row in rows]
    return {
        "kind": RUN_KIND,
        "config": config,
        "totals": {
            "pages": len(rows),
            "tokens": sum(tokens),
            "characters": sum(row.characters for row in rows),
            "chunks": sum(row.chunks for row in rows),
        },
        "distribution": distribution(tokens),
        "shares_under": shares_under(tokens),
        "read_page_budgets": read_page_fits(tokens),
        "largest_pages": [row.model_dump() for row in largest_pages(rows)],
        "by_kind": totals_by_kind(rows),
    }
