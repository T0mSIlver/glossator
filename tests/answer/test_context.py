"""Context assembly: de-duplication, merging, ordering, budget, numbering."""

from glossator.answer.context import assemble, count_mistral_tokens
from tests.answer.conftest import chunked_hit, make_hit, word_tokens

OTHER_PAGE = "https://docs.mistral.ai/capabilities/structured-output"
THIRD_PAGE = "https://docs.mistral.ai/capabilities/streaming"


def test_duplicate_chunks_appear_once() -> None:
    hit = make_hit("a", "Tools are declared as JSON objects.")
    context = assemble([hit, hit], token_budget=500, count_tokens=word_tokens)

    assert len(context.sources) == 1
    assert context.sources[0].chunk_ids == ("a",)


def test_touching_chunks_of_one_page_merge_into_one_source() -> None:
    first = chunked_hit("a", "Declare the tool.", start=0, end=17, score=2.0)
    second = chunked_hit("b", "Then call it.", start=17, end=30, score=1.0)

    context = assemble([second, first], token_budget=500, count_tokens=word_tokens)

    assert len(context.sources) == 1
    source = context.sources[0]
    assert source.chunk_ids == ("a", "b")
    assert "Declare the tool." in source.content
    assert "Then call it." in source.content
    # The heading prefix the chunker adds is carried once, not once per chunk.
    assert source.content.count("Function calling") == 1


def test_overlapping_chunks_do_not_repeat_the_overlap() -> None:
    first = chunked_hit("a", "alpha beta gamma", start=0, end=16)
    second = chunked_hit("b", "beta gamma delta", start=6, end=22)

    context = assemble([first, second], token_budget=500, count_tokens=word_tokens)

    assert context.sources[0].content.count("gamma") == 1
    assert context.sources[0].content.endswith("delta")


def test_a_gap_between_chunks_keeps_them_separate() -> None:
    first = chunked_hit("a", "Declare the tool.", start=0, end=17)
    second = chunked_hit("b", "Then call it.", start=400, end=413)

    context = assemble([first, second], token_budget=500, count_tokens=word_tokens)

    assert [source.chunk_ids for source in context.sources] == [("a",), ("b",)]


def test_sources_are_numbered_in_page_then_offset_order() -> None:
    late = chunked_hit("late", "Third paragraph.", start=900, end=916, score=3.0)
    early = chunked_hit("early", "First paragraph.", start=0, end=16, score=1.0)
    elsewhere = chunked_hit(
        "other",
        "Structured output.",
        start=0,
        end=18,
        score=2.0,
        source_id=OTHER_PAGE,
        heading_path=("Structured output",),
    )

    # Input order is relevance order: the best hit's page comes first.
    context = assemble([late, elsewhere, early], token_budget=500, count_tokens=word_tokens)

    assert [source.n for source in context.sources] == [1, 2, 3]
    assert [source.chunk_ids[0] for source in context.sources] == ["early", "late", "other"]
    assert context.text.startswith("[1] ")


def test_the_budget_drops_the_weakest_sources() -> None:
    keep = chunked_hit("keep", "one two three four five", start=0, end=23, score=9.0)
    drop = chunked_hit(
        "drop",
        "six seven eight nine ten",
        start=0,
        end=24,
        score=0.5,
        source_id=OTHER_PAGE,
        heading_path=("Structured output",),
    )

    context = assemble([keep, drop], token_budget=32, count_tokens=word_tokens)

    assert [source.chunk_ids for source in context.sources] == [("keep",)]
    assert context.dropped_chunk_ids == ("drop",)


def test_the_best_source_survives_a_budget_it_cannot_fit() -> None:
    only = chunked_hit("only", "one two three four five six", start=0, end=27)

    context = assemble([only], token_budget=1, count_tokens=word_tokens)

    assert [source.chunk_ids for source in context.sources] == [("only",)]


def test_rendering_carries_the_citation_url_and_heading_path() -> None:
    hit = chunked_hit("a", "Tools are JSON.", start=0, end=15, heading_path=("Guide", "Tools"))

    context = assemble([hit], token_budget=500, count_tokens=word_tokens)

    assert context.sources[0].citation_url.endswith("#tools")
    assert "Guide > Tools" in context.text
    assert "Tools are JSON." in context.text


def test_no_hits_gives_an_empty_context() -> None:
    context = assemble([], token_budget=500, count_tokens=word_tokens)

    assert context.sources == ()
    assert context.text == ""
    assert context.tokens == 0


def test_a_group_over_budget_does_not_block_a_cheaper_one_behind_it() -> None:
    """The budget fills best-effort: a source that does not fit is skipped, not final."""
    keep = chunked_hit("keep", "one two three", start=0, end=13, score=9.0)
    fat = chunked_hit(
        "fat",
        " ".join(f"word{i}" for i in range(40)),
        start=0,
        end=300,
        score=5.0,
        source_id=OTHER_PAGE,
        heading_path=("Structured output",),
    )
    cheap = chunked_hit(
        "cheap",
        "four five six",
        start=0,
        end=13,
        score=1.0,
        source_id=THIRD_PAGE,
        heading_path=("Streaming",),
    )

    context = assemble([keep, fat, cheap], token_budget=60, count_tokens=word_tokens)

    assert [source.chunk_ids[0] for source in context.sources] == ["keep", "cheap"]
    assert context.dropped_chunk_ids == ("fat",)


def test_the_default_counter_is_the_mistral_tokenizer_the_chunker_used() -> None:
    """The budget and the chunk sizes it was built from have to agree on a token."""
    hit = chunked_hit("a", "Tools are declared as JSON objects.", start=0, end=34)

    context = assemble([hit], token_budget=500)

    assert context.tokens == count_mistral_tokens(context.text)
    # BPE on this text is nowhere near a word count, which is what makes reusing
    # the chunker's tokenizer rather than an estimate worth the import.
    assert context.tokens > len(context.text.split())
