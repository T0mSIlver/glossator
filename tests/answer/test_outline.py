"""Outline: what happens when the picker fails, and what a page read is capped at."""

import asyncio
import json
from pathlib import Path

import pytest

from glossator.answer import outline, single_pass
from glossator.answer.config import AnswerConfig
from glossator.answer.outline import PagePick
from glossator.answer.service import ask
from tests.answer.conftest import PAGE, Collector, FakeIndex, FakeLLM, completion, make_hit
from tests.answer.test_strategies import TOOLS_TEXT, grounded


def one_page_manifest(tmp_path: Path) -> Path:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([{"url": PAGE, "path": "a.md", "title": "A", "kind": "doc"}]))
    return manifest


def test_a_picker_that_never_parses_does_not_read_as_a_refusal(
    tmp_path: Path, config: AnswerConfig
) -> None:
    """A broken picker is a bug, not "the documentation does not cover this"."""
    engine = FakeIndex(pages={PAGE: [make_hit("a", TOOLS_TEXT)]})
    llm = FakeLLM([completion(text="I could not answer in JSON.", parsed=None)])

    answer = asyncio.run(
        outline.answer(
            "How?", engine=engine, llm=llm, config=config, manifest_path=one_page_manifest(tmp_path)
        )
    )

    assert [event.name for event in answer.trace.events][0] == "unparsed"
    assert "the step that picks pages" in answer.answer_markdown
    assert "index returned nothing" not in answer.answer_markdown
    assert engine.page(PAGE).calls == []
    assert answer.insufficient_evidence


def test_a_page_read_stops_at_the_configured_cap(tmp_path: Path, config: AnswerConfig) -> None:
    page = [
        make_hit(f"c{i}", f"Chunk {i} declared as JSON objects.", start=i * 40, end=i * 40 + 39)
        for i in range(60)
    ]
    engine = FakeIndex(pages={PAGE: page})
    llm = FakeLLM(
        [
            completion(parsed=PagePick(page_numbers=[1], reason="")),
            completion(parsed=grounded("declared as JSON objects")),
        ]
    )

    answer = asyncio.run(
        outline.answer(
            "How?", engine=engine, llm=llm, config=config, manifest_path=one_page_manifest(tmp_path)
        )
    )

    read_event = next(event for event in answer.trace.events if event.name == "read")
    assert len(read_event.result_ids) == config.page_read_top_k


def test_ask_refuses_a_recorder_it_would_have_to_ignore(config: AnswerConfig) -> None:
    """An injected llm owns its recorder; dropping this one silently loses the run."""
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT)]])
    llm = FakeLLM([completion(parsed=grounded("declared as JSON objects"))])

    with pytest.raises(ValueError, match="either llm or recorder"):
        asyncio.run(ask("How?", engine=engine, llm=llm, config=config, recorder=Collector()))


def test_the_trace_carries_the_context_the_model_saw_and_the_hit_scores(
    config: AnswerConfig,
) -> None:
    engine = FakeIndex([[make_hit("a", TOOLS_TEXT, score=12.5)]])
    llm = FakeLLM([completion(parsed=grounded("declared as JSON objects"))])

    answer = asyncio.run(single_pass.answer("How?", engine=engine, llm=llm, config=config))

    assert TOOLS_TEXT in answer.trace.context_text
    assert answer.trace.sources[0].score == 12.5
