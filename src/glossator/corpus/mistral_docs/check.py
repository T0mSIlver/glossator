"""Verify the built corpus against the live site.

Two things can silently rot: a URL that stops resolving, and an anchor that no longer
exists on the page it points at. Both would turn a citation into a dead link, so both
are checked against production rather than against the repo.
"""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import httpx
import structlog

from .fences import iter_lines
from .frontmatter import split as split_frontmatter
from .writer import MANIFEST_NAME

log = structlog.get_logger(__name__)

MAX_CONCURRENCY = 8
REQUEST_TIMEOUT = 45.0
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})
RETRY_DELAY_SECONDS = 2.0
USER_AGENT = "glossator-corpus-check/1.0 (+https://github.com/mistralai/platform-docs-public)"

_ANCHOR = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.*?)\s+\{#(?P<anchor>[^}]+)\}\s*$")


@dataclass
class UrlResult:
    url: str
    status: int
    redirect_target: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        # Only 200 passes. The manifest URL is what a citation points at, so a redirect
        # means the corpus is carrying a stale path even though the content still exists.
        return self.error is None and self.status == 200

    @property
    def failed(self) -> bool:
        return not self.ok


@dataclass
class AnchorResult:
    url: str
    anchor: str
    found_in_html: bool
    found_in_toc: bool
    error: str | None = None

    @property
    def ok(self) -> bool:
        # The DOM id is what a `#anchor` link scrolls to. The RSC table of contents is
        # reported alongside it but cannot stand in for it: it lists entries the page
        # never renders an id for.
        return self.error is None and self.found_in_html


@dataclass
class CheckReport:
    urls: list[UrlResult] = field(default_factory=list)
    anchors: list[AnchorResult] = field(default_factory=list)

    @property
    def url_failures(self) -> list[UrlResult]:
        return [result for result in self.urls if result.failed]

    @property
    def not_found(self) -> list[UrlResult]:
        return [result for result in self.urls if result.status >= 400]

    @property
    def redirects(self) -> list[UrlResult]:
        return [result for result in self.urls if 300 <= result.status < 400]

    @property
    def anchor_failures(self) -> list[AnchorResult]:
        return [result for result in self.anchors if not result.ok]

    @property
    def passed(self) -> bool:
        return not self.url_failures and not self.anchor_failures


@dataclass(frozen=True)
class PageAnchors:
    url: str
    path: str
    anchors: tuple[str, ...]


def read_manifest(corpus_dir: Path) -> list[dict[str, str]]:
    payload = json.loads((corpus_dir / MANIFEST_NAME).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{corpus_dir / MANIFEST_NAME} is not a manifest list")
    return payload


def collect_anchors(corpus_dir: Path) -> list[PageAnchors]:
    """Read every `{#anchor}` a page emitted, in file order."""
    pages: list[PageAnchors] = []
    for entry in read_manifest(corpus_dir):
        path = corpus_dir / entry["path"]
        _, body = split_frontmatter(path.read_text(encoding="utf-8"))
        anchors = [
            match.group("anchor")
            for line, in_fence in iter_lines(body)
            if not in_fence
            for match in [_ANCHOR.match(line)]
            if match is not None
        ]
        pages.append(PageAnchors(url=entry["url"], path=entry["path"], anchors=tuple(anchors)))
    return pages


async def run_live_check(
    corpus_dir: Path,
    check_anchors: bool = True,
    concurrency: int = MAX_CONCURRENCY,
) -> CheckReport:
    """HEAD every manifest URL and verify every emitted anchor on the live page."""
    report = CheckReport()
    pages = collect_anchors(corpus_dir)
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
    semaphore = asyncio.Semaphore(concurrency)
    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient(
        timeout=REQUEST_TIMEOUT, limits=limits, headers=headers, follow_redirects=False
    ) as client:
        report.urls = list(
            await asyncio.gather(*(_head(client, semaphore, page.url) for page in pages))
        )
        if check_anchors:
            with_anchors = [page for page in pages if page.anchors]
            results = await asyncio.gather(
                *(_check_page_anchors(client, semaphore, page) for page in with_anchors)
            )
            report.anchors = [result for page in results for result in page]

    log.info(
        "live check finished",
        urls=len(report.urls),
        url_failures=len(report.url_failures),
        redirects=len(report.redirects),
        anchors=len(report.anchors),
        anchor_failures=len(report.anchor_failures),
    )
    return report


async def _request(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    """One polite request: bounded concurrency, one retry on 429 or 5xx."""
    async with semaphore:
        response = await client.request(method, url, headers=headers)
        if response.status_code in RETRY_STATUS:
            await asyncio.sleep(RETRY_DELAY_SECONDS)
            response = await client.request(method, url, headers=headers)
        return response


async def _head(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, url: str) -> UrlResult:
    try:
        response = await _request(client, semaphore, "HEAD", url)
    except httpx.HTTPError as error:
        return UrlResult(url=url, status=0, error=repr(error))
    target = response.headers.get("location") if 300 <= response.status_code < 400 else None
    return UrlResult(url=url, status=response.status_code, redirect_target=target)


async def _check_page_anchors(
    client: httpx.AsyncClient, semaphore: asyncio.Semaphore, page: PageAnchors
) -> list[AnchorResult]:
    """Fetch the page once as HTML and once as an RSC payload, then match anchors.

    `SectionTab` and FAQ anchors render as `id` attributes; the RSC payload carries the
    table of contents, which is the site's own record of what is deep-linkable.
    """
    try:
        html = await _request(client, semaphore, "GET", page.url)
        rsc = await _request(client, semaphore, "GET", page.url, headers={"RSC": "1"})
    except httpx.HTTPError as error:
        return [
            AnchorResult(page.url, anchor, False, False, repr(error)) for anchor in page.anchors
        ]
    html_body = html.text if html.status_code == 200 else ""
    toc_body = rsc.text if rsc.status_code == 200 else ""
    return [
        AnchorResult(
            url=page.url,
            anchor=anchor,
            found_in_html=f'id="{anchor}"' in html_body,
            found_in_toc=f'"id":"{anchor}"' in toc_body,
        )
        for anchor in page.anchors
    ]


def format_report(report: CheckReport) -> str:
    lines = [
        "live check",
        f"  urls checked     {len(report.urls)}",
        f"  200              {sum(1 for r in report.urls if r.status == 200)}",
        f"  redirects        {len(report.redirects)} (counted as failures)",
        f"  4xx or transport {len(report.not_found) + sum(1 for r in report.urls if r.error)}",
        f"  failures         {len(report.url_failures)}",
        f"  anchors checked  {len(report.anchors)}",
        f"  anchors ok       {sum(1 for r in report.anchors if r.ok)}",
        f"  anchors in html  {sum(1 for r in report.anchors if r.found_in_html)}",
        f"  anchors in toc   {sum(1 for r in report.anchors if r.found_in_toc)}",
        f"  anchor failures  {len(report.anchor_failures)}",
    ]
    if report.redirects:
        lines += ["", "redirects (a manifest url must be canonical, so these fail)"]
        lines += [f"  {r.status} {r.url} -> {r.redirect_target}" for r in report.redirects]
    other_failures = [r for r in report.url_failures if r not in report.redirects]
    if other_failures:
        lines += ["", "url failures"]
        lines += [f"  {r.status or r.error} {r.url}" for r in other_failures]
    if report.anchor_failures:
        lines += ["", "anchor failures"]
        lines += [
            f"  {r.url}#{r.anchor}" + (f" ({r.error})" if r.error else "")
            for r in report.anchor_failures
        ]
    return "\n".join(lines)
