"""The generators: what they sample, what they keep, and what they record."""

import json
import random
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from glossator.eval.corpus import estimate_tokens, load_documents
from glossator.eval.datasets import QuestionType
from glossator.eval.generate import (
    CapabilityOutput,
    CorpusCheckOutput,
    CrossPageOutput,
    FilterOutput,
    PageAloneOutput,
    _allocations,
    cross_page_groups,
    foreign_vendors_named,
    generate_questions,
    normalize_question,
    plan_attempts,
    sample_sections,
)
from glossator.eval.providers import Completion, ProviderCallError, TokenUsage
from glossator.eval.run_records import RunRecorder

FIXTURE_CORPUS = Path("tests/fixtures/corpus")

RUN_CONFIG = {
    "model": "stub",
    "corpus": str(FIXTURE_CORPUS),
    "prompt_version": "test",
    "provider": "zai",
    "thinking": "disabled",
    "seed": 0,
    "corpus_commit": "fixture",
    "n": 6,
}


class StubProvider:
    """A provider that answers every schema with a valid, configurable object."""

    def __init__(
        self,
        *,
        filter_overrides: dict[str, bool] | None = None,
        page_a_answerable: bool = False,
        corpus_answers: bool = False,
        fully_answered: bool | None = None,
        question_text: str | None = None,
        fail_on: str | None = None,
    ) -> None:
        self.filter_overrides = filter_overrides or {}
        self.page_a_answerable = page_a_answerable
        self.corpus_answers = corpus_answers
        self.fully_answered = fully_answered
        self.question_text = question_text
        self.fail_on = fail_on
        self.candidate_number = 0
        self.prompts: list[str] = []

    async def complete(
        self,
        messages: Sequence[Any],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        response_schema: type[BaseModel] | None,
        thinking: Any,
        cache_nonce: str | None = None,
    ) -> Completion:
        del model, temperature, max_tokens, thinking, cache_nonce
        prompt = messages[-1]["content"]
        self.prompts.append(prompt)
        if self.fail_on and self.fail_on in prompt:
            raise ProviderCallError("stub failure")
        parsed: BaseModel | None
        if response_schema is FilterOutput:
            flags: dict[str, Any] = {
                "standalone": True,
                "gold_condition_met": True,
                "not_answerable_from_title_alone": True,
                "uses_every_gold_source": True,
                "about_the_documented_product": True,
            }
            flags.update(self.filter_overrides)
            parsed = FilterOutput(reasons=[], **flags)
        elif response_schema is PageAloneOutput:
            page_a = "Page A alone" in prompt
            parsed = PageAloneOutput(
                fully_answerable=page_a and self.page_a_answerable,
                reason="stub verdict",
            )
        elif response_schema is CorpusCheckOutput:
            parsed = CorpusCheckOutput(answered_by_corpus=self.corpus_answers, reason="stub")
        elif response_schema is None:
            return Completion(
                text="A closed-book guess.",
                parsed=None,
                usage=TokenUsage(),
                cached=False,
                model="stub",
                provider="zai",
            )
        else:
            self.candidate_number += 1
            unanswerable = "documentation does not answer" in prompt
            expected = not unanswerable if self.fully_answered is None else self.fully_answered
            question = (
                self.question_text
                or f"What behaviour applies to generated case {self.candidate_number}?"
            )
            fields: dict[str, Any] = {
                "question": question,
                "reference_answer": "One fact from the first source.\nAnother from the second.",
                "fully_answered": expected,
            }
            if response_schema is CrossPageOutput:
                fields["page_a_contribution"] = "the state model"
                fields["page_b_contribution"] = "the tool-call loop"
            if response_schema is CapabilityOutput:
                fields["names_single_model"] = False
            parsed = response_schema.model_validate(fields)
        return Completion(
            text=parsed.model_dump_json(),
            parsed=parsed,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5),
            cached=False,
            model="stub",
            provider="zai",
        )


@pytest.fixture
def documents() -> list[Any]:
    return load_documents(FIXTURE_CORPUS)


def recorder_for(tmp_path: Path) -> RunRecorder:
    return RunRecorder.start(tmp_path / "run", RUN_CONFIG)


# --------------------------------------------------------------------------- #
# Sampling
# --------------------------------------------------------------------------- #


def test_section_sampling_balances_top_level_site_groups(documents: list[Any]) -> None:
    sampled = sample_sections(documents, 12, random.Random(4))
    groups = Counter(document.top_level for document, _section in sampled)

    assert len(groups) > 1
    assert max(groups.values()) - min(groups.values()) <= 1


def test_section_sampling_draws_without_replacement(documents: list[Any]) -> None:
    sampled = sample_sections(documents, 1000, random.Random(0))
    keys = [(document.url, section.start_offset) for document, section in sampled]

    assert len(keys) == len(set(keys))


def test_short_and_level_one_sections_are_skipped(documents: list[Any]) -> None:
    sampled = sample_sections(documents, 1000, random.Random(0))

    assert sampled
    for _document, section in sampled:
        assert section.level > 1
        assert estimate_tokens(section.body) >= 80


def test_post_cutoff_sampling_is_restricted_to_the_post_cutoff_prefixes(
    documents: list[Any],
) -> None:
    assert sample_sections(documents, 5, random.Random(0), post_cutoff_only=True) == []


def test_cross_page_pairs_come_from_links_as_well_as_breadcrumbs(documents: list[Any]) -> None:
    groups = cross_page_groups(documents)
    pairs = [pair for group in groups.values() for pair in group]
    titles = {frozenset((left.title, right.title)) for left, right in pairs}

    assert any(name.startswith("links:") for name in groups)
    assert frozenset(("Quickstart", "Function calling")) in titles
    assert frozenset(("Quickstart", "Embeddings")) in titles


def test_api_reference_plans_sample_operations_with_an_anchor(documents: list[Any]) -> None:
    plans = plan_attempts(documents, QuestionType.API_REFERENCE, 4, random.Random(0))

    assert plans
    for plan in plans:
        assert plan.sources[0].anchor is not None
        assert plan.gold[0].anchor == plan.sources[0].anchor


def test_capability_plans_pair_the_matrix_with_a_model_card(documents: list[Any]) -> None:
    plans = plan_attempts(documents, QuestionType.CAPABILITY, 6, random.Random(0))
    urls = {source.url for plan in plans for source in plan.sources}

    assert plans
    assert "https://docs.mistral.ai/models/mistral-medium" in urls


def test_planning_is_deterministic_for_one_seed(documents: list[Any]) -> None:
    first = plan_attempts(documents, QuestionType.SINGLE_PAGE, 8, random.Random(0))
    second = plan_attempts(documents, QuestionType.SINGLE_PAGE, 8, random.Random(0))

    assert [plan.candidate_id for plan in first] == [plan.candidate_id for plan in second]
    assert first != plan_attempts(documents, QuestionType.SINGLE_PAGE, 8, random.Random(1))


def test_allocations_spread_a_remainder_over_the_types() -> None:
    allocations = _allocations(20)

    assert sum(allocations.values()) == 20
    assert max(allocations.values()) - min(allocations.values()) <= 1


def test_normalize_question_ignores_punctuation_and_case() -> None:
    assert normalize_question("Which models support Function Calling?") == normalize_question(
        "which models  support function calling"
    )


def test_foreign_vendor_names_are_found_and_ordinary_words_are_not() -> None:
    assert foreign_vendors_named("How does this compare to OpenAI's GPT models?") == [
        "OpenAI",
        "GPT",
    ]
    assert foreign_vendors_named("Which Mistral models support vision?") == []


# --------------------------------------------------------------------------- #
# Generation
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_generation_returns_every_type_it_can_fill(
    documents: list[Any], tmp_path: Path
) -> None:
    recorder = recorder_for(tmp_path)
    questions, attempts, results = await generate_questions(
        StubProvider(),
        documents,
        n=6,
        model="stub",
        seed=0,
        recorder=recorder,
    )
    recorder.finalize(
        dataset_path=None,
        error=None,
        shortfalls={result.question_type.value: result.shortfall for result in results},
        requested_by_type={result.question_type.value: result.requested for result in results},
    )

    kinds = Counter(question.type for question in questions)
    assert kinds[QuestionType.SINGLE_PAGE] == 1
    assert kinds[QuestionType.CROSS_PAGE] == 1
    assert kinds[QuestionType.API_REFERENCE] == 1
    assert kinds[QuestionType.CAPABILITY] == 1
    assert kinds[QuestionType.UNANSWERABLE] == 1
    records = [json.loads(line) for line in (recorder.records_path).read_text().splitlines()]
    assert len(records) == len(attempts)
    assert all(record["candidate_id"].startswith("cand-") for record in records)


@pytest.mark.asyncio
async def test_a_candidate_beyond_the_target_is_recorded_as_surplus(
    documents: list[Any], tmp_path: Path
) -> None:
    recorder = recorder_for(tmp_path)
    questions, attempts, _results = await generate_questions(
        StubProvider(), documents, n=6, model="stub", seed=0, recorder=recorder
    )
    surplus = [
        attempt
        for attempt in attempts
        if "surplus, the type was already filled" in attempt.drop_reasons
    ]

    # A wave overshoots on purpose; what it produced past the target is recorded
    # rather than counted as kept, so the record and the dataset agree.
    assert surplus
    assert len(questions) == sum(attempt.kept for attempt in attempts)


@pytest.mark.asyncio
async def test_a_type_the_corpus_cannot_fill_is_short_not_fatal(
    documents: list[Any], tmp_path: Path
) -> None:
    recorder = recorder_for(tmp_path)
    questions, _attempts, results = await generate_questions(
        StubProvider(), documents, n=6, model="stub", seed=0, recorder=recorder
    )

    post_cutoff = next(
        result for result in results if result.question_type == QuestionType.POST_CUTOFF
    )
    assert post_cutoff.accepted == 0
    assert post_cutoff.shortfall == 1
    assert questions


@pytest.mark.asyncio
async def test_the_reference_answer_carries_no_page_scaffolding(
    documents: list[Any], tmp_path: Path
) -> None:
    recorder = recorder_for(tmp_path)
    questions, _attempts, _results = await generate_questions(
        StubProvider(), documents, n=6, model="stub", seed=0, recorder=recorder
    )
    cross = next(question for question in questions if question.type == QuestionType.CROSS_PAGE)

    assert "Page A" not in cross.reference_answer
    assert cross.generator is not None
    contributions = cross.generator["contributions"]
    assert [item["contribution"] for item in contributions] == [
        "the state model",
        "the tool-call loop",
    ]


@pytest.mark.asyncio
async def test_the_french_page_produces_a_french_question(
    documents: list[Any], tmp_path: Path
) -> None:
    recorder = recorder_for(tmp_path)
    questions, _attempts, _results = await generate_questions(
        StubProvider(), documents, n=60, model="stub", seed=0, recorder=recorder
    )

    assert any(question.language == "fr" for question in questions)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("flag", "reason"),
    [
        ("standalone", "not standalone"),
        ("gold_condition_met", "gold condition failed"),
        ("not_answerable_from_title_alone", "answerable from title alone"),
        ("uses_every_gold_source", "does not require every gold source"),
        ("about_the_documented_product", "not about the documented product"),
    ],
)
async def test_each_filter_flag_produces_its_own_drop_reason(
    documents: list[Any], tmp_path: Path, flag: str, reason: str
) -> None:
    recorder = recorder_for(tmp_path)
    questions, attempts, _results = await generate_questions(
        StubProvider(filter_overrides={flag: False}),
        documents,
        n=6,
        model="stub",
        seed=0,
        recorder=recorder,
    )

    assert questions == []
    assert all(reason in attempt.drop_reasons for attempt in attempts)


@pytest.mark.asyncio
async def test_a_question_naming_another_vendor_is_dropped(
    documents: list[Any], tmp_path: Path
) -> None:
    recorder = recorder_for(tmp_path)
    questions, attempts, _results = await generate_questions(
        StubProvider(question_text="How does this differ from OpenAI's GPT function calling?"),
        documents,
        n=6,
        model="stub",
        seed=0,
        recorder=recorder,
    )

    assert questions == []
    assert attempts[0].foreign_vendors == ["OpenAI", "GPT"]
    assert "names another vendor's product" in attempts[0].drop_reasons


@pytest.mark.asyncio
async def test_a_repeated_question_is_dropped_as_a_duplicate(
    documents: list[Any], tmp_path: Path
) -> None:
    recorder = recorder_for(tmp_path)
    questions, attempts, _results = await generate_questions(
        StubProvider(question_text="Which models support function calling?"),
        documents,
        n=6,
        model="stub",
        seed=0,
        recorder=recorder,
    )

    assert len(questions) == 1
    assert sum(attempt.duplicate for attempt in attempts) == len(attempts) - 1
    assert "duplicate question" in attempts[1].drop_reasons


@pytest.mark.asyncio
async def test_a_fully_answered_mismatch_is_dropped(documents: list[Any], tmp_path: Path) -> None:
    recorder = recorder_for(tmp_path)
    questions, attempts, _results = await generate_questions(
        StubProvider(fully_answered=False),
        documents,
        n=6,
        model="stub",
        seed=0,
        recorder=recorder,
    )

    answerable = [
        attempt for attempt in attempts if attempt.generator_type != QuestionType.UNANSWERABLE
    ]
    assert all(
        "fully_answered conflicts with question type" in attempt.drop_reasons
        for attempt in answerable
    )
    assert all(question.type == QuestionType.UNANSWERABLE for question in questions)


@pytest.mark.asyncio
async def test_a_cross_page_question_one_page_answers_is_dropped(
    documents: list[Any], tmp_path: Path
) -> None:
    recorder = recorder_for(tmp_path)
    _questions, attempts, _results = await generate_questions(
        StubProvider(page_a_answerable=True),
        documents,
        n=6,
        model="stub",
        seed=0,
        recorder=recorder,
    )
    cross = [attempt for attempt in attempts if attempt.generator_type == "cross_page"]

    assert cross
    assert all("answerable from one page alone" in attempt.drop_reasons for attempt in cross)
    assert all(len(attempt.page_alone) == 2 for attempt in cross)


@pytest.mark.asyncio
async def test_an_unanswerable_question_the_corpus_answers_is_dropped(
    documents: list[Any], tmp_path: Path
) -> None:
    recorder = recorder_for(tmp_path)
    _questions, attempts, _results = await generate_questions(
        StubProvider(corpus_answers=True),
        documents,
        n=6,
        model="stub",
        seed=0,
        recorder=recorder,
    )
    unanswerable = [attempt for attempt in attempts if attempt.generator_type == "unanswerable"]

    assert unanswerable
    for attempt in unanswerable:
        assert "the corpus answers it after all" in attempt.drop_reasons
        assert attempt.consulted_sections


@pytest.mark.asyncio
async def test_an_unanswerable_candidate_records_the_sections_consulted(
    documents: list[Any], tmp_path: Path
) -> None:
    recorder = recorder_for(tmp_path)
    questions, _attempts, _results = await generate_questions(
        StubProvider(), documents, n=6, model="stub", seed=0, recorder=recorder
    )
    unanswerable = next(
        question for question in questions if question.type == QuestionType.UNANSWERABLE
    )

    assert unanswerable.gold == []
    assert unanswerable.generator is not None
    assert unanswerable.generator["sections_consulted"]


@pytest.mark.asyncio
async def test_a_provider_failure_drops_one_candidate_and_the_run_continues(
    documents: list[Any], tmp_path: Path
) -> None:
    recorder = recorder_for(tmp_path)
    questions, attempts, _results = await generate_questions(
        StubProvider(fail_on="Audit this generated evaluation question"),
        documents,
        n=6,
        model="stub",
        seed=0,
        recorder=recorder,
    )

    assert questions == []
    assert attempts
    assert all(attempt.drop_reasons == ["provider_error"] for attempt in attempts)
    assert all(attempt.error == "stub failure" for attempt in attempts)
    assert all(attempt.filter is None for attempt in attempts)
    # The row still validates against the one record model.
    rows = [json.loads(line) for line in recorder.records_path.read_text().splitlines()]
    assert rows and all(row["filter"] is None for row in rows)


@pytest.mark.asyncio
async def test_a_post_cutoff_candidate_records_a_closed_book_probe(tmp_path: Path) -> None:
    documents = load_documents(FIXTURE_CORPUS)
    # The fixture has no post-cutoff pages, so one is added for this check only.
    page = documents[0]
    object.__setattr__(page.page, "url", "https://docs.mistral.ai/vibe/overview")
    recorder = recorder_for(tmp_path)
    _questions, attempts, _results = await generate_questions(
        StubProvider(), documents, n=6, model="stub", seed=0, recorder=recorder
    )
    post_cutoff = [attempt for attempt in attempts if attempt.generator_type == "post_cutoff"]

    assert post_cutoff
    assert all(attempt.closed_book_answer == "A closed-book guess." for attempt in post_cutoff)
