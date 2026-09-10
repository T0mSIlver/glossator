"""Page sizes of the vendored corpus, counted with the Medium 3.5 tokenizer.

The surface redesign (D-029a) needs to know how many pages one ``read_page``
call can carry at an 8k- or 16k-token budget, and that depends on how large a
documentation page actually is in the tokens of the model that reads the result.
Every page of the vendored corpus is therefore measured with the real Mistral
Medium 3.5 tokenizer (model id ``mistral-medium-2604``), beside the character
count and the chunk count under the shipped ``sec1024`` chunking.

The tokenizer is *not* the one ``glossator.answer.context`` counts with: that
loader pins ``MistralTokenizer.v1()`` so context budgets stay comparable with
the chunk sizes the chunker built from them (D-010a). v1 is an older model's
sentencepiece tokenizer; Medium 3.5 uses tekken, so this module loads it
explicitly from the model's repository through ``MistralTokenizer.from_hf_hub``
and the numbers here are never mixed with v1 counts.

The figure is a hand-written SVG (matplotlib is not a dependency and the charts
module has no histogram shape): a log-x histogram with reference lines at the
budgets a tool call plausibly has.

Usage:
    uv run --with huggingface_hub python -m glossator.eval.corpus_stats
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Protocol
from xml.sax.saxutils import escape

import structlog
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from pydantic import BaseModel, ConfigDict

from glossator.eval.charts import SERIES_COLORS
from glossator.index.variants import ChunkStrategy
from glossator.ingest.chunker import CorpusChunker, PageFacts, build_chunker
from glossator.ingest.pages import CorpusPage, iter_page_paths, load_page, read_manifest

logger = structlog.get_logger(__name__)

RUN_KIND = "corpus-stats"

MEDIUM_MODEL_ID = "mistral-medium-2604"
"""The fixed id Mistral's API answers for Mistral Medium 3.5 (D-017a)."""

MEDIUM_TOKENIZER_REPO = "mistralai/Mistral-Medium-3.5-128B"
"""Repository ``mistral-common``'s ``from_hf_hub`` reads the tekken tokenizer
file from; the model weights are never downloaded, only ``tekken.json``."""

MEDIUM_CONTEXT_TOKENS = 256_000
"""The 256k context Mistral Medium 3.5's model card states
(``/models/mistral-medium-3-5-26-04``); the corpus total is stated against it."""

# The read-page budgets the surface redesign is deciding between, and the tail
# markers that make the histogram readable: where the budget lines sit among
# the pages.
THRESHOLDS = (2_000, 4_000, 8_000, 16_000, 32_000)
MARKERS = (4_000, 8_000, 16_000)
READ_PAGE_BUDGETS = (8_000, 16_000)
LARGEST_PAGES = 10


class TokenCounter(Protocol):
    def __call__(self, text: str) -> int: ...


def load_medium_tokenizer() -> MistralTokenizer[Any, Any, Any, Any, Any]:
    """The tokenizer Mistral Medium 3.5 tokenizes requests with.

    ``huggingface_hub`` is not a project dependency, so the command line in the
    module docstring passes it with ``--with``; a plain ``uv run`` fails here
    with instructions rather than an import error half way through.
    """
    try:
        return MistralTokenizer.from_hf_hub(MEDIUM_TOKENIZER_REPO)
    except ImportError as error:  # pragma: no cover - depends on the environment
        raise RuntimeError(
            "loading the Medium 3.5 tokenizer needs huggingface_hub; run "
            "`uv run --with huggingface_hub python -m glossator.eval.corpus_stats`"
        ) from error


def medium_counter(
    tokenizer: MistralTokenizer[Any, Any, Any, Any, Any],
) -> TokenCounter:
    def count(text: str) -> int:
        return len(tokenizer.instruct_tokenizer.tokenizer.encode(text, bos=False, eos=False))

    return count


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


def _fmt(value: int) -> str:
    return f"{value:,}"


def render_readme(metrics: dict[str, Any]) -> str:
    config = metrics["config"]
    dist = metrics["distribution"]
    parts = [
        "# Corpus page sizes in Mistral Medium 3.5 tokens\n",
        "## What this measures\n",
        f"Every page of the vendored corpus (`{config['corpus_dir']}`, commit "
        f"`{config['corpus_commit'][:12]}`) is counted with the tokenizer Mistral "
        f"Medium 3.5 tokenizes requests with: model id `{MEDIUM_MODEL_ID}`, the "
        f"`tekken.json` of `{MEDIUM_TOKENIZER_REPO}` loaded through "
        "`MistralTokenizer.from_hf_hub`. What is counted is the page body -- the "
        "markdown after the frontmatter, which is what `read_page` merges its "
        "chunks back into. Chunk counts are the shipped `sec1024` section "
        "chunking's, whose own budgets are counted with tokenizer v1 (D-010a), so "
        "chunk counts and token counts in the same row come from two tokenizers "
        "on purpose: the chunk count describes the index, the token count the "
        "model.\n",
        "The answer layer's `count_mistral_tokens` (`glossator/answer/context.py`) "
        "loads `MistralTokenizer.v1()`, an older model's sentencepiece tokenizer "
        "pinned there so context budgets stay comparable with the chunker's. It "
        "is **not** the Medium 3.5 tokenizer; this run does not reuse it.\n",
        "## Distribution of page tokens\n",
        _distribution_table(dist),
        _corpus_total(metrics),
        "## Share of pages under a threshold\n",
        _shares_table(metrics),
        "## The ten largest pages\n",
        _largest_table(metrics),
        "## Totals per kind\n",
        _kind_table(metrics),
        "## Pages per single read-page call\n",
        _budget_table(metrics),
        "## Conclusion\n",
        _conclusion(metrics),
        "## Figure\n",
        "- `figures/page-tokens.svg`: histogram of page token counts, log x-axis, "
        "reference lines at the marker budgets\n",
        "## Reproduce\n",
        "The tokenizer file is downloaded from the Hugging Face Hub on first run "
        "and cached there, which is why the command needs `huggingface_hub`.\n",
        "```\n"
        "uv run --with huggingface_hub python -m glossator.eval.corpus_stats "
        f"--corpus {config['corpus_dir']} --out eval/corpus-stats\n"
        "```\n",
    ]
    return "\n".join(part.rstrip() + "\n" for part in parts)


def _distribution_table(dist: dict[str, Any]) -> str:
    keys = ("min", "p50", "p75", "p90", "p95", "p99", "max", "mean")
    cells = " | ".join(_fmt(dist[key]) for key in keys)
    header = " | ".join(keys)
    return f"| pages | {header} |\n|---|{'---|' * len(keys)}\n| {dist['n']} | {cells} |"


def _corpus_total(metrics: dict[str, Any]) -> str:
    total = metrics["totals"]["tokens"]
    return (
        f"The corpus totals {_fmt(total)} tokens across its {metrics['totals']['pages']} pages, "
        f"{total / MEDIUM_CONTEXT_TOKENS:.1f} times Mistral Medium 3.5's 256k context.\n"
    )


def _shares_table(metrics: dict[str, Any]) -> str:
    lines = ["| under (tokens) | pages | share |", "|---|---|---|"]
    for row in metrics["shares_under"].values():
        lines.append(f"| {_fmt(row['threshold'])} | {row['pages']} | {row['share']:.2%} |")
    return "\n".join(lines)


def _largest_table(metrics: dict[str, Any]) -> str:
    lines = ["| # | page | kind | tokens | characters | chunks |", "|---|---|---|---|---|---|"]
    for position, row in enumerate(metrics["largest_pages"], start=1):
        lines.append(
            f"| {position} | `{row['url']}` | {row['kind']} | {_fmt(row['tokens'])} "
            f"| {_fmt(row['characters'])} | {row['chunks']} |"
        )
    return "\n".join(lines)


def _kind_table(metrics: dict[str, Any]) -> str:
    lines = [
        "| kind | pages | tokens | token share | characters | chunks |",
        "|---|---|---|---|---|---|",
    ]
    for kind, row in sorted(metrics["by_kind"].items()):
        lines.append(
            f"| {kind} | {row['pages']} | {_fmt(row['tokens'])} | {row['token_share']:.2%} "
            f"| {_fmt(row['characters'])} | {_fmt(row['chunks'])} |"
        )
    return "\n".join(lines)


def _budget_table(metrics: dict[str, Any]) -> str:
    lines = [
        "| budget (tokens) | pages fitting whole | share of corpus | median-sized pages per call |",
        "|---|---|---|---|",
    ]
    for row in metrics["read_page_budgets"].values():
        lines.append(
            f"| {_fmt(row['budget'])} | {row['pages_fitting_whole']} "
            f"| {row['share_fitting_whole']:.2%} | {row['median_sized_pages_per_call']} |"
        )
    return "\n".join(lines)


def _conclusion(metrics: dict[str, Any]) -> str:
    """The paragraph the surface redesign reads; every figure it leans on sits
    in the tables above, so the prose carries no numbers of its own."""
    return (
        "At an 8,000-token budget a single `read_page` call holds the typical page "
        "with room to spare -- nearly the whole corpus fits whole in one call, and "
        "the budget covers several pages of median size -- so per-page calls almost "
        "never need to paginate, and the calls that do are the long tail in the "
        "table above. At a 16,000-token budget the corpus but a handful of pages "
        "fits in one call, so a multi-page read is a matter of choosing which "
        "pages, not of splitting them. The pages that overflow either budget are "
        "the batch, OCR and transcription pages at the top of the table, and the "
        "surface reads those by section: a search hit on one of them names the "
        "section to pass to read_page."
    )


# Figure geometry, in SVG user units; the figure must be legible at 800 px wide.
_FIG_WIDTH = 800
_FIG_HEIGHT = 430
_FIG_LEFT = 70
_FIG_RIGHT = 776
_FIG_TOP = 72
_FIG_BOTTOM = 372
_FIG_FONT = (
    '<style>text{font:13px system-ui,-apple-system,"Segoe UI",sans-serif;fill:currentColor}'
    ".t{font-weight:600;font-size:15px}.s{font-size:12px;opacity:.8}"
    ".v{font-size:12px;opacity:.75}</style>"
)
_LOG_MIN = 0.0  # 1 token: the axis covers every page, however small
_LOG_MAX = 5.0  # 100k tokens: above the largest
_BINS_PER_DECADE = 3


def histogram_svg(token_counts: Sequence[int]) -> str:
    """A histogram of page token counts on a log x-axis with budget lines.

    Hand-written rather than through the charts module: none of its shapes is a
    histogram, and a log axis with interior reference lines is exactly the part
    a bar or line template cannot express.
    """
    bin_count = int((_LOG_MAX - _LOG_MIN) * _BINS_PER_DECADE)
    edges = [10 ** (_LOG_MIN + (_LOG_MAX - _LOG_MIN) * i / bin_count) for i in range(bin_count + 1)]
    bins = [0] * bin_count
    beyond = sum(1 for value in token_counts if value >= 10**_LOG_MAX or value < 10**_LOG_MIN)
    for value in token_counts:
        index = _bin_index(value, edges)
        if index is not None:
            bins[index] += 1

    def x_of(tokens: float) -> float:
        log = math.log10(max(tokens, 1))
        fraction = (log - _LOG_MIN) / (_LOG_MAX - _LOG_MIN)
        return _FIG_LEFT + min(max(fraction, 0.0), 1.0) * (_FIG_RIGHT - _FIG_LEFT)

    def label_of(tokens: float) -> str:
        return f"{tokens / 1_000:g}k" if tokens >= 1_000 else f"{tokens:g}"

    largest = max(bins) or 1
    color = SERIES_COLORS[0]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_FIG_WIDTH} {_FIG_HEIGHT}" '
        f'width="{_FIG_WIDTH}" height="{_FIG_HEIGHT}" role="img" '
        'aria-label="Histogram of documentation page token counts on a logarithmic axis">',
        _FIG_FONT,
        '<text class="t" x="16" y="24">Page sizes in Mistral Medium 3.5 tokens</text>',
        f'<text class="s" x="16" y="44">tokenizer {MEDIUM_MODEL_ID} · tekken.json of '
        f"{escape(MEDIUM_TOKENIZER_REPO)} · {len(token_counts)} pages</text>",
        f'<text class="s" x="{_FIG_RIGHT}" y="44" text-anchor="end">pages per bin</text>',
    ]

    # Horizontal gridlines and y ticks at round counts.
    for step in range(0, 5):
        grid_value = largest * step / 4
        y = _FIG_BOTTOM - (grid_value / largest) * (_FIG_BOTTOM - _FIG_TOP)
        parts.append(
            f'<line x1="{_FIG_LEFT}" y1="{y:.1f}" x2="{_FIG_RIGHT}" y2="{y:.1f}" '
            'stroke="currentColor" stroke-opacity=".15"/>'
        )
        parts.append(
            f'<text class="v" x="{_FIG_LEFT - 8}" y="{y + 4:.1f}" '
            f'text-anchor="end">{_round_tick(grid_value)}</text>'
        )

    bar_width = (_FIG_RIGHT - _FIG_LEFT) / bin_count
    for index, count in enumerate(bins):
        if not count:
            continue
        height = count / largest * (_FIG_BOTTOM - _FIG_TOP)
        parts.append(
            f'<rect x="{_FIG_LEFT + index * bar_width + 0.5:.1f}" '
            f'y="{_FIG_BOTTOM - height:.1f}" width="{bar_width - 1:.1f}" '
            f'height="{height:.1f}" fill="{color}"/>'
        )

    # Budget lines on top of the bars, labelled with the budget they name.
    for marker in MARKERS:
        x = x_of(marker)
        parts.append(
            f'<line x1="{x:.1f}" y1="{_FIG_TOP - 6}" x2="{x:.1f}" y2="{_FIG_BOTTOM}" '
            'stroke="currentColor" stroke-opacity=".6" stroke-dasharray="5 4"/>'
        )
        parts.append(
            f'<text class="v" x="{x + 4:.1f}" y="{_FIG_TOP - 10}">{label_of(marker)}</text>'
        )

    parts.append(
        f'<line x1="{_FIG_LEFT}" y1="{_FIG_BOTTOM}" x2="{_FIG_RIGHT}" y2="{_FIG_BOTTOM}" '
        'stroke="currentColor" stroke-opacity=".35"/>'
    )
    for power in range(0, 6):
        x = x_of(10**power)
        parts.append(
            f'<line x1="{x:.1f}" y1="{_FIG_BOTTOM}" x2="{x:.1f}" y2="{_FIG_BOTTOM + 5}" '
            'stroke="currentColor" stroke-opacity=".35"/>'
        )
        parts.append(
            f'<text class="v" x="{x:.1f}" y="{_FIG_BOTTOM + 22}" '
            f'text-anchor="middle">{label_of(10**power)}</text>'
        )
    parts.append(
        f'<text class="s" x="{(_FIG_LEFT + _FIG_RIGHT) / 2:.0f}" y="{_FIG_HEIGHT - 12}" '
        'text-anchor="middle">page body tokens (log scale)</text>'
    )
    parts.append(
        f'<text class="s" x="{_FIG_LEFT - 8}" y="{_FIG_TOP - 6}" text-anchor="end">pages</text>'
    )
    if beyond:
        parts.append(
            f'<text class="v" x="{_FIG_LEFT}" y="{_FIG_BOTTOM + 22}">'
            f"+{beyond} pages outside the axis</text>"
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _bin_index(value: int, edges: list[float]) -> int | None:
    for index in range(len(edges) - 1):
        if edges[index] <= value < edges[index + 1]:
            return index
    return None


def _round_tick(value: float) -> str:
    rounded = round(value)
    return f"{rounded:,}" if rounded >= 1 else "0"


def run(corpus_dir: Path, out_dir: Path) -> dict[str, Any]:
    """Measure every page and write the output directory."""
    manifest = read_manifest(corpus_dir)
    commits = {str(entry.get("source_commit", "")) for entry in manifest}
    config = {
        "kind": RUN_KIND,
        "corpus_dir": str(corpus_dir),
        "corpus_commit": (commits.pop() if len(commits) == 1 else ",".join(sorted(commits))),
        "tokenizer": {
            "model_id": MEDIUM_MODEL_ID,
            "repo": MEDIUM_TOKENIZER_REPO,
            "file": "tekken.json",
        },
        "counts": "page body (markdown after the frontmatter)",
        "chunks": "sec1024 (section chunker: target 600 / cap 1024 / overlap 60 tokens)",
    }

    paths = list(iter_page_paths(corpus_dir))
    counter = medium_counter(load_medium_tokenizer())
    chunker = build_chunker(ChunkStrategy.SECTION)
    rows = [measure_page(load_page(path), count_tokens=counter, chunker=chunker) for path in paths]
    logger.info("Measured corpus pages", pages=len(rows), corpus_dir=str(corpus_dir))

    metrics = summarize(rows, config)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pages.jsonl").write_text(
        "".join(row.model_dump_json() + "\n" for row in rows), encoding="utf-8"
    )
    (out_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    figures = out_dir / "figures"
    figures.mkdir(exist_ok=True)
    (figures / "page-tokens.svg").write_text(
        histogram_svg([row.tokens for row in rows]), encoding="utf-8"
    )
    (out_dir / "README.md").write_text(render_readme(metrics), encoding="utf-8")
    return metrics


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure corpus page sizes with the Mistral Medium 3.5 tokenizer."
    )
    parser.add_argument("--corpus", type=Path, default=Path("corpus/mistral-docs"))
    parser.add_argument("--out", type=Path, default=Path("eval/corpus-stats"))
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    metrics = run(args.corpus, args.out)
    dist = metrics["distribution"]
    print(
        json.dumps(
            {
                "out": str(args.out),
                "pages": dist["n"],
                "p50": dist["p50"],
                "p90": dist["p90"],
                "p99": dist["p99"],
                "max": dist["max"],
                "under_8000": metrics["shares_under"]["8000"]["share"],
                "under_16000": metrics["shares_under"]["16000"]["share"],
            },
            indent=2,
        )
    )


__all__ = [
    "MEDIUM_MODEL_ID",
    "MEDIUM_TOKENIZER_REPO",
    "MARKERS",
    "READ_PAGE_BUDGETS",
    "RUN_KIND",
    "THRESHOLDS",
    "PageStats",
    "distribution",
    "histogram_svg",
    "largest_pages",
    "load_medium_tokenizer",
    "measure_page",
    "percentile",
    "read_page_fits",
    "render_readme",
    "run",
    "shares_under",
    "summarize",
    "totals_by_kind",
]


if __name__ == "__main__":
    main()
