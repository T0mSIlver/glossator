"""A corpus page read as a list of sections.

A section is a heading plus the text directly under it, up to the next heading of
any level; a nested subsection is a section of its own, not part of its parent.
That is the unit a citation wants to name, because it is the unit the docs site
deep-links to.
"""

from dataclasses import dataclass

from glossator.ingest.markdown import parse_heading, scan_lines


@dataclass(frozen=True, slots=True)
class Section:
    """One heading's own text, located in the page body."""

    index: int
    """Position of the section in the page, in reading order, from 0."""

    level: int
    """Heading level, 1 for ``#``. 0 for text that precedes the first heading."""

    heading: str
    anchor: str | None
    """The nearest deep-link fragment on this heading or one of its ancestors."""

    own_anchor: str | None
    """The heading's own deep-link fragment, when it has one."""

    heading_path: tuple[str, ...]
    """Ancestor headings from the page title down to this one, inclusive."""

    body: str
    """Verbatim ``page_body[start_offset:end_offset]``, including the heading line."""

    start_offset: int
    end_offset: int

    @property
    def text(self) -> str:
        """The section's prose, with its own heading line removed.

        A level-0 section is the page's preamble and carries no heading line.
        """
        if self.level == 0:
            return self.body
        _heading_line, _newline, rest = self.body.partition("\n")
        return rest

    @property
    def is_empty(self) -> bool:
        """True for a heading that only introduces subsections."""
        return not self.text.strip()


def title_from_body(body: str) -> str:
    """The title the body declares for itself: its first heading, or "".

    Corpus pages carry their title in the frontmatter, which is authoritative.
    This is for callers that only have the markdown -- notably the ``TextSplitter``
    fragment interface, which is handed bare text.
    """
    for line in scan_lines(body):
        heading = parse_heading(line)
        if heading is not None:
            return heading.text
    return ""


def parse_sections(body: str, *, page_title: str) -> list[Section]:
    """Split a page body into sections.

    ``page_title`` heads every ``heading_path``, so a chunk's context line reads
    ``page title > H2 > H3`` even on a page whose H1 is missing or worded
    differently from the frontmatter title.
    """
    lines = scan_lines(body)
    starts: list[tuple[int, int, str, str | None]] = []  # line start, level, text, anchor
    for line in lines:
        heading = parse_heading(line)
        if heading is not None:
            starts.append((line.start, heading.level, heading.text, heading.anchor))

    sections: list[Section] = []
    stack: list[tuple[int, str, str | None]] = []

    # Text before the first heading has no heading of its own; it is attributed to
    # the page. Pages whose H1 opens the body (the normal case) have none.
    preamble_end = starts[0][0] if starts else len(body)
    if body[:preamble_end].strip():
        sections.append(
            Section(
                index=0,
                level=0,
                heading=page_title,
                anchor=None,
                own_anchor=None,
                heading_path=(page_title,),
                body=body[:preamble_end],
                start_offset=0,
                end_offset=preamble_end,
            )
        )

    for position, (start, level, text, anchor) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(body)
        while stack and stack[-1][0] >= level:
            stack.pop()
        path = tuple(heading for _level, heading, _anchor in stack) + (text,)
        if path[0] != page_title:
            path = (page_title, *path)
        citation_anchor = anchor or next(
            (
                ancestor_anchor
                for _level, _heading, ancestor_anchor in reversed(stack)
                if ancestor_anchor
            ),
            None,
        )
        stack.append((level, text, anchor))
        sections.append(
            Section(
                index=len(sections),
                level=level,
                heading=text,
                anchor=citation_anchor,
                own_anchor=anchor,
                heading_path=path,
                body=body[start:end],
                start_offset=start,
                end_offset=end,
            )
        )

    return sections
