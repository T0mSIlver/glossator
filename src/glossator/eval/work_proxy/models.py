"""The proxy run's configuration and a conversation response reduced to its parts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from glossator.eval.consumer.models import HarnessTokens
from glossator.eval.datasets import dataset_hash

QUESTION_TIMEOUT_S = 300.0

ReasoningEffortChoice = Literal["high", "none"]
"""What the Work demo runs: reasoning on (high) or off (none). The Conversations
API accepts the same values its ``CompletionArgs`` lists."""


@dataclass(frozen=True, slots=True)
class ParsedToolExecution:
    """One ``tool.execution`` output entry, kept verbatim enough for a transcript."""

    name: str
    arguments: str
    result: str
    failed: bool


@dataclass(slots=True)
class ParsedConversation:
    """One conversation response, reduced to what a record and a transcript hold."""

    answer_text: str = ""
    thinking: list[str] = field(default_factory=list)
    calls: list[ParsedToolExecution] = field(default_factory=list)
    usage: HarnessTokens = HarnessTokens()
    raw_usage: dict[str, Any] = field(default_factory=dict)


def consumer_name(model: str, reasoning_effort: str) -> str:
    return f"work-proxy-{model}-{reasoning_effort}"


@dataclass(slots=True)
class WorkProxyConfig:
    name: str
    model: str
    reasoning_effort: ReasoningEffortChoice
    connector: str
    dataset: Path
    run_dir: Path
    timeout_s: float

    def as_dict(
        self,
        *,
        agent_id: str | None,
        question_count: int,
        connector_tools: list[str] | None = None,
        instructions: str | None = None,
    ) -> dict[str, Any]:
        consumer = consumer_name(self.model, self.reasoning_effort)
        return {
            "kind": "work_proxy_eval",
            "instructions": instructions,
            "name": self.name,
            "run_dir": str(self.run_dir),
            "consumer": consumer,
            "model": self.model,
            "reasoning_effort": self.reasoning_effort,
            "connector": self.connector,
            "connector_tools": connector_tools,
            "agent_id": agent_id,
            "dataset": str(self.dataset),
            "dataset_hash": dataset_hash(self.dataset),
            "question_count": question_count,
            # The consumer `score` README renderer reads these; on a single
            # arbitrary dataset every question counts as mined.
            "mined_count": question_count,
            "fresh_count": 0,
            "consumers": [consumer],
            "timeout_s": self.timeout_s,
            "judge_model": None,
        }
