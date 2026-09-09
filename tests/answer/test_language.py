"""Detection, the English rendering, and what each half of the run is shown."""

import asyncio

import pytest

from glossator.answer import search_loop, single_pass
from glossator.answer.config import AnswerConfig
from glossator.answer.generation import GeneratedAnswer, GeneratedCitation
from glossator.answer.language import (
    ENGLISH,
    FRENCH,
    UNKNOWN,
    EnglishRendering,
    detect_language,
    render_for_retrieval,
)
from glossator.answer.llm import Completion
from tests.answer.conftest import FakeIndex, FakeLLM, completion, invocation, make_hit

TOOLS_TEXT = "Tools are declared as JSON objects with a name and parameters."
FRENCH_QUESTION = "Comment déclarer un outil dans l'API ?"
ENGLISH_RENDERING = "How do I declare a tool in the API?"

ENGLISH_QUESTIONS = [
    "How do I declare a tool?",
    "What models support function calling?",
    "Set safe_prompt on a chat completion request",
    "Which endpoint returns the list of models?",
    "temperature",
]

FRENCH_QUESTIONS = [
    "Comment déclarer un outil ?",
    "Quels modèles supportent le function calling ?",
    "Pourquoi ma requête renvoie-t-elle une erreur 429 ?",
    "Je veux activer le mode streaming, que dois-je faire ?",
    # Typed without its accents, and still French.
    "Comment definir la temperature dans une requete ?",
]

MIXED_QUESTIONS = [
    ("Comment activer safe_prompt sur /v1/chat/completions ?", FRENCH),
    ("Quelle est la valeur par défaut de max_tokens pour mistral-medium-2604 ?", FRENCH),
    ("How do I set safe_prompt on /v1/chat/completions?", ENGLISH),
    ("Does mistral-embed-2312 support the encoding_format parameter?", ENGLISH),
]


def grounded(quote: str = "declared as JSON objects") -> GeneratedAnswer:
    return GeneratedAnswer(
        answer_markdown="Vous les déclarez en JSON [1].",
        citations=[GeneratedCitation(n=1, quote=quote)],
    )


def rendered(text: str = ENGLISH_RENDERING) -> Completion:
    return completion(parsed=EnglishRendering(english_question=text))


@pytest.mark.parametrize("question", ENGLISH_QUESTIONS)
def test_english_questions_are_detected_as_english(question: str) -> None:
    assert detect_language(question) == ENGLISH


@pytest.mark.parametrize("question", FRENCH_QUESTIONS)
def test_french_questions_are_detected_as_french(question: str) -> None:
    assert detect_language(question) == FRENCH


@pytest.mark.parametrize(("question", "expected"), MIXED_QUESTIONS)
def test_identifiers_do_not_decide_the_language(question: str, expected: str) -> None:
    assert detect_language(question) == expected


def test_a_question_with_no_words_at_all_is_treated_as_english() -> None:
    assert detect_language("") == ENGLISH
    assert detect_language("safe_prompt?") == ENGLISH


def test_another_script_is_not_english_even_though_it_is_not_identified() -> None:
    assert detect_language("如何声明一个工具？") == UNKNOWN


def test_an_english_question_is_rendered_without_a_model_call(config: AnswerConfig) -> None:
    llm = FakeLLM([])

    query = asyncio.run(render_for_retrieval("How do I declare a tool?", llm=llm, config=config))

    assert llm.requests == []
    assert query.text == "How do I declare a tool?"
    assert query.language == ENGLISH
    assert not query.translated
    assert query.completion is None


def test_a_french_question_is_rendered_in_english_by_one_call(config: AnswerConfig) -> None:
    llm = FakeLLM([rendered()])

    query = asyncio.run(render_for_retrieval(FRENCH_QUESTION, llm=llm, config=config))

    assert len(llm.requests) == 1
    request = llm.requests[0]
    assert request["response_schema"] is EnglishRendering
    assert request["purpose"] == "retrieval_query"
    assert FRENCH_QUESTION in request["messages"][1]["content"]
    assert query.language == FRENCH
    assert query.text == ENGLISH_RENDERING
    assert query.question == FRENCH_QUESTION
    assert query.translated


def test_the_rendering_call_is_deterministic_and_short(config: AnswerConfig) -> None:
    llm = FakeLLM([rendered()])

    asyncio.run(render_for_retrieval(FRENCH_QUESTION, llm=llm, config=config))

    assert llm.requests[0]["temperature"] == 0.0
    assert llm.requests[0]["max_tokens"] == config.render_max_tokens


def test_a_rendering_that_does_not_parse_falls_back_to_the_question(config: AnswerConfig) -> None:
    llm = FakeLLM([completion(text="désolé", parsed=None)])

    query = asyncio.run(render_for_retrieval(FRENCH_QUESTION, llm=llm, config=config))

    assert query.text == FRENCH_QUESTION
    assert query.language == FRENCH
    assert not query.translated
    assert query.note is not None
    # The failed call is still charged to the run.
    assert query.completion is not None


def test_the_switch_turns_the_rendering_off(config: AnswerConfig) -> None:
    settings = config.model_copy(update={"translate_for_retrieval": False})
    llm = FakeLLM([])

    query = asyncio.run(render_for_retrieval(FRENCH_QUESTION, llm=llm, config=settings))

    assert llm.requests == []
    assert query.text == FRENCH_QUESTION
    assert query.language == FRENCH


def test_single_pass_retrieves_in_english_and_generates_from_the_original(
    config: AnswerConfig,
) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([rendered(), completion(parsed=grounded())])

    answer = asyncio.run(single_pass.answer(FRENCH_QUESTION, engine=engine, llm=llm, config=config))

    assert [query for query, _, _ in engine.queries] == [ENGLISH_RENDERING]
    generation = llm.requests[1]["messages"][1]["content"]
    assert FRENCH_QUESTION in generation
    assert ENGLISH_RENDERING not in generation
    assert answer.question == FRENCH_QUESTION
    assert answer.citations[0].verified


def test_the_trace_records_the_language_the_query_and_the_call(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([rendered(), completion(parsed=grounded())])

    answer = asyncio.run(single_pass.answer(FRENCH_QUESTION, engine=engine, llm=llm, config=config))

    assert answer.trace.question_language == FRENCH
    assert answer.trace.retrieval_query == ENGLISH_RENDERING
    step = answer.trace.events[0]
    assert (step.kind, step.name) == ("query", "retrieval_query")
    assert step.arguments == {"language": FRENCH, "query": ENGLISH_RENDERING}
    # Both calls are charged to the answer.
    assert answer.usage.prompt_tokens == 200


def test_an_english_run_records_the_question_as_its_retrieval_query(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([completion(parsed=grounded())])

    answer = asyncio.run(
        single_pass.answer("How do I declare a tool?", engine=engine, llm=llm, config=config)
    )

    assert answer.trace.question_language == ENGLISH
    assert answer.trace.retrieval_query == "How do I declare a tool?"
    assert [event.kind for event in answer.trace.events] == ["retrieval", "assembly"]


def test_switching_the_rendering_off_retrieves_in_french(config: AnswerConfig) -> None:
    settings = config.model_copy(update={"translate_for_retrieval": False})
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([completion(parsed=grounded())])

    answer = asyncio.run(
        single_pass.answer(FRENCH_QUESTION, engine=engine, llm=llm, config=settings)
    )

    assert [query for query, _, _ in engine.queries] == [FRENCH_QUESTION]
    assert answer.trace.question_language == FRENCH
    assert answer.trace.retrieval_query == FRENCH_QUESTION


def test_the_loop_searches_from_the_english_rendering(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)], [make_hit("b", "Streaming uses SSE.")]])
    llm = FakeLLM(
        [
            rendered(),
            completion(tool_calls=[invocation("search", query="how to declare a tool")]),
            completion(text="I have enough."),
            completion(parsed=grounded()),
        ]
    )

    answer = asyncio.run(search_loop.answer(FRENCH_QUESTION, engine=engine, llm=llm, config=config))

    assert [query for query, _, _ in engine.queries][0] == ENGLISH_RENDERING
    assert ENGLISH_RENDERING in llm.requests[1]["messages"][1]["content"]
    assert FRENCH_QUESTION not in llm.requests[1]["messages"][1]["content"]
    assert FRENCH_QUESTION in llm.requests[3]["messages"][1]["content"]
    assert answer.trace.retrieval_query == ENGLISH_RENDERING
