"""One question's consumer record and readable transcript."""

from __future__ import annotations

from glossator.eval.consumer.answers import extract_links
from glossator.eval.consumer.models import ConsumerRecord
from glossator.eval.consumer.tools import is_server_tool, is_verify_tool
from glossator.eval.datasets import EvalQuestion
from glossator.eval.pricing import estimate_usd
from glossator.eval.providers import TokenUsage
from glossator.eval.work_proxy.models import ParsedConversation
from glossator.eval.work_proxy.parsing import connector_call_count, tool_call_records


def record_for(
    question: EvalQuestion,
    parsed: ParsedConversation,
    *,
    consumer: str,
    model: str,
    wall_seconds: float,
    transcript: str,
    error: str | None,
) -> ConsumerRecord:
    """One consumer record for one question, priced with the eval price table."""
    calls = tool_call_records(parsed.calls)
    cost = estimate_usd(
        model,
        TokenUsage(
            prompt_tokens=parsed.usage.input_tokens,
            completion_tokens=parsed.usage.output_tokens,
        ),
    )
    return ConsumerRecord(
        consumer=consumer,
        arm="A1",
        question_id=question.id,
        question_type=question.type.value,
        question=question.question,
        reference_answer=question.reference_answer,
        gold_urls=[gold.url for gold in question.gold],
        answer_text=parsed.answer_text,
        wall_seconds=wall_seconds,
        tokens=parsed.usage,
        harness_cost_usd=cost or 0.0,
        tool_calls=calls,
        mcp_called=any(is_server_tool(call.name) for call in calls),
        cite_called=any(is_verify_tool(call.name) for call in calls),
        links=extract_links(parsed.answer_text),
        transcript=transcript,
        error=error,
    )


def render_transcript(question: EvalQuestion, parsed: ParsedConversation, error: str | None) -> str:
    calls_note = (
        f"{question.type.value}, {connector_call_count(parsed)} connector calls"
        if parsed.raw_usage
        else question.type.value
    )
    lines = [
        f"# {question.id} ({calls_note})",
        "",
        "## Question",
        "",
        question.question,
        "",
    ]
    if parsed.thinking:
        lines += ["## Thinking", "", "\n\n".join(parsed.thinking), ""]
    if parsed.calls:
        lines += ["## Tool calls", ""]
        for index, call in enumerate(parsed.calls, 1):
            lines += [f"### {index}. {call.name}", "", "```json", call.arguments, "```", ""]
            if call.result:
                lines += ["Result:", "", "```", call.result, "```", ""]
            if call.failed:
                lines += ["> the tool reported an error", ""]
    lines += ["## Answer", "", parsed.answer_text or "(no answer text)", ""]
    if error:
        lines += [f"> conversation error: {error}", ""]
    return "\n".join(lines) + "\n"
