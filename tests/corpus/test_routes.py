"""Redirect application and breadcrumb labelling."""

from __future__ import annotations

from pathlib import Path

import pytest

from glossator.corpus.mistral_docs.routes import (
    RedirectRule,
    RedirectTable,
    enumerate_routes,
    title_case,
)

REDIRECT_TS = """
const rawRedirects: RedirectRule[] = [
  { source: "/capabilities/function_calling", destination: "/studio/conversations/function-calling", permanent: true },
  { source: "/studio-api/:path*", destination: "/studio/:path*", permanent: true },
  { source: "/products/:path*", destination: "/getting-started/platform-overview", permanent: true },
  { source: "/studio/search-toolkit/:path*", destination: "/studio/search/search-toolkit/:path*", permanent: true },
];
"""


@pytest.fixture
def table(tmp_path: Path) -> RedirectTable:
    path = tmp_path / "redirect.ts"
    path.write_text(REDIRECT_TS, encoding="utf-8")
    return RedirectTable.parse(path)


def test_exact_rule(table: RedirectTable) -> None:
    assert (
        table.resolve("/capabilities/function_calling") == "/studio/conversations/function-calling"
    )


def test_route_without_a_rule_is_unchanged(table: RedirectTable) -> None:
    assert table.resolve("/studio/conversations/vision") == "/studio/conversations/vision"


def test_wildcard_rule_keeps_the_tail(table: RedirectTable) -> None:
    assert table.resolve("/studio-api/workflows/basics") == "/studio/workflows/basics"


def test_wildcard_rule_without_a_tail_in_the_destination_drops_it(table: RedirectTable) -> None:
    # Next.js discards the captured segments when the destination has no `:path*`.
    assert table.resolve("/products/anything") == "/getting-started/platform-overview"


def test_rules_are_applied_until_they_stop_matching(table: RedirectTable) -> None:
    assert (
        table.resolve("/studio-api/search-toolkit/quickstart")
        == "/studio/search/search-toolkit/quickstart"
    )


def test_redirect_cycles_terminate() -> None:
    table = RedirectTable(
        [RedirectRule("/a", "/b"), RedirectRule("/b", "/a")],
    )
    assert table.resolve("/a") in {"/a", "/b"}


def test_title_case_matches_the_site() -> None:
    assert title_case("agent-tools") == "Agent Tools"
    assert title_case("speech_to_text") == "Speech To Text"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_enumeration_skips_partials_and_carries_breadcrumbs(tmp_path: Path) -> None:
    docs = tmp_path / "src" / "content" / "en" / "docs"
    _write(tmp_path / "redirect.ts", REDIRECT_TS)
    _write(docs / "studio" / "_category_.json", '{"label": "Studio"}')
    _write(docs / "studio" / "conversations" / "_category_.json", '{"label": "Conversations"}')
    _write(
        docs / "studio" / "conversations" / "function-calling" / "page.mdx",
        "---\ntitle: Function Calling\n---\n\n# Function Calling\n",
    )
    _write(
        docs / "studio" / "conversations" / "_shared" / "page.mdx",
        "---\ntitle: Shared\n---\n",
    )
    _write(
        docs / "studio" / "observability" / "_category_.json", '{"label": "Obs", "hidden": true}'
    )
    _write(docs / "studio" / "observability" / "traces" / "page.mdx", "---\ntitle: Traces\n---\n")

    result = enumerate_routes(tmp_path)
    routes = {route.route: route for route in result.routes}

    assert set(routes) == {
        "/studio/conversations/function-calling",
        "/studio/observability/traces",
    }
    page = routes["/studio/conversations/function-calling"]
    assert page.breadcrumbs == ["Studio", "Conversations"]
    assert page.hidden is False
    assert routes["/studio/observability/traces"].hidden is True


def test_a_directory_page_title_wins_over_its_category_label(tmp_path: Path) -> None:
    docs = tmp_path / "src" / "content" / "en" / "docs"
    _write(tmp_path / "redirect.ts", REDIRECT_TS)
    _write(
        docs / "studio" / "agents" / "agent-tools" / "_category_.json", '{"label": "Agent Tools"}'
    )
    _write(
        docs / "studio" / "agents" / "agent-tools" / "page.mdx",
        "---\ntitle: Agents Tools Overview\n---\n",
    )
    _write(
        docs / "studio" / "agents" / "agent-tools" / "websearch" / "page.mdx",
        "---\ntitle: Web Search\n---\n",
    )

    result = enumerate_routes(tmp_path)
    child = next(r for r in result.routes if r.route.endswith("/websearch"))
    assert child.breadcrumbs == ["Studio", "Agents", "Agents Tools Overview"]
