import json
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
    PageAloneOutput,
    cross_page_pairs,
    generate_questions,
    sample_sections,
)
from glossator.eval.providers import Completion, TokenUsage
from glossator.eval.run_records import RunRecorder

FIXTURE_CORPUS = Path("tests/fixtures/corpus")


class StubProvider:
    def __init__(self) -> None:
        self.candidate_number = 0
        self.page_a_checks = 0

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
        elif response_schema is PageAloneOutput:
            page_a = "Page A alone" in prompt
            reject = page_a and self.page_a_checks == 0
            if page_a:
                self.page_a_checks += 1
            parsed = PageAloneOutput(
                fully_answerable=reject,
                reason=(
                    "Page A contains every required fact."
                    if reject
                    else "The other page supplies a required fact."
                ),
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
async def test_generation_returns_every_type_with_stub_provider(tmp_path: Path) -> None:
    pages = read_corpus(FIXTURE_CORPUS)
    run_dir = tmp_path / "run"
    recorder = RunRecorder(
        run_dir,
        {
            "model": "stub",
            "corpus": str(FIXTURE_CORPUS),
            "prompt_version": "test",
            "provider": "zai",
            "thinking": "disabled",
            "seed": 0,
            "corpus_commit": "fixture",
            "n": 6,
        },
    )
    questions, attempts = await generate_questions(
        StubProvider(),
        pages,
        n=6,
        model="stub",
        seed=0,
        recorder=recorder,
        run_dir=str(run_dir),
    )
    recorder.finalize(dataset_path=run_dir / "questions.jsonl", error=None)

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
    records = [
        json.loads(line)
        for line in (run_dir / "records.jsonl").read_text().splitlines()
    ]
    assert len(records) == len(attempts)
    cross_records = [
        record for record in records if record["generator_type"] == "cross_page"
    ]
    rejected_cross, cross_record = cross_records
    assert rejected_cross["page_a_alone"]["fully_answerable"] is True
    assert rejected_cross["page_b_alone"]["fully_answerable"] is False
    assert rejected_cross["kept"] is False
    assert "answerable from page A alone" in rejected_cross["drop_reasons"]
    assert cross_record["page_a_alone"]["fully_answerable"] is False
    assert cross_record["page_b_alone"]["fully_answerable"] is False
    assert cross_record["kept"] is True
    assert cross_record["sampled_sources"][0]["content"]
    assert json.loads((run_dir / "metrics.json").read_text())["kept"] == 6
