"""Which part of the pipeline a failure belongs to, decided on hand-built records.

Every answer here is built by hand so that a class can be checked on paper: the
chunk map is three entries, the traces name the chunks they returned, and no
corpus, index, judge or network is involved. The one test that does read a corpus
checks the thing the analysis cannot get wrong quietly -- that a chunk id
recomputed from the corpus is the id the pipeline recorded.
"""

import json
from pathlib import Path
from typing import Any

import pytest
from mistralai.search.toolkit.common.text import sanitize_text
from mistralai.search.toolkit.document import compute_char_locator, compute_id

from glossator.answer.citations import Citation, Trace, TracedSource, TraceEvent
from glossator.eval.answer_eval.models import JudgeRecord, JudgeVerdict, QuestionRecord
from glossator.eval.charts import stacked_bar_chart
from glossator.eval.failures import (
    FAILURES_KIND,
    AnalysedRun,
    ChunkFacts,
    ChunkIndex,
    DefectSignal,
    FailureClass,
    SkippedRun,
    SubLabel,
    analyse_run,
    chunk_index,
    classify,
    defect_input,
    is_failure,
    parse_judge_model,
    regenerate,
    rerank_candidates,
    resolve_run_directory,
    write_run,
)
from glossator.eval.report import rebuild, run_kind
from glossator.index.variants import ChunkStrategy
from glossator.ingest.chunker import PageFacts, build_chunker
from glossator.ingest.pages import iter_page_paths, load_page

GOLD = "https://docs.mistral.ai/capabilities/function-calling"
OTHER = "https://docs.mistral.ai/getting-started/quickstart"
MATRIX = "https://docs.mistral.ai/models"
CARD = "https://docs.mistral.ai/models/mistral-medium-3-5-26-04"
"""A real model card: the capability relaxation reads the card's own API names out
of the corpus, so the slug has to be one the corpus has."""

GOLD_CHUNK = "gold-chunk"
GOLD_OTHER_SECTION = "gold-other-section"
OTHER_CHUNK = "other-chunk"
CARD_CHUNK = "card-chunk"

INDEX = ChunkIndex(
    facts={
        GOLD_CHUNK: ChunkFacts(
            url=GOLD, anchor="tools", heading_path=("Function calling", "Tools")
        ),
        GOLD_OTHER_SECTION: ChunkFacts(
            url=GOLD, anchor="streaming", heading_path=("Function calling", "Streaming")
        ),
        OTHER_CHUNK: ChunkFacts(url=OTHER, anchor=None, heading_path=("Quickstart",)),
        CARD_CHUNK: ChunkFacts(url=CARD, anchor=None, heading_path=("Mistral Medium 3.5",)),
    },
    chunking=ChunkStrategy.SECTION,
)

FIXTURE_CORPUS = Path("tests/fixtures/corpus")


def trace(
    *,
    retrieved: list[str],
    assembled: list[str] | None = None,
    dropped: list[str] | None = None,
    context_tokens: int = 500,
) -> Trace:
    """A trace that returned `retrieved` and assembled `assembled` into the context."""
    sources = assembled if assembled is not None else retrieved
    return Trace(
        strategy="single_pass",
        variant="sec1024",
        prompt_version="grounded-answer/v2",
        rounds=1,
        events=[
            TraceEvent(step=1, kind="retrieval", name="search", round=1, result_ids=retrieved),
            TraceEvent(step=2, kind="assembly", name="context", round=1, result_ids=sources),
        ],
        sources=[
            TracedSource(
                n=index + 1,
                citation_url=INDEX.facts[chunk_id].url,
                heading_path=list(INDEX.facts[chunk_id].heading_path),
                chunk_ids=[chunk_id],
                tokens=50,
            )
            for index, chunk_id in enumerate(sources)
        ],
        context_tokens=context_tokens,
        dropped_chunk_ids=dropped or [],
    )


def judge(correctness: str, reason: str = "It disagrees on the substance.") -> JudgeRecord:
    return JudgeRecord(
        model="glm-5.3",
        provider="zai",
        prompt_version="answer-judge/v2",
        input_text="(the judge input)",
        verdict=JudgeVerdict(
            correctness=correctness,  # type: ignore[arg-type]
            correctness_reason=reason,
            claims_total=1,
            claims_supported=1,
        ),
    )


def record(
    *,
    question_id: str = "q1",
    question_type: str = "single_page",
    gold_urls: list[str] | None = None,
    gold_anchors: list[str | None] | None = None,
    citations: list[Citation] | None = None,
    unverified: list[Citation] | None = None,
    insufficient: bool = False,
    verdict: str | None = "wrong",
    reason: str = "It disagrees on the substance.",
    trace_value: Trace | None = None,
) -> QuestionRecord:
    return QuestionRecord(
        question_id=question_id,
        question="How do I define a tool?",
        question_type=question_type,
        language="en",
        gold_urls=[GOLD] if gold_urls is None else gold_urls,
        gold_anchors=["tools"] if gold_anchors is None else gold_anchors,
        reference_answer="Describe it as JSON Schema.",
        strategy="single_pass",
        variant="sec1024",
        model="ministral-14b-2512",
        answer_markdown="An answer.",
        citations=citations or [],
        unverified_citations=unverified or [],
        insufficient_evidence=insufficient,
        trace=trace_value if trace_value is not None else trace(retrieved=[GOLD_CHUNK]),
        judge=judge(verdict, reason) if verdict else None,
    )


def classified(record_value: QuestionRecord, **overrides: Any) -> Any:
    options: dict[str, Any] = {
        "index": INDEX,
        "run_name": "run",
        "run_dir": Path("eval/runs/run"),
        "reranked": {},
        "human": None,
    }
    options.update(overrides)
    return classify(record_value, **options)


def cite(url: str, *, anchor: str | None = None, verified: bool = True) -> Citation:
    return Citation(
        n=1,
        url=url,
        anchor=anchor,
        quote="a quoted span",
        verified=verified,
        reason=None if verified else "quote is not in the cited source",
    )


# --------------------------------------------------------------------------- #
# What counts as a failure at all
# --------------------------------------------------------------------------- #


def test_a_correct_answer_with_a_correct_refusal_is_not_a_failure() -> None:
    assert not is_failure(record(verdict="correct"))
    assert classified(record(verdict="correct")) is None


def test_an_unjudged_answer_that_refused_correctly_is_not_a_failure() -> None:
    unjudged = record(question_type="unanswerable", gold_urls=[], gold_anchors=[], verdict=None)
    assert classified(unjudged.model_copy(update={"insufficient_evidence": True})) is None


def test_a_correct_verdict_with_a_wrong_refusal_is_still_a_failure() -> None:
    refused = record(verdict="correct", insufficient=True)
    assert is_failure(refused)
    assert classified(refused).failure_class is FailureClass.REFUSAL


# --------------------------------------------------------------------------- #
# The four classes
# --------------------------------------------------------------------------- #


def test_no_gold_chunk_in_any_round_is_a_retrieval_miss() -> None:
    failure = classified(record(trace_value=trace(retrieved=[OTHER_CHUNK])))

    assert failure.failure_class is FailureClass.RETRIEVAL_MISS
    assert failure.sub_label is SubLabel.CANDIDATES_NOT_RECORDED
    assert not failure.gold_retrieved
    assert failure.retrieved_pages == [OTHER]
    assert GOLD in failure.evidence


def test_a_gold_chunk_found_in_a_later_round_is_not_a_retrieval_miss() -> None:
    late = trace(retrieved=[OTHER_CHUNK], assembled=[OTHER_CHUNK])
    late = late.model_copy(
        update={
            "events": [
                *late.events,
                TraceEvent(step=3, kind="tool", name="search", round=2, result_ids=[GOLD_CHUNK]),
            ]
        }
    )

    failure = classified(record(trace_value=late))

    assert failure.gold_retrieved
    assert failure.failure_class is FailureClass.CONTEXT_MISS


def test_the_reranker_sub_label_names_the_reranker_when_it_was_offered_the_page() -> None:
    offered = {("q1", "single_pass"): {GOLD, OTHER}}

    failure = classified(record(trace_value=trace(retrieved=[OTHER_CHUNK])), reranked=offered)

    assert failure.sub_label is SubLabel.RERANKER_DROP
    assert failure.gold_page_reranked_in is True


def test_the_reranker_sub_label_names_the_search_when_it_was_not_offered_the_page() -> None:
    offered = {("q1", "single_pass"): {OTHER}}

    failure = classified(record(trace_value=trace(retrieved=[OTHER_CHUNK])), reranked=offered)

    assert failure.sub_label is SubLabel.SEARCH_MISS
    assert failure.gold_page_reranked_in is False


def test_a_gold_chunk_dropped_from_the_context_is_a_context_miss() -> None:
    dropped = trace(
        retrieved=[GOLD_CHUNK, OTHER_CHUNK], assembled=[OTHER_CHUNK], dropped=[GOLD_CHUNK]
    )

    failure = classified(record(trace_value=dropped))

    assert failure.failure_class is FailureClass.CONTEXT_MISS
    assert failure.sub_label is SubLabel.DROPPED_FROM_CONTEXT
    assert failure.gold_chunk_dropped


def test_a_gold_chunk_left_out_of_the_context_without_a_drop_is_outranked() -> None:
    left_out = trace(retrieved=[GOLD_CHUNK, OTHER_CHUNK], assembled=[OTHER_CHUNK])

    failure = classified(record(trace_value=left_out))

    assert failure.failure_class is FailureClass.CONTEXT_MISS
    assert failure.sub_label is SubLabel.OUTRANKED_IN_ASSEMBLY
    assert not failure.gold_chunk_dropped


def test_a_wrong_answer_that_cited_another_page_is_a_generation_failure() -> None:
    failure = classified(
        record(
            trace_value=trace(retrieved=[GOLD_CHUNK, OTHER_CHUNK]),
            citations=[cite(OTHER)],
        )
    )

    assert failure.failure_class is FailureClass.GENERATION
    assert failure.sub_label is SubLabel.NO_CITATION_TO_GOLD
    assert OTHER in failure.evidence


def test_a_rejected_quote_from_the_gold_section_is_its_own_sub_label() -> None:
    failure = classified(
        record(unverified=[cite(GOLD, anchor="tools", verified=False)]),
    )

    assert failure.sub_label is SubLabel.UNVERIFIED_QUOTE_FROM_GOLD
    assert "quote is not in the cited source" in failure.evidence


def test_a_verified_quote_from_the_gold_section_is_the_strongest_model_limit() -> None:
    failure = classified(record(citations=[cite(GOLD, anchor="tools")]))

    assert failure.failure_class is FailureClass.GENERATION
    assert failure.sub_label is SubLabel.VERIFIED_QUOTE_FROM_GOLD
    assert failure.gold_section_in_context


def test_a_refusal_with_the_gold_section_in_context_is_a_false_refusal() -> None:
    failure = classified(record(insufficient=True))

    assert failure.failure_class is FailureClass.REFUSAL
    assert failure.sub_label is SubLabel.FALSE_REFUSAL
    assert failure.gold_section_in_context


def test_answering_an_unanswerable_question_is_a_missed_refusal() -> None:
    answered = record(
        question_type="unanswerable",
        gold_urls=[],
        gold_anchors=[],
        trace_value=trace(retrieved=[OTHER_CHUNK]),
    )

    failure = classified(answered)

    assert failure.failure_class is FailureClass.REFUSAL
    assert failure.sub_label is SubLabel.MISSED_REFUSAL
    assert not failure.answerable


# --------------------------------------------------------------------------- #
# The order between the classes
# --------------------------------------------------------------------------- #


def test_a_refusal_after_a_retrieval_miss_is_the_retrieval_miss() -> None:
    """Refusing when the evidence never arrived is the pipeline working."""
    failure = classified(record(insufficient=True, trace_value=trace(retrieved=[OTHER_CHUNK])))

    assert failure.failure_class is FailureClass.RETRIEVAL_MISS


def test_a_refusal_after_a_context_miss_is_the_context_miss() -> None:
    failure = classified(
        record(
            insufficient=True,
            trace_value=trace(retrieved=[GOLD_CHUNK, OTHER_CHUNK], assembled=[OTHER_CHUNK]),
        )
    )

    assert failure.failure_class is FailureClass.CONTEXT_MISS


def test_a_refusal_wins_over_a_generation_failure_when_the_gold_was_there() -> None:
    failure = classified(record(insufficient=True, citations=[cite(GOLD, anchor="tools")]))

    assert failure.failure_class is FailureClass.REFUSAL


# --------------------------------------------------------------------------- #
# Gold matching
# --------------------------------------------------------------------------- #


def test_a_gold_source_with_no_anchor_is_matched_by_any_section_of_the_page() -> None:
    failure = classified(
        record(
            gold_anchors=[None],
            trace_value=trace(retrieved=[GOLD_OTHER_SECTION]),
            citations=[cite(GOLD, anchor="streaming")],
        )
    )

    assert failure.failure_class is FailureClass.GENERATION
    assert failure.gold_section_in_context


def test_another_section_of_the_gold_page_is_not_the_gold_section() -> None:
    failure = classified(record(trace_value=trace(retrieved=[GOLD_OTHER_SECTION])))

    assert failure.failure_class is FailureClass.GENERATION
    assert failure.gold_in_context
    assert not failure.gold_section_in_context


def test_a_named_models_card_stands_in_for_the_capability_matrix() -> None:
    capability = record(
        question_type="capability",
        gold_urls=[MATRIX],
        gold_anchors=[None],
        trace_value=trace(retrieved=[CARD_CHUNK]),
    ).model_copy(update={"question": "What is the context length of Mistral Medium 3.5?"})

    failure = classified(capability)

    assert failure.failure_class is FailureClass.GENERATION
    assert failure.gold_retrieved


# --------------------------------------------------------------------------- #
# The reference-defect flag
# --------------------------------------------------------------------------- #


def test_a_judge_reason_that_names_the_reference_raises_the_flag() -> None:
    failure = classified(record(reason="It omits what the reference answer states."))

    assert failure.reference_defect_suspected
    assert failure.defect_signals == [DefectSignal.JUDGE_NAMES_THE_REFERENCE]


def test_a_human_label_above_the_judges_raises_the_flag() -> None:
    failure = classified(record(reason="It disagrees."), human="correct")

    assert failure.defect_signals == [DefectSignal.HUMAN_IS_MORE_LENIENT]
    assert failure.human_label == "correct"


def test_a_human_label_below_the_judges_raises_nothing() -> None:
    failure = classified(record(verdict="partial", reason="It disagrees."), human="wrong")

    assert failure.defect_signals == []
    assert not failure.reference_defect_suspected


def test_the_defect_judge_is_shown_the_question_the_reference_and_the_section() -> None:
    failure = classified(record())

    rendered = defect_input(failure, "Describe it as JSON Schema.", "## Tools\nA tool is JSON.")

    assert "How do I define a tool?" in rendered
    assert "Describe it as JSON Schema." in rendered
    assert "## Tools" in rendered


@pytest.mark.parametrize("value", ["glm-5.3", "openai:gpt", "zai:"])
def test_an_invalid_judge_model_is_rejected(value: str) -> None:
    with pytest.raises(ValueError, match="invalid judge model"):
        parse_judge_model(value)


def test_a_judge_model_carries_its_provider() -> None:
    assert parse_judge_model("zai:glm-5.3") == ("zai", "glm-5.3")


# --------------------------------------------------------------------------- #
# Reranker candidates out of a call ledger
# --------------------------------------------------------------------------- #


def test_the_reranker_candidates_come_out_of_the_call_ledger(tmp_path: Path) -> None:
    prompt = (
        "Question: x\n\nCandidates:\n"
        f"[1] {OTHER} | Quickstart\nsome text\n\n"
        f"[2] {GOLD}#tools | Function calling > Tools\nmore text"
    )
    (tmp_path / "calls.jsonl").write_text(
        json.dumps(
            {
                "source": "answer",
                "purpose": "rerank",
                "question_id": "q1",
                "strategy": "single_pass",
                "messages": [
                    {"role": "system", "content": "rank"},
                    {"role": "user", "content": prompt},
                ],
            }
        )
        + "\n"
    )

    assert rerank_candidates(tmp_path) == {("q1", "single_pass"): {OTHER, GOLD}}


def test_a_ledger_without_reranker_calls_yields_no_candidates(tmp_path: Path) -> None:
    (tmp_path / "calls.jsonl").write_text(
        json.dumps({"source": "answer", "purpose": "single_pass:grounded_answer"}) + "\n"
    )

    assert rerank_candidates(tmp_path) == {}


# --------------------------------------------------------------------------- #
# The chunk map
# --------------------------------------------------------------------------- #


def test_the_chunk_map_reproduces_the_ids_the_ingest_would_write() -> None:
    """The whole classification rests on this identity, so it is checked directly."""
    index = chunk_index(FIXTURE_CORPUS, ChunkStrategy.SECTION)
    chunker = build_chunker(ChunkStrategy.SECTION)

    expected: dict[str, str] = {}
    for path in iter_page_paths(FIXTURE_CORPUS):
        page = load_page(path)
        body = sanitize_text(page.body)
        facts = PageFacts(url=page.url, title=page.title, kind=page.kind, locale=page.locale)
        for spec in chunker.plan(body, facts):
            expected[compute_id(page.url, compute_char_locator(spec.start, spec.end))] = page.url

    assert expected
    assert {chunk_id: facts.url for chunk_id, facts in index.facts.items()} == expected


def test_an_unknown_chunk_id_resolves_to_nothing() -> None:
    assert INDEX.page("not-a-chunk") is None
    assert INDEX.resolves([GOLD_CHUNK, "not-a-chunk"]) == 1


# --------------------------------------------------------------------------- #
# A whole run directory
# --------------------------------------------------------------------------- #

ANSWER_EVAL_CONFIG: dict[str, Any] = {
    "kind": "answer_eval",
    "model": "ministral-14b-2512",
    "variant": "sec1024",
    "dataset": "tests/fixtures/answer-questions.jsonl",
    "strategies": ["single_pass"],
    "rerank": True,
}


def source_run(tmp_path: Path, records: list[QuestionRecord]) -> Path:
    run_dir = tmp_path / "source-run"
    (run_dir / "figures").mkdir(parents=True)
    (run_dir / "config.json").write_text(json.dumps(ANSWER_EVAL_CONFIG))
    (run_dir / "records.jsonl").write_text(
        "".join(json.dumps(row.model_dump(mode="json")) + "\n" for row in records)
    )
    return run_dir


def analysed_run(tmp_path: Path, records: list[QuestionRecord]) -> AnalysedRun:
    result = analyse_run(source_run(tmp_path, records), corpus_dir=FIXTURE_CORPUS, labels_path=None)
    assert isinstance(result, AnalysedRun)
    return result


def test_a_run_of_another_kind_is_skipped_with_its_kind_named(tmp_path: Path) -> None:
    run_dir = tmp_path / "perturb-run"
    run_dir.mkdir()
    (run_dir / "config.json").write_text(json.dumps({"kind": "perturb"}))

    skipped = analyse_run(run_dir, corpus_dir=FIXTURE_CORPUS, labels_path=None)

    assert isinstance(skipped, SkippedRun)
    assert skipped.kind == "perturb"
    assert "holds no answers" in skipped.reason


def test_a_run_directory_holds_one_row_per_failure_and_a_readme_that_counts_them(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("glossator.eval.failures.chunk_index", lambda corpus_dir, chunking: INDEX)
    records = [
        record(question_id="q1", verdict="correct"),
        record(question_id="q2", trace_value=trace(retrieved=[OTHER_CHUNK])),
        record(question_id="q3", citations=[cite(GOLD, anchor="tools")], verdict="partial"),
        record(question_id="q4", insufficient=True, verdict="wrong"),
        record(
            question_id="q5",
            question_type="unanswerable",
            gold_urls=[],
            gold_anchors=[],
            trace_value=trace(retrieved=[OTHER_CHUNK]),
        ),
    ]
    analysed = analysed_run(tmp_path, records)
    out = tmp_path / "out"
    config = {"kind": FAILURES_KIND, "corpus": str(FIXTURE_CORPUS), "run_dir": str(out)}

    metrics = write_run(out, [analysed], [], config)

    rows = [json.loads(line) for line in (out / "records.jsonl").read_text().splitlines()]
    assert [row["question_id"] for row in rows] == ["q2", "q3", "q4", "q5"]
    assert metrics["totals"]["by_class"] == {
        "retrieval_miss": 1,
        "context_miss": 0,
        "generation_failure": 1,
        "refusal_failure": 2,
    }
    assert metrics["totals"]["answers"] == 5
    readme = (out / "README.md").read_text()
    assert "| retrieval miss |" in readme
    assert "`q2`" in readme
    assert (out / "figures" / "failure-classes.svg").exists()


def test_the_readme_and_metrics_regenerate_from_the_rows_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("glossator.eval.failures.chunk_index", lambda corpus_dir, chunking: INDEX)
    records = [
        record(question_id="q1", trace_value=trace(retrieved=[OTHER_CHUNK])),
        record(question_id="q2", citations=[cite(GOLD, anchor="tools")]),
    ]
    analysed = analysed_run(tmp_path, records)
    out = tmp_path / "out"
    write_run(out, [analysed], [], {"kind": FAILURES_KIND, "corpus": "c", "run_dir": str(out)})
    before = (out / "README.md").read_text(), (out / "metrics.json").read_text()

    regenerate(out)

    assert ((out / "README.md").read_text(), (out / "metrics.json").read_text()) == before


def test_the_report_cli_dispatches_on_the_run_kind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("glossator.eval.failures.chunk_index", lambda corpus_dir, chunking: INDEX)
    analysed = analysed_run(tmp_path, [record(question_id="q1")])
    out = tmp_path / "out"
    write_run(out, [analysed], [], {"kind": FAILURES_KIND, "corpus": "c", "run_dir": str(out)})

    assert run_kind(out) == FAILURES_KIND
    assert rebuild(out)["kind"] == FAILURES_KIND


def test_a_run_directory_is_named_for_the_moment_it_started(tmp_path: Path) -> None:
    first = resolve_run_directory("Failure Analysis", root=tmp_path)
    first.mkdir()
    second = resolve_run_directory("Failure Analysis", root=tmp_path)

    assert first.name.endswith("-failure-analysis")
    assert second.name.endswith("-failure-analysis-2")


# --------------------------------------------------------------------------- #
# The figure
# --------------------------------------------------------------------------- #


def test_a_stacked_bar_lays_its_segments_end_to_end() -> None:
    svg = stacked_bar_chart("Failures", [("run a", (1.0, 3.0)), ("run b", (0.0, 0.0))], ("x", "y"))

    assert svg.startswith("<svg")
    # Two segments for the first row, none for the empty one.
    assert svg.count("<rect") == 2 + 2  # bars plus the two legend swatches
    assert ">4<" in svg
