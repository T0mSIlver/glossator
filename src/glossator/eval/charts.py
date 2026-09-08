"""The two chart shapes a run README needs, written straight to SVG.

D-023 asks for charts rendered by a script so they can be regenerated. Hand-written
SVG has no fonts to find, no backend to select, and nothing to download, which is
worth more here than a plotting library's flexibility: every figure in this project
is a bar chart, a line per configuration over a few k values, or a scatter of a
dozen points.
"""

from __future__ import annotations

from collections.abc import Sequence
from xml.sax.saxutils import escape

# Figure geometry, in SVG user units.
WIDTH = 720
ROW_HEIGHT = 26
BAR_HEIGHT = 16
LABEL_WIDTH = 240
MARGIN = 16
TITLE_HEIGHT = 34
PLOT_HEIGHT = 180
LEGEND_WIDTH = 190

# Chosen for contrast in both light and dark viewers; the SVG carries no
# background, so it inherits the page's.
SERIES_COLORS = ("#3b6fd4", "#c05621", "#2f855a", "#805ad5")

# Applied in turn each time the colours wrap, so a line chart of more than four
# series stays readable. The empty first entry is a solid line.
DASH_PATTERNS = (
    "",
    ' stroke-dasharray="6 3"',
    ' stroke-dasharray="2 3"',
    ' stroke-dasharray="9 3 2 3"',
)

_FONT = (
    '<style>text{font:13px system-ui,-apple-system,"Segoe UI",sans-serif;fill:currentColor}'
    ".t{font-weight:600;font-size:14px}.v{font-size:12px;opacity:.75}</style>"
)


def bar_chart(
    title: str,
    rows: Sequence[tuple[str, Sequence[float]]],
    series_names: Sequence[str],
) -> str:
    """A horizontal bar chart, one group of bars per row."""
    series_count = max(len(series_names), 1)
    bar = max(4, BAR_HEIGHT // series_count)
    height = TITLE_HEIGHT + max(len(rows), 1) * ROW_HEIGHT + MARGIN + 20
    largest = max((value for _label, values in rows for value in values), default=0.0) or 1.0
    plot_width = WIDTH - LABEL_WIDTH - MARGIN * 2 - 60

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" role="img" aria-label="{escape(title)}">',
        _FONT,
        f'<text class="t" x="{MARGIN}" y="22">{escape(title)}</text>',
    ]
    for index, (label, values) in enumerate(rows):
        top = TITLE_HEIGHT + index * ROW_HEIGHT
        parts.append(
            f'<text x="{LABEL_WIDTH}" y="{top + ROW_HEIGHT / 2 + 4}" '
            f'text-anchor="end">{escape(label)}</text>'
        )
        offset = top + (ROW_HEIGHT - bar * series_count) / 2
        for series, value in enumerate(values):
            width = max(0.0, value) / largest * plot_width
            color = SERIES_COLORS[series % len(SERIES_COLORS)]
            parts.append(
                f'<rect x="{LABEL_WIDTH + 8}" y="{offset + series * bar:.1f}" '
                f'width="{width:.1f}" height="{bar - 1}" fill="{color}"/>'
            )
        total_label = " / ".join(f"{value:g}" for value in values)
        parts.append(
            f'<text class="v" x="{LABEL_WIDTH + 12 + plot_width + 6}" '
            f'y="{top + ROW_HEIGHT / 2 + 4}">{escape(total_label)}</text>'
        )
    if series_names:
        legend_y = height - 8
        x = MARGIN
        for series, name in enumerate(series_names):
            color = SERIES_COLORS[series % len(SERIES_COLORS)]
            parts.append(
                f'<rect x="{x}" y="{legend_y - 9}" width="10" height="10" fill="{color}"/>'
            )
            parts.append(f'<text class="v" x="{x + 14}" y="{legend_y}">{escape(name)}</text>')
            x += 20 + 8 * len(name)
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def scatter(
    title: str,
    points: Sequence[tuple[str, float, float]],
    *,
    x_label: str,
    y_label: str,
) -> str:
    """A labelled scatter: one dot per point, with the axes' ranges printed.

    Both axes start at zero. A trade-off chart whose axes start at the data hides
    the size of the trade-off, which is the only thing it is drawn for.
    """
    height = 340
    left = 64
    bottom = height - 44
    top = TITLE_HEIGHT + 8
    right = WIDTH - MARGIN - 8
    x_max = max((x for _label, x, _y in points), default=1.0) or 1.0
    y_max = max((y for _label, _x, y in points), default=1.0) or 1.0
    x_max *= 1.15
    y_max = min(1.0, y_max * 1.15) if y_max <= 1.0 else y_max * 1.15

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" role="img" aria-label="{escape(title)}">',
        _FONT,
        f'<text class="t" x="{MARGIN}" y="22">{escape(title)}</text>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" '
        'stroke="currentColor" stroke-opacity=".35"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" '
        'stroke="currentColor" stroke-opacity=".35"/>',
        f'<text class="v" x="{right}" y="{bottom + 30}" text-anchor="end">{escape(x_label)}</text>',
        f'<text class="v" x="{MARGIN}" y="{top - 6}">{escape(y_label)}</text>',
        f'<text class="v" x="{left - 6}" y="{bottom + 4}" text-anchor="end">0</text>',
        f'<text class="v" x="{left - 6}" y="{top + 10}" text-anchor="end">{y_max:.2f}</text>',
        f'<text class="v" x="{right}" y="{bottom + 16}" text-anchor="end">{x_max:.1f}</text>',
    ]
    for index, (label, x_value, y_value) in enumerate(points):
        cx = left + (max(0.0, x_value) / x_max) * (right - left)
        cy = bottom - (max(0.0, y_value) / y_max) * (bottom - top)
        color = SERIES_COLORS[index % len(SERIES_COLORS)]
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{color}"/>')
        parts.append(
            f'<text class="v" x="{cx + 10:.1f}" y="{cy + 4:.1f}">'
            f"{escape(label)} ({x_value:.1f}, {y_value:.2f})</text>"
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


__all__ = ["SERIES_COLORS", "bar_chart", "scatter"]


def line_chart(
    title: str,
    x_labels: Sequence[str],
    series: Sequence[tuple[str, Sequence[float]]],
    *,
    y_max: float = 1.0,
) -> str:
    """A line per series over shared x positions, for a metric measured at several k."""
    height = TITLE_HEIGHT + PLOT_HEIGHT + 46
    left = MARGIN + 34
    plot_width = WIDTH - left - MARGIN - LEGEND_WIDTH
    steps = max(len(x_labels) - 1, 1)

    def point(index: int, value: float) -> tuple[float, float]:
        x = left + index / steps * plot_width
        y = TITLE_HEIGHT + PLOT_HEIGHT * (1 - min(max(value, 0.0), y_max) / (y_max or 1.0))
        return x, y

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" role="img" aria-label="{escape(title)}">',
        '<style>text{font:13px system-ui,-apple-system,"Segoe UI",sans-serif;fill:currentColor}'
        ".t{font-weight:600;font-size:14px}.v{font-size:11px;opacity:.75}"
        ".g{stroke:currentColor;opacity:.18}</style>",
        f'<text class="t" x="{MARGIN}" y="22">{escape(title)}</text>',
    ]
    for step in range(5):
        value = y_max * step / 4
        y = TITLE_HEIGHT + PLOT_HEIGHT * (1 - step / 4)
        parts.append(
            f'<line class="g" x1="{left}" y1="{y:.1f}" x2="{left + plot_width}" y2="{y:.1f}"/>'
        )
        parts.append(f'<text class="v" x="{MARGIN}" y="{y + 4:.1f}">{value:.2f}</text>')
    for index, label in enumerate(x_labels):
        x, _y = point(index, 0)
        parts.append(
            f'<text class="v" x="{x:.1f}" y="{TITLE_HEIGHT + PLOT_HEIGHT + 18:.1f}" '
            f'text-anchor="middle">{escape(label)}</text>'
        )
    for order, (name, values) in enumerate(series):
        color = SERIES_COLORS[order % len(SERIES_COLORS)]
        # A grid is a dozen or more rows and there are four colours, so the dash
        # pattern changes each time the colours wrap: sixteen series stay apart,
        # and a reader can follow one line without counting.
        dash = DASH_PATTERNS[(order // len(SERIES_COLORS)) % len(DASH_PATTERNS)]
        points = " ".join(
            f"{x:.1f},{y:.1f}" for x, y in (point(i, v) for i, v in enumerate(values))
        )
        parts.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"{dash}/>'
        )
        for x, y in (point(i, v) for i, v in enumerate(values)):
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{color}"/>')
        legend_y = TITLE_HEIGHT + 12 + order * 16
        parts.append(
            f'<line x1="{left + plot_width + 12}" y1="{legend_y - 4}" '
            f'x2="{left + plot_width + 22}" y2="{legend_y - 4}" stroke="{color}" '
            f'stroke-width="2"{dash}/>'
        )
        parts.append(
            f'<text class="v" x="{left + plot_width + 25}" y="{legend_y}">{escape(name)}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"
