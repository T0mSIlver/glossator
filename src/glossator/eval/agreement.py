"""Reliability measures for ordinal answer-correctness labels."""

from __future__ import annotations

import itertools
import statistics
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

CorrectnessLabel = Literal["wrong", "partial", "correct"]
type ItemKey = tuple[str, str]

LABELS: tuple[CorrectnessLabel, ...] = ("wrong", "partial", "correct")
LABEL_SCORE: dict[CorrectnessLabel, float] = {
    "wrong": 0.0,
    "partial": 0.5,
    "correct": 1.0,
}


class HumanLabel(BaseModel):
    """One answer label exported by the annotation page."""

    model_config = ConfigDict(frozen=True)

    question_id: str
    strategy: str
    run: str
    label: CorrectnessLabel
    note: str = ""

    @property
    def key(self) -> ItemKey:
        return (self.question_id, self.strategy)


def read_human_labels(path: Path) -> list[HumanLabel]:
    """Read annotation JSONL, rejecting duplicate answer keys within a run."""
    rows = [
        HumanLabel.model_validate_json(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (row.run, *row.key)
        if key in seen:
            raise ValueError(f"duplicate human label for {key}")
        seen.add(key)
    return rows


def labels_for_run(
    labels: Sequence[HumanLabel], run_names: Sequence[str]
) -> dict[ItemKey, CorrectnessLabel]:
    """Select labels whose run field matches a run path, directory name, or configured name."""
    accepted = set(run_names)
    selected = [row for row in labels if row.run in accepted]
    return {row.key: row.label for row in selected}


def quadratic_weighted_kappa(
    first: Sequence[CorrectnessLabel], second: Sequence[CorrectnessLabel]
) -> float | None:
    """Quadratic-weighted Cohen's kappa over wrong, partial, and correct."""
    if len(first) != len(second):
        raise ValueError("the two raters must label the same number of items")
    if not first:
        return None
    observed = statistics.fmean(_squared_distance(a, b) for a, b in zip(first, second, strict=True))
    first_counts = Counter(first)
    second_counts = Counter(second)
    count = len(first)
    expected = sum(
        first_counts[a] * second_counts[b] * _squared_distance(a, b) for a in LABELS for b in LABELS
    ) / (count * count)
    if expected == 0:
        return 1.0 if observed == 0 else None
    return 1.0 - observed / expected


def percentage_agreement(
    first: Sequence[CorrectnessLabel], second: Sequence[CorrectnessLabel]
) -> float | None:
    """The fraction of items on which two raters chose the same label."""
    if len(first) != len(second):
        raise ValueError("the two raters must label the same number of items")
    if not first:
        return None
    return sum(a == b for a, b in zip(first, second, strict=True)) / len(first)


def krippendorff_alpha_ordinal(
    units: Sequence[Sequence[CorrectnessLabel | None]],
) -> float | None:
    """Krippendorff's alpha with ordinal distance and missing-rating support.

    Each inner sequence contains all available ratings for one item. The ordinal
    distance uses the observed category marginals, as defined by Krippendorff,
    rather than treating the three labels as interval measurements.
    """
    usable = [[label for label in unit if label is not None] for unit in units]
    usable = [unit for unit in usable if len(unit) >= 2]
    if not usable:
        return None
    marginals = Counter(label for unit in usable for label in unit)
    total = sum(marginals.values())
    if total < 2:
        return None

    observed_sum = 0.0
    observed_pairs = 0
    for unit in usable:
        for first, second in itertools.permutations(unit, 2):
            observed_sum += _ordinal_distance(first, second, marginals)
            observed_pairs += 1
    observed = observed_sum / observed_pairs

    expected_sum = sum(
        marginals[first]
        * (marginals[second] - int(first == second))
        * _ordinal_distance(first, second, marginals)
        for first in LABELS
        for second in LABELS
    )
    expected = expected_sum / (total * (total - 1))
    if expected == 0:
        return 1.0 if observed == 0 else None
    return 1.0 - observed / expected


def confusion_matrix(
    human: Sequence[CorrectnessLabel], judge: Sequence[CorrectnessLabel]
) -> dict[str, dict[str, int]]:
    """Counts with human labels as rows and judge labels as columns."""
    if len(human) != len(judge):
        raise ValueError("human and judge must label the same number of items")
    matrix: dict[str, dict[str, int]] = {
        actual: {predicted: 0 for predicted in LABELS} for actual in LABELS
    }
    for actual, predicted in zip(human, judge, strict=True):
        matrix[actual][predicted] += 1
    return matrix


def agreement_report(
    judges: Mapping[str, Mapping[Any, CorrectnessLabel]],
    human: Mapping[Any, CorrectnessLabel] | None = None,
) -> dict[str, Any]:
    """Compute pairwise, multi-rater, and optional human agreement metrics."""
    pairwise: list[dict[str, Any]] = []
    for first_name, second_name in itertools.combinations(judges, 2):
        first, second = _aligned(judges[first_name], judges[second_name])
        pairwise.append(
            {
                "first": first_name,
                "second": second_name,
                "items": len(first),
                "quadratic_weighted_kappa": quadratic_weighted_kappa(first, second),
                "percentage_agreement": percentage_agreement(first, second),
            }
        )

    all_keys = sorted(set().union(*(ratings.keys() for ratings in judges.values())), key=str)
    judge_units = [[ratings.get(key) for ratings in judges.values()] for key in all_keys]
    report: dict[str, Any] = {
        "pairwise": pairwise,
        "krippendorff_alpha_ordinal": krippendorff_alpha_ordinal(judge_units),
        "percentage_agreement": _multi_rater_percentage(judge_units),
        "per_judge": {
            name: {
                "items": len(ratings),
                "mean_correctness": (
                    statistics.fmean(LABEL_SCORE[label] for label in ratings.values())
                    if ratings
                    else None
                ),
            }
            for name, ratings in judges.items()
        },
    }
    if human is None:
        return report

    human_pairs: list[dict[str, Any]] = []
    per_judge = report["per_judge"]
    for name, ratings in judges.items():
        judge_values, human_values = _aligned(ratings, human)
        human_pairs.append(
            {
                "judge": name,
                "items": len(judge_values),
                "quadratic_weighted_kappa": quadratic_weighted_kappa(judge_values, human_values),
                "percentage_agreement": percentage_agreement(judge_values, human_values),
            }
        )
        per_judge[name]["human_items"] = len(judge_values)
        per_judge[name]["confusion_matrix_human_rows"] = confusion_matrix(
            human_values, judge_values
        )

    human_keys = sorted(set(all_keys) | set(human), key=str)
    human_units = [
        [*(ratings.get(key) for ratings in judges.values()), human.get(key)] for key in human_keys
    ]
    report["human"] = {
        "items": len(human),
        "pairwise": human_pairs,
        "krippendorff_alpha_ordinal": krippendorff_alpha_ordinal(human_units),
        "percentage_agreement": _multi_rater_percentage(human_units),
    }
    return report


def _aligned(
    first: Mapping[Any, CorrectnessLabel], second: Mapping[Any, CorrectnessLabel]
) -> tuple[list[CorrectnessLabel], list[CorrectnessLabel]]:
    keys = sorted(first.keys() & second.keys(), key=str)
    return [first[key] for key in keys], [second[key] for key in keys]


def _squared_distance(first: CorrectnessLabel, second: CorrectnessLabel) -> float:
    return (LABEL_SCORE[first] - LABEL_SCORE[second]) ** 2


def _ordinal_distance(
    first: CorrectnessLabel,
    second: CorrectnessLabel,
    marginals: Mapping[CorrectnessLabel, int],
) -> float:
    if first == second:
        return 0.0
    low, high = sorted((LABELS.index(first), LABELS.index(second)))
    between = float(sum(marginals[LABELS[index]] for index in range(low, high + 1)))
    between -= (marginals[first] + marginals[second]) / 2
    return between * between


def _multi_rater_percentage(
    units: Sequence[Sequence[CorrectnessLabel | None]],
) -> float | None:
    agreements = 0
    comparisons = 0
    for unit in units:
        present = [label for label in unit if label is not None]
        for first, second in itertools.combinations(present, 2):
            agreements += first == second
            comparisons += 1
    return agreements / comparisons if comparisons else None


__all__ = [
    "CorrectnessLabel",
    "HumanLabel",
    "ItemKey",
    "agreement_report",
    "confusion_matrix",
    "krippendorff_alpha_ordinal",
    "labels_for_run",
    "percentage_agreement",
    "quadratic_weighted_kappa",
    "read_human_labels",
]
