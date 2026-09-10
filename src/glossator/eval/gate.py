"""Decide whether a refreshed snapshot may become the served index (D-045).

The refresh workflow evaluates the frozen question sets against the newest
snapshot. This module compares that run, question by question, with the run
recorded for the snapshot currently served, and says pass or regression. The
criterion is paired: for each signal, the questions that got worse are counted
against the questions that got better, and only a net loss beyond the noise of
a repeat run is a regression. Per-question churn of about one answer in ten is
what two runs of the same configuration produce on the same questions
(D-045), so a rule that fires on any single flipped question would fire on
every refresh.

Signals, all read from the run's records:

- ``retrieved``: a chunk of an accepted page reached the assembled context.
- ``cited``: a verified citation lands on an accepted page.
- ``refused``: the answer set ``insufficient_evidence`` (judged on the cells
  the labels call absent, and on unanswerable questions).
- ``correct``: the primary judge's verdict, when the run was judged.

The population is the questions labelled present in both snapshots, so a fact
the documentation removed is never counted as a regression of the pipeline;
those cells feed the changelog instead (D-041).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

PRESENT = {"present", "present_rephrased"}
ABSENT = {"absent"}
SCORE = {"correct": 1.0, "partial": 0.5, "wrong": 0.0}

DEFAULT_NET_LOSS_SHARE = 0.05
"""Net loss tolerated on each signal, as a share of the paired population."""

DEFAULT_NET_LOSS_FLOOR = 4
"""Net loss tolerated on a small population, whatever the share says. At sixty
questions and a flip rate of one in ten this is 1.6 standard deviations of the
repeat-run churn; the 5% share takes over above eighty questions."""

DEFAULT_MIN_PAIRED = 20
"""Below this many paired answerable questions the gate is inconclusive: a
verdict on a handful of questions is not a verdict."""

DEFAULT_MAX_UNSCORED_SHARE = 0.10
"""Above this share of candidate cells without an answer or a label, the gate
is inconclusive rather than passed: an outage is not evidence of no regression."""


def page(url: str) -> str:
    """A URL without its fragment, which is what a gold page is keyed on."""
    parts = urlsplit(url)
    return parts._replace(fragment="").geturl()


@dataclass(frozen=True, slots=True)
class Cell:
    """One (question, snapshot) answer, reduced to the gate's signals."""

    question_id: str
    dataset: str
    question_type: str
    label: str | None
    accepted_pages: frozenset[str]
    retrieved: bool
    cited: bool
    refused: bool
    verdict: str | None
    error: str | None

    @property
    def answerable(self) -> bool:
        return self.question_type != "unanswerable" and self.label in PRESENT

    @property
    def refusal_expected(self) -> bool:
        return self.question_type == "unanswerable" or self.label in ABSENT

    @property
    def scored(self) -> bool:
        return self.error is None and self.label is not None


def read_cells(
    records_path: Path, *, snapshot: str, labels_path: Path | None = None
) -> dict[str, Cell]:
    """The cells of one snapshot in a snapshot-evaluation run, keyed by question."""
    labels: dict[str, Mapping[str, Any]] = {}
    if labels_path is not None:
        for row in _jsonl(labels_path):
            if row.get("snapshot") == snapshot:
                labels[row["question_id"]] = row
    cells: dict[str, Cell] = {}
    for row in _jsonl(records_path):
        if row.get("snapshot") != snapshot:
            continue
        label_row = labels.get(row["question_id"], {})
        label = label_row.get("label") or row.get("availability_label")
        if label == "unknown":
            label = None
        accepted = {page(url) for url in row.get("gold_urls", [])}
        if label_row.get("page"):
            accepted.add(page(str(label_row["page"])))
        sources = ((row.get("trace") or {}).get("sources")) or []
        retrieved = any(page(source["citation_url"]) in accepted for source in sources)
        cited = any(page(citation["url"]) in accepted for citation in row.get("citations", []))
        verdict = ((row.get("judge") or {}).get("verdict") or {}).get("correctness")
        cells[row["question_id"]] = Cell(
            question_id=row["question_id"],
            dataset=str(row.get("dataset") or label_row.get("dataset") or ""),
            question_type=str(row.get("question_type") or ""),
            label=label,
            accepted_pages=frozenset(accepted),
            retrieved=retrieved,
            cited=cited,
            refused=bool(row.get("insufficient_evidence")),
            verdict=verdict if verdict in SCORE else None,
            error=row.get("error"),
        )
    return cells


@dataclass(slots=True)
class SignalResult:
    name: str
    population: int
    worse: list[dict[str, Any]] = field(default_factory=list)
    better: list[dict[str, Any]] = field(default_factory=list)
    threshold: int = 0
    baseline_mean: float | None = None
    candidate_mean: float | None = None

    @property
    def net_loss(self) -> int:
        return len(self.worse) - len(self.better)

    @property
    def regressed(self) -> bool:
        return self.net_loss > self.threshold

    def as_dict(self) -> dict[str, Any]:
        return {
            "signal": self.name,
            "population": self.population,
            "worse": self.worse,
            "better": self.better,
            "net_loss": self.net_loss,
            "threshold": self.threshold,
            "regressed": self.regressed,
            "baseline_mean": self.baseline_mean,
            "candidate_mean": self.candidate_mean,
        }


def threshold_for(population: int, *, share: float, floor: int) -> int:
    return max(floor, math.ceil(population * share))


def _compare_bool(
    name: str,
    pairs: Iterable[tuple[Cell, Cell]],
    *,
    value: Any,
    share: float,
    floor: int,
) -> SignalResult:
    pairs = list(pairs)
    result = SignalResult(name=name, population=len(pairs))
    result.threshold = threshold_for(len(pairs), share=share, floor=floor)
    before = []
    after = []
    for old, new in pairs:
        a, b = value(old), value(new)
        before.append(a)
        after.append(b)
        if a and not b:
            result.worse.append({"question_id": new.question_id, "before": a, "after": b})
        elif b and not a:
            result.better.append({"question_id": new.question_id, "before": a, "after": b})
    if pairs:
        result.baseline_mean = sum(before) / len(pairs)
        result.candidate_mean = sum(after) / len(pairs)
    return result


def _compare_verdict(
    pairs: Iterable[tuple[Cell, Cell]], *, share: float, floor: int
) -> SignalResult:
    pairs = [(old, new) for old, new in pairs if old.verdict and new.verdict]
    result = SignalResult(name="correct", population=len(pairs))
    result.threshold = threshold_for(len(pairs), share=share, floor=floor)
    before = []
    after = []
    for old, new in pairs:
        a, b = SCORE[old.verdict or "wrong"], SCORE[new.verdict or "wrong"]
        before.append(a)
        after.append(b)
        row = {"question_id": new.question_id, "before": old.verdict, "after": new.verdict}
        if b < a:
            result.worse.append(row)
        elif b > a:
            result.better.append(row)
    if pairs:
        result.baseline_mean = sum(before) / len(pairs)
        result.candidate_mean = sum(after) / len(pairs)
    return result


def compare(
    baseline: Mapping[str, Cell],
    candidate: Mapping[str, Cell],
    *,
    share: float = DEFAULT_NET_LOSS_SHARE,
    floor: int = DEFAULT_NET_LOSS_FLOOR,
    max_unscored_share: float = DEFAULT_MAX_UNSCORED_SHARE,
    min_paired: int = DEFAULT_MIN_PAIRED,
) -> dict[str, Any]:
    """The gate's verdict: ``pass``, ``regression`` or ``inconclusive``."""
    candidate_cells = list(candidate.values())
    # A question the baseline answered and the candidate did not, or one the
    # baseline judged and the candidate did not, is an outage on the candidate
    # side and counts as unscored; both sides unjudged is a deterministic-only
    # gate and counts as nothing.
    judged_baseline = any(cell.verdict for cell in baseline.values())
    unscored = {cell.question_id for cell in candidate_cells if not cell.scored}
    unscored |= {q for q in baseline if q not in candidate}
    if judged_baseline:
        unscored |= {
            q
            for q, cell in candidate.items()
            if q in baseline and baseline[q].verdict and not cell.verdict and cell.scored
        }
    denominator = len(set(candidate) | set(baseline))
    unscored_share = len(unscored) / denominator if denominator else 1.0

    common = sorted(baseline.keys() & candidate.keys())
    answerable = [
        (baseline[q], candidate[q])
        for q in common
        if baseline[q].answerable
        and candidate[q].answerable
        and baseline[q].scored
        and candidate[q].scored
    ]
    refusal = [
        (baseline[q], candidate[q])
        for q in common
        if baseline[q].refusal_expected
        and candidate[q].refusal_expected
        and baseline[q].scored
        and candidate[q].scored
    ]
    signals = [
        _compare_bool(
            "retrieved", answerable, value=lambda c: c.retrieved, share=share, floor=floor
        ),
        _compare_bool("cited", answerable, value=lambda c: c.cited, share=share, floor=floor),
        _compare_bool("refused", refusal, value=lambda c: c.refused, share=share, floor=floor),
        _compare_verdict(answerable, share=share, floor=floor),
    ]
    regressed = [s.name for s in signals if s.regressed]
    if unscored_share > max_unscored_share or len(answerable) < min_paired:
        verdict = "inconclusive"
    elif regressed:
        verdict = "regression"
    else:
        verdict = "pass"
    return {
        "verdict": verdict,
        "regressed_signals": regressed,
        "paired_answerable": len(answerable),
        "paired_refusal": len(refusal),
        "candidate_cells": len(candidate_cells),
        "candidate_unscored": len(unscored),
        "candidate_unscored_share": unscored_share,
        "max_unscored_share": max_unscored_share,
        "min_paired": min_paired,
        "net_loss_share": share,
        "net_loss_floor": floor,
        "signals": [s.as_dict() for s in signals],
        "dropped_from_population": sorted(
            (set(baseline) | set(candidate))
            - {new.question_id for _old, new in answerable}
            - {new.question_id for _old, new in refusal}
        ),
    }


def render(result: Mapping[str, Any], *, baseline_name: str, candidate_name: str) -> str:
    """The Markdown a reviewer or an issue reads."""
    lines = [
        f"# Refresh gate: {result['verdict']}",
        "",
        f"Candidate `{candidate_name}` against baseline `{baseline_name}`. "
        f"Paired on {result['paired_answerable']} answerable and {result['paired_refusal']} "
        f"refusal-expected questions present in both snapshots. A signal regresses when the "
        f"questions that got worse outnumber the questions that got better by more than "
        f"max({result['net_loss_floor']}, {result['net_loss_share']:.0%} of the population).",
        "",
        "| signal | population | worse | better | net loss | threshold "
        "| baseline | candidate | verdict |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in result["signals"]:
        b = "-" if s["baseline_mean"] is None else f"{s['baseline_mean']:.2f}"
        c = "-" if s["candidate_mean"] is None else f"{s['candidate_mean']:.2f}"
        lines.append(
            f"| {s['signal']} | {s['population']} | {len(s['worse'])} | {len(s['better'])} | "
            f"{s['net_loss']} | {s['threshold']} | {b} | {c} | "
            f"{'regression' if s['regressed'] else 'ok'} |"
        )
    if result["verdict"] == "inconclusive":
        lines += [
            "",
            f"Inconclusive: {result['candidate_unscored']} questions "
            f"({result['candidate_unscored_share']:.0%}) have no answer, label or verdict on the "
            f"candidate side (the gate accepts {result['max_unscored_share']:.0%}), and "
            f"{result['paired_answerable']} answerable questions were paired (the gate needs "
            f"{result['min_paired']}). Nothing was accepted.",
        ]
    for s in result["signals"]:
        if not s["worse"] and not s["better"]:
            continue
        lines += ["", f"## {s['signal']}", ""]
        if s["worse"]:
            lines += ["Worse:", ""]
            lines += [f"- `{r['question_id']}`: {r['before']} → {r['after']}" for r in s["worse"]]
        if s["better"]:
            lines += ["", "Better:", ""]
            lines += [f"- `{r['question_id']}`: {r['before']} → {r['after']}" for r in s["better"]]
    if result["dropped_from_population"]:
        lines += [
            "",
            "Not paired (absent from one run, unscored, or not present in both snapshots): "
            + ", ".join(f"`{q}`" for q in result["dropped_from_population"]),
        ]
    return "\n".join(lines) + "\n"


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="snapshot-eval run directory of the served snapshot",
    )
    parser.add_argument(
        "--baseline-snapshot", required=True, help="date of the served snapshot in that run"
    )
    parser.add_argument("--baseline-labels", type=Path, default=None)
    parser.add_argument(
        "--candidate",
        type=Path,
        required=True,
        help="snapshot-eval run directory of the refreshed snapshot",
    )
    parser.add_argument("--candidate-snapshot", required=True)
    parser.add_argument("--candidate-labels", type=Path, default=None)
    parser.add_argument(
        "--output", type=Path, required=True, help="directory for gate.json and gate.md"
    )
    parser.add_argument("--net-loss-share", type=float, default=DEFAULT_NET_LOSS_SHARE)
    parser.add_argument("--net-loss-floor", type=int, default=DEFAULT_NET_LOSS_FLOOR)
    parser.add_argument("--max-unscored-share", type=float, default=DEFAULT_MAX_UNSCORED_SHARE)
    parser.add_argument("--min-paired", type=int, default=DEFAULT_MIN_PAIRED)
    args = parser.parse_args(argv)

    baseline = read_cells(
        args.baseline / "records.jsonl",
        snapshot=args.baseline_snapshot,
        labels_path=args.baseline_labels,
    )
    candidate = read_cells(
        args.candidate / "records.jsonl",
        snapshot=args.candidate_snapshot,
        labels_path=args.candidate_labels,
    )
    result = compare(
        baseline,
        candidate,
        share=args.net_loss_share,
        floor=args.net_loss_floor,
        max_unscored_share=args.max_unscored_share,
        min_paired=args.min_paired,
    )
    result["baseline"] = {"run": str(args.baseline), "snapshot": args.baseline_snapshot}
    result["candidate"] = {"run": str(args.candidate), "snapshot": args.candidate_snapshot}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "gate.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    markdown = render(
        result,
        baseline_name=f"{args.baseline.name}@{args.baseline_snapshot}",
        candidate_name=f"{args.candidate.name}@{args.candidate_snapshot}",
    )
    (args.output / "gate.md").write_text(markdown)
    print(markdown)
    return {"pass": 0, "regression": 1, "inconclusive": 2}[result["verdict"]]


def run() -> int:
    """Exit 0 pass, 1 regression, 2 inconclusive, 3 the gate itself failed."""
    try:
        return main()
    except Exception as error:  # noqa: BLE001 - the exit code is the contract
        print(f"gate failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(run())
