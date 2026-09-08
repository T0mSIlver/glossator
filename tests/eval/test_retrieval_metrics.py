"""Metric arithmetic on rankings built by hand, at both matchings.

The numbers come out of the toolkit's calculator, so what is checked here is the
part this project owns: which hits count, which questions are scoreable, and what
happens when one page contributes several chunks.
"""

import asyncio
from collections.abc import Sequence

import pytest
from mistralai.search.toolkit.document import ChunkType
from mistralai.search.toolkit.evals import RetrievalMetrics
from mistralai.search.toolkit.search import SearchResult, SearchResultChunk

from glossator.eval.datasets import EvalQuestion, GoldSource, QuestionSource, QuestionType
from glossator.eval.retrieval_metrics import (
    Matching,
    aggregate,
    as_row,
    deduplicate,
    evaluate,
    gold_proxies,
    scoreable,
)

STREAM = "https://docs.mistral.ai/getting-started/quickstart"
TOOLS = "https://docs.mistral.ai/capabilities/function-calling"


def hit(url: str, anchor: str | None, *, rank: int) -> SearchResult:
    return SearchResult(
        chunk=SearchResultChunk(
            id=f"{url}#{anchor}:{rank}",
            source_id=url,
            locator=f"rank:{rank}",
            start_offset=None,
            end_offset=None,
            chunk_type=ChunkType.CONTENT,
            content="",
            metadata={"url": url, "anchor": anchor},
        ),
        score=1.0 / rank,
    )


def question(
    identifier: str,
    gold: list[tuple[str, str | None]],
    question_type: QuestionType = QuestionType.SINGLE_PAGE,
) -> EvalQuestion:
    return EvalQuestion(
        id=identifier,
        question=f"question {identifier}",
        type=question_type,
        gold=[GoldSource(url=url, anchor=anchor) for url, anchor in gold],
        reference_answer="an answer",
        language="en",
        source=QuestionSource.HANDWRITTEN,
    )


def score(
    questions: Sequence[EvalQuestion],
    results: dict[str, list[SearchResult]],
    matching: Matching,
) -> dict[str, RetrievalMetrics]:
    return asyncio.run(evaluate(questions, results, matching, top_k=10))


ANCHORED = question("q1", [(STREAM, "stream-a-response")])
ANCHORLESS = question("q2", [(TOOLS, None)])
UNANSWERABLE = question("q3", [], QuestionType.UNANSWERABLE)


def test_gold_is_proxied_the_way_the_harness_proxies_a_hit() -> None:
    assert gold_proxies(ANCHORED, Matching.PAGE) == [f"url_{STREAM}"]
    assert gold_proxies(ANCHORED, Matching.SECTION) == [f"url_{STREAM}_anchor_stream-a-response"]


def test_a_question_without_a_gold_anchor_is_page_level_only() -> None:
    assert gold_proxies(ANCHORLESS, Matching.PAGE) == [f"url_{TOOLS}"]
    assert gold_proxies(ANCHORLESS, Matching.SECTION) is None


def test_an_unanswerable_question_is_scoreable_at_neither_matching() -> None:
    assert gold_proxies(UNANSWERABLE, Matching.PAGE) is None
    assert gold_proxies(UNANSWERABLE, Matching.SECTION) is None


def test_scoreable_selects_per_matching() -> None:
    questions = [ANCHORED, ANCHORLESS, UNANSWERABLE]
    assert [item.id for item in scoreable(questions, Matching.PAGE)] == ["q1", "q2"]
    assert [item.id for item in scoreable(questions, Matching.SECTION)] == ["q1"]


def test_several_chunks_of_one_page_collapse_to_one_result() -> None:
    ranked = [
        hit(STREAM, "stream-a-response", rank=1),
        hit(STREAM, "stream-a-response", rank=2),
        hit(STREAM, "make-your-first-request", rank=3),
        hit(TOOLS, "tool-choice", rank=4),
    ]
    assert len(deduplicate(ranked, Matching.PAGE)) == 2
    # Section level keeps the two distinct anchors of the same page apart.
    assert len(deduplicate(ranked, Matching.SECTION)) == 3
    # The best rank survives, so the collapse never demotes a hit.
    assert deduplicate(ranked, Matching.PAGE)[0].chunk.locator == "rank:1"


def test_a_gold_page_at_rank_one_scores_perfectly() -> None:
    results = {"q1": [hit(STREAM, "stream-a-response", rank=1), hit(TOOLS, "tool-choice", rank=2)]}
    row = as_row(score([ANCHORED], results, Matching.PAGE)["q1"], questions=1)
    assert row["recall@1"] == 1.0
    assert row["mrr"] == 1.0
    assert row["ndcg@10"] == 1.0


def test_repeated_chunks_of_the_gold_page_do_not_push_ndcg_above_one() -> None:
    """The harness's ideal DCG assumes one entry per relevant id; four chunks of
    the right page would otherwise score 2.13."""
    results = {"q1": [hit(STREAM, "stream-a-response", rank=rank) for rank in range(1, 5)]}
    row = as_row(score([ANCHORED], results, Matching.PAGE)["q1"], questions=1)
    assert row["ndcg@10"] == 1.0
    assert row["recall@1"] == 1.0


def test_a_gold_page_at_rank_four_is_missed_at_three_and_found_at_five() -> None:
    # Three distinct decoy pages, so the collapse leaves the gold page at rank 4.
    ranked = [hit(f"https://docs.mistral.ai/other/{n}", None, rank=n) for n in range(1, 4)]
    ranked.append(hit(STREAM, "stream-a-response", rank=4))
    row = as_row(score([ANCHORED], {"q1": ranked}, Matching.PAGE)["q1"], questions=1)
    assert row["recall@1"] == 0.0
    assert row["recall@3"] == 0.0
    assert row["recall@5"] == 1.0
    assert row["mrr"] == 0.25


def test_decoy_chunks_of_one_page_do_not_hold_the_gold_page_out_of_the_top_three() -> None:
    """Three chunks of one decoy page are one result, so the gold page is second."""
    ranked = [hit(TOOLS, f"other-{n}", rank=n) for n in range(1, 4)]
    ranked.append(hit(STREAM, "stream-a-response", rank=4))
    row = as_row(score([ANCHORED], {"q1": ranked}, Matching.PAGE)["q1"], questions=1)
    assert row["recall@3"] == 1.0
    assert row["mrr"] == 0.5


def test_the_right_page_with_the_wrong_anchor_counts_at_page_level_only() -> None:
    results = {"q1": [hit(STREAM, "make-your-first-request", rank=1)]}
    page = score([ANCHORED], results, Matching.PAGE)
    section = score([ANCHORED], results, Matching.SECTION)
    assert as_row(page["q1"], questions=1)["recall@1"] == 1.0
    assert as_row(section["q1"], questions=1)["recall@1"] == 0.0


def test_an_anchorless_question_is_absent_from_the_section_metrics() -> None:
    results = {"q2": [hit(TOOLS, "tool-choice", rank=1)]}
    assert score([ANCHORLESS], results, Matching.SECTION) == {}
    assert set(score([ANCHORLESS], results, Matching.PAGE)) == {"q2"}


def test_a_cross_page_question_needs_both_pages_for_full_recall() -> None:
    both = question("q4", [(STREAM, "stream-a-response"), (TOOLS, "tool-choice")])
    half = {"q4": [hit(STREAM, "stream-a-response", rank=1)]}
    whole = {"q4": [hit(STREAM, "stream-a-response", rank=1), hit(TOOLS, "tool-choice", rank=2)]}
    assert as_row(score([both], half, Matching.PAGE)["q4"], 1)["recall@5"] == 0.5
    assert as_row(score([both], whole, Matching.PAGE)["q4"], 1)["recall@5"] == 1.0


def test_two_questions_with_the_same_text_are_refused() -> None:
    twin = question("q5", [(STREAM, "stream-a-response")]).model_copy(
        update={"question": ANCHORED.question}
    )
    results = {"q1": [hit(STREAM, "stream-a-response", rank=1)], "q5": []}
    with pytest.raises(ValueError, match="identical text"):
        score([ANCHORED, twin], results, Matching.PAGE)


def test_aggregating_averages_the_questions() -> None:
    second = question("q6", [(STREAM, "stream-a-response")])
    results = {
        "q1": [hit(STREAM, "stream-a-response", rank=1)],
        "q6": [hit(TOOLS, "tool-choice", rank=1), hit(STREAM, "stream-a-response", rank=2)],
    }
    metrics = score([ANCHORED, second], results, Matching.PAGE)
    row = as_row(aggregate(list(metrics.values())), questions=2)
    assert row["recall@1"] == 0.5
    assert row["mrr"] == 0.75


def test_an_empty_group_has_no_aggregate() -> None:
    assert aggregate([]) is None
    assert as_row(None, questions=0) == {"questions": 0}
