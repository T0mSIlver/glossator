"""One test per MDX conversion rule, on snippets shaped like the real docs."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from glossator.corpus.mistral_docs.mdx import Dropped, MdxNormalizer

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


def test_section_tab_without_section_id_gets_no_anchor(tmp_path: Path) -> None:
    # The component sets its DOM id from `sectionId` only, so there is nothing to link to.
    page = tmp_path / "page.mdx"
    page.write_text(
        '# Example\n\n<SectionTab as="h2">Set Up</SectionTab>\n\n<SectionTab as="h2">Set Up</SectionTab>\n',
        encoding="utf-8",
    )
    result = MdxNormalizer(PAGE_URL).render_page(page, "Example")
    assert "## Set Up" in result.markdown
    assert "{#" not in result.markdown
    assert result.anchors == []
    assert result.suppressed_anchors == 2


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
    assert render_result.dropped[Dropped("MysteryWidget", "unsupported component, text kept")] == 1


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


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("/studio/agents", "https://docs.mistral.ai/studio/agents"),
        ("#step-1", f"{PAGE_URL}#step-1"),
        ("./sibling", "https://docs.mistral.ai/studio/sibling"),
        ("../inference/sampling", "https://docs.mistral.ai/inference/sampling"),
        ("sibling", "https://docs.mistral.ai/studio/sibling"),
        ("../models?tab=all#pricing", "https://docs.mistral.ai/models?tab=all#pricing"),
        ("https://mistral.ai/news", "https://mistral.ai/news"),
        ("mailto:support@mistral.ai", "mailto:support@mistral.ai"),
    ],
)
def test_every_relative_link_target_is_resolved(tmp_path: Path, target: str, expected: str) -> None:
    output = render(tmp_path, f"# Example\n\nSee [here]({target}).\n")
    assert f"[here]({expected})" in output


def test_relative_image_targets_are_resolved_too(tmp_path: Path) -> None:
    output = render(tmp_path, "# Example\n\n![diagram](../img/flow.png)\n")
    assert "![diagram](https://docs.mistral.ai/img/flow.png)" in output


def test_embeds_survive_as_titled_links(tmp_path: Path) -> None:
    page = tmp_path / "page.mdx"
    page.write_text(
        "# Example\n\n"
        '<iframe src="https://www.youtube.com/embed/abc" title="Fine-tuning walkthrough" />\n\n'
        '<video src="/media/demo.mp4" title="Demo" />\n',
        encoding="utf-8",
    )
    result = MdxNormalizer(PAGE_URL).render_page(page, "Example")
    assert "[Fine-tuning walkthrough](https://www.youtube.com/embed/abc)" in result.markdown
    assert "[Demo](https://docs.mistral.ai/media/demo.mp4)" in result.markdown
    assert result.dropped == Counter()


def test_a_media_element_with_no_source_is_recorded(tmp_path: Path) -> None:
    page = tmp_path / "page.mdx"
    page.write_text('# Example\n\n<iframe title="Nothing" />\n', encoding="utf-8")
    result = MdxNormalizer(PAGE_URL).render_page(page, "Example")
    assert result.dropped[Dropped("iframe", "no resolvable source")] == 1


def test_an_image_with_an_expression_source_is_recorded(tmp_path: Path) -> None:
    page = tmp_path / "page.mdx"
    page.write_text('# Example\n\n<img src={diagram} alt="x" />\n', encoding="utf-8")
    result = MdxNormalizer(PAGE_URL).render_page(page, "Example")
    assert result.dropped[Dropped("img", "image source is an expression")] == 1


def test_a_missing_partial_is_recorded(tmp_path: Path) -> None:
    page = tmp_path / "page.mdx"
    page.write_text(
        "# Example\n\nimport Gone from './gone/_page.mdx';\n\n<Gone />\n", encoding="utf-8"
    )
    result = MdxNormalizer(PAGE_URL).render_page(page, "Example")
    assert result.dropped[Dropped("Gone", "partial file not found")] == 1


def test_a_partial_cycle_stops_at_the_depth_limit(tmp_path: Path) -> None:
    # Two partials importing each other would otherwise recurse forever.
    first = tmp_path / "one"
    second = tmp_path / "two"
    first.mkdir()
    second.mkdir()
    (first / "_page.mdx").write_text(
        "import Two from '../two/_page.mdx';\n\nOne.\n\n<Two />\n", encoding="utf-8"
    )
    (second / "_page.mdx").write_text(
        "import One from '../one/_page.mdx';\n\nTwo.\n\n<One />\n", encoding="utf-8"
    )
    page = tmp_path / "page.mdx"
    page.write_text("# Example\n\nimport One from './one/_page.mdx';\n\n<One />\n", "utf-8")
    result = MdxNormalizer(PAGE_URL).render_page(page, "Example")
    assert "One." in result.markdown
    assert any(
        dropped.reason == "partial nesting deeper than the limit" for dropped in result.dropped
    )


def test_a_concatenated_href_expression_is_resolved(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        "# Example\n\n"
        '<AppLink href={"https://" + "admin.mistral.ai/plateforme/privacy"} '
        'path={["Admin Panel", "Privacy"]} />\n',
    )
    assert "[Admin Panel > Privacy](https://admin.mistral.ai/plateforme/privacy)" in output


def test_a_dual_theme_image_uses_the_light_variant(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        "# Example\n\n<Image url={['/img/chat.png', '/img/chat_dark.png']} alt=\"Chat\" />\n",
    )
    assert "![Chat](https://docs.mistral.ai/img/chat.png)" in output


def test_a_raw_html_table_keeps_its_fenced_cells(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        "# Example\n\n"
        '<table class="prompt-example">\n'
        "    <tr>\n        <td>Assistant</td>\n        <td>\n\n"
        '```\n{"Summary": "text"}\n```\n\n'
        "        </td>\n    </tr>\n</table>\n",
    )
    assert "**Assistant**" in output
    assert '```\n{"Summary": "text"}\n```' in output


def test_an_audio_element_becomes_a_link_to_its_source(tmp_path: Path) -> None:
    output = render(
        tmp_path,
        "# Example\n\n<audio controls>\n"
        '    <source src="/audio/obama.mp3" type="audio/mp3"/>\n'
        "    Your browser does not support the audio element.\n"
        "</audio>\n",
    )
    assert "[Audio sample](https://docs.mistral.ai/audio/obama.mp3)" in output
    assert "does not support" not in output
