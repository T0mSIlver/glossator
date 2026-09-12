"""Section keys and citation links (D-047)."""

from glossator.citing import (
    SectionKey,
    citation_link,
    first_sentence,
    page_search_text,
    section_keys,
    slugify,
    unique_phrase,
)
from glossator.ingest.sections import parse_sections

URL = "https://docs.mistral.ai/studio/batch-processing"

BODY = """# Batch Processing

Batching allows you to run asynchronous inference on large inputs in parallel.

## Prepare Batch {#prepare-batch-file}

### Prepare and Upload your Batch

A batch is composed of a list of API requests.

### Explanation

The body request will follow the same format as the endpoint you want to run.

### Explanation

The body request will follow the same format as the endpoint you want to run.

### Explanation

To upload your batch file, you need to use the files endpoint.

## Batch Creation {#batch-creation}

Create a new batch job, it will be queued for processing.

### File Batching {#file-batching}

We support up to 1 million requests in a single batch.
"""


def _keys() -> list[SectionKey]:
    return section_keys(parse_sections(BODY, page_title="Batch Processing"))


def test_slugify_folds_case_and_punctuation() -> None:
    assert slugify("Prepare and Upload your Batch") == "prepare-and-upload-your-batch"
    assert slugify("  ¿Qué?  ") == "qu"
    assert slugify("***") == "section"


def test_anchored_headings_keep_their_anchor_as_key() -> None:
    keys = {k.heading: k.key for k in _keys()}
    assert keys["Prepare Batch"] == "prepare-batch-file"
    assert keys["Batch Creation"] == "batch-creation"
    assert keys["File Batching"] == "file-batching"


def test_unanchored_headings_get_ancestor_slug_keys_with_ordinals() -> None:
    keys = [k.key for k in _keys()]
    assert keys == [
        "batch-processing",
        "prepare-batch-file",
        "prepare-batch-file/prepare-and-upload-your-batch",
        "prepare-batch-file/explanation",
        "prepare-batch-file/explanation-2",
        "prepare-batch-file/explanation-3",
        "batch-creation",
        "file-batching",
    ]


def test_keys_are_unique_and_index_aligned() -> None:
    sections = parse_sections(BODY, page_title="Batch Processing")
    keys = section_keys(sections)
    assert len(keys) == len(sections)
    assert len({k.key for k in keys}) == len(keys)
    for section, key in zip(sections, keys, strict=True):
        assert key.start == section.start_offset
        assert key.anchor == section.anchor


def test_a_generated_key_never_collides_with_an_anchor() -> None:
    body = (
        "# T\n\n## Retrieval {#retrieval}\n\ntext one here for the test.\n\n"
        "## Retrieval\n\ntext two here for the test.\n"
    )
    keys = [k.key for k in section_keys(parse_sections(body, page_title="T"))]
    assert keys == ["t", "retrieval", "retrieval-2"]


def test_anchor_start_is_where_the_link_lands() -> None:
    by_heading = {k.heading: k for k in _keys()}
    prepare = by_heading["Prepare Batch"]
    explanation = [k for k in _keys() if k.key == "prepare-batch-file/explanation-3"][0]
    assert explanation.anchor == "prepare-batch-file"
    assert explanation.anchor_start == prepare.start
    assert by_heading["Batch Processing"].anchor_start == 0


def test_first_sentence_skips_code_tables_headings_and_callouts() -> None:
    text = (
        "### Explanation\n\n```python\nprint('The code is not a sentence at all.')\n```\n"
        "| Column | Value in a table row that is long enough. |\n"
        "> **Tip**\n>\n> For batches with less than 10k requests, we support inline batching.\n"
    )
    assert (
        first_sentence(text)
        == "For batches with less than 10k requests, we support inline batching."
    )
    assert first_sentence("short. words only") is None


def test_unique_phrase_is_the_shortest_unique_run_anywhere_in_the_sentence() -> None:
    hay = page_search_text(
        "Chunk of content, usually tokens corresponding to the model reply. "
        "Chunk of content, usually tokens corresponding to the function tool call."
    )
    sentence = "Chunk of content, usually tokens corresponding to the function tool call."
    assert unique_phrase(hay, sentence) == "to the function"
    assert unique_phrase(hay, "Chunk of content, usually tokens") is None


def test_citation_link_is_the_anchor_alone_within_a_screen() -> None:
    hay = page_search_text(BODY)
    link = citation_link(
        URL,
        "batch-creation",
        landing=1000,
        text_start=1200,
        text="Create a new batch job, it will be queued.",
        haystack=hay,
    )
    assert link == f"{URL}#batch-creation"


def test_citation_link_adds_a_text_fragment_far_below_the_anchor() -> None:
    hay = page_search_text(BODY)
    link = citation_link(
        URL,
        "prepare-batch-file",
        landing=100,
        text_start=100 + 5_000,
        text="To upload your batch file, you need to use the files endpoint.",
        haystack=hay,
    )
    assert link == f"{URL}#prepare-batch-file:~:text=To%20upload%20your"


def test_citation_link_without_any_anchor_uses_a_bare_text_fragment() -> None:
    hay = page_search_text(BODY)
    link = citation_link(
        URL,
        None,
        landing=0,
        text_start=5_000,
        text="We support up to 1 million requests in a single batch.",
        haystack=hay,
    )
    assert link == f"{URL}#:~:text=We%20support%20up"


def test_citation_link_stays_plain_when_no_short_phrase_is_unique() -> None:
    hay = page_search_text(BODY)
    repeated = "The body request will follow the same format as the endpoint you want to run."
    link = citation_link(
        URL, "prepare-batch-file", landing=0, text_start=9_000, text=repeated, haystack=hay
    )
    assert link == f"{URL}#prepare-batch-file"
