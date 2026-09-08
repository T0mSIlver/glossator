"""The evaluation set: what a question is, how it is stored, how it is checked.

A dataset row is only useful if its gold sources still exist in the corpus, so
validation against the manifest and the pages is part of this module rather than
of whatever wrote the row.
"""

from __future__ import annotations

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


class QuestionSource(StrEnum):
    GENERATED = "generated"
    GITHUB_ISSUE = "github_issue"
    HANDWRITTEN = "handwritten"


class GoldSource(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    anchor: str | None = None


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
