"""The blind consumer runner on a fake harness: no models, no sockets."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from glossator.eval import consumer as consumer_module
from glossator.eval.consumer import (
    ConsumerRecord,
    ConsumerSpec,
    HarnessTokens,
    ToolCallRecord,
    aggregate,
    build_question_set,
    cite_verdicts,
    claude_command,
    claude_failure,
    codex_command,
    collect_defects,
    copy_transcript,
    corpus_page_urls,
    extract_links,
    is_quota_error,
    is_server_tool,
    is_verify_tool,
    judged_citations,
    load_records,
    opencode_command,
    parse_claude_events,
    parse_claude_tokens,
    parse_opencode_events,
    parse_opencode_tokens,
    prompt_for,
    record_metrics,
    refused,
    render_samples,
    write_claude_mcp_config,
)
from glossator.eval.datasets import EvalQuestion, GoldSource, QuestionSource, QuestionType

STREAMS = Path(__file__).parent.parent / "fixtures" / "consumer-streams"
"""Event streams recorded from real headless runs of each harness, trimmed."""


def _stream(name: str) -> list[str]:
    return (STREAMS / name).read_text().splitlines()


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


def test_a_smaller_question_set_is_a_prefix_of_the_larger_one() -> None:
    """A run on thirty questions is comparable with one on sixty: the smaller
    draw is the larger one's first rows, stratified all the way down."""
    thirty = build_question_set(20, 10)
    sixty = build_question_set()

    assert len(thirty) == 30
    mined = [q.id for q in sixty if q.id.startswith("mined-")]
    fresh = [q.id for q in sixty if not q.id.startswith("mined-")]
    assert [q.id for q in thirty if q.id.startswith("mined-")] == mined[:20]
    assert [q.id for q in thirty if not q.id.startswith("mined-")] == fresh[:10]


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
                        "input": {"query": "limit", "max_hits": 5},
                        "output": "query: limit\nResults: 1/20 kept/considered",
                    },
                },
            }
        ),
        json.dumps(
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "mcp__mistral-docs__mistral_docs_verify_quotes",
                    "state": {
                        "status": "completed",
                        "input": {"draft": "x [1]", "quotes": []},
                        "output": "verified: 1 of 1 quotes ([1])\n",
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
    assert [call.name for call in calls] == [
        "glossator_search",
        "mcp__mistral-docs__mistral_docs_verify_quotes",
    ]
    assert calls[0].arguments == {"query": "limit", "max_hits": "5"}
    tokens, cost = parse_opencode_tokens(lines)
    assert (tokens.input_tokens, tokens.output_tokens, tokens.reasoning_tokens) == (10, 5, 2)
    assert cost == 0
    assert cite_verdicts(calls) == (1, 0)


def test_tool_names_match_on_the_suffix_whatever_the_harness_prefixes() -> None:
    """Harnesses name the same tool their own way; a recorded run keeps reading."""
    assert is_server_tool("mcp__mistral-docs__mistral_docs_search")
    assert is_server_tool("mistral_docs_read_page")
    assert is_server_tool("glossator_search")
    assert not is_server_tool("webfetch")
    assert is_verify_tool("mcp__mistral-docs__mistral_docs_verify_quotes")
    assert is_verify_tool("glossator_cite")
    assert not is_verify_tool("mistral_docs_search")


def test_verdicts_are_read_from_the_old_per_quote_lines() -> None:
    """Runs recorded before the count line still count."""
    lines = [
        json.dumps(
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "glossator_cite",
                    "state": {
                        "status": "completed",
                        "input": {"draft": "x [1] y [2]", "quotes": []},
                        "output": (
                            "[1] verified: https://docs.mistral.ai/a#x\n"
                            "[2] NOT verified: quote is not in the cited source\n"
                        ),
                    },
                },
            }
        )
    ]
    _answer, calls = parse_opencode_events(lines)

    assert cite_verdicts(calls) == (1, 1)


def test_verdicts_are_read_from_the_count_line() -> None:
    lines = [
        json.dumps(
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "mcp__mistral-docs__mistral_docs_verify_quotes",
                    "state": {
                        "status": "completed",
                        "input": {"draft": "x [1] y [2] z [3]", "quotes": []},
                        "output": (
                            "[2] NOT verified: quote is not in the cited source — "
                            "mistral_docs_open_section(chunk_id=…) and copy the sentence\n"
                            "verified: 2 of 3 quotes ([1], [3])\n"
                        ),
                    },
                },
            }
        )
    ]
    _answer, calls = parse_opencode_events(lines)

    assert cite_verdicts(calls) == (2, 1)


def test_an_abandoned_opencode_tool_call_is_an_error_row() -> None:
    """A call the harness gave up on prints nothing, so the status is the only
    place its failure shows."""
    lines = [
        json.dumps(
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "glossator_search",
                    "state": {"status": "error", "input": {"query": "x"}},
                },
            }
        )
    ]

    _answer, calls = parse_opencode_events(lines)

    assert calls[0].error == "tool status: error"
    assert calls[0].notes == []


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


def test_an_announced_clamp_is_counted_as_a_clamp_not_an_error() -> None:
    """The server announces a clamp on a `note:` line, never on an `error:` one
    (D-029), so reading clamps out of the error field counted none of them."""
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
                        "output": (
                            'query: "x"\n'
                            "note: clamped server-side: top_k=500 → 50\n"
                            "hits: 5/40 kept/considered"
                        ),
                    },
                },
            }
        )
    ]

    _answer, calls = parse_opencode_events(lines)

    assert calls[0].error is None
    assert calls[0].notes == ["note: clamped server-side: top_k=500 → 50"]
    metrics = record_metrics(_record(tool_calls=calls), set())
    assert metrics["clamps"] == 1.0


def test_the_judge_ledger_keeps_usage_as_numbers(tmp_path: Path) -> None:
    """Token counts written as a Python repr cannot be summed, which is the
    whole point of the ledger (D-023b)."""
    from glossator.answer.llm import TokenUsage
    from glossator.eval.consumer import _CallsRecorder

    recorder = _CallsRecorder(tmp_path)
    recorder.record_call(
        model="glm-5.3",
        messages=[{"role": "user", "content": "hi"}],
        usage=TokenUsage(prompt_tokens=12, completion_tokens=3),
    )

    row = json.loads((tmp_path / "calls.jsonl").read_text().splitlines()[0])
    assert row["usage"] == {"prompt_tokens": 12, "completion_tokens": 3}
    assert row["messages"] == [{"role": "user", "content": "hi"}]
    assert row["timestamp"]


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
                name="mcp__mistral-docs__mistral_docs_verify_quotes",
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


def test_parse_claude_events() -> None:
    """A recorded claude run: the answer, the tool calls under the names claude
    gives MCP tools, and the quotes the server verified."""
    lines = _stream("claude-a1.jsonl")

    answer, calls = parse_claude_events(lines)

    assert answer == "Done."
    assert [call.name for call in calls] == [
        "ToolSearch",
        "mcp__mistral-docs__mistral_docs_search",
        "mcp__mistral-docs__mistral_docs_verify_quotes",
    ]
    assert calls[1].arguments["query"] == "Codestral 25.08 context length"
    # The tool's printed output is unwrapped from the {"result": ...} envelope,
    # so the note line and the verdict line are readable.
    assert calls[1].notes == [
        "note: index ranking only; rerank=true reorders with a model (about 5 s)"
    ]
    assert calls[1].output_chars > 0
    assert cite_verdicts(calls) == (1, 0)
    assert claude_failure(lines) is None
    record = _record(consumer="claude-sonnet-low", tool_calls=calls, answer_text=answer)
    assert record.mcp_called is False  # set by the runner, not by the parser
    assert any(is_server_tool(call.name) for call in calls)
    assert any(is_verify_tool(call.name) for call in calls)


def test_claude_tokens_count_cached_prompt_tokens() -> None:
    tokens, cost = parse_claude_tokens(_stream("claude-a1.jsonl"))

    assert tokens.input_tokens == 36 + 10349 + 80623
    assert tokens.output_tokens == 672
    assert tokens.reasoning_tokens == 310
    assert cost == 0.0332223


def test_a_rejected_claude_tool_call_is_an_error_row() -> None:
    """The server's typed error reaches the record through claude's own
    `is_error` result, so the defect list and the metrics see it."""
    _answer, calls = parse_claude_events(_stream("claude-bad-param.jsonl"))

    assert [call.name for call in calls] == ["mcp__mistral-docs__mistral_docs_search"]
    assert calls[0].error == "mcp__mistral-docs__mistral_docs_search: error: E_BAD_PARAM"
    metrics = record_metrics(_record(tool_calls=calls), set())
    assert metrics["bad_param_errors"] == 1.0
    assert collect_defects([_record(tool_calls=calls)])[0]["severity"] == "extra-calls"


def test_claude_command_and_config_declare_one_arm() -> None:
    spec = ConsumerSpec(name="claude-sonnet-low", harness="claude", model="sonnet", variant="low")
    command = claude_command(spec, "the prompt", Path("/tmp/scratch/q/mcp.json"))

    assert command[:3] == ["claude", "-p", "the prompt"]
    for flag in ("--effort", "low", "--strict-mcp-config", "--verbose"):
        assert flag in command
    assert command[command.index("--output-format") + 1] == "stream-json"
    assert command[command.index("--permission-mode") + 1] == "bypassPermissions"


def test_claude_mcp_config_is_written_per_arm(tmp_path: Path) -> None:
    with_server = json.loads(
        write_claude_mcp_config(tmp_path, "http://127.0.0.1:8111/mcp", "s3cret").read_text()
    )
    assert with_server["mcpServers"]["mistral-docs"]["type"] == "http"
    assert with_server["mcpServers"]["mistral-docs"]["headers"]["Authorization"] == "Bearer s3cret"

    without = json.loads(write_claude_mcp_config(tmp_path, None, "s3cret").read_text())
    assert without == {"mcpServers": {}}


def test_codex_command_names_the_verified_mcp_keys() -> None:
    spec = ConsumerSpec(
        name="codex-gpt-luna-low", harness="codex", model="gpt-5.6-luna", variant="low"
    )
    command = codex_command(spec, Path("/tmp/scratch/q/answer.md"), "http://127.0.0.1:8111/mcp")

    assert command[:5] == ["codex", "exec", "--skip-git-repo-check", "--ignore-user-config", "-m"]
    assert command[-1] == "-", "the prompt arrives on stdin"
    assert "mcp_servers.mistral-docs.url=http://127.0.0.1:8111/mcp" in command
    assert "mcp_servers.mistral-docs.bearer_token_env_var=GLOSSATOR_MCP_TOKEN" in command
    assert "model_reasoning_effort='\"low\"'" in command
    # No server at all in A0, and the token never travels on the command line.
    without = codex_command(spec, Path("/tmp/a.md"), None)
    assert not any("mcp_servers" in part for part in without)


def test_the_transcript_travels_with_the_run(tmp_path: Path) -> None:
    """A reviewer opens the conversation behind a row from the run directory
    itself, not from the consumer's scratch directory (D-023c)."""
    scratch = tmp_path / "scratch" / "events.jsonl"
    scratch.parent.mkdir(parents=True)
    scratch.write_text('{"type": "result"}\n')
    run_dir = tmp_path / "run"

    relative = copy_transcript(
        run_dir, scratch, consumer="claude-sonnet-low", arm="A1", question_id="mined-001"
    )

    assert relative == "transcripts/claude-sonnet-low/A1/mined-001.jsonl"
    assert (run_dir / relative).read_text() == '{"type": "result"}\n'
    assert (
        copy_transcript(run_dir, tmp_path / "gone.jsonl", consumer="c", arm="A0", question_id="q")
        == ""
    )


def test_a_second_consumer_joins_the_run_it_is_added_to() -> None:
    """Consumers run one command each, so the config has to describe every
    consumer the records hold, not the last command's."""
    first = {
        "consumers": ["claude-sonnet-low"],
        "consumer_models": {"claude-sonnet-low": "sonnet"},
        "arms": ["A0", "A1"],
        "questions": ["mined-001"],
        "judge_model": "zai:glm-5.3",
    }
    second = {
        "consumers": ["codex-gpt-luna-low"],
        "consumer_models": {"codex-gpt-luna-low": "gpt-5.6-luna"},
        "arms": ["A1", "A2"],
        "questions": ["mined-001"],
        "judge_model": None,
    }

    merged = consumer_module.merge_config(first, second)

    assert merged["consumers"] == ["claude-sonnet-low", "codex-gpt-luna-low"]
    assert merged["consumer_models"] == {
        "claude-sonnet-low": "sonnet",
        "codex-gpt-luna-low": "gpt-5.6-luna",
    }
    assert merged["arms"] == ["A0", "A1", "A2"]
    assert merged["judge_model"] == "zai:glm-5.3"
    assert consumer_module.merge_config({}, second) == second


def test_a_run_directory_refuses_a_different_question_set() -> None:
    with pytest.raises(SystemExit):
        consumer_module.merge_config({"questions": ["mined-001"]}, {"questions": ["mined-002"]})


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


def test_a_collection_run_directory_is_self_describing_from_the_start(
    tmp_path: Path,
) -> None:
    """Collecting, judging and scoring are three commands, so a run interrupted
    between them has to say what it is and what it still owes (D-023)."""
    from glossator.eval.consumer import _start_run_directory

    _start_run_directory(tmp_path)

    assert (tmp_path / "figures").is_dir()
    assert (tmp_path / "calls.jsonl").is_file()
    assert (tmp_path / "records.jsonl").is_file()
    readme = (tmp_path / "README.md").read_text()
    assert "no judge has run" in readme

    # A README a scoring pass already wrote is never overwritten by a resume.
    (tmp_path / "README.md").write_text("# scored\n")
    _start_run_directory(tmp_path)
    assert (tmp_path / "README.md").read_text() == "# scored\n"
