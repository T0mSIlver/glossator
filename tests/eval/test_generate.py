import random
from collections import Counter
from pathlib import Path

import pytest
from pydantic import BaseModel

from glossator.eval.corpus_reader import read_corpus
from glossator.eval.datasets import QuestionType
from glossator.eval.generate import (
    CandidateOutput,
    FilterOutput,
    cross_page_pairs,
    generate_questions,
    sample_sections,
)
from glossator.eval.providers import Completion, TokenUsage

FIXTURE_CORPUS = Path("tests/fixtures/corpus")


class StubProvider:
    def __init__(self) -> None:
        self.candidate_number = 0

    async def complete(
        self,
        messages,
        *,
        model,
        temperature,
        max_tokens,
        response_schema,
        thinking,
    ) -> Completion:
        del model, temperature, max_tokens, thinking
        prompt = messages[-1]["content"]
        if response_schema is FilterOutput:
            parsed: BaseModel = FilterOutput(
                standalone=True,
                gold_condition_met=True,
                not_answerable_from_title_alone=True,
                uses_every_gold_source=True,
                reasons=[],
            )
        else:
            self.candidate_number += 1
            unanswerable = "documentation does not answer" in prompt
            parsed = CandidateOutput(
                question=f"What behavior applies to generated case {self.candidate_number}?",
                reference_answer="First source contributes one fact.\nSecond source contributes another.",
                fully_answered=not unanswerable,
            )
        return Completion(
            text=parsed.model_dump_json(),
            parsed=parsed,
            usage=TokenUsage(),
            cached=False,
            model="stub",
            provider="zai",
        )


def test_section_sampling_balances_top_level_site_groups() -> None:
    pages = read_corpus(FIXTURE_CORPUS)
    sections = sample_sections(pages, 6000, random.Random(4))
    groups = Counter(section.url.split("/")[3] for section in sections)

    assert set(groups) == {"api", "models", "studio"}
    assert max(groups.values()) / min(groups.values()) < 1.15


def test_cross_page_pairs_use_breadcrumbs_or_links() -> None:
    pages = read_corpus(FIXTURE_CORPUS)
    pairs = cross_page_pairs(pages)
    titles = [{left.title, right.title} for left, right in pairs]

    assert {"Conversations API", "Function calling"} in titles


@pytest.mark.asyncio
async def test_generation_returns_every_type_with_stub_provider() -> None:
    pages = read_corpus(FIXTURE_CORPUS)
    questions, attempts = await generate_questions(
        StubProvider(), pages, n=6, model="stub", seed=0
    )

    assert len(questions) == 6
    assert Counter(question.type for question in questions) == {
        QuestionType.SINGLE_PAGE: 1,
        QuestionType.CROSS_PAGE: 1,
        QuestionType.API_REFERENCE: 1,
        QuestionType.CAPABILITY: 1,
        QuestionType.UNANSWERABLE: 1,
        QuestionType.POST_CUTOFF: 1,
    }
    assert all(question.generator is not None for question in questions)
    assert attempts
