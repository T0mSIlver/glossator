"""The reranker's call is part of what an answer costs and of what its trace shows."""

import asyncio

import pytest

from glossator.answer import search_loop, single_pass
from glossator.answer.config import AnswerConfig
from glossator.answer.generation import GeneratedAnswer, GeneratedCitation
from glossator.answer.llm import TokenUsage
from glossator.retrieval.reranker import RerankTrace
from tests.answer.conftest import FakeIndex, FakeLLM, completion, invocation, make_hit

TOOLS_TEXT = "Tools are declared as JSON objects with a name and parameters."
STREAM_TEXT = "Set stream to true to receive the response as server-sent events."

# The fresh-clone run's numbers: a rerank call dearer than the generation it fed.
RERANK = RerankTrace(
    model="mistral-small-2603",
    candidates=20,
    applied=True,
    usage=TokenUsage(prompt_tokens=5000, completion_tokens=300),
    cost_usd=0.000761,
)


def grounded(quote: str) -> GeneratedAnswer:
    return GeneratedAnswer(
        answer_markdown="You declare them as JSON [1].",
        citations=[GeneratedCitation(n=1, quote=quote)],
    )


def test_single_pass_bills_the_rerank_call(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    engine.rerank = RERANK
    llm = FakeLLM([completion(parsed=grounded("declared as JSON objects"), cost_usd=0.000623)])

    answer = asyncio.run(
        single_pass.answer("How do I declare a tool?", engine=engine, llm=llm, config=config)
    )

    assert answer.cost_usd == pytest.approx(0.000761 + 0.000623)
    assert answer.usage.prompt_tokens == 5000 + 100
    assert answer.usage.completion_tokens == 300 + 20
    reranks = [event for event in answer.trace.events if event.kind == "rerank"]
    assert [event.name for event in reranks] == ["mistral-small-2603"]
    assert reranks[0].arguments["cost_usd"] == pytest.approx(0.000761)
    kinds = [event.kind for event in answer.trace.events]
    assert kinds == ["rerank", "retrieval", "assembly"]
    assert "3 steps" in answer.trace.summary()


def test_every_search_of_the_loop_bills_its_rerank_call(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)], [make_hit("b", STREAM_TEXT)]])
    engine.rerank = RERANK
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("search", query="streaming")]),
            completion(text="done"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    answer = asyncio.run(
        search_loop.answer("How do I declare a tool?", engine=engine, llm=llm, config=config)
    )

    # Seed search and one tool search: two rerank calls on top of three completions.
    assert answer.cost_usd == pytest.approx(2 * 0.000761 + 3 * 0.001)
    assert sum(event.kind == "rerank" for event in answer.trace.events) == 2


def test_a_rerank_that_made_no_call_costs_nothing(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    engine.rerank = RerankTrace(model="mistral-small-2603", candidates=1, applied=False)
    llm = FakeLLM([completion(parsed=grounded("declared as JSON objects"))])

    answer = asyncio.run(
        single_pass.answer("How do I declare a tool?", engine=engine, llm=llm, config=config)
    )

    assert answer.cost_usd == pytest.approx(0.001)
    assert all(event.kind != "rerank" for event in answer.trace.events)
