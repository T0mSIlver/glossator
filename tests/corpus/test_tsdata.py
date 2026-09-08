"""The TypeScript data reader keeps values or fails; it never guesses."""

from __future__ import annotations

import pytest

from glossator.corpus.mistral_docs.tsdata import (
    FUNCTION,
    TsParseError,
    parse_named_const,
    parse_object_after,
)


def test_object_spread_is_applied() -> None:
    source = """
    const base = { status: 'GA', frontier: true };
    export default { ...base, slug: 'x' } as const;
    """
    assert parse_object_after(source, "export default") == {
        "status": "GA",
        "frontier": True,
        "slug": "x",
    }


def test_a_later_key_wins_over_the_spread() -> None:
    source = """
    const base = { status: 'GA' };
    export default { ...base, status: 'Deprecated' } as const;
    """
    assert parse_object_after(source, "export default")["status"] == "Deprecated"


def test_array_spread_is_applied() -> None:
    source = """
    const shared = ['batching', 'prefix'];
    export default { features: [...shared, 'function-calling'] } as const;
    """
    assert parse_object_after(source, "export default")["features"] == [
        "batching",
        "prefix",
        "function-calling",
    ]


def test_a_file_local_constant_reference_is_resolved() -> None:
    source = """
    const STATUS = 'PublicPreview';
    export default { slug: 'x', status: STATUS } as const;
    """
    assert parse_object_after(source, "export default")["status"] == "PublicPreview"


def test_an_imported_constant_fails_loudly() -> None:
    source = """
    import { STATUS } from '../schema';
    export default { slug: 'x', status: STATUS } as const;
    """
    # Silently reading this as `None` would erase a real field after an upstream refactor.
    with pytest.raises(TsParseError, match="not defined in this file"):
        parse_object_after(source, "export default")


def test_a_self_referential_constant_fails_loudly() -> None:
    source = """
    const LOOP = LOOP;
    export default { value: LOOP } as const;
    """
    with pytest.raises(TsParseError, match="refers to itself"):
        parse_object_after(source, "export default")


def test_a_spread_of_something_that_is_not_an_object_fails() -> None:
    source = """
    const base = 'not an object';
    export default { ...base, slug: 'x' } as const;
    """
    with pytest.raises(TsParseError, match="not an object"):
        parse_object_after(source, "export default")


def test_escaped_unicode_and_hex_are_decoded() -> None:
    source = r"""
    export default {
      name: 'Café',
      wide: '\u{1F600}',
      hex: '\x41',
      tab: 'a\tb',
      quote: 'it\'s',
    } as const;
    """
    parsed = parse_object_after(source, "export default")
    assert parsed["name"] == "Café"
    assert parsed["wide"] == "\U0001f600"
    assert parsed["hex"] == "A"
    assert parsed["tab"] == "a\tb"
    assert parsed["quote"] == "it's"


def test_a_template_literal_without_substitution_is_a_plain_string() -> None:
    source = "export default { blurb: `A frontier model.` } as const;"
    assert parse_object_after(source, "export default")["blurb"] == "A frontier model."


def test_a_template_substitution_in_data_fails_loudly() -> None:
    source = "export default { blurb: `Released ${year}.` } as const;"
    with pytest.raises(TsParseError, match="no literal value"):
        parse_object_after(source, "export default")


def test_a_template_substitution_inside_a_function_is_skipped() -> None:
    source = """
    export default {
      slug: 'x',
      describe: (l) => ({ description: l.text(`Model ${name} is fast.`) }),
    } as const;
    """
    parsed = parse_object_after(source, "export default")
    assert parsed["slug"] == "x"
    assert parsed["describe"] is FUNCTION


def test_comments_and_trailing_commas_are_tolerated() -> None:
    source = """
    export default {
      // a line comment
      slug: 'x', /* and a block one */
      list: [1, 2,],
    } as const satisfies StaticModel;
    """
    parsed = parse_object_after(source, "export default")
    assert parsed == {"slug": "x", "list": [1, 2]}


def test_a_truncated_object_fails() -> None:
    with pytest.raises(TsParseError):
        parse_object_after("export default { slug: ", "export default")


def test_a_missing_marker_fails() -> None:
    with pytest.raises(TsParseError, match="not found"):
        parse_object_after("const x = 1;", "export default")


def test_named_const_reads_a_table() -> None:
    source = """
    export const AVAILABLE_FEATURES = {
      'function-calling': { name: 'Function Calling', endpoints: ['chat-completions'] },
    } as const satisfies Features;
    """
    table = parse_named_const(source, "AVAILABLE_FEATURES")
    assert table["function-calling"]["name"] == "Function Calling"
