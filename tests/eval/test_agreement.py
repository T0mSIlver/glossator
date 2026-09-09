"""Hand-checkable tests for judge agreement statistics."""

from pathlib import Path

import pytest

from glossator.eval.agreement import (
    CorrectnessLabel,
    agreement_report,
    krippendorff_alpha_ordinal,
    percentage_agreement,
    quadratic_weighted_kappa,
    read_human_labels,
)


def test_quadratic_weighted_kappa_matches_a_hand_calculation() -> None:
    first: list[CorrectnessLabel] = ["correct", "partial", "wrong"]
    second: list[CorrectnessLabel] = ["correct", "wrong", "wrong"]

    # Observed weighted disagreement is 1/12. The disagreement expected from
    # the two marginals is 5/12, so kappa is 1 - (1/12)/(5/12) = 0.8.
    assert quadratic_weighted_kappa(first, second) == pytest.approx(0.8)
    assert percentage_agreement(first, second) == pytest.approx(2 / 3)


def test_kappa_and_alpha_are_one_for_identical_constant_labels() -> None:
    labels: list[CorrectnessLabel] = ["correct", "correct", "correct"]
    assert quadratic_weighted_kappa(labels, labels) == 1.0
    assert krippendorff_alpha_ordinal([[label, label] for label in labels]) == 1.0


def test_ordinal_alpha_accepts_missing_ratings() -> None:
    complete = krippendorff_alpha_ordinal(
        [["wrong", "wrong", "wrong"], ["partial", "partial", None], ["correct", "correct"]]
    )
    assert complete == 1.0


def test_report_aligns_each_pair_on_the_items_both_judges_labeled() -> None:
    report = agreement_report(
        {
            "zai:a": {"q1": "correct", "q2": "partial"},
            "zai:b": {"q1": "correct", "q3": "wrong"},
        }
    )
    pair = report["pairwise"][0]
    assert pair["items"] == 1
    assert pair["percentage_agreement"] == 1.0


def test_human_comparison_includes_mean_and_confusion_matrix() -> None:
    report = agreement_report(
        {"zai:a": {"q1": "correct", "q2": "wrong"}},
        {"q1": "correct", "q2": "partial"},
    )
    judge = report["per_judge"]["zai:a"]
    assert judge["mean_correctness"] == 0.5
    assert judge["confusion_matrix_human_rows"]["partial"]["wrong"] == 1
    assert report["human"]["pairwise"][0]["items"] == 2


def test_the_annotation_fixture_parses() -> None:
    labels = read_human_labels(Path("tests/fixtures/answer-labels.jsonl"))
    assert [(label.question_id, label.strategy, label.label) for label in labels] == [
        ("q1", "single_pass", "correct"),
        ("q1", "search_loop", "partial"),
        ("q2", "single_pass", "wrong"),
    ]
