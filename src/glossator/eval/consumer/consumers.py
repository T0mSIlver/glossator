"""The consumers under test and the arms each one runs in."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ARMS = ("A0", "A1", "A2", "V0", "VA", "VB", "VC", "VD")

ARM_TOOLS: dict[str, str | None] = {
    "A0": None,
    "A1": "mistral_docs_search,mistral_docs_read_page",
    "A2": "mistral_docs_answer",
    "V0": "vibe: bash in an empty directory",
    "VA": "vibe: bash over the raw docs repository",
    "VB": "vibe: bash over the normalised pages and snapshots",
    "VC": "mistral_docs_search,mistral_docs_read_page,mistral_docs_history",
    "VD": "vibe: bash over the normalised pages and snapshots, plus all three tools",
}
"""The GLOSSATOR_MCP_TOOLS allowlist each arm's server runs. A0 never sees an
MCP server at all; A1 talks to a server started with this allowlist. A2 named
the answer tool while it was on the MCP surface (runs up to 2026-09-10); it is
kept so recorded runs read back, and a new A2 cell needs the API's `POST /ask`
instead (D-044). The V arms run only with the vibe harness; their tools and
environment are in `vibe_arms.py`."""

VIBE_ARM_NAMES = ("V0", "VA", "VB", "VC", "VD")


@dataclass(frozen=True, slots=True)
class ConsumerSpec:
    """One weak consumer: harness, model, and low-reasoning setting."""

    name: str
    harness: Literal["opencode", "codex", "claude", "vibe"]
    model: str
    variant: str | None = None
    """The reasoning effort, named the way the harness names it: opencode's
    ``--variant``, claude's ``--effort``, codex's ``model_reasoning_effort``.
    None means the harness default; weak consumers always name the lowest."""


CONSUMERS: tuple[ConsumerSpec, ...] = (
    ConsumerSpec(
        name="opencode-muse-minimal",
        harness="opencode",
        model="opencode/muse-spark-1.3-contributor-free",
        variant="minimal",
    ),
    ConsumerSpec(
        name="opencode-glm-flash-low",
        harness="opencode",
        model="zai-coding-plan/glm-5.3-flash",
        variant="low",
    ),
    ConsumerSpec(
        name="codex-gpt-luna-low",
        harness="codex",
        model="gpt-5.6-luna",
        variant="low",
    ),
    ConsumerSpec(
        name="claude-sonnet-low",
        harness="claude",
        model="sonnet",
        variant="low",
    ),
    ConsumerSpec(
        name="claude-haiku-low",
        harness="claude",
        model="haiku",
        variant="low",
    ),
    ConsumerSpec(
        name="vibe-medium35-high",
        harness="vibe",
        model="mistral-medium-3.5",
        variant="high",
    ),
)
"""Every weak consumer. The muse consumer is first: it is the contributor-free
model with quota while the z.ai window and the codex quota are exhausted."""

CONSUMER_NAMES = tuple(spec.name for spec in CONSUMERS)


def consumer_spec(name: str) -> ConsumerSpec:
    for spec in CONSUMERS:
        if spec.name == name:
            return spec
    raise SystemExit(f"unknown consumer {name!r}; available: {list(CONSUMER_NAMES)}")
