"""The answer eval's arithmetic, its judge, its checkpoint and its report.

Every test here builds its answers by hand: the point is that a number in a run
README can be derived on paper from the records under it, without a model, an
index or a network.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from glossator.answer.citations import (
    VERIFIED_AFTER_EMPHASIS,
    Citation,
    RejectionReason,
    Trace,
    TracedSource,
    TraceEvent,
)
from glossator.answer.llm import TokenUsage
from glossator.eval.answer_eval import (
    JUDGE_VERSION,
    CitationVerdict,
    JudgeRecord,
    JudgeVerdict,
    QuestionRecord,
    RunDirectory,
    aggregate,
    cell,
    judge_input,
    parse_judge_models,
    question_metrics,
    regenerate,
    rejudge,
    render_readme,
    resolve_run_directory,
    source_texts,
)
from glossator.eval.datasets import (
    EvalQuestion,
    GoldSource,
    QuestionSource,
    QuestionType,
    stratified_subset,
)
from glossator.eval.providers import TokenUsage as ProviderTokenUsage
from glossator.eval.providers import extract_json_object
from glossator.eval.report import rebuild, run_kind

PAGE = "https://docs.mistral.ai/capabilities/function-calling"
OTHER = "https://docs.mistral.ai/getting-started/quickstart"

CONFIG: dict[str, Any] = {
    "kind": "answer_eval",
    "model": "ministral-14b-2512",
    "judge_model": "glm-5.3",
    "variant": "sec128",
    "dataset": "tests/fixtures/answer-questions.jsonl",
    "dataset_sha256": "0" * 64,
    "strategies": ["single_pass", "outline"],
    "top_k": 8,
    "context_token_budget": 6000,
    "run_dir": "eval/runs/test",
}


def trace(*sources: tuple[int, str, str], tool_events: int = 0, rounds: int = 1) -> Trace:
    """A trace whose context text is rendered the way the answer layer renders it."""
    return Trace(
        strategy="single_pass",
        variant="sec128",
        prompt_version="grounded-answer/v1",
        rounds=rounds,
        events=[
            TraceEvent(step=index + 1, kind="tool", name="search", round=1)
            for index in range(tool_events)
        ],
        sources=[
            TracedSource(
                n=n,
                citation_url=url,
                heading_path=["Function calling"],
                chunk_ids=[],
                tokens=len(text.split()),
            )
            for n, url, text in sources
        ],
        context_text="\n\n".join(
            f"[{n}] {url}\nFunction calling\n{text}" for n, url, text in sources
        ),
    )


def citation(
    n: int, url: str, *, anchor: str | None = None, quote: str = "a quoted span"
) -> Citation:
    return Citation(n=n, url=url, anchor=anchor, quote=quote, verified=True)


def rejected(n: int, reason: str) -> Citation:
    return Citation(n=n, url=PAGE, quote="x", verified=False, reason=reason)


def record(
    *,
    question_id: str = "q1",
    question: str = "How do I define a tool?",
    question_type: str = "single_page",
    strategy: str = "single_pass",
    gold_urls: list[str] | None = None,
    gold_anchors: list[str | None] | None = None,
    citations: list[Citation] | None = None,
    unverified: list[Citation] | None = None,
    insufficient: bool = False,
    latency_ms: float = 1000.0,
    prompt_tokens: int = 1000,
    completion_tokens: int = 100,
    cost_usd: float = 0.0,
    judge: JudgeRecord | None = None,
    trace_value: Trace | None = None,
) -> QuestionRecord:
    return QuestionRecord(
        question_id=question_id,
        question=question,
        question_type=question_type,
        language="en",
        gold_urls=[PAGE] if gold_urls is None else gold_urls,
        gold_anchors=[None] if gold_anchors is None else gold_anchors,
        reference_answer="Describe it as JSON Schema.",
        strategy=strategy,
        variant="sec128",
        model="ministral-14b-2512",
        answer_markdown="Describe the function as JSON Schema [1].",
        citations=citations if citations is not None else [citation(1, PAGE)],
        unverified_citations=unverified or [],
        insufficient_evidence=insufficient,
        trace=trace_value if trace_value is not None else trace((1, PAGE, "body")),
        usage=TokenUsage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens),
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        judge=judge,
    )


def verdict(
    correctness: str = "correct",
    *,
    total: int = 4,
    supported: int = 3,
    citations: list[CitationVerdict] | None = None,
) -> JudgeRecord:
    return JudgeRecord(
        model="glm-5.3",
        prompt_version=JUDGE_VERSION,
        input_text="rendered",
        raw_output="{}",
        verdict=JudgeVerdict.model_validate(
            {
                "correctness": correctness,
                "correctness_reason": "because",
                "claims_total": total,
                "claims_supported": supported,
                "citations": [c.model_dump() for c in (citations or [])],
            }
        ),
    )


# --------------------------------------------------------------------------- #
# Deterministic metrics
# --------------------------------------------------------------------------- #


def test_a_citation_to_a_gold_page_matches_on_url_and_on_anchor() -> None:
    metrics = question_metrics(
        record(
            gold_urls=[PAGE],
            gold_anchors=["defining-tools"],
            citations=[citation(1, PAGE, anchor="defining-tools")],
        )
    )
    assert metrics["cited_url_match"] == 1.0
    assert metrics["cited_anchor_match"] == 1.0


def test_the_right_page_at_the_wrong_section_matches_the_url_only() -> None:
    metrics = question_metrics(
        record(
            gold_urls=[PAGE],
            gold_anchors=["defining-tools"],
            citations=[citation(1, PAGE, anchor="limits")],
        )
    )
    assert metrics["cited_url_match"] == 1.0
    assert metrics["cited_anchor_match"] == 0.0


def test_a_gold_source_without_an_anchor_is_matched_by_any_citation_to_that_page() -> None:
    metrics = question_metrics(
        record(gold_anchors=[None], citations=[citation(1, PAGE, anchor="limits")])
    )
    assert metrics["cited_anchor_match"] == 1.0


def test_a_citation_to_another_page_matches_nothing() -> None:
    metrics = question_metrics(record(citations=[citation(1, OTHER)]))
    assert metrics["cited_url_match"] == 0.0
    assert metrics["cited_anchor_match"] == 0.0


@pytest.mark.parametrize("name", ["Ministral 3 14B", "ministral-14b-2512"])
def test_a_named_model_card_matches_capability_gold_through_the_documented_relaxation(
    name: str,
) -> None:
    metrics = question_metrics(
        record(
            question=f"Does {name} support function calling?",
            question_type="capability",
            gold_urls=["https://docs.mistral.ai/models"],
            gold_anchors=[None],
            citations=[citation(1, "https://docs.mistral.ai/models/ministral-3-14b-25-12")],
        )
    )

    assert metrics["cited_url_match"] == 1.0
    assert metrics["cited_anchor_match"] == 1.0
    assert metrics["gold_relaxed_matches"] == 1.0


def test_a_model_card_does_not_match_when_the_question_names_no_model() -> None:
    metrics = question_metrics(
        record(
            question="Which models support function calling?",
            question_type="capability",
            gold_urls=["https://docs.mistral.ai/models"],
            gold_anchors=[None],
            citations=[citation(1, "https://docs.mistral.ai/models/ministral-3-14b-25-12")],
        )
    )

    assert metrics["cited_url_match"] == 0.0
    assert metrics["cited_anchor_match"] == 0.0
    assert metrics["gold_relaxed_matches"] == 0.0


def test_an_unanswerable_question_has_no_gold_match_to_report() -> None:
    metrics = question_metrics(
        record(question_type="unanswerable", gold_urls=[], gold_anchors=[], insufficient=True)
    )
    assert metrics["cited_url_match"] is None
    assert metrics["cited_anchor_match"] is None
    assert metrics["refusal_correct"] == 1.0


def test_refusing_an_answerable_question_is_as_wrong_as_answering_an_unanswerable_one() -> None:
    assert question_metrics(record(insufficient=True))["refusal_correct"] == 0.0
    assert (
        question_metrics(
            record(question_type="unanswerable", gold_urls=[], gold_anchors=[], insufficient=False)
        )["refusal_correct"]
        == 0.0
    )


def test_fabricated_and_cosmetic_rejections_are_counted_apart() -> None:
    metrics = question_metrics(
        record(
            unverified=[
                rejected(2, RejectionReason.FABRICATED),
                rejected(3, RejectionReason.TOO_SHORT),
                rejected(9, f"{RejectionReason.NO_SUCH_SOURCE}: 9"),
            ]
        )
    )
    assert metrics["citations_fabricated"] == 2.0
    assert metrics["citations_cosmetic"] == 1.0
    assert metrics["unverified_citations_per_answer"] == 3.0


def test_a_quote_that_only_matched_after_normalization_is_verified_and_counted_apart() -> None:
    normalized = Citation(
        n=1, url=PAGE, quote="Maximum tools: 128", verified=True, reason=VERIFIED_AFTER_EMPHASIS
    )
    metrics = question_metrics(record(citations=[normalized]))
    assert metrics["citations_verified"] == 1.0
    assert metrics["citations_normalized"] == 1.0
    assert metrics["citations_fabricated"] == 0.0


def test_the_verification_rate_is_verified_over_emitted_across_the_cell() -> None:
    rows = [
        record(citations=[citation(1, PAGE)], unverified=[rejected(2, RejectionReason.FABRICATED)]),
        record(
            question_id="q2",
            citations=[citation(1, PAGE), citation(2, PAGE)],
            unverified=[],
        ),
    ]
    summary = cell(rows)
    assert summary["citations_emitted"] == 4
    assert summary["citations_verified"] == 3
    assert summary["citation_verification_rate"] == pytest.approx(0.75)
    assert summary["unverified_citations_per_answer"] == pytest.approx(0.5)
    assert summary["gold_relaxed_matches"] == 0


def test_latency_percentiles_and_token_totals_come_from_the_records() -> None:
    rows = [
        record(question_id=f"q{index}", latency_ms=index * 1000.0, prompt_tokens=100 * index)
        for index in range(1, 11)
    ]
    summary = cell(rows)
    assert summary["latency_p50_s"] == pytest.approx(5.0)
    assert summary["latency_p95_s"] == pytest.approx(10.0)
    assert summary["tokens_in_total"] == 5500
    assert summary["tokens_in"] == pytest.approx(550.0)


def test_what_judging_spent_is_counted_apart_from_what_answering_spent() -> None:
    judged = verdict("correct").model_copy(
        update={
            "usage": ProviderTokenUsage(
                prompt_tokens=2000, completion_tokens=100, reasoning_tokens=40
            ),
            "latency_ms": 2000.0,
        }
    )
    summary = cell([record(judge=judged), record(question_id="q2")])
    assert summary["judge_calls"] == 1
    assert summary["judge_tokens_in"] == 2000
    assert summary["judge_reasoning_tokens"] == 40
    assert summary["judge_failures"] == 0
    # The judge's tokens never reach the answer totals: the run pays for them on
    # another plan (D-020) and adding them would misprice both.
    assert summary["tokens_in_total"] == 2000
    assert summary["judge_reference_usd_total"] == pytest.approx(0.003 + 0.00075)


def test_a_verdict_that_never_validated_is_counted_as_a_judge_failure() -> None:
    failed = JudgeRecord(
        model="glm-5.3",
        prompt_version=JUDGE_VERSION,
        input_text="rendered",
        error="the judge's output did not validate",
    )
    summary = cell([record(judge=failed)])
    assert summary["judge_calls"] == 1
    assert summary["judge_failures"] == 1
    assert summary["judged"] == 0
    assert summary["correctness"] is None


def test_the_reference_cost_prices_the_recorded_tokens_at_the_shipped_model() -> None:
    # 1000 prompt tokens at 1.50 USD/Mtok and 100 completion at 7.50 USD/Mtok.
    summary = cell([record(prompt_tokens=1000, completion_tokens=100)])
    assert summary["reference_usd"] == pytest.approx(0.0015 + 0.00075)


def test_tool_calls_and_rounds_are_read_off_the_trace() -> None:
    metrics = question_metrics(
        record(trace_value=trace((1, PAGE, "body"), tool_events=3, rounds=2))
    )
    assert metrics["tool_calls"] == 3.0
    assert metrics["rounds"] == 2.0


def test_the_judged_columns_are_empty_until_a_verdict_exists() -> None:
    assert question_metrics(record())["correctness"] is None
    scored = question_metrics(record(judge=verdict("partial", total=4, supported=2)))
    assert scored["correctness"] == 0.5
    assert scored["groundedness"] == pytest.approx(0.5)


def test_a_verdict_that_claims_more_support_than_claims_is_clamped() -> None:
    graded = JudgeVerdict(
        correctness="correct", correctness_reason="r", claims_total=2, claims_supported=5
    )
    assert graded.groundedness == 1.0


def test_an_answer_with_no_factual_claim_has_no_groundedness_to_report() -> None:
    graded = JudgeVerdict(correctness="wrong", correctness_reason="r", claims_total=0)
    assert graded.groundedness is None


def test_citation_relevance_is_the_fraction_of_citations_that_support_their_sentence() -> None:
    graded = JudgeVerdict(
        correctness="correct",
        correctness_reason="r",
        citations=[
            CitationVerdict(n=1, supports=True),
            CitationVerdict(n=2, supports=False),
        ],
    )
    assert graded.citation_relevance == pytest.approx(0.5)


def test_aggregation_splits_by_strategy_and_by_question_type_and_names_a_winner() -> None:
    rows = [
        record(strategy="single_pass", judge=verdict("correct")),
        record(
            question_id="q2",
            question_type="unanswerable",
            gold_urls=[],
            gold_anchors=[],
            insufficient=True,
            strategy="single_pass",
            judge=verdict("correct"),
        ),
        record(strategy="outline", citations=[citation(1, OTHER)], judge=verdict("wrong")),
        record(
            question_id="q2",
            question_type="unanswerable",
            gold_urls=[],
            gold_anchors=[],
            insufficient=False,
            strategy="outline",
            judge=verdict("wrong"),
        ),
    ]
    metrics = aggregate(rows, CONFIG)
    assert metrics["question_types"] == ["single_page", "unanswerable"]
    assert metrics["by_strategy"]["single_pass"]["by_type"]["single_page"]["cited_url_match"] == 1.0
    assert metrics["by_strategy"]["outline"]["by_type"]["single_page"]["cited_url_match"] == 0.0
    assert metrics["by_strategy"]["single_pass"]["all"]["refusal_correct"] == 1.0
    assert metrics["winners"]["correctness"] == "single_pass"
    assert metrics["winners"]["cited_url_match"] == "single_pass"


# --------------------------------------------------------------------------- #
# The judge's input and its output
# --------------------------------------------------------------------------- #


def question(question_type: QuestionType = QuestionType.SINGLE_PAGE) -> EvalQuestion:
    return EvalQuestion(
        id="q1",
        question="How do I define a tool?",
        type=question_type,
        gold=[] if question_type == QuestionType.UNANSWERABLE else [GoldSource(url=PAGE)],
        reference_answer="Describe it as JSON Schema.",
        language="en",
        source=QuestionSource.HANDWRITTEN,
    )


def test_the_cited_passage_is_cut_back_out_of_the_context_the_model_saw() -> None:
    context = trace((1, PAGE, "First passage."), (2, OTHER, "Second passage."))
    assert source_texts(context) == {
        1: "Function calling\nFirst passage.",
        2: "Function calling\nSecond passage.",
    }


def test_a_source_missing_from_the_context_text_is_skipped_rather_than_guessed() -> None:
    context = trace((1, PAGE, "First passage."))
    broken = context.model_copy(
        update={
            "sources": [
                *context.sources,
                TracedSource(n=2, citation_url=OTHER, heading_path=[], chunk_ids=[], tokens=0),
            ]
        }
    )
    assert source_texts(broken) == {1: "Function calling\nFirst passage."}


def test_the_judge_sees_the_passage_behind_each_citation_and_no_strategy_name() -> None:
    context = trace((1, PAGE, "A tool is a JSON Schema description of one function."))
    payload = judge_input(
        question(),
        record(
            citations=[citation(1, PAGE, quote="a JSON Schema description")], trace_value=context
        ),
    )
    rendered = payload.render()
    assert "A tool is a JSON Schema description of one function." in rendered
    assert "a JSON Schema description" in rendered
    assert "single_pass" not in rendered
    assert "ministral" not in rendered
    assert PAGE not in rendered
    assert "GOLD SOURCES" not in rendered


def test_an_answer_with_no_verified_citation_says_so_to_the_judge() -> None:
    payload = judge_input(question(), record(citations=[]))
    assert "no verified citation" in payload.render()


def test_an_unanswerable_question_does_not_reveal_that_gold_has_no_source() -> None:
    payload = judge_input(
        question(QuestionType.UNANSWERABLE),
        record(question_type="unanswerable", gold_urls=[], gold_anchors=[], insufficient=True),
    )
    rendered = payload.render()
    assert "GOLD SOURCES" not in rendered
    assert "documentation does not cover this" not in rendered


def test_provider_qualified_judge_models_keep_the_primary_first() -> None:
    judges = parse_judge_models("zai:glm-5.3, mistral:ministral-14b-2512")
    assert [judge.identifier for judge in judges] == [
        "zai:glm-5.3",
        "mistral:ministral-14b-2512",
    ]


@pytest.mark.parametrize("value", ["glm-5.3", "openai:gpt", "zai:", "zai:a,zai:a"])
def test_invalid_or_duplicate_judge_models_are_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        parse_judge_models(value)


def test_a_verdict_wrapped_in_prose_and_a_fence_still_parses() -> None:
    body = json.dumps(
        {
            "correctness": "partial",
            "correctness_reason": "misses the tool_choice default",
            "claims_total": 3,
            "claims_supported": 2,
            "groundedness_reason": "one claim is not in the passage",
            "citations": [{"n": 1, "supports": True, "reason": "quotes the schema"}],
        }
    )
    raw = f"Here is my grade:\n```json\n{body}\n```\nLet me know if you want more detail."
    graded = JudgeVerdict.model_validate_json(extract_json_object(raw))
    assert graded.correctness == "partial"
    assert graded.groundedness == pytest.approx(2 / 3)
    assert graded.citation_relevance == 1.0


def test_a_verdict_with_an_unknown_correctness_label_is_refused() -> None:
    with pytest.raises(ValueError):
        JudgeVerdict.model_validate({"correctness": "excellent", "correctness_reason": "r"})


def test_an_unexpected_field_in_a_verdict_does_not_lose_the_verdict() -> None:
    graded = JudgeVerdict.model_validate(
        {"correctness": "correct", "correctness_reason": "r", "confidence": 0.9}
    )
    assert graded.correctness == "correct"


# --------------------------------------------------------------------------- #
# Stratified sampling
# --------------------------------------------------------------------------- #


def sample(question_type: QuestionType, index: int) -> EvalQuestion:
    return EvalQuestion(
        id=f"{question_type.value}-{index}",
        question=f"Question {index}?",
        type=question_type,
        gold=[] if question_type == QuestionType.UNANSWERABLE else [GoldSource(url=PAGE)],
        reference_answer="An answer.",
        language="en",
        source=QuestionSource.GENERATED,
    )


def population() -> list[EvalQuestion]:
    return [sample(QuestionType.SINGLE_PAGE, index) for index in range(20)] + [
        sample(question_type, index)
        for question_type in (QuestionType.CROSS_PAGE, QuestionType.UNANSWERABLE)
        for index in range(3)
    ]


def test_a_subset_covers_every_type_even_when_one_type_dominates() -> None:
    chosen = stratified_subset(population(), 6, seed=0)
    assert len(chosen) == 6
    assert {question.type for question in chosen} == {
        QuestionType.SINGLE_PAGE,
        QuestionType.CROSS_PAGE,
        QuestionType.UNANSWERABLE,
    }


def test_a_subset_smaller_than_the_number_of_types_takes_the_rarest_types_first() -> None:
    chosen = stratified_subset(population(), 2, seed=0)
    assert {question.type for question in chosen} == {
        QuestionType.CROSS_PAGE,
        QuestionType.UNANSWERABLE,
    }


def test_the_same_seed_gives_the_same_subset_and_another_seed_does_not() -> None:
    people = population()
    assert [q.id for q in stratified_subset(people, 8, seed=0)] == [
        q.id for q in stratified_subset(people, 8, seed=0)
    ]
    assert [q.id for q in stratified_subset(people, 8, seed=1)] != [
        q.id for q in stratified_subset(people, 8, seed=0)
    ]


def test_asking_for_more_than_there_is_returns_everything_once() -> None:
    people = population()
    chosen = stratified_subset(people, 500, seed=0)
    assert len(chosen) == len(people)
    assert len({question.id for question in chosen}) == len(people)


def test_an_empty_or_zero_request_is_empty() -> None:
    assert stratified_subset(population(), 0, seed=0) == []
    assert stratified_subset([], 5, seed=0) == []


# --------------------------------------------------------------------------- #
# The run directory: checkpoint, resumption, report
# --------------------------------------------------------------------------- #


def config_for(path: Path) -> dict[str, Any]:
    return {**CONFIG, "run_dir": str(path)}


def test_a_recorded_pair_is_not_run_again(tmp_path: Path) -> None:
    run = RunDirectory.open(tmp_path / "run", config_for(tmp_path / "run"))
    run.record(record(question_id="q1", strategy="single_pass"))
    run.record(record(question_id="q1", strategy="outline"))
    run.finalize(status="complete", error=None)

    resumed = RunDirectory.open(tmp_path / "run", config_for(tmp_path / "run"))
    assert resumed.done == {("q1", "single_pass"), ("q1", "outline")}
    assert len(resumed.records) == 2
    assert resumed.config["resumed_records"] == 2


def test_reopening_a_run_keeps_the_rows_it_already_paid_for(tmp_path: Path) -> None:
    run = RunDirectory.open(tmp_path / "run", config_for(tmp_path / "run"))
    run.record(record(question_id="q1"))
    reopened = RunDirectory.open(tmp_path / "run", config_for(tmp_path / "run"))
    reopened.record(record(question_id="q2"))
    lines = (tmp_path / "run" / "records.jsonl").read_text().splitlines()
    assert [json.loads(line)["question_id"] for line in lines] == ["q1", "q2"]


def test_resuming_without_notes_keeps_the_notes_the_run_was_published_with(
    tmp_path: Path,
) -> None:
    path = tmp_path / "run"
    RunDirectory.open(path, {**config_for(path), "notes": ["the index is not isolated"]})
    resumed = RunDirectory.open(path, {**config_for(path), "notes": []})
    assert resumed.config["notes"] == ["the index is not isolated"]
    readme = render_readme(
        resumed.config, {**aggregate([], resumed.config), "status": "complete", "error": None}
    )
    assert "the index is not isolated" in readme


def test_resuming_with_new_notes_replaces_the_old_ones(tmp_path: Path) -> None:
    path = tmp_path / "run"
    RunDirectory.open(path, {**config_for(path), "notes": ["first"]})
    resumed = RunDirectory.open(path, {**config_for(path), "notes": ["second"]})
    assert resumed.config["notes"] == ["second"]


def test_a_run_name_resolves_to_the_newest_directory_that_carries_it(tmp_path: Path) -> None:
    (tmp_path / "2026-09-01-0900-answers").mkdir()
    (tmp_path / "2026-09-02-0900-answers").mkdir()
    assert resolve_run_directory("answers", root=tmp_path).name == "2026-09-02-0900-answers"


def test_an_unused_run_name_gets_a_fresh_dated_directory(tmp_path: Path) -> None:
    fresh = resolve_run_directory("Answers Fixture!", root=tmp_path)
    assert fresh.name.endswith("-answers-fixture")
    assert not fresh.exists()


def test_the_answer_and_judge_calls_land_in_one_ledger_tagged_by_client(tmp_path: Path) -> None:
    run = RunDirectory.open(tmp_path / "run", config_for(tmp_path / "run"))
    run.append_call("answer", {"model": "ministral-14b-2512"})
    run.append_call("judge", {"model": "glm-5.3"})
    rows = [json.loads(line) for line in run.calls_path.read_text().splitlines()]
    assert [row["source"] for row in rows] == ["answer", "judge"]


def test_a_readme_names_the_generation_model_in_every_table(tmp_path: Path) -> None:
    metrics = aggregate([record(judge=verdict("correct"))], config_for(tmp_path))
    readme = render_readme(config_for(tmp_path), {**metrics, "status": "complete", "error": None})
    tables = [line for line in readme.splitlines() if line.startswith("| `single_pass`")]
    assert tables
    assert all("`ministral-14b-2512`" in line for line in tables)


def test_a_run_directory_is_rebuilt_from_its_rows_alone(tmp_path: Path) -> None:
    path = tmp_path / "run"
    run = RunDirectory.open(path, config_for(path))
    run.record(record(strategy="single_pass", judge=verdict("correct")))
    run.record(record(strategy="outline", judge=verdict("wrong")))
    run.finalize(status="complete", error=None)

    (path / "README.md").write_text("stale")
    (path / "metrics.json").write_text(json.dumps({"status": "complete"}))
    metrics = regenerate(path)

    assert metrics["records"] == 2
    assert "Answer evaluation" in (path / "README.md").read_text()
    assert metrics["by_strategy"]["single_pass"]["all"]["correctness"] == 1.0


@pytest.mark.asyncio
async def test_rejudge_keeps_answers_and_archives_the_old_judge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "fixture-run"
    run = RunDirectory.open(path, config_for(path))
    original = record(
        judge=verdict("wrong").model_copy(update={"prompt_version": "answer-judge/v1"})
    )
    run.record(original)

    class FakeProvider:
        async def aclose(self) -> None:
            pass

    async def no_quota_wait(_: int) -> None:
        return None

    async def fake_judges(
        answer: QuestionRecord, judges: list[Any], providers: dict[str, Any]
    ) -> dict[str, JudgeRecord]:
        del answer, providers
        return {
            judge.identifier: verdict("correct").model_copy(
                update={"model": judge.model, "provider": judge.provider}
            )
            for judge in judges
        }

    monkeypatch.setattr("glossator.eval.answer_eval.wait_for_quota", no_quota_wait)
    monkeypatch.setattr(
        "glossator.eval.answer_eval.make_judge_providers",
        lambda judges, run_dir: {"zai": FakeProvider()},
    )
    monkeypatch.setattr("glossator.eval.answer_eval.judge_with_models", fake_judges)

    metrics = await rejudge(path, judge_models=parse_judge_models("zai:new"))
    rewritten = json.loads((path / "records.jsonl").read_text())
    assert rewritten["answer_markdown"] == original.answer_markdown
    assert rewritten["judges_v1"]["zai:glm-5.3"]["verdict"]["correctness"] == "wrong"
    assert rewritten["judges"]["zai:new"]["verdict"]["correctness"] == "correct"
    assert rewritten["judge"] == rewritten["judges"]["zai:new"]
    assert metrics["agreement"]["per_judge"]["zai:new"]["mean_correctness"] == 1.0


def test_make_eval_report_picks_the_renderer_from_the_run_itself(tmp_path: Path) -> None:
    path = tmp_path / "run"
    run = RunDirectory.open(path, config_for(path))
    run.record(record(judge=verdict("correct")))
    run.finalize(status="complete", error=None)

    assert run_kind(path) == "answer_eval"
    metrics = rebuild(path)
    assert metrics["kind"] == "answer_eval"
    assert sorted(figure.name for figure in (path / "figures").glob("*.svg")) == [
        "citation-match.svg",
        "correctness.svg",
        "cost-per-question.svg",
        "groundedness.svg",
        "latency-vs-correctness.svg",
        "verification-rate.svg",
    ]


def test_every_figure_is_a_well_formed_svg(tmp_path: Path) -> None:
    path = tmp_path / "run"
    run = RunDirectory.open(path, config_for(path))
    run.record(record(judge=verdict("correct")))
    run.finalize(status="complete", error=None)
    for figure in (path / "figures").glob("*.svg"):
        body = figure.read_text()
        assert body.startswith("<svg")
        assert body.rstrip().endswith("</svg>")


def test_a_run_with_no_records_still_renders_rather_than_dividing_by_zero(tmp_path: Path) -> None:
    path = tmp_path / "run"
    run = RunDirectory.open(path, config_for(path))
    metrics = run.finalize(status="failed", error="the index was unreachable")
    assert metrics["records"] == 0
    assert "Answer evaluation" in (path / "README.md").read_text()
