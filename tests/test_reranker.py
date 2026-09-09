"""The listwise reranker against a model that never touches the network.

The interesting cases are the ones where the model misbehaves: retrieval order is
a usable answer and a serving path must never raise on a reranker's account.
"""

import asyncio
from collections.abc import Callable
from typing import Any

from glossator.answer.config import MISTRAL_SMALL_4
from glossator.answer.llm import Completion, Message
from glossator.retrieval.config import DEFAULT_RERANK_MODEL, RERANK_MODEL, RetrievalConfig
from glossator.retrieval.engine import Hit
from glossator.retrieval.reranker import (
    CANDIDATE_TOKEN_BUDGET,
    ListwiseReranker,
    RankedCandidate,
    Ranking,
    RerankResult,
    render_candidates,
    rerank_llm_config,
    truncate_tokens,
)
from tests.answer.conftest import FakeLLM, completion, make_hit

MODEL = "ministral-8b-2512"


def candidates(count: int = 4) -> list[Hit]:
    return [
        make_hit(
            f"chunk-{index}",
            f"body {index}",
            score=10.0 - index,
            anchor=f"anchor-{index}",
            heading_path=("Function calling", f"Section {index}"),
        )
        for index in range(count)
    ]


Scripted = Completion | Callable[[list[Message]], Completion]


def rerank(hits: list[Hit], *entries: Scripted, **config: Any) -> RerankResult:
    reranker = ListwiseReranker(
        RetrievalConfig(rerank=True, rerank_model=MODEL, **config), FakeLLM(list(entries))
    )
    return asyncio.run(reranker.rerank("how do I call a tool?", hits))


def ranking(*positions: int) -> Ranking:
    return Ranking(
        ranking=[
            RankedCandidate(index=position, reason=f"reason {position}") for position in positions
        ]
    )


def test_the_default_rerank_model_is_the_priced_mistral_small_4_id() -> None:
    """The id is spelled out in the retrieval config to avoid an import cycle;
    this is what stops the two spellings from drifting apart."""
    assert DEFAULT_RERANK_MODEL == MISTRAL_SMALL_4
    assert RetrievalConfig().rerank_model == RERANK_MODEL


def test_an_unpriced_rerank_model_builds_and_costs_zero() -> None:
    """A local server's rerank model is unknown to the price list (D-035c): the
    reranker builds, its calls are recorded, and the cost is zero with one
    warning per process rather than a refusal."""
    reranker = ListwiseReranker(RetrievalConfig(rerank_model="not-a-model"), FakeLLM([]))
    assert reranker.config.rerank_model == "not-a-model"
    assert rerank_llm_config(reranker.config).cost_usd("not-a-model", 1_000, 100) == 0.0


def test_the_ranking_reorders_the_hits() -> None:
    result = rerank(candidates(), completion(parsed=ranking(3, 1, 4, 2)))
    assert result.trace.applied
    assert [hit.chunk_id for hit in result.hits] == ["chunk-2", "chunk-0", "chunk-3", "chunk-1"]


def test_both_scores_survive_a_rerank() -> None:
    result = rerank(candidates(), completion(parsed=ranking(4, 3, 2, 1)))
    first = result.hits[0]
    assert first.chunk_id == "chunk-3"
    # Four candidates: first scores 1.0, last 0.25.
    assert first.rerank_score == 1.0
    assert result.hits[-1].rerank_score == 0.25
    # The retrieval score is kept, and `score` follows the new order.
    assert first.retrieval_score == 7.0
    assert first.score == 1.0


def test_the_top_positions_carry_their_reasons() -> None:
    result = rerank(candidates(), completion(parsed=ranking(2, 1, 3, 4)))
    assert result.trace.reasons[0] == ("chunk-1", "reason 2")


def test_a_response_that_does_not_validate_keeps_retrieval_order() -> None:
    result = rerank(candidates(), completion(text="I cannot rank these.", parsed=None))
    assert not result.trace.applied
    assert result.trace.error is not None
    assert [hit.chunk_id for hit in result.hits] == [f"chunk-{n}" for n in range(4)]
    # No rerank score is written, which is how a reader tells a fallback from a
    # ranking that happened to agree with retrieval.
    assert all(hit.rerank_score is None for hit in result.hits)
    assert [hit.retrieval_score for hit in result.hits] == [10.0, 9.0, 8.0, 7.0]


def test_a_ranking_that_repeats_a_candidate_falls_back() -> None:
    result = rerank(candidates(), completion(parsed=ranking(1, 1, 2, 3)))
    assert result.trace.error == "ranking repeats a candidate"
    assert [hit.chunk_id for hit in result.hits] == [f"chunk-{n}" for n in range(4)]


def test_a_ranking_that_drops_a_candidate_falls_back() -> None:
    result = rerank(candidates(), completion(parsed=ranking(1, 2, 3)))
    assert result.trace.error == "ranking covers 3 of 4 candidates"


def test_a_ranking_that_invents_a_candidate_falls_back() -> None:
    result = rerank(candidates(), completion(parsed=ranking(1, 2, 3, 9)))
    assert result.trace.error is not None
    assert "not offered: [9]" in result.trace.error


def test_a_failed_call_keeps_retrieval_order_rather_than_raising() -> None:
    def explode(_messages: list[Message]) -> Completion:
        raise RuntimeError("429 Rate limit exceeded")

    result = rerank(candidates(), explode)
    assert not result.trace.applied
    assert result.trace.error is not None
    assert "429" in result.trace.error
    assert len(result.hits) == 4


def test_a_single_candidate_costs_no_call() -> None:
    llm = FakeLLM([])
    reranker = ListwiseReranker(RetrievalConfig(rerank=True, rerank_model=MODEL), llm)
    result = asyncio.run(reranker.rerank("anything?", candidates(1)))
    assert llm.requests == []
    assert not result.trace.applied
    assert result.hits[0].retrieval_score == 10.0


def test_only_the_configured_number_of_candidates_reaches_the_model() -> None:
    result = rerank(
        candidates(6), completion(parsed=ranking(3, 2, 1)), rerank_candidates=3, top_k=3
    )
    assert result.trace.candidates == 3
    # The three the model read come back reordered, the other three follow in
    # retrieval order: reranking a prefix must not narrow the result set.
    assert [hit.chunk_id for hit in result.hits] == [
        "chunk-2",
        "chunk-1",
        "chunk-0",
        "chunk-3",
        "chunk-4",
        "chunk-5",
    ]
    assert [hit.rerank_score is None for hit in result.hits] == [False] * 3 + [True] * 3
    # One descending scale over the whole list, so nothing behind outranks anything
    # in front of it.
    scores = [hit.score for hit in result.hits]
    assert scores == sorted(scores, reverse=True)


def test_the_usage_and_cost_of_the_call_are_recorded() -> None:
    result = rerank(
        candidates(), completion(parsed=ranking(1, 2, 3, 4), prompt_tokens=4000, cost_usd=0.0008)
    )
    assert result.trace.usage.prompt_tokens == 4000
    assert result.trace.cost_usd == 0.0008
    assert result.trace.model == MODEL


def test_a_candidate_renders_as_its_citation_heading_and_opening() -> None:
    rendered = render_candidates(candidates(2))
    assert rendered.startswith("[1] ")
    assert "#anchor-0 | Function calling > Section 0" in rendered
    assert "[2] " in rendered


def test_a_long_candidate_is_cut_to_the_token_budget_and_says_so() -> None:
    long_text = "tool calling " * 400
    cut = truncate_tokens(long_text, CANDIDATE_TOKEN_BUDGET)
    assert cut.endswith("[...]")
    assert len(cut) < len(long_text)
    assert truncate_tokens("short enough", CANDIDATE_TOKEN_BUDGET) == "short enough"


def test_the_prompt_carries_the_question_and_every_candidate() -> None:
    llm = FakeLLM([completion(parsed=ranking(1, 2, 3, 4))])
    reranker = ListwiseReranker(RetrievalConfig(rerank=True, rerank_model=MODEL), llm)
    asyncio.run(reranker.rerank("how do I call a tool?", candidates()))
    sent = llm.requests[0]
    assert sent["purpose"] == "rerank"
    assert sent["response_schema"] is Ranking
    user = sent["messages"][1]["content"]
    assert "how do I call a tool?" in user
    assert user.count("] https://") == 4
