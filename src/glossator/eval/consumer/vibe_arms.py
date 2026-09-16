"""The Vibe CLI arms: what each agent may call, what it sees on disk, what it is told.

Every arm runs the same harness (Vibe, headless), the same model and the same
answer and citation rules; only the environment changes. The shell tool, where
an arm has it, runs inside a sandbox with no network and no view of anything
but the arm's own directory (``eval/vibe-arms/sandbox-shell``).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DOCS_COMMIT = "2e094f7bbe1395de4a738a3483def3573143d973"

ANSWER_RULES = """\
You answer developers' questions about Mistral's platform from Mistral's documentation \
as it stood at commit 2e094f7 of its repository (7 September 2026).

# How to answer

- State the exact value, limit or name first, then explain briefly.
- If the documentation does not answer the question, say so in one sentence, and say \
what it does cover, with its link.
- Questions about when something appeared, changed or was renamed: answer with the \
interval between two dated versions of the documentation, the last one without the \
change and the first one with it. Never give a single day.

# Citation format

Put a Markdown link right after each claim. The link text is the heading of the \
section you used; the target is the page URL followed by `#` and the section's anchor:

[Which models are supported?](https://docs.mistral.ai/studio/agents/introduction#which-models-are-supported)

- The page URL is `https://docs.mistral.ai/` followed by the page path: no trailing \
slash, no file extension, no `page.mdx`.
- When the section has no anchor, link the page URL alone.
- Cite only URLs you derived from what you read here. Never guess a URL."""

FROM_DOCS_ONLY = "- Answer only from the documentation you read here, never from memory."

ENV_NONE = """\
# Your environment

- The documentation is not available here: the shell runs in an empty directory with \
no network. Answer from what you know, with the same citation format."""

ENV_RAW = f"""\
# Your environment

{FROM_DOCS_ONLY}
- The working directory is a checkout of the documentation repository \
`platform-docs-public` at that commit, with its git history up to it. Use the shell: \
`rg`, `grep`, `fd`, `find`, `sed`, `jq`, `git` and `python3` are installed. There is \
no network.
- A guide page's source is `src/content/en/docs/<page path>/page.mdx` and its URL \
`https://docs.mistral.ai/<page path>`. API endpoint pages are generated from \
`openapi.yaml` under `https://docs.mistral.ai/api/endpoint/...` (layout in \
`src/content/en/api/sidebar-metadata.json`); model pages from `src/schema/models` under \
`https://docs.mistral.ai/models/...`. Routing and redirects: `route-utils.ts`, \
`redirect.ts`.
- A heading's anchor is its text passed through `slugify` in \
`src/lib/heading-utils.ts`: lower case, characters other than letters, digits, `_`, \
spaces and `-` dropped, spaces to `-`.
- For when something changed, `git log` on the source file: commit dates bound the \
change."""

ENV_FILES = f"""\
# Your environment

{FROM_DOCS_ONLY}
- `docs/` holds the documentation at that commit, one Markdown file per page. Each \
file's front matter gives its `url:`; `docs/manifest.json` lists every page's URL and \
path. A heading ending in `{{#anchor}}` carries that section's anchor. Use the shell: \
`rg`, `grep`, `fd`, `find`, `sed`, `jq` and `python3` are installed. There is no network.
- `snapshots/<date>/` holds the same documentation as it stood on each date, same \
layout: 2026-06-01, 06-15, 07-01, 07-15, 08-01, 08-15, 09-01 and 09-07. For when \
something changed, compare them: the change lies between the last date without it and \
the first date with it."""

ENV_TOOLS = f"""\
# Your environment

{FROM_DOCS_ONLY}
- The `mistral_docs` tools search and read the documentation at that commit. Search \
with one sentence, search again with other words before concluding, and read the page \
before answering. Every search hit prints a `cite:` line: use that URL exactly as \
printed, with the section heading as link text.
- `mistral_docs_history` answers when something appeared or changed across the dated \
versions; report the interval it prints."""

ENV_FILES_AND_TOOLS = f"""\
# Your environment

{FROM_DOCS_ONLY}
- The `mistral_docs` tools search and read the documentation at that commit; every \
search hit prints a `cite:` line to use exactly as printed, with the section heading \
as link text. `mistral_docs_history` answers when something appeared or changed.
- The same documentation is also on disk. `docs/` holds one Markdown file per page, its \
`url:` in the front matter, anchors as `{{#anchor}}` after headings; `snapshots/<date>/` \
holds the dated versions (2026-06-01 to 2026-09-07). Use the shell (`rg`, `grep`, `fd`, \
`find`, `sed`, `jq`, `python3`) for exact strings. There is no network."""


@dataclass(frozen=True, slots=True)
class VibeArm:
    name: str
    shell: bool
    mcp: bool
    environment: str
    """Directory under the environments root the agent works in."""
    environment_prompt: str
    description: str

    def system_prompt(self) -> str:
        return f"{ANSWER_RULES}\n\n{self.environment_prompt}\n"

    def workdir(self, environments_root: Path) -> Path:
        return environments_root / self.environment


VIBE_ARMS: dict[str, VibeArm] = {
    arm.name: arm
    for arm in (
        VibeArm(
            name="V0",
            shell=True,
            mcp=False,
            environment="empty",
            environment_prompt=ENV_NONE,
            description="control: shell in an empty directory, no documentation",
        ),
        VibeArm(
            name="VA",
            shell=True,
            mcp=False,
            environment="VA/platform-docs-public",
            environment_prompt=ENV_RAW,
            description="shell over the raw docs repository at 2e094f7, git history included",
        ),
        VibeArm(
            name="VB",
            shell=True,
            mcp=False,
            environment="VB",
            environment_prompt=ENV_FILES,
            description="shell over glossator's normalised pages and the eight dated snapshots",
        ),
        VibeArm(
            name="VC",
            shell=False,
            mcp=True,
            environment="empty",
            environment_prompt=ENV_TOOLS,
            description="the three mistral_docs MCP tools only",
        ),
        VibeArm(
            name="VD",
            shell=True,
            mcp=True,
            environment="VB",
            environment_prompt=ENV_FILES_AND_TOOLS,
            description="the MCP tools plus the shell over the normalised pages and snapshots",
        ),
    )
}
