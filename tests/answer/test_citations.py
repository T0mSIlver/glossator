"""Marker parsing and the quote check that decides whether a citation counts."""

from glossator.answer.citations import (
    DEFAULT_MIN_QUOTE_CHARS,
    FRAGMENT_EDGE_WORDS,
    FRAGMENT_MAX_CHARS,
    VERIFIED_AFTER_EMPHASIS,
    RejectionReason,
    cosmetic,
    fabricated,
    fragment_link,
    markers,
    mask_code,
    normalize,
    resolve,
    strip_markers,
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
    assert reason == RejectionReason.FABRICATED


def test_a_quote_too_short_to_be_evidence_is_rejected() -> None:
    context = assemble(
        [make_hit("a", "Tools are JSON.")], token_budget=500, count_tokens=word_tokens
    )
    ok, _, reason = verify("JSON", context.sources[0])

    assert not ok
    assert reason == RejectionReason.TOO_SHORT


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
    assert len(rejected) == 1 and rejected[0].reason == RejectionReason.FABRICATED


def test_a_citation_naming_a_source_that_does_not_exist_is_rejected() -> None:
    context = assemble(
        [make_hit("a", "Tools are JSON objects.")], token_budget=500, count_tokens=word_tokens
    )
    verified, rejected = resolve([(7, "Tools are JSON objects")], context)

    assert verified == []
    assert rejected[0].reason == f"{RejectionReason.NO_SUCH_SOURCE}: 7"


def test_markers_without_a_citation_are_reported() -> None:
    context = assemble(
        [make_hit("a", "Tools are JSON objects.")], token_budget=500, count_tokens=word_tokens
    )
    verified, rejected = resolve([(1, "Tools are JSON objects")], context)

    assert unmatched("Sentence one [1]. Sentence two [3].", verified + rejected) == [3]


def test_array_indexing_in_code_is_not_a_citation_marker() -> None:
    answer = "Read the first choice [1].\n\n```python\nprint(response.choices[0].message)\n```\n"

    assert markers(answer) == [1]


def test_an_inline_code_span_is_not_a_citation_marker() -> None:
    assert markers("Use `messages[2]` to reach it [1].") == [1]


def test_stripping_a_prose_marker_keeps_the_same_marker_in_inline_code() -> None:
    assert strip_markers("Stray [2], but `messages[2]` is code.", {2}) == (
        "Stray, but `messages[2]` is code."
    )


def test_an_unclosed_code_fence_swallows_the_rest_of_the_text() -> None:
    answer = "Real citation [1].\n```python\nx = choices[2]\nnever closed [5]\n"

    assert markers(answer) == [1]
    assert "choices" not in mask_code(answer)


def test_an_unclosed_tilde_fence_is_masked_too() -> None:
    assert markers("Before [1].\n~~~\nmessages[3]\n") == [1]


def test_a_closed_fence_followed_by_prose_keeps_the_prose() -> None:
    answer = "First [1].\n```python\nx = choices[2]\n```\nThen [3]."

    assert markers(answer) == [1, 3]


def test_verification_is_case_sensitive() -> None:
    context = assemble(
        [make_hit("a", "Tools are declared as JSON objects.")],
        token_budget=500,
        count_tokens=word_tokens,
    )
    ok, _, reason = verify("DECLARED AS JSON OBJECTS", context.sources[0])

    # Documented rather than desired: D-027 says whitespace normalization only,
    # so a re-cased quote is a rejection the eval will see.
    assert not ok
    assert reason == RejectionReason.FABRICATED


def test_a_quote_that_dropped_markdown_emphasis_still_verifies() -> None:
    context = assemble(
        [make_hit("a", "Maximum number of tools per request: **128**.")],
        token_budget=500,
        count_tokens=word_tokens,
    )
    ok, chunk_id, reason = verify("Maximum number of tools per request: 128.", context.sources[0])

    assert ok and chunk_id == "a"
    assert reason == VERIFIED_AFTER_EMPHASIS


def test_a_quote_that_dropped_backticks_still_verifies() -> None:
    context = assemble(
        [make_hit("a", "Pass `response_format` to the call.")],
        token_budget=500,
        count_tokens=word_tokens,
    )
    ok, _, reason = verify("Pass response_format to the call.", context.sources[0])

    assert ok and reason == VERIFIED_AFTER_EMPHASIS


def test_emphasis_normalization_does_not_drop_identifier_underscores() -> None:
    context = assemble(
        [make_hit("a", "Pass `tool_call_id` with the result.")],
        token_budget=500,
        count_tokens=word_tokens,
    )

    ok, _, reason = verify("Pass toolcallid with the result.", context.sources[0])

    assert not ok and reason == RejectionReason.FABRICATED


def test_emphasis_normalization_does_not_rescue_a_fabrication() -> None:
    context = assemble(
        [make_hit("a", "Tools are declared as JSON objects.")],
        token_budget=500,
        count_tokens=word_tokens,
    )
    ok, _, reason = verify("Tools are declared as YAML documents.", context.sources[0])

    assert not ok and reason == RejectionReason.FABRICATED


def test_a_too_short_quote_is_rejected_through_resolve() -> None:
    context = assemble(
        [make_hit("a", "Tools are JSON.")], token_budget=500, count_tokens=word_tokens
    )
    verified, rejected = resolve([(1, "JSON")], context)

    assert verified == []
    assert rejected[0].reason == RejectionReason.TOO_SHORT
    # Nothing was located, so no chunk is named for it.
    assert rejected[0].chunk_id is None


def test_the_minimum_quote_length_is_configurable() -> None:
    context = assemble(
        [make_hit("a", "Tools are JSON.")], token_budget=500, count_tokens=word_tokens
    )

    assert resolve([(1, "are JSON")], context, min_quote_chars=DEFAULT_MIN_QUOTE_CHARS)[0]
    assert resolve([(1, "are JSON")], context, min_quote_chars=40)[0] == []


def test_rejections_split_into_fabricated_and_cosmetic() -> None:
    context = assemble(
        [make_hit("a", "Tools are declared as JSON objects.")],
        token_budget=500,
        count_tokens=word_tokens,
    )
    _, rejected = resolve([(1, "declared as YAML documents"), (1, "JSON")], context)

    assert [c.quote for c in fabricated(rejected)] == ["declared as YAML documents"]
    assert [c.quote for c in cosmetic(rejected)] == ["JSON"]


PAGE = "https://docs.mistral.ai/capabilities/function-calling"


def test_fragment_link_encodes_punctuation_commas_ampersands_and_accents() -> None:
    link = fragment_link(PAGE, "tools", "Café, thé & chocolat: oui!")

    assert link == f"{PAGE}#tools:~:text=Caf%C3%A9%2C%20th%C3%A9%20%26%20chocolat%3A%20oui%21"


def test_fragment_link_encodes_the_hyphen_directive_delimiter() -> None:
    assert fragment_link(PAGE, "tools", "well-known limits").endswith("text=well%2Dknown%20limits")


def test_fragment_link_without_an_anchor_puts_the_directive_right_after_the_hash() -> None:
    assert fragment_link(PAGE, None, "Tools are declared as JSON objects.") == (
        f"{PAGE}#:~:text=Tools%20are%20declared%20as%20JSON%20objects."
    )


def test_fragment_link_strips_emphasis_and_collapses_whitespace_like_the_verifier() -> None:
    link = fragment_link(PAGE, None, "  **Maximum**\nnumber of tools: `128` per request.\n")

    assert link.endswith("text=Maximum%20number%20of%20tools%3A%20128%20per%20request.")


def test_fragment_from_an_identifier_keeps_underscores() -> None:
    context = assemble(
        [make_hit("a", 'Set "tool_call_id": tool_call.id in the response.')],
        token_budget=500,
        count_tokens=word_tokens,
    )

    verified, _ = resolve([(1, '"tool_call_id": tool_call.id')], context)

    assert verified[0].fragment_url == (f"{PAGE}#tools:~:text=%22tool_call_id%22%3A%20tool_call.id")


def test_fragment_from_an_emphasized_word_uses_source_text_without_markers() -> None:
    context = assemble(
        [make_hit("a", "Use the _required_ value here.")],
        token_budget=500,
        count_tokens=word_tokens,
    )

    verified, _ = resolve([(1, "Use the required value here.")], context)

    assert verified[0].fragment_url == (f"{PAGE}#tools:~:text=Use%20the%20required%20value%20here.")


def test_fragment_from_bold_text_uses_source_text_without_markers() -> None:
    context = assemble(
        [make_hit("a", "This is a **bold phrase** in the source.")],
        token_budget=500,
        count_tokens=word_tokens,
    )

    verified, _ = resolve([(1, "This is a bold phrase in the source.")], context)

    assert verified[0].fragment_url == (
        f"{PAGE}#tools:~:text=This%20is%20a%20bold%20phrase%20in%20the%20source."
    )


def test_fragment_from_inline_code_keeps_the_identifier() -> None:
    context = assemble(
        [make_hit("a", "Pass `response_format` to the call.")],
        token_budget=500,
        count_tokens=word_tokens,
    )

    verified, _ = resolve([(1, "Pass response_format to the call.")], context)

    assert verified[0].fragment_url == (
        f"{PAGE}#tools:~:text=Pass%20response_format%20to%20the%20call."
    )


def test_fragment_from_a_code_block_uses_the_source_whitespace() -> None:
    content = "Example:\n\n```python\nresult = tool_call_id\nmessages.append(result)\n```"
    context = assemble([make_hit("a", content)], token_budget=500, count_tokens=word_tokens)

    verified, _ = resolve([(1, "result = tool_call_id\nmessages.append(result)")], context)

    assert verified[0].fragment_url == (
        f"{PAGE}#tools:~:text=result%20%3D%20tool_call_id%20messages.append%28result%29"
    )


def test_fragment_range_uses_the_source_span_at_both_ends() -> None:
    words = ["**first**", "source_word", *(f"word{i}" for i in range(3, 29)), "last_word"]
    source_quote = " ".join(words)
    model_quote = source_quote.replace("**", "")
    context = assemble([make_hit("a", source_quote)], token_budget=500, count_tokens=word_tokens)

    verified, _ = resolve([(1, model_quote)], context)

    assert verified[0].fragment_url == (
        f"{PAGE}#tools:~:text=first%20source_word%20word3%20word4%20word5,"
        "word25%20word26%20word27%20word28%20last_word"
    )


def test_a_long_quote_uses_the_start_end_form_with_its_edges() -> None:
    quote = " ".join(f"word{i}" for i in range(1, 31))

    link = fragment_link(PAGE, "tools", quote)

    head = " ".join(f"word{i}" for i in range(1, FRAGMENT_EDGE_WORDS + 1))
    tail = " ".join(f"word{i}" for i in range(31 - FRAGMENT_EDGE_WORDS, 31))
    # Only the separator comma is literal; the ones inside the value would be %2C.
    assert link == f"{PAGE}#tools:~:text={head.replace(' ', '%20')},{tail.replace(' ', '%20')}"
    assert len(quote) > FRAGMENT_MAX_CHARS


def test_a_long_quote_with_too_few_words_is_sent_whole() -> None:
    # 8 words of 20 characters: over the length cut, under twice the edge words,
    # so shortening it would overlap the edges and the full quote is the directive.
    quote = " ".join(f"token{i:0>15}" for i in range(8))

    link = fragment_link(PAGE, None, quote)

    assert link == f"{PAGE}#:~:text=" + quote.replace(" ", "%20")


def test_a_quote_across_two_paragraphs_uses_a_range_with_one_end_in_each() -> None:
    quote = "**Cost optimization**:\n\nLLM reranking is expensive (1 LLM call per chunk)."

    link = fragment_link(PAGE, "llm-reranker", quote)

    # The two paragraphs render as two <p>; a plain directive joining them never matches.
    assert link == (
        f"{PAGE}#llm-reranker:~:text=Cost%20optimization%3A,%281%20LLM%20call%20per%20chunk%29."
    )


def test_a_quote_across_list_items_takes_its_ends_from_the_first_and_last_item() -> None:
    quote = 'These include:\n- "auto": the model decides.\n- "none": no tool.'

    link = fragment_link(PAGE, None, quote)

    assert link == f"{PAGE}#:~:text=These%20include%3A,%22none%22%3A%20no%20tool."


def test_an_empty_quote_degrades_to_the_plain_link() -> None:
    assert fragment_link(PAGE, "tools", "  *`_`*  ") == f"{PAGE}#tools"
    assert fragment_link(PAGE, None, " \n ") == PAGE


def test_resolve_sets_a_fragment_link_on_verified_citations_only() -> None:
    context = assemble(
        [make_hit("a", "Tools are declared as JSON objects, in JSON.")],
        token_budget=500,
        count_tokens=word_tokens,
    )
    verified, rejected = resolve(
        [(1, "declared as JSON objects"), (1, "declared as YAML objects")], context
    )

    assert verified[0].fragment_url == (f"{PAGE}#tools:~:text=declared%20as%20JSON%20objects")
    assert verified[0].citation_url == f"{PAGE}#tools"
    assert rejected[0].fragment_url is None


def test_the_two_normalizers_agree_on_every_shape_of_whitespace() -> None:
    """`normalize` reaches the form `_searchable` builds by a different route,
    so a drift between them would silently split "the same sentence" in two."""
    from glossator.answer.citations import _searchable, normalize

    for text in (
        "",
        "   ",
        "one two",
        "  leading and trailing  ",
        "tabs\tand\nnewlines\r\nmixed",
        "non\u00a0breaking\u00a0space",
        "form\ffeed and vertical\vtab",
        "a\u2028line\u2029separator",
    ):
        assert normalize(text) == _searchable(text)[0], text


def test_find_span_returns_the_source_characters_not_the_normalized_ones() -> None:
    """The span is offsets into the original, so a caller slicing with them gets
    the page's own wrapping back rather than the collapsed form."""
    from glossator.answer.citations import contains_span, find_span

    body = "Intro.\n\nThe limit is\n  **128** tools\nper request."
    span = find_span(body, "The limit is **128** tools per request.")

    assert span is not None
    assert body[span[0] : span[1]] == "The limit is\n  **128** tools\nper request."
    assert contains_span(body, "the limit is") is False  # matching is case sensitive
    assert contains_span(body, "no such sentence") is False


def test_find_span_ignores_an_empty_phrase() -> None:
    from glossator.answer.citations import find_span

    assert find_span("some text", "   ") is None
