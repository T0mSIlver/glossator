"""Rebuild a run's README and figures from its records.

D-023 asks for charts rendered by a script so they can be regenerated. The SVG is
written directly rather than through a plotting library: three bar charts do not
justify a dependency, and hand-written SVG has no fonts to find, no backend to
select, and nothing to download.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from glossator.eval.run_records import regenerate

# Figure geometry, in SVG user units.
_WIDTH = 720
_ROW_HEIGHT = 26
_BAR_HEIGHT = 16
_LABEL_WIDTH = 240
_MARGIN = 16
_TITLE_HEIGHT = 34
_PLOT_HEIGHT = 180
_LEGEND_WIDTH = 190

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


def bar_chart(
    title: str,
    rows: Sequence[tuple[str, Sequence[float]]],
    series_names: Sequence[str],
) -> str:
    """A horizontal bar chart, one group of bars per row."""
    series_count = max(len(series_names), 1)
    bar = max(4, _BAR_HEIGHT // series_count)
    height = _TITLE_HEIGHT + max(len(rows), 1) * _ROW_HEIGHT + _MARGIN + 20
    largest = max((value for _label, values in rows for value in values), default=0.0) or 1.0
    plot_width = _WIDTH - _LABEL_WIDTH - _MARGIN * 2 - 60

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_WIDTH} {height}" '
        f'width="{_WIDTH}" height="{height}" role="img" aria-label="{escape(title)}">',
        '<style>text{font:13px system-ui,-apple-system,"Segoe UI",sans-serif;fill:currentColor}'
        ".t{font-weight:600;font-size:14px}.v{font-size:12px;opacity:.75}</style>",
        f'<text class="t" x="{_MARGIN}" y="22">{escape(title)}</text>',
    ]
    for index, (label, values) in enumerate(rows):
        top = _TITLE_HEIGHT + index * _ROW_HEIGHT
        parts.append(
            f'<text x="{_LABEL_WIDTH}" y="{top + _ROW_HEIGHT / 2 + 4}" '
            f'text-anchor="end">{escape(label)}</text>'
        )
        offset = top + (_ROW_HEIGHT - bar * series_count) / 2
        for series, value in enumerate(values):
            width = max(0.0, value) / largest * plot_width
            color = SERIES_COLORS[series % len(SERIES_COLORS)]
            parts.append(
                f'<rect x="{_LABEL_WIDTH + 8}" y="{offset + series * bar:.1f}" '
                f'width="{width:.1f}" height="{bar - 1}" fill="{color}"/>'
            )
        total_label = " / ".join(f"{value:g}" for value in values)
        parts.append(
            f'<text class="v" x="{_LABEL_WIDTH + 12 + plot_width + 6}" '
            f'y="{top + _ROW_HEIGHT / 2 + 4}">{escape(total_label)}</text>'
        )
    if series_names:
        legend_y = height - 8
        x = _MARGIN
        for series, name in enumerate(series_names):
            color = SERIES_COLORS[series % len(SERIES_COLORS)]
            parts.append(
                f'<rect x="{x}" y="{legend_y - 9}" width="10" height="10" fill="{color}"/>'
            )
            parts.append(f'<text class="v" x="{x + 14}" y="{legend_y}">{escape(name)}</text>')
            x += 20 + 8 * len(name)
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_figures(metrics: Mapping[str, Any], figures_dir: Path) -> list[Path]:
    """Write the run's three charts. Returns the files written."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    candidates_by_type = dict(metrics.get("candidates_by_type") or {})
    kept_by_type = dict(metrics.get("kept_by_type") or {})
    accepted_rows = [
        (name, (float(kept_by_type.get(name, 0)), float(count - kept_by_type.get(name, 0))))
        for name, count in sorted(candidates_by_type.items())
    ]
    reasons = dict(metrics.get("dropped_by_reason") or {})
    reason_rows = [
        (name, (float(count),))
        for name, count in sorted(reasons.items(), key=lambda item: (-item[1], item[0]))
    ]
    usage_by_kind = dict(metrics.get("usage_by_kind") or {})
    token_rows = [
        (
            name,
            (float(usage["prompt_tokens"]), float(usage["completion_tokens"])),
        )
        for name, usage in sorted(usage_by_kind.items())
    ]

    written = []
    for name, title, rows, series in (
        (
            "accepted-by-type.svg",
            "Candidates accepted and dropped, by question type",
            accepted_rows,
            ("accepted", "dropped"),
        ),
        ("drop-reasons.svg", "Dropped candidates by reason", reason_rows, ("candidates",)),
        (
            "tokens-by-call-kind.svg",
            "Tokens by call kind",
            token_rows,
            ("prompt", "completion"),
        ),
    ):
        path = figures_dir / name
        path.write_text(bar_chart(title, rows, series))
        written.append(path)
    return written


def line_chart(
    title: str,
    x_labels: Sequence[str],
    series: Sequence[tuple[str, Sequence[float]]],
    *,
    y_max: float = 1.0,
) -> str:
    """A line per series over shared x positions, for a metric measured at several k."""
    height = _TITLE_HEIGHT + _PLOT_HEIGHT + 46
    left = _MARGIN + 34
    plot_width = _WIDTH - left - _MARGIN - _LEGEND_WIDTH
    steps = max(len(x_labels) - 1, 1)

    def point(index: int, value: float) -> tuple[float, float]:
        x = left + index / steps * plot_width
        y = _TITLE_HEIGHT + _PLOT_HEIGHT * (1 - min(max(value, 0.0), y_max) / (y_max or 1.0))
        return x, y

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_WIDTH} {height}" '
        f'width="{_WIDTH}" height="{height}" role="img" aria-label="{escape(title)}">',
        '<style>text{font:13px system-ui,-apple-system,"Segoe UI",sans-serif;fill:currentColor}'
        ".t{font-weight:600;font-size:14px}.v{font-size:11px;opacity:.75}"
        ".g{stroke:currentColor;opacity:.18}</style>",
        f'<text class="t" x="{_MARGIN}" y="22">{escape(title)}</text>',
    ]
    for step in range(5):
        value = y_max * step / 4
        y = _TITLE_HEIGHT + _PLOT_HEIGHT * (1 - step / 4)
        parts.append(
            f'<line class="g" x1="{left}" y1="{y:.1f}" x2="{left + plot_width}" y2="{y:.1f}"/>'
        )
        parts.append(f'<text class="v" x="{_MARGIN}" y="{y + 4:.1f}">{value:.2f}</text>')
    for index, label in enumerate(x_labels):
        x, _y = point(index, 0)
        parts.append(
            f'<text class="v" x="{x:.1f}" y="{_TITLE_HEIGHT + _PLOT_HEIGHT + 18:.1f}" '
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
        legend_y = _TITLE_HEIGHT + 12 + order * 16
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


def rebuild(run_dir: Path) -> dict[str, Any]:
    """Regenerate metrics.json, README.md and figures/ for one run directory.

    Runs of different kinds answer different questions and get different READMEs,
    so the run says which kind it is in its own ``config.json`` and this dispatches
    on that. A run written before the field existed is a dataset generation run.
    """
    kind = _kind(run_dir)
    if kind is not None:
        from glossator.eval.retrieval_report import rebuild_by_kind

        return rebuild_by_kind(kind, run_dir)
    metrics = regenerate(run_dir)
    render_figures(metrics, run_dir / "figures")
    return metrics


def _kind(run_dir: Path) -> str | None:
    config = json.loads((run_dir / "config.json").read_text())
    kind = config.get("kind")
    return str(kind) if kind else None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate a run's README and figures from its records"
    )
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    metrics = rebuild(args.run_dir)
    print(
        json.dumps(
            {
                "run_dir": str(args.run_dir),
                "kind": metrics.get("kind", "dataset-generation"),
                "figures": sorted(path.name for path in (args.run_dir / "figures").glob("*.svg")),
            }
        )
    )


if __name__ == "__main__":
    main()
