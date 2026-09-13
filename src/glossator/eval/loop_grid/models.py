"""The grid's axes, the shipped point they vary around, its rows and its table columns."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

FULL_PREVIEWS = "full"
"""The preview axis's third value: no cut at all, spelled ``tool_result_chars=null``
in the run's configuration rather than a number that must track the longest
chunk (D-035c)."""

SHIPPED_POINT: dict[str, int | None] = {
    "round_cap": 4,
    "searches_per_round": 4,
    "tool_result_chars": 600,
}

AXIS_VALUES: tuple[tuple[str, tuple[tuple[str, int | None], ...]], ...] = (
    ("round_cap", (("4", 4), ("6", 6), ("8", 8))),
    ("searches_per_round", (("4", 4), ("6", 6))),
    ("tool_result_chars", (("600", 600), ("1500", 1500), (FULL_PREVIEWS, None))),
)


@dataclass(frozen=True)
class GridConfiguration:
    """One row of the grid: an axis value, or the shipped point itself."""

    axis: str | None
    """``None`` for the shipped point, which is the row every axis is compared to."""

    label: str
    overrides: dict[str, Any]

    @property
    def name(self) -> str:
        """The run-name suffix, in the dashed form run directories use."""
        return "shipped" if self.axis is None else f"{self.axis.replace('_', '-')}-{self.label}"


def configurations() -> list[GridConfiguration]:
    """Every listed axis value, with repeats of the shipped point collapsed.

    Each axis's shipped value appears in ``AXIS_VALUES`` so the axis stays
    readable; here those rows fold into the one shipped-point run, because a
    round_cap=4 row and the shipped point are the same experiment.
    """
    rows = [GridConfiguration(axis=None, label="shipped", overrides=dict(SHIPPED_POINT))]
    seen = {tuple(sorted(SHIPPED_POINT.items()))}
    for axis, values in AXIS_VALUES:
        for label, value in values:
            overrides = dict(SHIPPED_POINT)
            overrides[axis] = value
            key = tuple(sorted(overrides.items()))
            if key in seen:
                continue
            seen.add(key)
            rows.append(GridConfiguration(axis=axis, label=label, overrides=overrides))
    return rows


TABLE_COLUMNS: tuple[tuple[str, str, str], ...] = (
    ("correctness", "correctness (judge)", "pct"),
    ("groundedness", "groundedness (judge)", "pct"),
    ("cited_url_match", "cited URL matches gold", "pct"),
    ("citation_verification_rate", "quotes verified", "pct"),
    ("rounds", "rounds used", "num"),
    ("round_cap_hit", "round cap hit", "pct"),
    ("tool_calls", "tool calls", "num"),
    ("tokens_in", "prompt tokens per answer", "num"),
    ("latency_p50_s", "median seconds per answer", "sec"),
)
