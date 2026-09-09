"""The retrieval rewrite: when it runs, what it costs, what the trace says."""

import asyncio

import pytest

from glossator.answer import search_loop, single_pass
from glossator.answer.config import AnswerConfig
from glossator.answer.generation import GeneratedAnswer, GeneratedCitation
from glossator.answer.language import (
    ENGLISH,
    FRENCH,
    ORIGINAL,
    RENDERING,
    REWRITE,
    EnglishRendering,
    RetrievalQuery,
    RetrievalRewriting,
    rewrite_for_retrieval,
)
from glossator.answer.llm import Completion
from tests.answer.conftest import FakeIndex, FakeLLM, completion, invocation, make_hit

TOOLS_TEXT = "Tools are declared as JSON objects with a name and parameters."
KEYWORD_QUESTION = "tool json name params declare"
REWRITTEN = "function calling tool definition parameters schema"
FRENCH_QUESTION = "Comment declarer un outil avec des parametres ?"
ENGLISH_RENDERING = "How do I declare a tool with parameters?"


@pytest.fixture
def rewriting_config(config: AnswerConfig) -> AnswerConfig:
    return config.model_copy(update={"rewrite_for_retrieval": True})


def grounded(quote: str = "declared as JSON objects") -> GeneratedAnswer:
    return GeneratedAnswer(
        answer_markdown="You declare them as JSON [1].",
        citations=[GeneratedCitation(n=1, quote=quote)],
    )


def rewritten(text: str = REWRITTEN) -> Completion:
    return completion(parsed=RetrievalRewriting(retrieval_query=text))


def asked(question: str = KEYWORD_QUESTION) -> RetrievalQuery:
    return RetrievalQuery(question=question, language=ENGLISH, text=question)


def test_the_rewrite_is_off_unless_it_is_asked_for(config: AnswerConfig) -> None:
    llm = FakeLLM([])

    query = asyncio.run(rewrite_for_retrieval(asked(), llm=llm, config=config))

    assert llm.requests == []
    assert query.text == KEYWORD_QUESTION
    assert query.source == ORIGINAL


def test_the_rewrite_rewords_the_query(rewriting_config: AnswerConfig) -> None:
    llm = FakeLLM([rewritten()])

    query = asyncio.run(rewrite_for_retrieval(asked(), llm=llm, config=rewriting_config))

    assert len(llm.requests) == 1
    request = llm.requests[0]
    assert request["response_schema"] is RetrievalRewriting
    assert request["purpose"] == "retrieval_rewrite"
    assert KEYWORD_QUESTION in request["messages"][1]["content"]
    assert query.text == REWRITTEN
    assert query.source == REWRITE
    assert query.question == KEYWORD_QUESTION
    assert query.completion is not None


def test_the_rewrite_call_is_deterministic_and_short(rewriting_config: AnswerConfig) -> None:
    llm = FakeLLM([rewritten()])

    asyncio.run(rewrite_for_retrieval(asked(), llm=llm, config=rewriting_config))

    assert llm.requests[0]["temperature"] == 0.0
    assert llm.requests[0]["max_tokens"] == rewriting_config.rewrite_max_tokens


@pytest.mark.parametrize("bad", ["   ", ""])
def test_an_empty_rewrite_keeps_the_query_it_was_given(
    rewriting_config: AnswerConfig, bad: str
) -> None:
    llm = FakeLLM([completion(parsed=RetrievalRewriting(retrieval_query=bad))])

    query = asyncio.run(rewrite_for_retrieval(asked(), llm=llm, config=rewriting_config))

    assert query.text == KEYWORD_QUESTION
    assert query.source == ORIGINAL
    assert query.note is not None


def test_a_rewrite_that_does_not_parse_keeps_the_query_and_is_still_charged(
    rewriting_config: AnswerConfig,
) -> None:
    llm = FakeLLM([completion(text="sorry", parsed=None)])

    query = asyncio.run(rewrite_for_retrieval(asked(), llm=llm, config=rewriting_config))

    assert query.text == KEYWORD_QUESTION
    assert query.source == ORIGINAL
    assert query.note is not None
    assert query.completion is not None


def test_the_rewrite_runs_over_the_english_rendering(rewriting_config: AnswerConfig) -> None:
    llm = FakeLLM(
        [
            completion(parsed=EnglishRendering(english_question=ENGLISH_RENDERING)),
            rewritten(),
            completion(parsed=grounded()),
        ]
    )
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])

    answer = asyncio.run(
        single_pass.answer(FRENCH_QUESTION, engine=engine, llm=llm, config=rewriting_config)
    )

    # The rewrite is shown the rendering, not the French question it came from.
    assert ENGLISH_RENDERING in llm.requests[1]["messages"][1]["content"]
    assert FRENCH_QUESTION not in llm.requests[1]["messages"][1]["content"]
    assert [query for query, _, _ in engine.queries] == [REWRITTEN]
    assert answer.trace.question_language == FRENCH
    assert answer.trace.retrieval_query == REWRITTEN
    assert answer.trace.retrieval_query_source == REWRITE


def test_single_pass_searches_the_rewrite_and_answers_the_question(
    rewriting_config: AnswerConfig,
) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([rewritten(), completion(parsed=grounded())])

    answer = asyncio.run(
        single_pass.answer(KEYWORD_QUESTION, engine=engine, llm=llm, config=rewriting_config)
    )

    assert [query for query, _, _ in engine.queries] == [REWRITTEN]
    generation = llm.requests[1]["messages"][1]["content"]
    assert KEYWORD_QUESTION in generation
    assert REWRITTEN not in generation
    assert answer.question == KEYWORD_QUESTION
    assert answer.citations[0].verified


def test_the_trace_records_the_rewrite_as_a_step_and_charges_its_call(
    rewriting_config: AnswerConfig,
) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([rewritten(), completion(parsed=grounded())])

    answer = asyncio.run(
        single_pass.answer(KEYWORD_QUESTION, engine=engine, llm=llm, config=rewriting_config)
    )

    step = answer.trace.events[0]
    assert (step.kind, step.name) == ("query", "retrieval_rewrite")
    assert step.arguments == {"language": ENGLISH, "query": REWRITTEN}
    assert answer.trace.retrieval_query_source == REWRITE
    # Both calls are charged to the answer.
    assert answer.usage.prompt_tokens == 200


def test_a_run_without_the_rewrite_reports_the_question_as_its_own_query(
    config: AnswerConfig,
) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([completion(parsed=grounded())])

    answer = asyncio.run(
        single_pass.answer(KEYWORD_QUESTION, engine=engine, llm=llm, config=config)
    )

    assert answer.trace.retrieval_query == KEYWORD_QUESTION
    assert answer.trace.retrieval_query_source == ORIGINAL
    assert [event.kind for event in answer.trace.events] == ["retrieval", "assembly"]


def test_a_failed_rewrite_leaves_the_rendering_as_the_query(
    rewriting_config: AnswerConfig,
) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM(
        [
            completion(parsed=EnglishRendering(english_question=ENGLISH_RENDERING)),
            completion(text="{", parsed=None),
            completion(parsed=grounded()),
        ]
    )

    answer = asyncio.run(
        single_pass.answer(FRENCH_QUESTION, engine=engine, llm=llm, config=rewriting_config)
    )

    assert [query for query, _, _ in engine.queries] == [ENGLISH_RENDERING]
    assert answer.trace.retrieval_query == ENGLISH_RENDERING
    assert answer.trace.retrieval_query_source == RENDERING
    assert answer.trace.events[1].note is not None


def test_the_loop_searches_from_the_rewrite(rewriting_config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)], [make_hit("b", "Streaming uses SSE.")]])
    llm = FakeLLM(
        [
            rewritten(),
            completion(tool_calls=[invocation("search", query="how a tool is declared")]),
            completion(text="I have enough."),
            completion(parsed=grounded()),
        ]
    )

    answer = asyncio.run(
        search_loop.answer(KEYWORD_QUESTION, engine=engine, llm=llm, config=rewriting_config)
    )

    assert [query for query, _, _ in engine.queries][0] == REWRITTEN
    assert REWRITTEN in llm.requests[1]["messages"][1]["content"]
    assert KEYWORD_QUESTION in llm.requests[3]["messages"][1]["content"]
    assert answer.trace.retrieval_query_source == REWRITE
