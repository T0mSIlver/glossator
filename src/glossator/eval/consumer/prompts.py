"""The instruction every consumer receives ahead of the question."""

from __future__ import annotations

PROMPT_LEAD = (
    "You are helping a developer with Mistral's platform. "
    "Answer precisely and cite the documentation pages you used with links."
)
"""Fixed prompt text that does not reveal the evaluation or name its tools."""
