"""Marker parsing and the quote check that decides whether a citation counts."""

from glossator.answer.citations import (
    MIN_QUOTE_CHARS,
    markers,
    normalize,
    resolve,
    unmatched,
    verify,
)
from glossator.answer.context import assemble
from tests.answer.conftest import chunked_hit, make_hit, word_tokens


def test_markers_are_read_in_order_without_repeats() -> None:
    assert markers("First [2]. Second [1]. Third [2].") == [2, 1]


def test_text_without_markers_has_none() -> None:
    assert markers("No sources here.") == []


def test_normalize_collapses_every_kind_of_whitespace() -> None:
    assert normalize("  a\n\tb   c \n") == "a b c"


def test_a_quote_matching_the_source_verifies() -> None:
    context = assemble(
        [make_hit("a", "Tools are declared as JSON objects.")],
        token_budget=500,
        count_tokens=word_tokens,
    )
    ok, chunk_id, reason = verify("declared as JSON objects", context.sources[0])

    assert (ok, chunk_id, reason) == (True, "a", None)


def test_a_quote_re_wrapped_by_the_model_still_verifies() -> None:
    context = assemble(
        [make_hit("a", "Tools are declared\n  as JSON\tobjects.")],
        token_budget=500,
        count_tokens=word_tokens,
    )
    ok, chunk_id, _ = verify("declared as JSON objects", context.sources[0])

    assert ok and chunk_id == "a"


def test_a_quote_that_is_not_in_the_source_is_rejected() -> None:
    context = assemble(
        [make_hit("a", "Tools are declared as JSON objects.")],
        token_budget=500,
        count_tokens=word_tokens,
    )
    ok, _, reason = verify("tools are declared as YAML", context.sources[0])

    assert not ok
    assert reason == "quote is not in the cited source"


def test_a_quote_too_short_to_be_evidence_is_rejected() -> None:
    context = assemble(
        [make_hit("a", "Tools are JSON.")], token_budget=500, count_tokens=word_tokens
    )
    ok, _, reason = verify("JSON", context.sources[0])

    assert not ok
    assert reason == f"quote shorter than {MIN_QUOTE_CHARS} characters"


def test_a_quote_spanning_a_merged_boundary_verifies() -> None:
    first = chunked_hit("a", "Set parallel_tool_calls to", start=0, end=26)
    second = chunked_hit("b", "false to disable it.", start=26, end=46)
    context = assemble([first, second], token_budget=500, count_tokens=word_tokens)

    ok, chunk_id, reason = verify("parallel_tool_calls to false to disable", context.sources[0])

    assert ok, reason
    # The match starts inside the first chunk, so that is the chunk cited.
    assert chunk_id == "a"


def test_a_quote_inside_the_second_merged_chunk_names_that_chunk() -> None:
    first = chunked_hit("a", "Set parallel_tool_calls to", start=0, end=26)
    second = chunked_hit("b", "false to disable it entirely.", start=26, end=55)
    context = assemble([first, second], token_budget=500, count_tokens=word_tokens)

    ok, chunk_id, _ = verify("disable it entirely", context.sources[0])

    assert ok and chunk_id == "b"


def test_resolve_splits_verified_from_rejected() -> None:
    context = assemble(
        [make_hit("a", "Tools are declared as JSON objects.")],
        token_budget=500,
        count_tokens=word_tokens,
    )
    verified, rejected = resolve(
        [(1, "declared as JSON objects"), (1, "declared as YAML documents")], context
    )

    assert [citation.quote for citation in verified] == ["declared as JSON objects"]
    assert [citation.verified for citation in verified] == [True]
    assert verified[0].chunk_id == "a"
    assert verified[0].citation_url.endswith("#tools")
    assert len(rejected) == 1 and rejected[0].reason == "quote is not in the cited source"


def test_a_citation_naming_a_source_that_does_not_exist_is_rejected() -> None:
    context = assemble(
        [make_hit("a", "Tools are JSON objects.")], token_budget=500, count_tokens=word_tokens
    )
    verified, rejected = resolve([(7, "Tools are JSON objects")], context)

    assert verified == []
    assert rejected[0].reason == "no source numbered 7"


def test_markers_without_a_citation_are_reported() -> None:
    context = assemble(
        [make_hit("a", "Tools are JSON objects.")], token_budget=500, count_tokens=word_tokens
    )
    verified, rejected = resolve([(1, "Tools are JSON objects")], context)

    assert unmatched("Sentence one [1]. Sentence two [3].", verified + rejected) == [3]
