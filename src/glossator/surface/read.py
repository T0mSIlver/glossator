"""Reading a page: the whole page or one section in reading order, contained and
cut to a budget with the call that continues it, and the API's section list."""

from mistralai.search.toolkit.search.errors import IndexException, SourceNotFoundError

from glossator.answer.context import chunk_body
from glossator.doc_paths import SITE, split_docs_location
from glossator.retrieval.engine import Hit
from glossator.surface.containing import LANGS, contain
from glossator.surface.context import Surface
from glossator.surface.engines import EngineRegistry
from glossator.surface.errors import (
    api_unknown_page,
    api_upstream,
    bad_param,
    unknown_page,
    upstream,
)
from glossator.surface.names import READ_PAGE, SEARCH
from glossator.surface.pages import PageCatalog
from glossator.surface.search import PREFIX_LIST_MAX

READ_MAX_CHARS = 24_000
"""Per-call ceiling on a page read. Three pages in four are under it whole;
the rest arrive section by section (D-043)."""
READ_TOP_K = 400
"""Vespa's configured hit limit; the longest page holds under a hundred chunks."""


def _section_matches(pages: PageCatalog, hit: Hit, wanted: str) -> bool:
    """A section is addressed by its key; the heading text still works for a page
    outside the vendored corpus, whose sections have no generated key."""
    wanted = wanted.casefold()
    if pages.section_key(hit).casefold() == wanted:
        return True
    return bool(hit.heading_path) and hit.heading_path[-1].casefold() == wanted


def _split_part(section: str) -> tuple[str, int]:
    """``key:3`` names the third chunk of a section, the form a ``next:`` line
    prints when one section alone overflows a read; anything else is a key."""
    text = section.strip().lstrip("#")
    head, sep, tail = text.rpartition(":")
    if sep and head and tail.isdigit():
        return head, max(1, int(tail))
    return text, 1


def _contained_bodies(hits: list[Hit], keys: list[str], lang: str) -> list[str]:
    """The chunk bodies with tab groups, repeated samples and pasted outputs
    contained, one body per chunk. Containment is per section: a chunk group is
    a section's consecutive chunks, and the transform's state carries across the
    chunk boundaries inside one section."""
    contained: list[str] = []
    run: list[Hit] = []
    previous: str | None = None
    for hit, key in zip(hits, keys, strict=True):
        if previous is not None and key != previous and run:
            contained.extend(contain([chunk_body(item).rstrip() for item in run], lang))
            run = []
        previous = key
        run.append(hit)
    if run:
        contained.extend(contain([chunk_body(item).rstrip() for item in run], lang))
    return contained


async def read_page(surface: Surface, page_url: str, section: str | None, lang: str) -> str:
    """The ``mistral_docs_read_page`` result."""
    if not page_url.split("#", 1)[0].strip():
        raise bad_param("page_url is empty.", f"pass a page URL from a {SEARCH} hit.")
    try:
        path, _fragment = split_docs_location(page_url, "page_url")
    except ValueError as exc:
        raise bad_param(f"{exc}.", f"pass a page URL from a {SEARCH} hit.") from exc
    # The search and history tools accept the same four forms of a location, so
    # a path one of them printed or took reads here too.
    page_url = f"{SITE}{path or '/'}"
    if lang not in LANGS:
        raise bad_param(
            f'lang "{lang}" is not one of python, typescript, curl.',
            f'pass lang="python", "typescript" or "curl" with {READ_PAGE}.',
        )
    async with surface.admitted():
        try:
            navigation = surface.engine.navigation_at(page_url)
            chunks = await navigation.read(None, None, top_k=READ_TOP_K)
        except SourceNotFoundError as exc:
            raise unknown_page(page_url) from exc
        except IndexException as exc:
            raise upstream(f"read_page({page_url!r})", exc) from exc
    if not chunks:
        raise unknown_page(page_url)
    pages = surface.pages
    title = chunks[0].page_title
    keys = [pages.section_key(hit) for hit in chunks]
    order = list(dict.fromkeys(keys))
    if section is not None:
        wanted, part = _split_part(section)
        positions = [i for i, hit in enumerate(chunks) if _section_matches(pages, hit, wanted)]
        if not positions:
            raise bad_param(
                f'page {page_url} has no section "{wanted}".',
                f"sections on this page: {', '.join(order)}; omit section to read the whole page.",
            )
        start = positions[0] + min(part - 1, len(positions) - 1)
        stop = positions[-1] + 1
        heading = f'page: {page_url} | "{title}" | section: {wanted}'
        if start > positions[0]:
            heading += f" | from chunk {start - positions[0] + 1}"
    else:
        start, stop = 0, len(chunks)
        heading = f'page: {page_url} | "{title}"'
    lines = [heading, ""]
    contained = _contained_bodies(chunks[start:stop], keys[start:stop], lang)
    spent = 0
    shown = 0
    last_key: str | None = keys[start - 1] if start > 0 and section is not None else None
    for index in range(start, stop):
        hit = chunks[index]
        block: list[str] = []
        if keys[index] != last_key:
            block.extend(pages.section_header(hit))
            block.append(f"    cite: {pages.cite(hit)}")
            last_key = keys[index]
        block.append(contained[index - start])
        block.append("")
        size = sum(len(line) + 1 for line in block)
        if shown and spent + size > surface.read_max_chars:
            break
        spent += size
        shown += 1
        lines.extend(block)
    cut = start + shown
    if cut < stop:
        # The read stopped early. Continue at the next section, or inside the one
        # that was cut, at the chunk after the last one shown.
        next_key = keys[cut]
        if next_key == keys[cut - 1]:
            first = keys.index(next_key)
            target = f'section="{next_key}:{cut - first + 1}"'
        else:
            target = f'section="{next_key}"'
        complete = len(dict.fromkeys(keys[start:cut])) - (1 if next_key == keys[cut - 1] else 0)
        total = len(dict.fromkeys(keys[start:stop]))
        rest = list(dict.fromkeys(keys[cut:stop]))
        lines.append(f"Results: {complete} of {total} sections; the page continues.")
        lines.append(
            f'next: {READ_PAGE}(page_url="{page_url}", {target}) continues; '
            f"remaining sections: {', '.join(rest[:PREFIX_LIST_MAX])}"
        )
    elif section is not None:
        lines.append("Results: the whole section.")
        following = order.index(keys[stop - 1]) + 1
        if following < len(order):
            lines.append(
                f'next: {READ_PAGE}(page_url="{page_url}", section="{order[following]}") '
                "for the section after it"
            )
    else:
        lines.append(f"Results: {len(order)} sections, the whole page.")
    return "\n".join(lines).rstrip()


async def page_sections(
    registry: EngineRegistry, page_path: str, *, variant: str, start_offset: int, top_k: int
) -> tuple[str, list[Hit]]:
    """The URL and the sections ``GET /pages`` returns, from ``start_offset`` on."""
    clean = page_path.strip("/")
    if not clean:
        raise api_unknown_page(clean)
    url = f"{SITE}/{clean}"
    engine = registry.get(variant)
    try:
        sections = await engine.navigation_at(url).read(start_offset or None, None, top_k=top_k)
    except SourceNotFoundError as exc:
        raise api_unknown_page(clean) from exc
    except IndexException as exc:
        raise api_upstream("page read", exc) from exc
    if not sections:
        raise api_unknown_page(clean)
    return url, sections


__all__ = ["READ_MAX_CHARS", "READ_TOP_K", "page_sections", "read_page"]
