"""The work proxy offline: parsing, instructions assembly, resume."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from glossator.eval.consumer import ConsumerRecord, is_server_tool
from glossator.eval.datasets import EvalQuestion, GoldSource, QuestionSource, QuestionType
from glossator.eval.work_proxy import (
    ParsedConversation,
    agent_instructions,
    custom_instructions_block,
    parse_conversation_response,
    record_for,
    resolve_run_directory,
    select_pending,
    skill_body,
    strip_connector_prefix,
)

FIXTURES = Path(__file__).parent / "fixtures" / "work_proxy"
"""The first real smoke response, key-free, as the SDK dumped it, plus the
same response with the message content in chunk form (a reasoning model)."""


def _question(question_id: str) -> EvalQuestion:
    return EvalQuestion(
        id=question_id,
        question="What is the rate limit?",
        type=QuestionType.SINGLE_PAGE,
        gold=[GoldSource(url="https://docs.mistral.ai/limits")],
        reference_answer="1 request per second.",
        language="en",
        source=QuestionSource.GENERATED,
    )


def _load(name: str) -> dict[str, Any]:
    loaded = json.loads((FIXTURES / name).read_text())
    assert isinstance(loaded, dict)
    return loaded


def _record(parsed: ParsedConversation, model: str = "mistral-medium-3-5") -> ConsumerRecord:
    return record_for(
        _question("q"),
        parsed,
        consumer="work-proxy-test",
        model=model,
        wall_seconds=1.0,
        transcript="transcripts/q.md",
        error=None,
    )


def test_parse_recorded_response() -> None:
    fixture = _load("conversation-response.json")
    parsed = parse_conversation_response(fixture)
    record = _record(parsed)

    assert parsed.answer_text.startswith("Here are the query parameters")
    assert record.answer_text == parsed.answer_text
    usage = fixture["usage"]
    assert parsed.usage.input_tokens == usage["prompt_tokens"]
    assert parsed.usage.output_tokens == usage["completion_tokens"]
    assert record.tokens.total == usage["prompt_tokens"] + usage["completion_tokens"]
    assert record.harness_cost_usd > 0.0


def test_tool_calls_parsed_with_arguments() -> None:
    parsed = parse_conversation_response(_load("conversation-response.json"))
    record = _record(parsed)

    names = [call.name for call in record.tool_calls]
    assert names[0] == "mistral_docs_search"
    assert "mistral_docs_ca30" not in names[0]
    assert names.count("mistral_docs_read_page") == 2
    assert all(is_server_tool(name) for name in names)
    assert record.mcp_called

    search = record.tool_calls[0]
    assert search.arguments["q"].startswith("Admin API audit logs")
    assert search.arguments["max_hits"] == "5"
    assert search.output_chars > 0
    assert search.error is None


def test_thinking_kept_out_of_answer() -> None:
    parsed = parse_conversation_response(_load("conversation-response-chunks.json"))
    record = _record(parsed)

    assert parsed.thinking == ["I should search the documentation first."]
    assert parsed.answer_text == (
        "The Admin API audit logs endpoint filters with actor_type, event_type and"
        " target_type.\nDefault limit is 20, sorted descending."
    )
    assert "search the documentation first" not in record.answer_text


def test_chunked_tool_notes() -> None:
    fixture = _load("conversation-response-chunks.json")
    fixture["outputs"][0]["info"] = {
        "result": [{"type": "text", "text": "note: clamped server-side\n[1] hit text"}]
    }
    record = _record(parse_conversation_response(fixture))

    assert record.tool_calls[0].notes == ["note: clamped server-side"]


def test_unpriced_model_costs_zero() -> None:
    parsed = parse_conversation_response(_load("conversation-response.json"))
    record = _record(parsed, model="mistral-small-latest")
    assert record.harness_cost_usd == 0.0


def test_instructions_assembled_from_skill_files() -> None:
    body = skill_body()
    assert body.startswith("# Answer from the Mistral documentation")
    assert "name: mistral-docs" not in body
    assert "---" not in body

    block = custom_instructions_block()
    assert block.startswith("When I ask about Mistral products")
    assert block.endswith("say so.")

    assert agent_instructions() == f"{body}\n\n{block}"


def test_connector_prefix_stripped() -> None:
    assert strip_connector_prefix("mistral_docs_search") == "mistral_docs_search"
    assert strip_connector_prefix("mistral_docs_ca30_mistral_docs_search") == (
        "mistral_docs_search"
    )
    assert strip_connector_prefix("mistral_docs__mistral_docs_read_page") == (
        "mistral_docs_read_page"
    )
    assert strip_connector_prefix("mistral-docs-cite") == "mistral-docs-cite"
    assert strip_connector_prefix("web_search") == "web_search"


def test_resume_skips_done_ids(tmp_path: Path) -> None:
    questions = [_question("q1"), _question("q2"), _question("q3")]
    assert select_pending(questions, set()) == questions
    assert select_pending(questions, {"q1", "q3"}) == [questions[1]]

    run_dir = resolve_run_directory("resume-check", root=tmp_path)
    again = resolve_run_directory("resume-check", root=tmp_path)
    assert again == run_dir
    assert run_dir.name.endswith("resume-check")
