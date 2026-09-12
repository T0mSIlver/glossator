"""The contain transform: one language tab, no duplicate sample, no pasted
output beyond its head."""

import pytest

from glossator.containing import contain


def group_page() -> str:
    return (
        "intro text\n"
        "\n"
        "**Python**\n"
        "\n"
        "```python\nclient = Mistral()\n```\n"
        "\n"
        "**TypeScript**\n"
        "\n"
        "```typescript\nconst client = new Mistral();\n```\n"
        "\n"
        "**cURL**\n"
        "\n"
        "```bash\ncurl https://api.mistral.ai\n```\n"
        "\n"
        "after the group\n"
    )


def test_a_group_with_three_tabs_prints_one_and_names_two() -> None:
    out = contain([group_page()], "python")
    assert "**Python**" in out[0]
    assert "```python\nclient = Mistral()\n```" in out[0]
    assert "**TypeScript**" not in out[0]
    assert "const client" not in out[0]
    assert "**cURL**" not in out[0]
    assert "curl https" not in out[0]
    assert (
        '(samples in TypeScript and cURL omitted: pass lang="typescript" or lang="curl")' in out[0]
    )
    assert "after the group" in out[0]


def test_a_lang_absent_from_a_group_prints_the_first_tab() -> None:
    page = (
        "**TypeScript**\n"
        "\n"
        "```typescript\nconst a = 1;\n```\n"
        "\n"
        "**cURL**\n"
        "\n"
        "```bash\ncurl -X GET\n```\n"
    )
    out = contain([page], "python")
    assert "**TypeScript**" in out[0]
    assert "const a = 1;" in out[0]
    assert "curl -X GET" not in out[0]
    assert '(sample in cURL omitted: pass lang="curl")' in out[0]


def test_bash_counts_as_the_curl_tab() -> None:
    page = "**Python**\n\n```python\na = 1\n```\n\n**Bash**\n\n```bash\ncurl x\n```\n"
    out = contain([page], "curl")
    assert "**Bash**" in out[0]
    assert "curl x" in out[0]
    assert "a = 1" not in out[0]
    assert '(sample in Python omitted: pass lang="python")' in out[0]


def test_identical_v1_v2_prints_once() -> None:
    page = (
        "**Python**\n"
        "\n"
        "**V1**\n"
        "\n"
        "```python\nclient = Mistral()\nanswer = client.chat()\n```\n"
        "\n"
        "**V2**\n"
        "\n"
        "```python\nclient = Mistral()\nanswer  =  client.chat()\n```\n"
        "\n"
        "**TypeScript**\n"
        "\n"
        "```typescript\nconst a = 1;\n```\n"
    )
    out = contain([page], "python")
    assert out[0].count("```python") == 1
    assert "**V2**" in out[0]
    assert "(V1 identical)" in out[0]
    assert "answer  =  client.chat()" in out[0]


def test_differing_v1_v2_prints_both() -> None:
    page = (
        "**Python**\n"
        "\n"
        "**V1**\n"
        "\n"
        "```python\nold = Mistral(v1=True)\n```\n"
        "\n"
        "**V2**\n"
        "\n"
        "```python\nnew = Mistral()\n```\n"
        "\n"
        "**TypeScript**\n"
        "\n"
        "```typescript\nconst a = 1;\n```\n"
    )
    out = contain([page], "python")
    assert "old = Mistral(v1=True)" in out[0]
    assert "new = Mistral()" in out[0]
    assert "(V1 identical)" not in out[0]


def test_a_duplicate_fence_outside_groups() -> None:
    page = "first\n\n```python\nx = 1\n```\n\nbetween\n\n```python\nx =   1\n```\n\nlast\n"
    out = contain([page], "python")
    assert out[0].count("```python") == 1
    assert "(same sample as above)" in out[0]
    assert "between" in out[0]
    assert "last" in out[0]


def test_an_output_over_the_ceiling_is_cut_at_a_line_boundary() -> None:
    lines = [f'"entry {index:03d} ' + "x" * 88 + '"' for index in range(40)]
    assert len(lines[0]) == 100
    page = "```json\n" + "\n".join(lines) + "\n```\n"
    out = contain([page], "python")
    body = out[0].split("\n")
    assert body[0] == "```json"
    assert body[1 : 1 + 14] == lines[:14]
    assert body[15] == "```"
    assert body[16] == "(output cut after 1,500 characters; 26 more lines)"


def test_a_single_long_line_is_cut_at_the_ceiling() -> None:
    page = "```\n" + "y" * 3000
    out = contain([page], "python")
    body = out[0].split("\n")
    assert body[0] == "```"
    assert body[1] == "y" * 1500
    assert body[2] == "```"
    assert body[3] == "(output cut after 1,500 characters; 1 more line)"


def test_a_vector_fence_is_an_output_whatever_its_tag() -> None:
    line = "  0.123456789012345678901234567890,  " + "v" * 3
    assert len(line) == 40
    page = "```python\n" + "\n".join([line] * 40) + "\n```\n"
    out = contain([page], "python")
    assert "(output cut after 1,500 characters; 4 more lines)" in out[0]
    assert out[0].count(line) == 36


def test_a_code_fence_over_the_ceiling_is_untouched() -> None:
    body = "\n".join(f"# line {index:04d} " + "z" * 60 for index in range(40))
    page = "```python\n" + body + "\n```\n"
    assert contain([page], "python")[0] == page


def test_a_label_at_the_end_of_one_chunk_with_its_fence_in_the_next() -> None:
    head = "text\n\n**Python**"
    tail = (
        "\n```python\nx = 1\n```\n\n**TypeScript**\n\n```typescript\nconst x = 1;\n```\n\nlater\n"
    )
    out = contain([head, tail], "python")
    assert out[0] == "text\n\n**Python**"
    assert "```python\nx = 1\n```" in out[1]
    assert "const x = 1;" not in out[1]
    assert '(sample in TypeScript omitted: pass lang="typescript")' in out[1]
    assert "later" in out[1]


def test_a_fence_split_across_chunks_is_one_output() -> None:
    lines = [f'"value {index:04d} ' + "v" * 87 + '"' for index in range(60)]
    assert len(lines[0]) == 100
    head = "```json\n" + "\n".join(lines[:30])
    tail = "\n".join(lines[30:]) + "\n```\n\nprose after"
    out = contain([head, tail], "python")
    body = out[0].split("\n")
    assert body[1 : 1 + 14] == lines[:14]
    assert body[15] == "```"
    assert body[16] == "(output cut after 1,500 characters; 46 more lines)"
    # The fence's remaining lines print nothing in the continuation chunk; the
    # blank that separated the close from the prose stays.
    assert out[1] == "\nprose after"


def test_prose_and_tables_are_byte_identical() -> None:
    page = (
        "# Heading\n"
        "\n"
        "A paragraph with **bold** and `code`.\n"
        "\n"
        "| Col | Other |\n"
        "| --- | ----- |\n"
        "| 1 | 2 |\n"
        "| 3 | 4 |\n"
        "\n"
        "- list item\n"
        "- another\n"
        "\n"
        "    cite: https://docs.mistral.ai/page#section\n"
    )
    assert contain([page], "curl") == [page]


def test_a_lone_tab_label_without_a_fence_is_not_a_group() -> None:
    page = "**Python**\n\nNo fence follows the label.\n"
    assert contain([page], "python") == [page]


def test_an_output_label_ends_a_group_and_its_fence_is_cut() -> None:
    rows = ['{"k": "' + "o" * 91 + '"}']
    assert len(rows[0]) == 100
    page = (
        "**Python**\n"
        "\n"
        "```python\nx = 1\n```\n"
        "\n"
        "**TypeScript**\n"
        "\n"
        "```typescript\nconst x = 1;\n```\n"
        "\n"
        "**Output**\n"
        "\n"
        "```json\n" + "\n".join(rows * 40) + "\n```\n"
    )
    out = contain([page], "python")
    assert "**Output**" in out[0]
    assert "const x = 1;" not in out[0]
    assert out[0].count(rows[0]) == 14
    assert "(output cut after 1,500 characters; 26 more lines)" in out[0]


def test_bad_lang_is_rejected() -> None:
    with pytest.raises(ValueError, match="lang must be one of"):
        contain(["x"], "java")
