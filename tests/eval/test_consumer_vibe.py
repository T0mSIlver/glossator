"""The Vibe CLI consumer: its per-cell home and its event stream."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

from glossator.eval.consumer.consumers import consumer_spec
from glossator.eval.consumer.tools import is_server_tool
from glossator.eval.consumer.vibe import parse_vibe_events, write_vibe_home
from glossator.eval.consumer.vibe_arms import ANSWER_RULES, VIBE_ARMS

STREAMS = Path(__file__).parent.parent / "fixtures" / "consumer-streams"


def test_parse_vibe_events_reads_the_answer_and_the_server_calls() -> None:
    lines = (STREAMS / "vibe-vd-history.jsonl").read_text().splitlines()
    answer, calls = parse_vibe_events(lines)
    assert answer.startswith("The Agentic Search page was added between")
    assert len(calls) == 7
    assert all(is_server_tool(call.name) for call in calls)
    assert {call.name for call in calls} == {
        "mistral_docs_mistral_docs_history",
        "mistral_docs_mistral_docs_search",
    }


def test_an_unknown_tool_the_harness_refused_is_an_error_row() -> None:
    event = {
        "type": "effect",
        "detail": {"toolName": "read_file", "input": None},
        "state": {"status": "failed", "outputText": ""},
    }
    _answer, calls = parse_vibe_events([json.dumps(event)])
    assert calls[0].name == "read_file"
    assert calls[0].error is not None


def test_narration_before_more_tool_calls_is_not_the_answer() -> None:
    events = [
        {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Let me look."}],
        },
        {
            "type": "effect",
            "detail": {"toolName": "bash", "input": {"command": "ls"}},
            "state": {"status": "completed", "outputText": "docs\n"},
        },
        {"type": "message", "role": "assistant", "content": [{"type": "text", "text": "Final."}]},
    ]
    answer, calls = parse_vibe_events([json.dumps(event) for event in events])
    assert answer == "Final."
    assert calls[0].arguments == {"command": "ls"}


@pytest.mark.parametrize("arm_name", sorted(VIBE_ARMS))
def test_every_arm_gets_the_same_rules_and_only_its_own_tools(
    tmp_path: Path, arm_name: str
) -> None:
    arm = VIBE_ARMS[arm_name]
    home = tmp_path / arm_name
    write_vibe_home(
        home,
        consumer_spec("vibe-medium35-high"),
        arm,
        mcp_url="https://example.invalid/mcp" if arm.mcp else None,
        token_env="GLOSSATOR_MCP_TOKEN",
    )
    config = tomllib.loads((home / "config.toml").read_text())
    expected = (["bash"] if arm.shell else []) + (["mistral_docs_*"] if arm.mcp else [])
    assert config["enabled_tools"] == expected
    assert config["experiments"] == {"enable": False}
    assert bool(config.get("mcp_servers")) == arm.mcp
    prompt = (home / "prompts" / "glossator-arm.md").read_text()
    assert prompt.startswith(ANSWER_RULES)
    assert "https://docs.mistral.ai/studio/agents/introduction#which-models-are-supported" in prompt
    if arm.mcp:
        assert config["mcp_servers"][0]["auth"] == {
            "type": "static",
            "api_key_env": "GLOSSATOR_MCP_TOKEN",
        }
