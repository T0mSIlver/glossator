"""Search: the ranked sections a query finds, the pages under a path, and the
API's structured mirror of the same engine call."""

import json

from mistralai.search.toolkit.retrieval.errors import RetrieverException
from pydantic import ValidationError

from glossator.answer.context import chunk_body
from glossator.retrieval.config import KINDS, RetrievalConfig
from glossator.retrieval.engine import Hit
from glossator.surface.context import Surface
from glossator.surface.engines import EngineRegistry
from glossator.surface.errors import api_upstream, bad_param, upstream
from glossator.surface.names import READ_PAGE, SEARCH
from glossator.surface.pages import PageCatalog, prefix_from

MAX_HITS = 20
SNIPPET_CHARS = 400
PREFIX_LIST_MAX = 40
"""Pages a listing prints before asking for a narrower ``under``."""
SCOPED_HITS = 60
"""Sections a scoped search ranks before keeping the ones under the prefix."""


def _snippet(hit: Hit) -> str:
    body = chunk_body(hit)
    # The heading path above the snippet already names the section, so a
    # leading markdown heading line would only repeat it.
    if body.lstrip().startswith("#"):
        body = body.lstrip().split("\n", 1)[1] if "\n" in body.lstrip() else ""
    text = " ".join(body.split())
    if len(text) > SNIPPET_CHARS:
        return text[:SNIPPET_CHARS].rstrip() + " …"
    return text


def _distinct_sections(pages: PageCatalog, hits: list[Hit]) -> list[Hit]:
    """One hit per section, at its best rank. A long section is several chunks
    and they crowd the top of the ranking (D-012a); the model reads the section
    once either way."""
    seen: set[tuple[str, str]] = set()
    kept: list[Hit] = []
    for hit in hits:
        key = (hit.url, pages.section_key(hit))
        if key in seen:
            continue
        seen.add(key)
        kept.append(hit)
    return kept


def _large_page_line(pages: PageCatalog, hit: Hit) -> str:
    key = pages.section_key(hit)
    return f'    large page: {READ_PAGE}(page_url="{hit.url}", section="{key}") reads this section'


def list_pages_under(surface: Surface, prefix: str) -> str:
    pages = surface.pages.under(prefix)
    lines = [f"pages under {prefix}", ""]
    if not pages:
        lines.append(f"Results: no page under {prefix} at this commit.")
        parent = surface.pages.nearest_parent_with_pages(prefix)
        if parent:
            lines.append(f'next: {SEARCH}(under="{parent}") lists the pages that do exist there.')
        else:
            lines.append("next: search with words from the question instead of a URL.")
        return "\n".join(lines)
    for url, title in pages[:PREFIX_LIST_MAX]:
        lines.append(f"- {url}")
        lines.append(f"    {title}")
    lines.append("")
    if len(pages) > PREFIX_LIST_MAX:
        lines.append(
            f"Results: {len(pages)} pages, the first {PREFIX_LIST_MAX} listed; narrow the prefix."
        )
    else:
        lines.append(
            f"Results: {len(pages)} pages; a page not listed does not exist at this commit."
        )
    if READ_PAGE in surface.enabled:
        lines.append(f'next: {READ_PAGE}(page_url="{pages[0][0]}") reads the first one.')
    return "\n".join(lines)


async def search(surface: Surface, q: str, max_hits: int, under: str | None) -> str:
    """The ``mistral_docs_search`` result: hits with keys and ``cite:`` lines, or
    the page listing when ``q`` is empty or ``under`` names no page."""
    pages = surface.pages
    prefix = prefix_from(under) if under and under.strip() else None
    if not q.strip():
        if prefix is None:
            raise bad_param(
                "q is empty.", "say what you want to find in one sentence, or set under."
            )
        return list_pages_under(surface, prefix)
    if prefix is not None and not pages.under(prefix):
        return list_pages_under(surface, prefix)
    top_k = max(1, min(MAX_HITS, max_hits))
    # A scoped search filters after ranking, since the index has no URL-prefix
    # clause; asking for more hits keeps a small subtree from ranking out.
    ask_for = top_k * 3 if prefix is None else max(top_k * 3, SCOPED_HITS)
    async with surface.admitted():
        try:
            ranked = await surface.engine.search(q, top_k=ask_for, rerank=False)
        except RetrieverException as exc:
            raise upstream(f"search({q!r})", exc) from exc
    if prefix is not None:
        ranked = [hit for hit in ranked if hit.url == prefix or hit.url.startswith(prefix + "/")]
    hits = _distinct_sections(pages, ranked)[:top_k]
    lines = [f"q: {json.dumps(q)}" + (f" | under: {prefix}" if prefix else ""), ""]
    for n, hit in enumerate(hits, 1):
        lines.extend(pages.section_header(hit, n))
        lines.append(f"    {_snippet(hit)}")
        lines.append(f"    cite: {pages.cite(hit)}")
        if pages.is_large(hit.url):
            lines.append(_large_page_line(pages, hit))
        lines.append("")
    if not hits and prefix is not None:
        count = len(pages.under(prefix))
        lines.append(f"Results: no section under {prefix} matched; {count} pages exist there.")
        lines.append(
            f'next: {SEARCH}(under="{prefix}") lists them; a page not listed does not exist '
            "at this commit."
        )
        return "\n".join(lines)
    if not hits:
        lines.append("Results: no section matched.")
        lines.append(
            "next: search again with other words from the question; if nothing matches, "
            "the documentation does not cover it."
        )
        return "\n".join(lines)
    lines.append(f"Results: {len(hits)} hits")
    if READ_PAGE in surface.enabled:
        first = hits[0]
        target = f'page_url="{first.url}"'
        if pages.is_large(first.url):
            target += f', section="{pages.section_key(first)}"'
        lines.append(f"next: {READ_PAGE}({target}) to read hit 1 on its page")
    return "\n".join(lines)


async def search_hits(
    registry: EngineRegistry,
    query: str,
    *,
    variant: str,
    top_k: int,
    kinds: frozenset[str],
    locales: frozenset[str],
    exclude_ids: set[str] | None,
) -> list[Hit]:
    """The ranked chunks ``POST /search`` returns, after validating its filters."""
    bad_kinds = sorted(kinds - KINDS)
    if bad_kinds:
        raise bad_param(
            f"unknown page kind(s) {bad_kinds}", f"kinds are {sorted(KINDS)}; omit for no filter"
        )
    # Before the config, so an unknown variant never surfaces as a locale hint:
    # the config constructor validates the variant too, but with a message this
    # would wrongly answer as if locales were the problem.
    engine = registry.get(variant)
    try:
        RetrievalConfig(variant=variant, top_k=top_k, kinds=kinds, locales=locales)
    except ValidationError as exc:
        raise bad_param(
            str(exc), "locales look like 'en' or 'pt-BR'; kinds are doc, api, model"
        ) from exc
    try:
        return await engine.search(
            query,
            exclude_ids=exclude_ids,
            top_k=top_k,
            kinds=kinds or None,
            locales=locales or None,
        )
    except RetrieverException as exc:
        raise api_upstream("search", exc) from exc


__all__ = [
    "MAX_HITS",
    "PREFIX_LIST_MAX",
    "SCOPED_HITS",
    "list_pages_under",
    "search",
    "search_hits",
]
