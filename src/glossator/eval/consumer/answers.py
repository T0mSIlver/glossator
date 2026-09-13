"""What a collected answer says: its links, a refusal, quote verdicts, a quota failure."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence

from glossator.eval.consumer.models import ToolCallRecord
from glossator.eval.consumer.tools import is_verify_tool

QUOTA_HINTS = ("quota", "rate limit", "rate_limit", "usage limit", "429", "limit reached")
"""Substrings marking a harness failure as an exhausted provider window rather
than a broken question. Quota errors become error rows, not a crashed run."""

REFUSAL_PATTERNS = (
    r"documentation (does not|doesn't|do not|don't) (say|state|mention|cover|document|specify)",
    r"no(t| (such| record of| information| mention of)) .* in the documentation",
    r"(could|cannot|can't|could not) find .* in the documentation",
    r"not (covered|documented|stated|mentioned|specified) (in|by) the",
    r"(i |we |this server |the index )?(do not|don't|does not|doesn't) have .*documentation",
    r"unable to (find|locate|answer)",
    r"(decline|refuse) to answer",
    r"no evidence",
)
_REFUSAL = re.compile("|".join(REFUSAL_PATTERNS), re.IGNORECASE)

_URL = re.compile(r"https?://[^\s)>\]\"']+")


def extract_links(answer: str) -> list[str]:
    """Documentation URLs in the answer, in order, deduplicated."""
    seen: list[str] = []
    for match in _URL.finditer(answer):
        url = match.group(0).rstrip(".,;:")
        if url not in seen:
            seen.append(url)
    return seen


def refused(answer: str) -> bool:
    """Whether the answer declines for lack of documentation (heuristic)."""
    return _REFUSAL.search(answer) is not None


def cite_verdicts(calls: Sequence[ToolCallRecord]) -> tuple[int, int]:
    """(verified, rejected) cite quotes, counted from the verdict lines the
    consumer itself saw in each cite output."""
    verified = rejected = 0
    for call in calls:
        if not is_verify_tool(call.name):
            continue
        try:
            verdicts = json.loads(call.arguments.get("__verdicts", "{}"))
        except ValueError:
            continue
        if isinstance(verdicts, dict):
            verified += sum(1 for held in verdicts.values() if held)
            rejected += sum(1 for held in verdicts.values() if not held)
    return verified, rejected


def is_quota_error(text: str) -> bool:
    lowered = text.casefold()
    return any(hint in lowered for hint in QUOTA_HINTS)
