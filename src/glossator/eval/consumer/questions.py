"""The fixed question set and the prompt built from each question."""

from __future__ import annotations

from pathlib import Path

from glossator.eval.consumer.prompts import PROMPT_LEAD
from glossator.eval.datasets import EvalQuestion, read_jsonl, stratified_subset

MINED_DATASET = Path("eval/mined.jsonl")
FRESH_DATASET = Path("eval/dev-fresh60.jsonl")

MINED_COUNT = 40
FRESH_COUNT = 20


def build_question_set(
    mined_count: int = MINED_COUNT,
    fresh_count: int = FRESH_COUNT,
    mined_path: Path = MINED_DATASET,
    fresh_path: Path = FRESH_DATASET,
) -> list[EvalQuestion]:
    """The fixed question set: ``mined_count`` stratified from mined (seed 0)
    and ``fresh_count`` from the fresh slice (seed 0). Same rows every run, and
    a smaller count is a prefix of a larger one, so a consumer run on thirty
    questions is comparable with one on sixty.

    The full forty keeps all nine mined unanswerables; a smaller draw keeps as
    many as round-robin stratification gives it, and the run's config records
    how many it got."""
    mined = stratified_subset(read_jsonl(mined_path), mined_count, seed=0)
    fresh = stratified_subset(read_jsonl(fresh_path), fresh_count, seed=0)
    unanswerable = [q for q in mined if q.type.value == "unanswerable"]
    if mined_count >= MINED_COUNT and len(unanswerable) != 9:
        raise ValueError(f"expected all 9 mined unanswerables in the 40, found {len(unanswerable)}")
    return mined + fresh


def prompt_for(question: EvalQuestion) -> str:
    return f"{PROMPT_LEAD}\n\n{question.question}"
