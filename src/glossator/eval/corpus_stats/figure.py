"""The page-size histogram: log x-axis, budget lines, hand-written SVG."""

from __future__ import annotations

import math
from collections.abc import Sequence
from xml.sax.saxutils import escape

from glossator.eval.charts import SERIES_COLORS
from glossator.eval.corpus_stats.measure import MARKERS
from glossator.eval.corpus_stats.tokens import MEDIUM_MODEL_ID, MEDIUM_TOKENIZER_REPO

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
