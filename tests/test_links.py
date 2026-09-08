"""Link extraction: which pages a page points at."""

from pathlib import Path

from glossator.ingest.links import extract_links, page_links
from glossator.ingest.pages import load_page

BASE = "https://docs.mistral.ai/capabilities/function-calling"


def test_relative_and_absolute_links_resolve_to_page_urls() -> None:
    body = (
        "See [the models](https://docs.mistral.ai/models) and "
        "[conversations](../agents/conversations) for the rest.\n"
    )

    assert extract_links(body, base_url=BASE) == [
        "https://docs.mistral.ai/models",
        "https://docs.mistral.ai/agents/conversations",
    ]


def test_fragments_are_dropped_and_a_repeated_target_counts_once() -> None:
    body = (
        "[first](https://docs.mistral.ai/models#text-models) "
        "[again](https://docs.mistral.ai/models) "
        "[third](https://docs.mistral.ai/models#embeddings)\n"
    )

    assert extract_links(body, base_url=BASE) == ["https://docs.mistral.ai/models"]


def test_a_url_inside_a_fenced_block_is_not_a_link() -> None:
    body = (
        "Prose links to [the API](https://docs.mistral.ai/api/endpoint/chat-completions).\n"
        "\n"
        "```python\n"
        'client = Mistral(server_url="[docs](https://docs.mistral.ai/models)")\n'
        "```\n"
    )

    assert extract_links(body, base_url=BASE) == [
        "https://docs.mistral.ai/api/endpoint/chat-completions"
    ]


def test_anchor_only_and_mailto_links_are_skipped() -> None:
    body = "[jump](#available-models) and [mail](mailto:support@mistral.ai)\n"

    assert extract_links(body, base_url=BASE) == []


def test_page_links_reads_the_page_body(corpus_dir: Path) -> None:
    quickstart = load_page(corpus_dir / "getting-started-quickstart.md")

    assert page_links(quickstart) == [
        "https://docs.mistral.ai/capabilities/function-calling",
        "https://docs.mistral.ai/capabilities/embeddings",
        "https://docs.mistral.ai/models",
    ]
