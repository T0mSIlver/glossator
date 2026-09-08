"""Enumerate English documentation pages and map each to its canonical URL.

The routing rule comes from the docs repo's `route-utils.ts`: a directory under
`src/content/en/docs` holding a `page.mdx` is a route at its path with the `docs/`
prefix dropped; `_`-prefixed directories are partials, not routes. Legacy paths are
normalized through `redirect.ts` (D-002). Hidden pages stay in (D-004).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
import structlog

from . import LOCALE, SITE_ORIGIN
from .frontmatter import split as split_frontmatter

log = structlog.get_logger(__name__)

PAGE_BASENAMES = ("page.mdx", "page.md")
META_BASENAMES = ("_meta.mdx", "_meta.md")
CATEGORY_JSON = "_category_.json"

SEARCH_DOCS_URL = f"{SITE_ORIGIN}/search-docs-en.json"

_REDIRECT_RULE = re.compile(
    r"source:\s*(['\"])(?P<source>.*?)\1\s*,\s*destination:\s*(['\"])(?P<destination>.*?)\3",
    re.DOTALL,
)
_DASH_UNDERSCORE = re.compile(r"[-_]+")
_WHITESPACE = re.compile(r"\s+")
_WORD_START = re.compile(r"\b\w")


@dataclass(frozen=True)
class RedirectRule:
    """One `redirect.ts` entry; `:path*` is the only wildcard the table uses."""

    source: str
    destination: str

    @property
    def is_wildcard(self) -> bool:
        return self.source.endswith("/:path*")

    def apply(self, route: str) -> str | None:
        if self.is_wildcard:
            prefix = self.source[: -len("/:path*")]
            if route != prefix and not route.startswith(prefix + "/"):
                return None
            if not self.destination.endswith("/:path*"):
                # No `:path*` on the destination: Next.js drops the captured tail and
                # sends every matching path to the one fixed target.
                return self.destination
            return self.destination[: -len("/:path*")] + route[len(prefix) :]
        return self.destination if route == self.source else None


class RedirectTable:
    """The `rawRedirects` array from `redirect.ts`, applied until it reaches a fixpoint."""

    MAX_HOPS = 8

    def __init__(self, rules: list[RedirectRule]) -> None:
        self.rules = rules

    @classmethod
    def parse(cls, redirect_ts: Path) -> RedirectTable:
        source = redirect_ts.read_text(encoding="utf-8")
        rules = [
            RedirectRule(source=match.group("source"), destination=match.group("destination"))
            for match in _REDIRECT_RULE.finditer(source)
        ]
        if not rules:
            raise ValueError(f"no redirect rules parsed from {redirect_ts}")
        return cls(rules)

    def resolve(self, route: str) -> str:
        seen = {route}
        current = route
        for _ in range(self.MAX_HOPS):
            for rule in self.rules:
                target = rule.apply(current)
                if target is not None and target != current:
                    if target in seen:
                        return current
                    seen.add(target)
                    current = target
                    break
            else:
                return current
        return current


@dataclass(frozen=True)
class DocRoute:
    """One English docs page and everything the writer needs to place it."""

    route: str
    source_path: str
    title: str
    breadcrumbs: list[str]
    hidden: bool
    redirected_from: str | None = None

    @property
    def url_path(self) -> str:
        return self.route


@dataclass
class BreadcrumbMismatch:
    route: str
    computed: list[str]
    expected: list[str]


@dataclass
class RouteEnumeration:
    routes: list[DocRoute] = field(default_factory=list)
    breadcrumb_mismatches: list[BreadcrumbMismatch] = field(default_factory=list)
    unchecked_breadcrumbs: list[str] = field(default_factory=list)
    unreachable: list[DocRoute] = field(default_factory=list)


def title_case(segment: str) -> str:
    """Port of `titleCase` in `src/scripts/build-search-index.ts`."""
    text = _DASH_UNDERSCORE.sub(" ", segment)
    text = _WHITESPACE.sub(" ", text).strip()
    return _WORD_START.sub(lambda m: m.group(0).upper(), text)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _page_file(directory: Path) -> Path | None:
    for name in PAGE_BASENAMES:
        candidate = directory / name
        if candidate.is_file():
            return candidate
    return None


def _meta_file(directory: Path) -> Path | None:
    for name in META_BASENAMES:
        candidate = directory / name
        if candidate.is_file():
            return candidate
    return None


def _frontmatter_of(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    data, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    return data


def _directory_title(directory: Path) -> str:
    """Port of `titleFor` in `build-search-index.ts`: page title, category label, name."""
    page = _page_file(directory)
    if page is not None:
        title = _frontmatter_of(page).get("title")
        if isinstance(title, str) and title.strip():
            return title.strip()
    label = _read_json(directory / CATEGORY_JSON).get("label")
    if isinstance(label, str) and label.strip():
        return label.strip()
    return title_case(directory.name)


def _is_hidden_flag(value: Any) -> bool:
    return value is True or (isinstance(value, str) and value.lower() == "true")


def _hidden_along_path(docs_root: Path, parts: list[str]) -> bool:
    """A page is hidden when it, or any ancestor category, sets `hidden: true`."""
    directory = docs_root
    for part in parts:
        directory = directory / part
        if _is_hidden_flag(_read_json(directory / CATEGORY_JSON).get("hidden")):
            return True
        if _is_hidden_flag(_frontmatter_of(_meta_file(directory)).get("hidden")):
            return True
    return _is_hidden_flag(_frontmatter_of(_page_file(directory)).get("hidden"))


def _walk_route_dirs(root: Path, parts: list[str]) -> list[list[str]]:
    found: list[list[str]] = []
    if parts and _page_file(root) is not None:
        found.append(list(parts))
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("_") or child.name.startswith("["):
            continue
        found.extend(_walk_route_dirs(child, [*parts, child.name]))
    return found


def fetch_search_docs(cache_dir: Path, url: str = SEARCH_DOCS_URL, refresh: bool = False) -> Path:
    """Download the site's own search index, which is the breadcrumb reference."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / "search-docs-en.json"
    if cached.is_file() and not refresh:
        return cached
    log.info("fetching search index", url=url)
    response = httpx.get(url, timeout=60.0, follow_redirects=True)
    response.raise_for_status()
    cached.write_bytes(response.content)
    return cached


def load_expected_breadcrumbs(search_docs: Path) -> dict[str, list[str]]:
    """URL path -> breadcrumb titles from the site's own `search-docs-en.json`.

    The site's list ends with the page itself; ours names only the ancestors, so the
    last entry is dropped here to make the two comparable.
    """
    payload = json.loads(search_docs.read_text(encoding="utf-8"))
    expected: dict[str, list[str]] = {}
    prefix = f"/{LOCALE}"
    for entry in payload:
        if not isinstance(entry, dict) or entry.get("type") != "docs":
            continue
        url = entry.get("url")
        crumbs = entry.get("breadcrumbs")
        if not isinstance(url, str) or not isinstance(crumbs, list):
            continue
        route = url[len(prefix) :] if url.startswith(prefix) else url
        titles = [c.get("title", "") for c in crumbs if isinstance(c, dict)]
        expected[route or "/"] = titles[:-1]
    return expected


def enumerate_routes(
    repo_root: Path,
    expected_breadcrumbs: dict[str, list[str]] | None = None,
) -> RouteEnumeration:
    """Enumerate every English docs page with its canonical URL and breadcrumbs."""
    docs_root = repo_root / "src" / "content" / LOCALE / "docs"
    if not docs_root.is_dir():
        raise FileNotFoundError(f"missing docs content root: {docs_root}")
    redirects = RedirectTable.parse(repo_root / "redirect.ts")

    result = RouteEnumeration()
    for parts in _walk_route_dirs(docs_root, []):
        raw_route = "/" + "/".join(parts)
        route = redirects.resolve(raw_route)
        page = _page_file(docs_root.joinpath(*parts))
        assert page is not None  # _walk_route_dirs only yields directories with a page
        meta = _frontmatter_of(page)
        title = meta.get("title")
        if not isinstance(title, str) or not title.strip():
            title = title_case(parts[-1])
        breadcrumbs = [
            _directory_title(docs_root.joinpath(*parts[: index + 1]))
            for index in range(len(parts) - 1)
        ]
        result.routes.append(
            DocRoute(
                route=route,
                source_path=str(page.relative_to(repo_root)),
                title=title.strip(),
                breadcrumbs=breadcrumbs,
                hidden=_hidden_along_path(docs_root, parts),
                redirected_from=raw_route if route != raw_route else None,
            )
        )

    result.routes.sort(key=lambda route: route.route)
    _drop_unreachable(result)
    _dedupe_routes(result)
    if expected_breadcrumbs is not None:
        _cross_check_breadcrumbs(result, expected_breadcrumbs)
    return result


def _drop_unreachable(result: RouteEnumeration) -> None:
    """Drop pages whose canonical URL nothing serves.

    A redirect rule can point a legacy path at a URL that no page.mdx produces, which
    leaves the source file on disk but its content unreachable on the site. Such a
    page cannot be cited, so it is reported and left out.
    """
    direct = {route.route for route in result.routes if route.redirected_from is None}
    kept: list[DocRoute] = []
    for route in result.routes:
        if route.redirected_from is not None and route.route not in direct:
            result.unreachable.append(route)
            log.warning(
                "route redirects to a url no page serves",
                source=route.redirected_from,
                target=route.route,
                path=route.source_path,
            )
            continue
        kept.append(route)
    result.routes = kept


def _dedupe_routes(result: RouteEnumeration) -> None:
    """Two source paths can redirect onto one canonical URL; keep the direct page."""
    by_route: dict[str, DocRoute] = {}
    for route in result.routes:
        existing = by_route.get(route.route)
        if existing is None:
            by_route[route.route] = route
            continue
        keep = existing if existing.redirected_from is None else route
        drop = route if keep is existing else existing
        log.warning(
            "duplicate canonical url",
            url=keep.route,
            kept=keep.source_path,
            dropped=drop.source_path,
        )
        by_route[route.route] = keep
    result.routes = sorted(by_route.values(), key=lambda route: route.route)


def _cross_check_breadcrumbs(
    result: RouteEnumeration, expected_breadcrumbs: dict[str, list[str]]
) -> None:
    for route in result.routes:
        expected = expected_breadcrumbs.get(route.route)
        if expected is None:
            result.unchecked_breadcrumbs.append(route.route)
            continue
        if expected != route.breadcrumbs:
            result.breadcrumb_mismatches.append(
                BreadcrumbMismatch(route=route.route, computed=route.breadcrumbs, expected=expected)
            )
