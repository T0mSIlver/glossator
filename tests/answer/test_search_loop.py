"""The search loop's tool surface: errors, clamps, empty results, the round cap.

These are the paths a weaker generator actually takes -- a half-remembered url, a
frugal `top_k`, one search too many -- and each one has to come back as a message
the model can act on rather than as an exception that ends the answer.
"""

import asyncio

from mistralai.search.toolkit.search.errors import SourceNotFoundError

from glossator.answer import search_loop
from glossator.answer.config import AnswerConfig
from tests.answer.conftest import (
    PAGE,
    FakeIndex,
    FakeLLM,
    completion,
    invocation,
    make_hit,
)
from tests.answer.test_strategies import STREAM_TEXT, TOOLS_TEXT, grounded


def test_a_page_the_index_does_not_hold_ends_the_tool_call_not_the_answer(
    config: AnswerConfig,
) -> None:
    """The real index raises for an unknown source_id; the loop has to survive it."""
    invented = "https://docs.mistral.ai/invented"
    engine = FakeIndex(
        [[make_hit("a", TOOLS_TEXT)]],
        pages={invented: []},
        raises=SourceNotFoundError(invented),
    )
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("read", source_id=invented)]),
            completion(text="giving up"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    answer = asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    tool_event = next(event for event in answer.trace.events if event.kind == "tool")
    assert tool_event.note is not None
    assert "read failed: Source not found" in tool_event.note
    assert "exactly as an earlier result printed it" in tool_event.note
    assert answer.citations[0].verified


def test_a_grep_on_a_page_the_index_does_not_hold_is_reported_back(config: AnswerConfig) -> None:
    engine = FakeIndex(
        [[make_hit("a", TOOLS_TEXT)]],
        pages={PAGE: []},
        raises=SourceNotFoundError(PAGE),
    )
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("grep", source_id=PAGE, pattern="tools")]),
            completion(text="done"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    answer = asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    tool_event = next(event for event in answer.trace.events if event.kind == "tool")
    assert tool_event.note is not None and "grep failed" in tool_event.note


def test_the_loop_reads_an_offset_range_of_a_page(config: AnswerConfig) -> None:
    early = make_hit("a", TOOLS_TEXT, start=0, end=60)
    late = make_hit("b", STREAM_TEXT, start=60, end=120)
    engine = FakeIndex([[early]], pages={PAGE: [early, late]})
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("read", source_id=PAGE, start=60, end=120)]),
            completion(text="enough"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    answer = asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    assert ("read", (60, 120)) in engine.page(PAGE).calls
    tool_event = next(event for event in answer.trace.events if event.kind == "tool")
    assert tool_event.result_ids == ["b"]


def test_reading_an_empty_range_says_which_kind_of_empty(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT, start=0, end=60)]], pages={PAGE: []})
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("read", source_id=PAGE, start=900, end=999)]),
            completion(text="done"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    reply = llm.requests[1]["messages"][-1]["content"]
    assert "No chunks between offsets 900 and 999" in reply
    assert "next:" in reply


def test_a_search_with_no_results_is_not_reported_as_all_seen(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)], []])
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("search", query="nothing like this exists")]),
            completion(text="done"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    assert "No results for that query" in llm.requests[1]["messages"][-1]["content"]


def test_a_search_returning_only_seen_chunks_says_so(config: AnswerConfig) -> None:
    seed = make_hit("a", TOOLS_TEXT)
    # The fake honours exclude_ids, so ask it for a page whose chunks are seen.
    engine = FakeIndex([[seed]], pages={PAGE: [seed]})
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("open", chunk_id="a")]),
            completion(text="done"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    reply = llm.requests[1]["messages"][-1]["content"]
    assert "No new chunks: all 1 results were already collected" in reply


def test_the_open_window_is_clamped_and_the_model_is_told(config: AnswerConfig) -> None:
    seed = make_hit("a", TOOLS_TEXT, start=0, end=60)
    engine = FakeIndex([[seed]], pages={PAGE: [seed]})
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("open", chunk_id="a", window=500)]),
            completion(text="enough"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    assert ("around", config.max_open_window) in engine.page(PAGE).calls
    reply = llm.requests[1]["messages"][-1]["content"]
    assert f"note: clamped server-side: window=500 → {config.max_open_window}" in reply


def test_a_clamped_top_k_is_reported_in_the_tool_result(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)], [make_hit("b", STREAM_TEXT)]])
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("search", query="one", top_k=1)]),
            completion(text="done"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    reply = llm.requests[1]["messages"][-1]["content"]
    assert f"note: clamped server-side: top_k=1 → {config.tool_top_k}" in reply


def test_a_top_k_inside_the_range_is_used_without_a_note(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)], [make_hit("b", STREAM_TEXT)]])
    llm = FakeLLM(
        [
            completion(tool_calls=[invocation("search", query="one", top_k=6)]),
            completion(text="done"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    assert engine.queries[1][1] == 6
    assert "clamped" not in llm.requests[1]["messages"][-1]["content"]


def test_only_searches_count_against_the_per_round_cap(config: AnswerConfig) -> None:
    seed = make_hit("a", TOOLS_TEXT, start=0, end=60)
    engine = FakeIndex([[seed], [], []], pages={PAGE: [seed]})
    llm = FakeLLM(
        [
            completion(
                tool_calls=[
                    invocation("search", query="one"),
                    invocation("search", query="two"),
                    invocation("open", chunk_id="a"),
                ]
            ),
            completion(text="done"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    answer = asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    # The fixture allows two searches per round; the `open` is not a search.
    assert [event.name for event in answer.trace.events if event.kind == "tool"] == [
        "search",
        "search",
        "open",
    ]


def test_a_search_over_the_cap_is_answered_with_the_reason_it_was_dropped(
    config: AnswerConfig,
) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)], [], []])
    llm = FakeLLM(
        [
            completion(
                tool_calls=[
                    invocation("search", query="one"),
                    invocation("search", query="two"),
                    invocation("search", query="three"),
                ]
            ),
            completion(text="done"),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    answer = asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    replies = [m for m in llm.requests[1]["messages"] if m["role"] == "tool"]
    # Every call the assistant made is answered, including the one that was dropped.
    assert len(replies) == 3
    assert "not run: this round already used its" in replies[-1]["content"]
    dropped_event = [event for event in answer.trace.events if event.kind == "tool"][-1]
    assert dropped_event.result_ids == []


def test_the_seed_hits_are_shown_in_the_first_user_message(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM(
        [
            completion(text="I have enough."),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    asyncio.run(
        search_loop.answer("How do I declare a tool?", engine=engine, llm=llm, config=config)
    )

    seed_message = llm.requests[0]["messages"][1]["content"]
    assert "chunk_id=a" in seed_message
    assert f"source_id={PAGE}" in seed_message
    assert "Tools are declared as JSON objects" in seed_message


def test_a_long_chunk_is_cut_at_the_configured_preview_size(config: AnswerConfig) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT * 12)]])
    llm = FakeLLM([completion(text="enough"), completion(parsed=grounded("enough said"))])

    asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=config))

    seed_message = llm.requests[0]["messages"][1]["content"]
    assert "..." in seed_message
    assert TOOLS_TEXT * 12 not in seed_message


def test_the_full_preview_configuration_cuts_nothing(config: AnswerConfig) -> None:
    """`tool_result_chars=null` is the grid's explicit "full" size (D-035c): the
    model sees the whole collapsed chunk, with no number to keep in step with
    the longest chunk in the index."""
    full = config.model_copy(update={"tool_result_chars": None})
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT * 12)]])
    llm = FakeLLM([completion(text="enough"), completion(parsed=grounded("enough said"))])

    asyncio.run(search_loop.answer("How?", engine=engine, llm=llm, config=full))

    seed_message = llm.requests[0]["messages"][1]["content"]
    assert "..." not in seed_message
    assert TOOLS_TEXT * 12 in seed_message
