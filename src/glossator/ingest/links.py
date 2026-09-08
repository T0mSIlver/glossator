"""Outgoing links of a corpus page.

Two pages that link to each other are about related things, which is what the
evaluation set's cross-page questions are drawn from. Links inside fenced code
are excluded: a URL in a curl example is a request target, not a cross-reference.
"""

import re
from urllib.parse import urldefrag, urljoin

from glossator.ingest.markdown import scan_lines
from glossator.ingest.pages import CorpusPage

# Inline markdown link. The destination stops at whitespace so that a title
# (``[text](url "title")``) is not swallowed into the URL.
_LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s<>]+)>?[^)]*\)")


def extract_links(body: str, *, base_url: str) -> list[str]:
    """Absolute destinations of the inline links in ``body``, in reading order.

    Fragments are dropped: a link to another section of a page and a link to the
    page itself name the same document. Duplicates are dropped too, so a page
    that links to a neighbour ten times counts once.
    """
    seen: dict[str, None] = {}
    for line in scan_lines(body):
        if line.in_fence:
            continue
        for match in _LINK.finditer(line.text):
            target = match.group(1)
            if target.startswith(("mailto:", "#")):
                continue
            resolved, _fragment = urldefrag(urljoin(base_url, target))
            seen.setdefault(resolved.rstrip("/") or resolved, None)
    return list(seen)


def page_links(page: CorpusPage) -> list[str]:
    """The pages this page points at, as absolute URLs."""
    return extract_links(page.body, base_url=page.url)
