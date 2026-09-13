"""Noise kinds, drop reasons, the model's structured outputs, and the rows a run records."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from glossator.eval.datasets import EvalQuestion

TYPOS = "typos"
KEYWORDS = "keywords"
VAGUE = "vague"
WRONG_TERM = "wrong_term"
CHATTY = "chatty"

KINDS: tuple[str, ...] = (TYPOS, KEYWORDS, VAGUE, WRONG_TERM, CHATTY)
"""Drawn round-robin over the subset, so every kind covers the same spread of
question types and no kind lands on the easy half of the dataset."""

MODEL_KINDS = frozenset(KINDS) - {TYPOS}
"""Typos are generated in code. A model asked for a typo writes a plausible
misspelling, which is a different failure from a finger on the wrong key, and it
writes a different one every time the run is repeated."""

GENERATION_TEMPERATURE = 0.7
GENERATION_MAX_TOKENS = 400
CHECK_TEMPERATURE = 0.0
CHECK_MAX_TOKENS = 300

DROP_PROVIDER_ERROR = "provider_error"
DROP_UNPARSED = "the model's reply did not parse"
DROP_EMPTY = "the variant came back empty"
DROP_UNCHANGED = "the variant is the question it came from"
DROP_TOO_SHORT = "the question has too few letters to mistype"
DROP_DIFFERENT_QUESTION = "the variant asks something else"
DROP_ADDS_FACTS = "the variant adds a fact the question did not carry"
DROP_NO_SUBSTITUTION = "no term substitution was reported"

FIGURES = ("kept-by-kind.svg", "drop-reasons.svg")


class NoisyQuestion(BaseModel):
    model_config = ConfigDict(frozen=True)

    noisy_question: str


class WrongTermQuestion(NoisyQuestion):
    original_term: str
    replacement_term: str


class SameQuestion(BaseModel):
    model_config = ConfigDict(frozen=True)

    asks_the_same_thing: bool
    adds_facts: bool
    reason: str


class Substitution(BaseModel):
    """The term a `wrong_term` variant removed, and what took its place."""

    model_config = ConfigDict(frozen=True)

    removed: str
    inserted: str


class PerturbationRow(BaseModel):
    """One row of ``records.jsonl``: every variant, kept or not."""

    model_config = ConfigDict(frozen=True)

    candidate_id: str
    source_id: str
    noise: str
    generator_type: str
    """The noise kind again, under the name the shared summarizer groups rows by,
    so ``metrics.json`` counts kept and dropped per kind without a second pass."""

    original_question: str
    variant: str | None = None
    substitution: Substitution | None = None
    filter: SameQuestion | None = None
    kept: bool
    drop_reasons: list[str]
    question: EvalQuestion | None = None
