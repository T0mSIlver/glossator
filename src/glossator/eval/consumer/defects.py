"""Surface defects read off the transcripts, and their table."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from glossator.eval.consumer.answers import is_quota_error
from glossator.eval.consumer.metrics import BAD_PARAM
from glossator.eval.consumer.models import ConsumerRecord
from glossator.eval.consumer.tools import is_server_tool


def collect_defects(records: Sequence[ConsumerRecord]) -> list[dict[str, str]]:
    """Every wrong turn the transcripts show, as a surface defect until proven
    otherwise. Severities: a turn that cost the answer is ``severe``; one that
    cost extra calls is ``extra-calls``; anything else is ``friction``."""
    defects: list[dict[str, str]] = []
    for record in records:
        for call in record.tool_calls:
            # The row already names the tool, so the observation reads it once.
            error = (call.error or "").removeprefix(f"{call.name}: ")
            if BAD_PARAM in error:
                defects.append(
                    {
                        "question_id": record.question_id,
                        "consumer": record.consumer,
                        "arm": record.arm,
                        "transcript": record.transcript,
                        "observation": f"{call.name} rejected with E_BAD_PARAM: {error}",
                        "severity": "extra-calls",
                        "proposal": (
                            "Read the transcript turn: if the parameter name came "
                            "from the tool description, rename the description's "
                            "wording; if it came from the guide, fix the guide."
                        ),
                    }
                )
            # Any refusal by one of this server's tools is friction, typed or
            # not: the error row names the tool before the line the tool
            # printed, so matching the line's start missed both the typed
            # errors and the schema rejections. A consumer's own shell or fetch
            # failing is not a defect of the surface under test.
            elif is_server_tool(call.name) and error:
                defects.append(
                    {
                        "question_id": record.question_id,
                        "consumer": record.consumer,
                        "arm": record.arm,
                        "transcript": record.transcript,
                        "observation": f"{call.name} returned {error}",
                        "severity": "friction",
                        "proposal": (
                            "Check whether the typed error and its next hint led "
                            "the consumer to a working call within two turns; if "
                            "not, sharpen the hint."
                        ),
                    }
                )
        if record.error and not is_quota_error(record.error):
            defects.append(
                {
                    "question_id": record.question_id,
                    "consumer": record.consumer,
                    "arm": record.arm,
                    "transcript": record.transcript,
                    "observation": f"harness failed: {record.error}",
                    "severity": "severe",
                    "proposal": (
                        "Re-run the cell by hand; if the failure repeats, the "
                        "harness or the prompt needs a fix before the numbers "
                        "are quoted."
                    ),
                }
            )
    return defects


def render_defects(defects: Sequence[Mapping[str, str]]) -> str:
    lines = [
        "# Surface defects",
        "",
        "Every wrong turn a consumer took, with the transcript path, a severity,",
        "and a proposed fix in prose. Fixes to the server belong in their own change.",
        "",
    ]
    if not defects:
        lines.append("No defects observed: no typed errors and no harness failures.")
        return "\n".join(lines) + "\n"
    for index, defect in enumerate(defects, 1):
        lines += [
            f"## {index}. {defect['question_id']} ({defect['consumer']} / {defect['arm']})",
            "",
            f"- Observation: {defect['observation']}",
            f"- Transcript: `{defect['transcript']}`",
            f"- Severity: {defect['severity']}",
            f"- Proposed fix: {defect['proposal']}",
            "",
        ]
    return "\n".join(lines)
