"""The blind consumer runner on a fake harness: no models, no sockets."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from glossator.eval import consumer as consumer_module
from glossator.eval.consumer import (
    ConsumerRecord,
    ConsumerSpec,
    HarnessTokens,
    ToolCallRecord,
    aggregate,
    build_question_set,
    cite_verdicts,
    collect_defects,
    corpus_page_urls,
    extract_links,
    is_quota_error,
    judged_citations,
    load_records,
    opencode_command,
    parse_opencode_events,
    parse_opencode_tokens,
    prompt_for,
    record_metrics,
    refused,
    render_samples,
)
from glossator.eval.datasets import EvalQuestion, GoldSource, QuestionSource, QuestionType


def _question(question_id: str, type_: QuestionType = QuestionType.SINGLE_PAGE) -> EvalQuestion:
    gold = (
        [] if type_ == QuestionType.UNANSWERABLE else [GoldSource(url="https://docs.mistral.ai/a")]
    )
    return EvalQuestion(
        id=question_id,
        question="What is the limit?",
        type=type_,
        gold=gold,
        reference_answer="The limit is 128.",
        language="en",
        source=QuestionSource.GENERATED,
    )


def _record(**overrides: object) -> ConsumerRecord:
    base: dict[str, object] = {
        "consumer": "opencode-muse-minimal",
        "arm": "A1",
        "question_id": "mined-001",
        "question_type": "single_page",
        "question": "What is the limit?",
        "reference_answer": "The limit is 128.",
        "gold_urls": ["https://docs.mistral.ai/a"],
        "answer_text": "The limit is 128 [1].\n\n[1] https://docs.mistral.ai/a#limit",
        "links": ["https://docs.mistral.ai/a#limit"],
    }
    base.update(overrides)
    return ConsumerRecord.model_validate(base)


def test_question_set_is_fixed_and_keeps_unanswerables() -> None:
    first = build_question_set()
    second = build_question_set()
    assert [q.id for q in first] == [q.id for q in second]
    assert len(first) == 60
    mined_ids = [q.id for q in first if q.id.startswith("mined-")]
    assert len(mined_ids) == 40
    mined_unanswerable = [
        q for q in first if q.id.startswith("mined-") and q.type == QuestionType.UNANSWERABLE
    ]
    assert len(mined_unanswerable) == 9


def test_prompt_hides_the_evaluation() -> None:
    prompt = prompt_for(_question("mined-001"))
    assert "What is the limit?" in prompt
    # "cite" is part of the fixed instruction sentence itself; everything else
    # that would name the setup must stay out.
    for word in ("evaluat", "benchmark", "glossator", "MCP"):
        assert word not in prompt


def test_parse_opencode_events() -> None:
    lines = [
        json.dumps({"type": "step_start", "part": {}}),
        json.dumps(
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "glossator_search",
                    "state": {
                        "status": "completed",
                        "input": {"query": "limit", "top_k": 5},
                        "output": "query: limit\nhits: 1/20",
                    },
                },
            }
        ),
        json.dumps(
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "glossator_cite",
                    "state": {
                        "status": "completed",
                        "input": {"draft": "x [1]", "quotes": []},
                        "output": "[1] verified: https://docs.mistral.ai/a#x\n",
                    },
                },
            }
        ),
        json.dumps({"type": "text", "part": {"type": "text", "text": "The limit is 128 [1]."}}),
        json.dumps(
            {
                "type": "step_finish",
                "part": {"tokens": {"input": 10, "output": 5, "reasoning": 2}, "cost": 0},
            }
        ),
    ]
    answer, calls = parse_opencode_events(lines)
    assert answer == "The limit is 128 [1]."
    assert [call.name for call in calls] == ["glossator_search", "glossator_cite"]
    assert calls[0].arguments == {"query": "limit", "top_k": "5"}
    tokens, cost = parse_opencode_tokens(lines)
    assert (tokens.input_tokens, tokens.output_tokens, tokens.reasoning_tokens) == (10, 5, 2)
    assert cost == 0
    assert cite_verdicts(calls) == (1, 0)


def test_parse_skips_garbage_lines() -> None:
    answer, calls = parse_opencode_events(["not json", "", "[]"])
    assert answer == "" and calls == []


def test_tool_error_extraction() -> None:
    lines = [
        json.dumps(
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "glossator_search",
                    "state": {
                        "status": "completed",
                        "input": {"query": "x"},
                        "output": "error: E_BAD_PARAM\nunknown parameter foo\nnext: ...",
                    },
                },
            }
        )
    ]
    _answer, calls = parse_opencode_events(lines)
    assert calls[0].error == "glossator_search: error: E_BAD_PARAM"


def test_judged_citations_keep_verified_quotes_only() -> None:
    quotes = json.dumps(
        [
            {"n": 1, "quote": "The limit is 128.", "chunk_id": "abc"},
            {"n": 2, "quote": "Something else.", "chunk_id": "def"},
        ]
    )
    record = _record(
        tool_calls=[
            ToolCallRecord(
                name="glossator_cite",
                arguments={"quotes": quotes, "__verdicts": '{"1": true, "2": false}'},
                output_chars=10,
            )
        ]
    )
    citations = judged_citations(record)
    assert len(citations) == 1
    assert citations[0].quote == "The limit is 128."
    assert citations[0].source_text == "The limit is 128."


def test_extract_links_and_refusal() -> None:
    assert extract_links(
        "See [1] https://docs.mistral.ai/a#x, and https://docs.mistral.ai/a#x."
    ) == ["https://docs.mistral.ai/a#x"]
    assert refused("The documentation does not cover local token counting.")
    assert not refused("The limit is 128.")


def test_is_quota_error() -> None:
    assert is_quota_error("Error: 429 rate limit reached")
    assert not is_quota_error("harness produced no answer text")


def test_record_metrics_against_corpus() -> None:
    corpus = {"https://docs.mistral.ai/a", "https://docs.mistral.ai/b"}
    metrics = record_metrics(_record(), corpus)
    assert metrics["links_resolve"] == 1.0
    assert metrics["links_on_gold"] == 1.0
    assert metrics["mcp_called"] == 0.0
    assert metrics["refusal_correct"] == 1.0
    off = _record(answer_text="I recall it is 7.", links=["https://example.com/x"])
    metrics = record_metrics(off, corpus)
    assert metrics["links_resolve"] == 0.0


def test_aggregate_cells() -> None:
    records = [
        _record(question_id="mined-001", arm="A0"),
        _record(question_id="mined-002", arm="A1", mcp_called=True),
    ]
    metrics = aggregate(records, {"https://docs.mistral.ai/a"})
    assert metrics["records"] == 2
    assert metrics["cells"]["opencode-muse-minimal / A0"]["n"] == 1
    assert metrics["cells"]["opencode-muse-minimal / A1"]["mcp_called"] == 1.0


def test_defects_list_typed_errors() -> None:
    record = _record(
        tool_calls=[
            ToolCallRecord(
                name="glossator_search",
                arguments={},
                output_chars=5,
                error="glossator_search: error: E_BAD_PARAM",
            )
        ]
    )
    defects = collect_defects([record])
    assert len(defects) == 1
    assert defects[0]["severity"] == "extra-calls"
    assert collect_defects([_record()]) == []


def test_samples_render_arms_side_by_side() -> None:
    records = [
        _record(question_id="mined-001", arm="A0", answer_text="From memory: 128."),
        _record(question_id="mined-001", arm="A1", answer_text="Cited: 128 [1]."),
    ]
    text = render_samples(records, consumer="opencode-muse-minimal")
    assert "### A0" in text and "### A1" in text and "From memory" in text


def test_opencode_command_names_lowest_variant() -> None:
    spec = ConsumerSpec(
        name="opencode-muse-minimal",
        harness="opencode",
        model="opencode/muse-spark-1.3-contributor-free",
        variant="minimal",
    )
    command = opencode_command(spec, "prompt", Path("/tmp/scratch/q"))
    assert "--variant" in command and "minimal" in command
    assert "--dir" in command and "--format" in command and "json" in command


def test_corpus_page_urls_empty_without_manifest(tmp_path: Path) -> None:
    assert corpus_page_urls(tmp_path) == set()


class _FakeHarness:
    """Stand-in for collect_opencode: canned events, no subprocess."""

    def __init__(self, events: list[str]) -> None:
        self.events = events

    def __call__(self, *args: object, **kwargs: object) -> consumer_module.CollectedAnswer:
        del args, kwargs
        answer, calls = parse_opencode_events(self.events)
        tokens, cost = parse_opencode_tokens(self.events)
        return consumer_module.CollectedAnswer(
            answer_text=answer,
            tool_calls=calls,
            tokens=tokens,
            cost_usd=cost,
            wall_seconds=0.5,
            transcript="/tmp/fake/events.jsonl",
            error=None,
        )


def test_collection_is_resumable(tmp_path: Path, monkeypatch: object) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    existing = _record()
    (run_dir / "records.jsonl").write_text(existing.model_dump_json() + "\n")
    assert {r.key for r in load_records(run_dir / "records.jsonl")} == {
        ("opencode-muse-minimal", "A1", "mined-001")
    }
    events = [json.dumps({"type": "text", "part": {"type": "text", "text": "hi"}})]
    fake = _FakeHarness(events)
    collected = fake()
    assert collected.answer_text == "hi"
    assert collected.tokens == HarnessTokens()


def test_run_collection_skips_recorded_cells(tmp_path: Path) -> None:
    async def go() -> list[ConsumerRecord]:
        run_dir = tmp_path / "run"
        run_dir.mkdir()
        # Both cells already recorded, so nothing runs: no harness needed.
        (run_dir / "records.jsonl").write_text(
            _record(question_id="mined-001").model_dump_json()
            + "\n"
            + _record(question_id="mined-002").model_dump_json()
            + "\n"
        )
        spec = ConsumerSpec(
            name="opencode-muse-minimal",
            harness="opencode",
            model="opencode/muse-spark-1.3-contributor-free",
            variant="minimal",
        )
        return await consumer_module.run_collection(
            [_question("mined-001"), _question("mined-002")],
            [spec],
            ["A1"],
            run_dir=run_dir,
            run_name="test",
            scratch_root=tmp_path / "scratch",
            mcp_urls={},
            token="",
            timeout_s=1.0,
        )

    assert asyncio.run(go()) == []
