"""One test per MDX conversion rule, on snippets shaped like the real docs."""

from __future__ import annotations

from pathlib import Path

import pytest

from glossator.corpus.mistral_docs.mdx import MdxNormalizer

PAGE_URL = "https://docs.mistral.ai/studio/example"


def render(tmp_path: Path, body: str, title: str | None = "Example") -> str:
    page = tmp_path / "page.mdx"
    page.write_text(body, encoding="utf-8")
    return MdxNormalizer(PAGE_URL).render_page(page, title).markdown


def test_section_tab_becomes_a_heading_with_its_anchor(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        '# Example\n\n<SectionTab as="h1" sectionId="before-you-start">Before You Start</SectionTab>\n\nBody.\n',
    )
    assert "## Before You Start {#before-you-start}" in output
    assert "SectionTab" not in output


def test_section_tab_without_section_id_falls_back_to_the_slug(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        '# Example\n\n<SectionTab as="h2">Set Up</SectionTab>\n\n<SectionTab as="h2">Set Up</SectionTab>\n',
    )
    assert "## Set Up {#set-up}" in output
    assert "## Set Up {#set-up-1}" in output


def test_secondary_section_tab_renders_one_level_deeper(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        '# Example\n\n<SectionTab as="h2" variant="secondary" sectionId="step-1">Step 1</SectionTab>\n',
    )
    assert "### Step 1 {#step-1}" in output


def test_nested_section_tab_keeps_the_heading_but_drops_the_anchor(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        "# Example\n"
        '\n<Tabs>\n  <TabItem value="python" label="python">\n'
        '\n<SectionTab as="h2" sectionId="visualization">Visualization</SectionTab>\n'
        "\n  </TabItem>\n</Tabs>\n",
    )
    assert "## Visualization" in output
    assert "{#visualization}" not in output


def test_nested_tabs_keep_every_variant_under_a_bold_label(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        "# Example\n\n"
        '<Tabs groupId="code">\n'
        '  <TabItem value="python" label="python" default>\n\n'
        "```python\nprint(1)\n```\n\n"
        "  </TabItem>\n"
        '  <TabItem value="typescript" label="typescript">\n\n'
        '<Tabs>\n  <TabItem value="curl" label="curl">\n\n'
        "```bash\ncurl -X POST\n```\n\n"
        "  </TabItem>\n</Tabs>\n\n"
        "  </TabItem>\n"
        "</Tabs>\n",
    )
    assert "**Python**" in output
    assert "**TypeScript**" in output
    assert "**cURL**" in output
    assert "```python\nprint(1)\n```" in output
    assert "```bash\ncurl -X POST\n```" in output
    # Tab labels must never become headings: they are alternatives, not sections.
    assert "# Python" not in output


def test_explorer_tabs_are_expanded_too(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        "# Example\n\n<ExplorerTabs>\n"
        '<ExplorerTab value="editing" label="Editing" default>\n\nEdit here.\n\n</ExplorerTab>\n'
        '<ExplorerTabItem value="sharing" label="Sharing">\n\nShare here.\n\n</ExplorerTabItem>\n'
        "</ExplorerTabs>\n",
    )
    assert "**Editing**" in output
    assert "Edit here." in output
    assert "**Sharing**" in output
    assert "Share here." in output


def test_partials_are_inlined(tmp_path: Path) -> None:
    partial_dir = tmp_path / "streaming_tab"
    partial_dir.mkdir()
    (partial_dir / "_page.mdx").write_text(
        "Streaming body.\n\n```python\nstream()\n```\n", encoding="utf-8"
    )
    output = render(
        tmp_path,
        "# Example\n\nimport StreamingTab from './streaming_tab/_page.mdx';\n\n<StreamingTab />\n",
    )
    assert "Streaming body." in output
    assert "```python\nstream()\n```" in output
    assert "import StreamingTab" not in output


def test_faq_items_become_headings_with_accordion_anchors(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        '# Example\n\n<Faq type="multiple">\n'
        '  <FaqItem question="What happens if I omit service_tier?">\n\n'
        "  The request runs on the standard tier.\n\n"
        "  </FaqItem>\n"
        "</Faq>\n",
    )
    assert (
        "### What happens if I omit service_tier? {#what-happens-if-i-omit-servicetier}" in output
    )
    assert "The request runs on the standard tier." in output


@pytest.mark.parametrize(
    ("directive", "label"),
    [("info", "Info"), ("warning", "Warning"), ("tip", "Tip"), ("note", "Note")],
)
def test_directives_become_labelled_blockquotes(tmp_path: Path, directive: str, label: str) -> None:
    output = render(tmp_path, f"# Example\n\n:::{directive}\nRead this first.\n:::\n")
    assert f"> **{label}**" in output
    assert "> Read this first." in output
    assert f":::{directive}" not in output


def test_directive_with_a_custom_title(tmp_path: Path) -> None:
    output = render(tmp_path, "# Example\n\n:::warning[Deprecated]\nGone soon.\n:::\n")
    assert "> **Deprecated**" in output


def test_table_cells_keep_their_content_and_flatten_br(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        "# Example\n\n"
        "| Model | Names |\n|---|---|\n"
        "| [Large](/models/mistral-large-3-25-12)<br/>- `mistral-large-latest` | <u>two</u> |\n",
    )
    row = next(line for line in output.split("\n") if line.startswith("| [Large]"))
    assert "<br/>" not in row
    assert "<u>" not in row
    assert "two" in row
    assert "https://docs.mistral.ai/models/mistral-large-3-25-12" in row


def test_a_stray_close_br_is_still_a_break(tmp_path: Path) -> None:
    output = render(tmp_path, "# Example\n\n| A | B |\n|---|---|\n| one </br> two | three |\n")
    row = next(line for line in output.split("\n") if line.startswith("| one"))
    assert "</br>" not in row
    assert "one" in row and "two" in row


def test_fences_are_never_rewritten(tmp_path: Path) -> None:
    body = (
        "# Example\n\n"
        "```python\n"
        "# This comment is not a heading\n"
        'client.chat(model="<MISTRAL_MODEL>")  # <PLACEHOLDER>\n'
        "url = '/studio/relative/link'\n"
        "```\n\n"
        "Prose links to [chat](/studio/conversations/chat-completion).\n"
    )
    output = render(tmp_path, body)
    assert "# This comment is not a heading" in output
    assert "<MISTRAL_MODEL>" in output
    assert "'/studio/relative/link'" in output
    assert "[chat](https://docs.mistral.ai/studio/conversations/chat-completion)" in output


def test_relative_anchors_point_at_the_page(tmp_path: Path) -> None:
    output = render(tmp_path, "# Example\n\nSee [step 1](#step-1).\n")
    assert f"[step 1]({PAGE_URL}#step-1)" in output


def test_link_components_become_markdown_links(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        "# Example\n\n"
        '<LinkCard title="Quickstart" href="/getting-started/quickstarts" description="Start here" />\n'
        '<AppLink href="https://admin.mistral.ai/organization/billing" app="admin" path={["Organization", "Billing"]} />\n'
        '<CtaButton href="/studio">Open Studio</CtaButton>\n',
    )
    assert "[Quickstart](https://docs.mistral.ai/getting-started/quickstarts)" in output
    assert "[Organization > Billing](https://admin.mistral.ai/organization/billing)" in output
    assert "[Open Studio](https://docs.mistral.ai/studio)" in output


def test_unknown_components_are_stripped_but_counted(tmp_path: Path) -> None:
    page = tmp_path / "page.mdx"
    page.write_text(
        '# Example\n\n<MysteryWidget prop="x">Kept text.</MysteryWidget>\n', encoding="utf-8"
    )
    render_result = MdxNormalizer(PAGE_URL).render_page(page, "Example")
    assert "Kept text." in render_result.markdown
    assert "MysteryWidget" not in render_result.markdown
    assert render_result.stripped["MysteryWidget"] == 1


def test_frontmatter_title_becomes_the_h1_when_the_body_has_none(tmp_path: Path) -> None:
    output = render(tmp_path, "---\ntitle: Example\n---\n\nJust a paragraph.\n", "Example")
    assert output.startswith("# Example\n")


def test_existing_h1_is_not_duplicated(tmp_path: Path) -> None:
    output = render(
        tmp_path, "---\ntitle: Example\n---\n\n# Function Calling\n\nBody.\n", "Example"
    )
    assert output.startswith("# Function Calling\n")
    assert output.count("\n# ") == 0


def test_images_become_absolute_markdown_images(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        '# Example\n\n<div style={{ textAlign: \'center\' }}>\n  <img src="/img/fc_steps.png" alt="steps" width="700" />\n</div>\n',
    )
    assert "![steps](https://docs.mistral.ai/img/fc_steps.png)" in output
    assert "<img" not in output
