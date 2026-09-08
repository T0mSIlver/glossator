"""Build the whole corpus: docs pages, API reference, model cards, manifest."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import structlog

from . import PINNED_REF, SITE_ORIGIN
from .fences import strip_fenced_lines, strip_inline_code
from .mdx import MdxNormalizer
from .models import MODELS_URL_PREFIX, load_catalog, render_capability_matrix, render_model_page
from .openapi import OPENAPI_URL, OpenApiSource, load_openapi, render_api_pages
from .routes import BreadcrumbMismatch, enumerate_routes, load_expected_breadcrumbs
from .source import DocsCheckout
from .writer import KIND_API, KIND_DOC, KIND_MODEL, CorpusPage, write_corpus

log = structlog.get_logger(__name__)

JSX_RESIDUE = re.compile(r"<[A-Z][A-Za-z]*[ >/]")


@dataclass
class BuildSummary:
    """Everything the CLI prints after a build."""

    ref: str = PINNED_REF
    commit: str = ""
    openapi_md5: str = ""
    openapi_origin: str = ""
    pages_by_kind: Counter[str] = field(default_factory=Counter)
    pages_by_section: Counter[str] = field(default_factory=Counter)
    hidden_pages: int = 0
    stripped_components: Counter[str] = field(default_factory=Counter)
    stripped_pages: dict[str, int] = field(default_factory=dict)
    breadcrumb_mismatches: list[BreadcrumbMismatch] = field(default_factory=list)
    breadcrumbs_unchecked: int = 0
    anchors_total: int = 0
    anchors_by_kind: Counter[str] = field(default_factory=Counter)
    pages_without_anchors: int = 0
    max_anchors: tuple[str, int] = ("", 0)
    partials_inlined: int = 0
    residue_pages: list[str] = field(default_factory=list)
    missing_operations: list[str] = field(default_factory=list)
    redirected_routes: list[tuple[str, str]] = field(default_factory=list)

    @property
    def total_pages(self) -> int:
        return sum(self.pages_by_kind.values())


def build_corpus(
    checkout: DocsCheckout,
    out_dir: Path,
    cache_dir: Path,
    search_docs: Path | None = None,
    openapi_offline: Path | None = None,
    openapi_url: str = OPENAPI_URL,
    refresh_openapi: bool = False,
) -> BuildSummary:
    """Normalize every source into pages and write them under `out_dir`."""
    summary = BuildSummary(ref=checkout.ref, commit=checkout.commit)
    pages: list[CorpusPage] = []

    pages += _build_doc_pages(checkout, summary, search_docs)
    openapi = load_openapi(
        cache_dir, url=openapi_url, offline_path=openapi_offline, refresh=refresh_openapi
    )
    pages += _build_api_pages(checkout, openapi, summary)
    pages += _build_model_pages(checkout, summary)

    for page in pages:
        summary.pages_by_kind[page.kind] += 1
        summary.pages_by_section[_section(page.url_path)] += 1
        body = strip_inline_code(strip_fenced_lines(page.markdown))
        if JSX_RESIDUE.search(body):
            summary.residue_pages.append(page.url_path)

    license_path = checkout.path / "LICENSE"
    license_text = license_path.read_text(encoding="utf-8") if license_path.is_file() else None
    if license_text is None:
        log.warning("upstream LICENSE not found", path=str(license_path))
    write_corpus(pages, out_dir, checkout.commit, license_text)
    log.info("corpus written", pages=len(pages), out_dir=str(out_dir))
    return summary


def _build_doc_pages(
    checkout: DocsCheckout, summary: BuildSummary, search_docs: Path | None
) -> list[CorpusPage]:
    expected = load_expected_breadcrumbs(search_docs) if search_docs is not None else None
    enumeration = enumerate_routes(checkout.path, expected)
    summary.breadcrumb_mismatches = enumeration.breadcrumb_mismatches
    summary.breadcrumbs_unchecked = len(enumeration.unchecked_breadcrumbs)
    summary.redirected_routes = [
        (route.redirected_from, route.route)
        for route in enumeration.routes
        if route.redirected_from is not None
    ]

    pages: list[CorpusPage] = []
    for route in enumeration.routes:
        normalizer = MdxNormalizer(f"{SITE_ORIGIN}{route.route}")
        render = normalizer.render_page(checkout.path / route.source_path, route.title)
        summary.stripped_components.update(render.stripped)
        if render.stripped:
            summary.stripped_pages[route.route] = sum(render.stripped.values())
        summary.partials_inlined += render.partials
        _record_anchors(summary, route.route, len(render.anchors), KIND_DOC)
        if route.hidden:
            summary.hidden_pages += 1
        pages.append(
            CorpusPage(
                url_path=route.route,
                title=route.title,
                kind=KIND_DOC,
                markdown=render.markdown,
                source_path=route.source_path,
                breadcrumbs=route.breadcrumbs,
                hidden=route.hidden,
            )
        )
    return pages


def _build_api_pages(
    checkout: DocsCheckout, openapi: OpenApiSource, summary: BuildSummary
) -> list[CorpusPage]:
    summary.openapi_md5 = openapi.md5
    summary.openapi_origin = openapi.origin
    result = render_api_pages(checkout.path, openapi)
    summary.missing_operations = result.missing_operations
    pages: list[CorpusPage] = []
    for page, markdown in result.pages:
        _record_anchors(summary, page.url_path, len(page.operations), KIND_API)
        pages.append(
            CorpusPage(
                url_path=page.url_path,
                title=f"{page.label} API",
                kind=KIND_API,
                markdown=markdown,
                source_path="openapi.yaml",
                breadcrumbs=["API", page.label],
                extra={"openapi_md5": openapi.md5, "openapi_url": openapi.origin},
            )
        )
    return pages


def _build_model_pages(checkout: DocsCheckout, summary: BuildSummary) -> list[CorpusPage]:
    catalog = load_catalog(checkout.path)
    pages = [
        CorpusPage(
            url_path=MODELS_URL_PREFIX,
            title="Model capability matrix",
            kind=KIND_MODEL,
            markdown=render_capability_matrix(catalog),
            source_path="src/schema/models",
            breadcrumbs=["Models"],
        )
    ]
    for model in catalog.models:
        pages.append(
            CorpusPage(
                url_path=model.url_path,
                title=model.name,
                kind=KIND_MODEL,
                markdown=render_model_page(model, catalog),
                source_path=model.source_path,
                breadcrumbs=["Models"],
            )
        )
    for page in pages:
        _record_anchors(summary, page.url_path, 0, KIND_MODEL)
    return pages


def _record_anchors(summary: BuildSummary, url_path: str, count: int, kind: str) -> None:
    summary.anchors_total += count
    summary.anchors_by_kind[kind] += count
    if count == 0:
        summary.pages_without_anchors += 1
    if count > summary.max_anchors[1]:
        summary.max_anchors = (url_path, count)


def _section(url_path: str) -> str:
    parts = [part for part in url_path.split("/") if part]
    return parts[0] if parts else "/"


def format_summary(summary: BuildSummary) -> str:
    """Render the run summary the CLI prints to stdout."""
    lines: list[str] = [
        "corpus build summary",
        f"  ref              {summary.ref}",
        f"  commit           {summary.commit}",
        f"  openapi          md5 {summary.openapi_md5} from {summary.openapi_origin}",
        f"  pages            {summary.total_pages}",
    ]
    lines.append("  by kind          " + _counter_line(summary.pages_by_kind))
    lines.append("  by section       " + _counter_line(summary.pages_by_section))
    lines.append(f"  hidden pages     {summary.hidden_pages}")
    lines.append(f"  partials inlined {summary.partials_inlined}")
    lines.append(
        f"  anchors          {summary.anchors_total} total, "
        f"{summary.pages_without_anchors} pages with none, "
        f"max {summary.max_anchors[1]} on {summary.max_anchors[0] or 'n/a'}"
    )
    lines.append("  anchors by kind  " + _counter_line(summary.anchors_by_kind))

    lines.append("")
    lines.append("stripped components (kept their text children)")
    if summary.stripped_components:
        for name, count in summary.stripped_components.most_common():
            lines.append(f"  {count:5d}  {name}")
        lines.append(f"  on {len(summary.stripped_pages)} pages")
    else:
        lines.append("  none")

    lines.append("")
    lines.append(
        f"breadcrumb mismatches vs search-docs-en.json: {len(summary.breadcrumb_mismatches)}"
    )
    for mismatch in summary.breadcrumb_mismatches[:20]:
        lines.append(f"  {mismatch.route}: {mismatch.computed} != {mismatch.expected}")
    lines.append(f"  {summary.breadcrumbs_unchecked} routes absent from the site's search index")

    if summary.redirected_routes:
        lines.append("")
        lines.append("routes normalized through redirect.ts")
        for source, target in summary.redirected_routes:
            lines.append(f"  {source} -> {target}")

    if summary.residue_pages:
        lines.append("")
        lines.append(f"pages with JSX residue: {len(summary.residue_pages)}")
        lines += [f"  {url}" for url in summary.residue_pages[:20]]

    if summary.missing_operations:
        lines.append("")
        lines.append(
            f"operations on the site but not in the spec: {len(summary.missing_operations)}"
        )
        lines += [f"  {name}" for name in summary.missing_operations[:20]]

    return "\n".join(lines)


def _counter_line(counter: Counter[str]) -> str:
    grouped: dict[str, int] = defaultdict(int)
    for key, value in counter.items():
        grouped[key] += value
    return ", ".join(f"{key} {grouped[key]}" for key in sorted(grouped))
