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
from glossator.paragraphs import paragraphs, without_list_marker

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


RERANKER_URL = "https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers"

RERANKER_SECTION = """**When to use**:
- Semantic relevance judgments beyond vector similarity
- Lower throughput tolerance (LLM calls are slower)

**Cost optimization**:

LLM reranking is expensive (1 LLM call per chunk). Reduce cost by:

```python
# 1. Get many results from retriever (fast)
query_engine = QueryEngine(retriever=vector_retriever)
```
"""


def test_first_sentence_never_joins_a_label_to_the_paragraph_below() -> None:
    text = RERANKER_SECTION[RERANKER_SECTION.index("**Cost optimization**") :]
    assert first_sentence(text) == "LLM reranking is expensive (1 LLM call per chunk)."


def test_the_reranker_cost_link_takes_its_phrase_from_one_paragraph() -> None:
    body = "# Rerankers\n\n## LLM Reranker {#llm-reranker}\n\n" + RERANKER_SECTION
    cost = RERANKER_SECTION[RERANKER_SECTION.index("**Cost optimization**") :]
    link = citation_link(
        RERANKER_URL,
        "llm-reranker",
        landing=0,
        text_start=5_000,
        text=cost,
        haystack=page_search_text(body),
    )
    assert link == f"{RERANKER_URL}#llm-reranker:~:text=LLM%20reranking%20is"


def test_first_sentence_never_runs_from_one_list_item_into_the_next() -> None:
    # Joined, the lines read as one sentence starting at "When"; on the page each
    # item is its own <li>, and only the last one holds a sentence.
    bullets = (
        "**When to use**:\n- Semantic relevance judgments beyond vector similarity\n"
        "- Lower throughput tolerance (LLM calls are slower)."
    )
    assert first_sentence(bullets) == "Lower throughput tolerance (LLM calls are slower)."
    numbered = "1. Chunks are sorted by LLM score\n2. The top results are returned to the caller."
    assert first_sentence(numbered) == "The top results are returned to the caller."


def test_paragraphs_split_at_blank_lines_and_list_items_but_not_bold_labels() -> None:
    assert paragraphs("**Bold** label\nstill the same paragraph\n\n- one\n* two\n3. three") == [
        "**Bold** label\nstill the same paragraph",
        "- one\n",
        "* two\n",
        "3. three",
    ]


def test_a_list_marker_is_not_text_on_the_page() -> None:
    assert without_list_marker("- `model` (string, required)") == "`model` (string, required)"
    assert without_list_marker("\n12. twelfth") == "twelfth"
    assert without_list_marker("**Bold** stays") == "**Bold** stays"


def test_a_prose_paragraph_without_a_full_stop_is_still_the_first_sentence() -> None:
    # The function-calling page introduces its code tabs this way; skipping the
    # paragraph would move the link forty lines down to the output list.
    text = (
        "We can now provide the output from the tools to our model, and in return the model "
        "can produce a final response\n\n**Python**\n\n```python\nmessages.append(result)\n```"
        "\n\n- **The status of your transaction with ID T1001 is Paid.**"
    )
    assert first_sentence(text) == (
        "We can now provide the output from the tools to our model, and in return the model "
        "can produce a final response"
    )
