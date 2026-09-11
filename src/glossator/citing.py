"""Section keys and citation links (D-047).

Terms, used strictly:

- **anchor**: the id a heading has on the rendered page, the part after ``#`` in
  ``url#prepare-batch-file``. Only headings written with ``{#...}`` in the source
  have one; on docs.mistral.ai the others render without an id.
- **key**: the name the MCP tools use for a section. The anchor when the heading
  has one; otherwise generated from the nearest anchored ancestor and the heading
  text, with an ordinal on collision (``prepare-batch-file/explanation-4``). A key
  is copied by the model, never built by it, and is never presented as a link.
- **text fragment**: the ``:~:text=`` directive that makes a browser scroll to a
  phrase. Printed only when it moves the landing: the cited text sits more than a
  screen below where the anchor link lands, and a short phrase of the text occurs
  once on the page.
- **citation link**: what the model cites. ``url#anchor`` when the heading has an
  anchor; otherwise the nearest ancestor's anchor, or the bare page URL, plus a
  text fragment when one is warranted.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from glossator.answer.citations import _encode_fragment_text, normalize
from glossator.ingest.sections import Section

FRAGMENT_MIN_DISTANCE = 1_500
"""Characters between where the anchor link lands and the cited text before a
text fragment is worth printing: about one screen."""
FRAGMENT_MIN_WORDS = 3
FRAGMENT_MAX_WORDS = 8

_SLUG = re.compile(r"[^a-z0-9]+")
_FENCE = re.compile(r"```.*?```", re.S)
_TABLE_ROW = re.compile(r"^\s*\|.*$", re.M)
_HEADING_LINE = re.compile(r"^#.*$", re.M)
_MARKUP = re.compile(r"[*`>\[\]]|\(https?://[^)]*\)|\{#[^}]*\}")
_CALLOUT = re.compile(r"^(Tip|Note|Info|Warning|Caution|Danger)\s+")
_SENTENCE = re.compile(r"[A-Z][^.!?\n]{30,}?[.!?](?=\s|$)")


def slugify(text: str) -> str:
    slug = _SLUG.sub("-", text.casefold()).strip("-")
    return slug or "section"


@dataclass(frozen=True, slots=True)
class SectionKey:
    """A section as the tools name and cite it."""

    key: str
    heading: str
    own_anchor: str | None
    anchor: str | None
    """The anchor the citation link uses: the heading's own or the nearest ancestor's."""
    start: int
    """Offset of the heading line in the page body."""
    anchor_start: int
    """Offset where ``url#anchor`` lands: the anchored heading's line, or 0 when
    the link lands at the page top."""


def section_keys(sections: list[Section]) -> list[SectionKey]:
    """One key per section, in page order, index-aligned with ``sections``.

    Anchored headings keep their anchor. The others get ``<ancestor anchor>/<slug>``
    or ``<slug>`` when nothing above them is anchored, with ``-2``, ``-3`` on
    repeats, and never a string another section already holds.
    """
    taken: set[str] = set(s.own_anchor for s in sections if s.own_anchor)
    anchor_at: dict[str, int] = {s.own_anchor: s.start_offset for s in sections if s.own_anchor}
    counts: dict[str, int] = {}
    keys: list[SectionKey] = []
    for s in sections:
        if s.own_anchor:
            key = s.own_anchor
        else:
            slug = slugify(s.heading) if s.level else "top"
            base = f"{s.anchor}/{slug}" if s.anchor else slug
            n = counts.get(base, 0) + 1
            counts[base] = n
            key = base if n == 1 else f"{base}-{n}"
            while key in taken:
                n += 1
                counts[base] = n
                key = f"{base}-{n}"
            taken.add(key)
        keys.append(
            SectionKey(
                key=key,
                heading=s.heading,
                own_anchor=s.own_anchor,
                anchor=s.anchor,
                start=s.start_offset,
                anchor_start=anchor_at.get(s.anchor, 0) if s.anchor else 0,
            )
        )
    return keys


def page_search_text(body: str) -> str:
    """The page as a phrase-uniqueness haystack: markup stripped, whitespace
    collapsed, case folded. The same normalisation ``first_sentence`` applies to a
    candidate, so a count of one here is a count of one on the rendered page."""
    return normalize(_MARKUP.sub("", body)).casefold()


def first_sentence(text: str) -> str | None:
    """The first prose sentence of a chunk or section body, as the rendered page
    shows it: no code fences, no table rows, no heading line, no markup, no
    callout label."""
    text = _FENCE.sub(" ", text)
    text = _TABLE_ROW.sub(" ", text)
    text = _HEADING_LINE.sub(" ", text)
    text = normalize(_MARKUP.sub("", text))
    for match in _SENTENCE.finditer(text):
        sentence = _CALLOUT.sub("", match.group(0)).strip()
        if len(sentence) >= 30:
            return sentence
    return None


def unique_phrase(haystack: str, sentence: str) -> str | None:
    """The shortest run of 3 to 8 consecutive words of ``sentence`` that occurs
    exactly once in ``haystack``; earlier runs win at equal length."""
    words = sentence.split(" ")
    for n in range(FRAGMENT_MIN_WORDS, FRAGMENT_MAX_WORDS + 1):
        for i in range(0, len(words) - n + 1):
            phrase = " ".join(words[i : i + n])
            if haystack.count(phrase.casefold()) == 1:
                return phrase
    return None


def citation_link(
    url: str,
    anchor: str | None,
    *,
    landing: int,
    text_start: int,
    text: str,
    haystack: str,
) -> str:
    """The link to cite for ``text``, which starts at ``text_start`` in the page
    body; ``landing`` is where ``url#anchor`` (or the bare URL) scrolls to.

    A text fragment is appended only when the text sits more than a screen
    below the landing and a short phrase of its first sentence is unique on the
    page. Otherwise the anchor link alone, which lands on the same screen."""
    base = f"{url}#{anchor}" if anchor else url
    if text_start - landing <= FRAGMENT_MIN_DISTANCE:
        return base
    sentence = first_sentence(text)
    if not sentence:
        return base
    phrase = unique_phrase(haystack, sentence)
    if not phrase:
        return base
    directive = _encode_fragment_text(phrase)
    return f"{base}:~:text={directive}" if anchor else f"{base}#:~:text={directive}"
