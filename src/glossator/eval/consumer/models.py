"""The consumer evaluation's records: one cell's answer, tool calls and harness tokens."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from glossator.eval.answer_eval.models import JudgeRecord


class HarnessTokens(BaseModel):
    model_config = ConfigDict(frozen=True)

    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens


class ToolCallRecord(BaseModel):
    """One harness tool call, extracted from the event stream."""

    model_config = ConfigDict(frozen=True)

    name: str
    arguments: dict[str, str] = {}
    output_chars: int = 0
    error: str | None = None
    notes: list[str] = []
    """The `note:` lines the tool printed. A clamp is announced there and never
    as an error (D-029), so counting clamps out of `error` counted none."""


class ConsumerRecord(BaseModel):
    """One (consumer, arm, question) cell: the answer and everything behind it."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    consumer: str
    arm: str
    question_id: str
    question_type: str
    question: str
    reference_answer: str
    gold_urls: list[str] = []
    answer_text: str = ""
    wall_seconds: float = 0.0
    tokens: HarnessTokens = HarnessTokens()
    harness_cost_usd: float = 0.0
    tool_calls: list[ToolCallRecord] = []
    mcp_called: bool = False
    cite_called: bool = False
    links: list[str] = []
    transcript: str = ""
    error: str | None = None
    judge: JudgeRecord | None = None

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.consumer, self.arm, self.question_id)


def load_records(path: Path) -> list[ConsumerRecord]:
    if not path.is_file():
        return []
    records: list[ConsumerRecord] = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(ConsumerRecord.model_validate_json(line))
    return records


def append_record(path: Path, record: ConsumerRecord) -> None:
    with path.open("a") as handle:
        handle.write(record.model_dump_json() + "\n")
