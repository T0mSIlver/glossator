"""The three strategies, driven end to end against a fake index and a fake model."""

import asyncio
import json
from pathlib import Path

import pytest

from glossator.answer import outline, search_loop, single_pass
from glossator.answer.citations import Answer
from glossator.answer.config import AnswerConfig
from glossator.answer.generation import GeneratedAnswer, GeneratedCitation
from glossator.answer.llm import Message
from glossator.answer.outline import PagePick, load_outline, render_outline
from glossator.answer.service import STRATEGIES, ask
from tests.answer.conftest import (
    PAGE,
    FakeIndex,
    FakeLLM,
    completion,
    invocation,
    make_hit,
)

TOOLS_TEXT = "Tools are declared as JSON objects with a name and parameters."
STREAM_TEXT = "Set stream to true to receive the response as server-sent events."
OTHER_PAGE = "https://docs.mistral.ai/capabilities/streaming"


def grounded(quote: str, *, n: int = 1, insufficient: bool = False) -> GeneratedAnswer:
    return GeneratedAnswer(
        answer_markdown=f"You declare them as JSON [{n}].",
        citations=[GeneratedCitation(n=n, quote=quote)],
        insufficient_evidence=insufficient,
    )


def test_single_pass_retrieves_once_and_verifies_the_citation(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([completion(parsed=grounded("declared as JSON objects"))])

    answer = asyncio.run(
        single_pass.answer("How do I declare a tool?", engine=engine, llm=llm, config=config)
    )

    assert engine.queries == [("How do I declare a tool?", config.top_k, frozenset())]
    assert answer.strategy == "single_pass"
    assert [citation.chunk_id for citation in answer.citations] == ["a"]
    assert answer.citations[0].verified
    assert not answer.insufficient_evidence
    assert answer.usage.prompt_tokens == 100
    assert answer.cost_usd == pytest.approx(0.001)
    assert answer.trace.sources[0].citation_url.endswith("#tools")


def test_the_grounded_prompt_shows_the_numbered_context(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([completion(parsed=grounded("declared as JSON objects"))])

    asyncio.run(
        single_pass.answer("How do I declare a tool?", engine=engine, llm=llm, config=config)
    )

    request = llm.requests[0]
    assert request["response_schema"] is GeneratedAnswer
    assert "[1] " in request["messages"][1]["content"]
    assert TOOLS_TEXT in request["messages"][1]["content"]


def test_an_unverifiable_quote_makes_the_answer_insufficient(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([completion(parsed=grounded("declared as YAML documents"))])

    answer = asyncio.run(
        single_pass.answer("How do I declare a tool?", engine=engine, llm=llm, config=config)
    )

    assert answer.citations == []
    assert answer.insufficient_evidence
    assert len(answer.trace.unverified_citations) == 1
    assert "[1]" not in answer.answer_markdown
    assert answer.trace.unverified_citations[0].n == 1


def test_a_stray_prose_marker_is_removed_and_kept_in_the_trace(config: AnswerConfig) -> None:
    generated = GeneratedAnswer(
        answer_markdown="Use `messages[3]` as shown [1]. Stray [3].",
        citations=[GeneratedCitation(n=1, quote="declared as JSON objects")],
    )
    answer = asyncio.run(
        single_pass.answer(
            "How?",
            engine=FakeIndex([[make_hit("a", TOOLS_TEXT)]]),
            llm=FakeLLM([completion(parsed=generated)]),
            config=config,
        )
    )

    assert answer.answer_markdown == "Use `messages[3]` as shown [1]. Stray ."
    assert answer.trace.unmatched_markers == [3]


def test_refusal_markers_without_citations_are_removed(config: AnswerConfig) -> None:
    generated = GeneratedAnswer(
        answer_markdown="The documentation does not say [1][2][3].",
        insufficient_evidence=True,
    )
    answer = asyncio.run(
        single_pass.answer(
            "Unknown?",
            engine=FakeIndex([[make_hit("a", TOOLS_TEXT)]]),
            llm=FakeLLM([completion(parsed=generated)]),
            config=config,
        )
    )

    assert answer.answer_markdown == "The documentation does not say ."
    assert answer.trace.unmatched_markers == [1, 2, 3]


def test_a_model_that_declares_insufficient_evidence_is_believed(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([completion(parsed=grounded("declared as JSON objects", insufficient=True))])

    answer = asyncio.run(single_pass.answer("Unrelated?", engine=engine, llm=llm, config=config))

    assert answer.insufficient_evidence
    assert answer.citations[0].verified


def test_retrieval_returning_nothing_answers_without_a_generation(config: AnswerConfig) -> None:
    engine = FakeIndex([[]])
    llm = FakeLLM([])

    answer = asyncio.run(single_pass.answer("Anything?", engine=engine, llm=llm, config=config))

    assert answer.insufficient_evidence
    assert llm.requests == []
    assert answer.trace.sources == []


def test_an_answer_that_never_parses_is_returned_uncited(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([completion(text="Sorry, prose instead of JSON.", parsed=None)])

    answer = asyncio.run(
        single_pass.answer("How do I declare a tool?", engine=engine, llm=llm, config=config)
    )

    assert answer.answer_markdown == "Sorry, prose instead of JSON."
    assert answer.insufficient_evidence
    assert [event.name for event in answer.trace.events][-1] == "unparsed"


def test_search_loop_runs_a_tool_round_and_then_answers(config: AnswerConfig) -> None:
    seed = make_hit("a", TOOLS_TEXT)
    found = make_hit("b", STREAM_TEXT, source_id=OTHER_PAGE, anchor="stream")
    engine = FakeIndex([[seed], [found]])
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("search", query="how to stream a response")]),
            completion(text="I have enough."),
            completion(
                parsed=GeneratedAnswer(
                    answer_markdown="Declare tools [1] and stream them [2].",
                    citations=[
                        GeneratedCitation(n=1, quote="declared as JSON objects"),
                        GeneratedCitation(n=2, quote="server-sent events"),
                    ],
                )
            ),
        ]
    )

    answer = asyncio.run(
        search_loop.answer("How do I stream tool calls?", engine=engine, llm=llm, config=config)
    )

    assert [query for query, _, _ in engine.queries] == [
        "How do I stream tool calls?",
        "how to stream a response",
    ]
    # Chunks already collected are excluded from the model's own searches.
    assert engine.queries[1][2] == frozenset({"a"})
    assert {citation.n for citation in answer.citations} == {1, 2}
    assert [event.name for event in answer.trace.events] == [
        "search",
        "search",
        "stop",
        "context",
    ]
    assert answer.trace.rounds == 2


def test_the_loop_replies_to_every_tool_call_it_was_given(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)], [make_hit("b", STREAM_TEXT)]])
    search = invocation("search", query="streaming")
    llm = FakeLLM(
        [
            completion(tool_calls=[search]),
            completion(text="done"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    second_round: list[Message] = llm.requests[1]["messages"]
    assistant = second_round[-2]
    tool_reply = second_round[-1]
    assert assistant["role"] == "assistant"
    assert [call["id"] for call in assistant["tool_calls"]] == [search.id]
    assert tool_reply["role"] == "tool"
    assert tool_reply["tool_call_id"] == search.id


def test_the_loop_stops_at_the_round_cap(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)], [], []])
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("search", query="one")]),
            completion(tool_calls=[invocation("search", query="two")]),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    answer = asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    assert answer.trace.rounds == config.round_cap
    assert [event.name for event in answer.trace.events][-2] == "round_cap"


def test_the_loop_opens_and_greps_a_page_it_already_found(config: AnswerConfig) -> None:
    seed = make_hit("a", TOOLS_TEXT, start=0, end=60)
    neighbour = make_hit("a2", STREAM_TEXT, start=60, end=120)
    engine = FakeIndex([[seed]], pages={PAGE: [seed, neighbour]})
    llm = FakeLLM(
        [
            completion(
                tool_calls=[
                    invocation("open", chunk_id="a", window=1),
                    invocation("grep", source_id=PAGE, pattern="server-sent"),
                ]
            ),
            completion(text="enough"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    answer = asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    assert ("around", 1) in engine.page(PAGE).calls
    assert ("grep", "server-sent") in engine.page(PAGE).calls
    tool_events = [event for event in answer.trace.events if event.kind == "tool"]
    assert [event.name for event in tool_events] == ["open", "grep"]
    # The neighbour arrived through `open`; `grep` returned nothing new.
    assert tool_events[0].result_ids == ["a2"]
    assert tool_events[1].result_ids == []


def test_a_tool_call_with_bad_arguments_is_reported_back_not_raised(
    config: AnswerConfig,
) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("open", chunk_id="nope")]),
            completion(text="giving up"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    answer = asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    tool_event = next(event for event in answer.trace.events if event.kind == "tool")
    assert tool_event.note is not None
    assert "No chunk with chunk_id='nope'" in tool_event.note
    assert "exactly as an earlier result printed it" in tool_event.note
    assert answer.citations[0].verified


def test_outline_picks_pages_and_reads_them(tmp_path: Path, config: AnswerConfig) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "url": PAGE,
                    "path": "capabilities/function-calling.md",
                    "title": "Function calling",
                    "kind": "doc",
                },
                {
                    "url": OTHER_PAGE,
                    "path": "capabilities/streaming.md",
                    "title": "Streaming",
                    "kind": "doc",
                },
                {
                    "url": "https://docs.mistral.ai/api/chat",
                    "path": "api/chat.md",
                    "title": "Chat endpoint",
                    "kind": "api",
                },
            ]
        )
    )
    engine = FakeIndex(pages={PAGE: [make_hit("a", TOOLS_TEXT)]})
    llm = FakeLLM(
        [
            completion(parsed=PagePick(page_numbers=[1], reason="it is the tools page")),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    answer = asyncio.run(
        outline.answer(
            "How do I declare a tool?",
            engine=engine,
            llm=llm,
            config=config,
            manifest_path=manifest,
        )
    )

    picker_prompt = llm.requests[0]["messages"][1]["content"]
    assert "1. capabilities > Function calling" in picker_prompt
    # API reference pages are not offered to the picker.
    assert "Chat endpoint" not in picker_prompt
    assert ("read", (None, None)) in engine.page(PAGE).calls
    assert answer.citations[0].verified
    assert answer.trace.events[0].note == "it is the tools page"


@pytest.mark.parametrize(
    "question",
    [
        "What does POST /v1/chat/completions return?",
        "Which parameter belongs in the request body?",
        "How do I call chat_completion_v1_chat_completions_post?",
    ],
)
def test_outline_offers_api_pages_for_api_questions(
    tmp_path: Path, config: AnswerConfig, question: str
) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "url": PAGE,
                    "path": "capabilities/function-calling.md",
                    "title": "Tools",
                    "kind": "doc",
                },
                {
                    "url": "https://docs.mistral.ai/api/endpoint/chat",
                    "path": "api/endpoint/chat.md",
                    "title": "Chat API",
                    "kind": "api",
                },
            ]
        )
    )
    engine = FakeIndex(pages={PAGE: []})
    llm = FakeLLM([completion(parsed=PagePick(page_numbers=[], reason=""))])

    asyncio.run(
        outline.answer(
            question,
            engine=engine,
            llm=llm,
            config=config,
            manifest_path=manifest,
        )
    )

    picker_prompt = llm.requests[0]["messages"][1]["content"]
    assert "Chat API [endpoint: chat]" in picker_prompt


def test_outline_ignores_page_numbers_that_do_not_exist(
    tmp_path: Path, config: AnswerConfig
) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([{"url": PAGE, "path": "a.md", "title": "A", "kind": "doc"}]))
    engine = FakeIndex(pages={PAGE: [make_hit("a", TOOLS_TEXT)]})
    llm = FakeLLM(
        [
            completion(parsed=PagePick(page_numbers=[99, 1, 1], reason="")),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    answer = asyncio.run(
        outline.answer("How?", engine=engine, llm=llm, config=config, manifest_path=manifest)
    )

    assert answer.trace.events[0].result_ids == [PAGE]


def test_outline_caps_the_pages_it_reads(tmp_path: Path, config: AnswerConfig) -> None:
    pages = [
        {
            "url": f"https://docs.mistral.ai/p{i}",
            "path": f"p{i}.md",
            "title": f"P{i}",
            "kind": "doc",
        }
        for i in range(5)
    ]
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(pages))
    engine = FakeIndex(pages={page["url"]: [] for page in pages})
    llm = FakeLLM([completion(parsed=PagePick(page_numbers=[1, 2, 3, 4, 5], reason=""))])

    answer = asyncio.run(
        outline.answer("How?", engine=engine, llm=llm, config=config, manifest_path=manifest)
    )

    assert len(answer.trace.events[0].result_ids) == config.page_cap
    assert answer.insufficient_evidence


def test_the_real_outline_covers_the_documentation() -> None:
    entries = load_outline()

    assert len(entries) > 300
    assert all(entry.url.startswith("https://docs.mistral.ai") for entry in entries)
    assert render_outline(entries).splitlines()[0].startswith("1. ")


def test_ask_dispatches_to_the_named_strategy(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([completion(parsed=grounded("declared as JSON objects"))])

    answer = asyncio.run(ask("How?", strategy="single_pass", engine=engine, llm=llm, config=config))

    assert isinstance(answer, Answer)
    assert answer.strategy == "single_pass"
    assert set(STRATEGIES) == {"single_pass", "search_loop", "outline"}


def test_ask_refuses_an_unknown_strategy() -> None:
    with pytest.raises(ValueError, match="unknown strategy"):
        asyncio.run(ask("How?", strategy="telepathy"))


def test_a_frugal_top_k_from_the_model_is_widened_to_the_configured_depth(
    config: AnswerConfig,
) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)], []])
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("search", query="one", top_k=1)]),
            completion(text="done"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    assert engine.queries[1][1] == config.tool_top_k


def test_an_extravagant_top_k_from_the_model_is_capped(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)], []])
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("search", query="one", top_k=500)]),
            completion(text="done"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    assert engine.queries[1][1] == config.max_tool_top_k
