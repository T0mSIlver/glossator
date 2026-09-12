"""The evaluation set: what a question is, how it is stored, how it is checked.

A dataset row is only useful if its gold sources still exist in the corpus, so
validation against the manifest and the pages is part of this module rather than
of whatever wrote the row.
"""

from __future__ import annotations

import hashlib
import random
from collections.abc import Iterable, Mapping, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from glossator.ingest.pages import CorpusPage
from glossator.ingest.sections import parse_sections


class QuestionType(StrEnum):
    SINGLE_PAGE = "single_page"
    CROSS_PAGE = "cross_page"
    API_REFERENCE = "api_reference"
    CAPABILITY = "capability"
    POST_CUTOFF = "post_cutoff"
    UNANSWERABLE = "unanswerable"
    HISTORY = "history"
    """Answered only from the dated snapshots: when a section was added, changed or
    moved. The gold carries the interval between two stored dates."""


class QuestionSource(StrEnum):
    GENERATED = "generated"
    GITHUB_ISSUE = "github_issue"
    HANDWRITTEN = "handwritten"
    TRANSCRIPT = "transcript"
    """Mined from a coding-agent session that stumbled while using a Mistral product."""
    STACK_OVERFLOW = "stack_overflow"
    """Mined from a Stack Overflow question about a Mistral product."""
    HACKER_NEWS = "hacker_news"
    """Mined from a Hacker News comment or thread asking about Mistral's platform."""


class GoldSource(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    anchor: str | None = None
    between: tuple[str, str] | None = None
    """For a history question: the two adjacent stored dates the change lies
    between. The snapshots are a fortnight apart, so no answer names a day."""


class EvalQuestion(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    question: str
    type: QuestionType
    gold: list[GoldSource]
    reference_answer: str
    language: Literal["en", "fr"]
    source: QuestionSource
    generator: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_gold_and_answer_length(self) -> EvalQuestion:
        if self.type == QuestionType.UNANSWERABLE and self.gold:
            raise ValueError("unanswerable questions must have no gold sources")
        if self.type != QuestionType.UNANSWERABLE and not self.gold:
            raise ValueError("answerable questions need at least one gold source")
        if len(self.reference_answer.splitlines()) > 2:
            raise ValueError("reference_answer must contain at most two lines")
        return self


class CorpusValidationIssue(BaseModel):
    model_config = ConfigDict(frozen=True)

    question_id: str
    url: str
    anchor: str | None
    message: str


def read_jsonl(path: Path) -> list[EvalQuestion]:
    questions: list[EvalQuestion] = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            questions.append(EvalQuestion.model_validate_json(line))
        except ValueError as error:
            raise ValueError(f"invalid question at {path}:{line_number}") from error
    return questions


def write_jsonl(path: Path, questions: Iterable[EvalQuestion]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [question.model_dump_json() for question in questions]
    path.write_text("".join(row + "\n" for row in rows))


def dataset_hash(path: Path) -> str:
    """sha256 of the dataset file, so a run names the exact rows it read."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stratified_subset(
    questions: Sequence[EvalQuestion], n: int, seed: int = 0
) -> list[EvalQuestion]:
    """``n`` questions that keep every type in the input represented.

    Types are drawn round-robin from independently shuffled pools, rarest type
    first, so a subset smaller than the number of types still covers as many as
    it has room for and a prefix of the result is itself stratified -- which is
    what makes ``--limit`` on a run a sample rather than "whatever the file
    happens to start with". The shuffle is seeded, so the same seed and the same
    dataset always give the same subset.
    """
    if n <= 0:
        return []
    pools: dict[str, list[EvalQuestion]] = {}
    for question in questions:
        pools.setdefault(question.type.value, []).append(question)
    rng = random.Random(seed)
    for pool in pools.values():
        rng.shuffle(pool)
    # Rarest first: a type with two rows loses its only chance of appearing if a
    # type with fifty is served first. Ties are broken by the seed rather than by
    # name, because alphabetical tie-breaking would make every small subset in
    # the project's history start with `api_reference`.
    order = sorted(pools)
    rng.shuffle(order)
    order.sort(key=lambda name: len(pools[name]))
    chosen: list[EvalQuestion] = []
    while len(chosen) < n and any(pools[name] for name in order):
        for name in order:
            if len(chosen) == n:
                break
            if pools[name]:
                chosen.append(pools[name].pop())
    return chosen


def validate_against_corpus(
    questions: Sequence[EvalQuestion],
    manifest: Sequence[Mapping[str, Any]],
    pages: Sequence[CorpusPage],
) -> list[CorpusValidationIssue]:
    """Gold sources that no longer name a page, or an anchor the page lacks.

    Anchors come from the section parser rather than a private scan, so a
    question is checked against the same section boundaries ingestion indexes.
    """
    manifest_urls = {str(entry.get("url", "")) for entry in manifest}
    anchors_by_url = {
        page.url: {
            section.anchor
            for section in parse_sections(page.body, page_title=page.title)
            if section.anchor is not None
        }
        for page in pages
    }
    issues: list[CorpusValidationIssue] = []
    for question in questions:
        for gold in question.gold:
            if gold.url not in manifest_urls:
                issues.append(
                    CorpusValidationIssue(
                        question_id=question.id,
                        url=gold.url,
                        anchor=gold.anchor,
                        message="gold URL is missing from the manifest",
                    )
                )
                continue
            if gold.anchor is not None and gold.anchor not in anchors_by_url.get(gold.url, set()):
                issues.append(
                    CorpusValidationIssue(
                        question_id=question.id,
                        url=gold.url,
                        anchor=gold.anchor,
                        message="gold anchor is missing from the page",
                    )
                )
    return issues
