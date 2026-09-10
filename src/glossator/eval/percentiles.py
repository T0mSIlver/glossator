"""Percentile conventions shared by evaluation reports."""

import math
from collections.abc import Sequence


def nearest_rank_percentile(values: Sequence[float], fraction: float) -> float | None:
    """Return the smallest observed value at or above the requested fraction."""
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def rounded_index_percentile(sorted_values: Sequence[float], fraction: float) -> float:
    """Select the nearest indexed value from an already sorted sequence."""
    if not sorted_values:
        return 0.0
    index = min(
        len(sorted_values) - 1,
        max(0, round(fraction * (len(sorted_values) - 1))),
    )
    return sorted_values[index]
