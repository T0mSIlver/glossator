"""What the proxy agent is told, assembled from the workspace skill files."""

from __future__ import annotations

from pathlib import Path

SKILL_PATH = Path("skills/mistral-docs/SKILL.md")
CUSTOM_INSTRUCTIONS_PATH = Path("skills/mistral-docs/custom-instructions.md")


def skill_body(skill_path: Path = SKILL_PATH) -> str:
    """The skill file after its frontmatter: the instructions the agent runs."""
    text = skill_path.read_text()
    if text.startswith("---"):
        _, _, body = text.split("---", 2)
        return body.strip()
    return text.strip()


def custom_instructions_block(custom_path: Path = CUSTOM_INSTRUCTIONS_PATH) -> str:
    """The quoted block of the custom-instructions file, unquoted and joined.

    The block is line-wrapped markdown; a Work session carries it as one
    paragraph of context, so the lines are joined with spaces, not newlines.
    """
    lines = [
        line.removeprefix(">").strip()
        for line in custom_path.read_text().splitlines()
        if line.startswith(">")
    ]
    return " ".join(part for part in lines if part)


def agent_instructions(
    skill_path: Path = SKILL_PATH, custom_path: Path = CUSTOM_INSTRUCTIONS_PATH
) -> str:
    """What the proxy agent is told: the skill body, then the Work context."""
    return f"{skill_body(skill_path)}\n\n{custom_instructions_block(custom_path)}"
