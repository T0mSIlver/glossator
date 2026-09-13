"""Every `path:line` citation in the stack notes points at lines that exist.

The two documents cite this repository and the installed packages by line
range. A refactor that shortens a file leaves those citations pointing past its
end without failing anything else, which is how `answer/service.py:61-68`
survived a 65-line file. This test only proves the range exists; whether the
lines still say what the sentence claims is checked by reading them.
"""

import re
from collections.abc import Iterator
from pathlib import Path

import mcp
import mistralai.search.toolkit as toolkit
import pytest

REPO = Path(__file__).resolve().parents[1]
SITE_PACKAGES = Path(mcp.__file__).resolve().parents[1]
TOOLKIT = Path(toolkit.__file__).resolve().parent
VESPA_PLUGIN = TOOLKIT / "plugins" / "vespa"
DOCUMENTS = ("docs/mistral-stack.md", "docs/search-toolkit.md")

# `src/search_app/` is the starter app the toolkit's copier generates; the
# comparison in docs/search-toolkit.md cites it, but it is not in this tree.
NOT_IN_THIS_TREE = ("src/search_app/",)

CITATION = re.compile(
    r"`(?P<path>[\w./…-]+(?:\.(?:py|md|toml|yml|yaml|json|lock)|/METADATA))"
    r":(?P<ranges>\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)"
)


def _citations() -> Iterator[tuple[str, str, str]]:
    for document in DOCUMENTS:
        text = (REPO / document).read_text()
        for match in CITATION.finditer(text):
            yield document, match["path"], match["ranges"]


def _resolve(path: str) -> Path | None:
    """The file a citation names: the repository, then the installed packages,
    then the toolkit and its Vespa plugin, whose paths the toolkit notes shorten."""
    if path.startswith(("…/", ".../")):
        suffix = path.split("/", 1)[1]
        matches = [p for p in TOOLKIT.rglob("*.py") if p.as_posix().endswith("/" + suffix)]
        return matches[0] if len(matches) == 1 else None
    for root in (REPO, SITE_PACKAGES, TOOLKIT, VESPA_PLUGIN):
        if (root / path).is_file():
            return root / path
    return None


def _lines(ranges: str) -> list[int]:
    ends = []
    for part in ranges.split(","):
        start, _, stop = part.partition("-")
        assert not stop or int(start) <= int(stop), f"backwards range {part}"
        ends.append(int(stop or start))
    return ends


CITATIONS = sorted(set(_citations()))


def test_the_documents_cite_code() -> None:
    assert len(CITATIONS) > 50


@pytest.mark.parametrize(("document", "path", "ranges"), CITATIONS)
def test_citation_points_at_existing_lines(document: str, path: str, ranges: str) -> None:
    if path.startswith(NOT_IN_THIS_TREE):
        return
    resolved = _resolve(path)
    assert resolved is not None, f"{document} cites {path}, which resolves to no single file"
    length = len(resolved.read_text().splitlines())
    for last in _lines(ranges):
        assert last <= length, f"{document} cites {path}:{ranges}; the file has {length} lines"
