"""The live checker's verdicts, against a mocked transport."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest

from glossator.corpus.mistral_docs import check as check_module
from glossator.corpus.mistral_docs.check import (
    AnchorResult,
    CheckReport,
    UrlResult,
    collect_anchors,
    format_report,
    run_live_check,
)

PAGE = """---
url: https://docs.mistral.ai/studio/example
title: Example
breadcrumbs: [Studio]
kind: doc
locale: en
source_path: src/content/en/docs/studio/example/page.mdx
source_commit: abc123
---

# Example

## Before you start {#before-you-start}

```text
## Not a heading {#not-an-anchor}
```

## Five steps {#five-steps}
"""

RunCheck = Callable[[Path, Callable[[httpx.Request], httpx.Response]], CheckReport]

MANIFEST = [
    {
        "url": "https://docs.mistral.ai/studio/example",
        "path": "studio/example.md",
        "title": "Example",
        "kind": "doc",
        "source_path": "src/content/en/docs/studio/example/page.mdx",
        "source_commit": "abc123",
        "sha256": "unused",
    }
]


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    (tmp_path / "studio").mkdir()
    (tmp_path / "studio" / "example.md").write_text(PAGE, encoding="utf-8")
    (tmp_path / "manifest.json").write_text(json.dumps(MANIFEST), encoding="utf-8")
    return tmp_path


@pytest.fixture
def run_check(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[Path, Callable[[httpx.Request], httpx.Response]], CheckReport]:
    """Run the checker with every request served by a handler instead of the network."""

    def run(corpus: Path, handler: Callable[[httpx.Request], httpx.Response]) -> CheckReport:
        original = httpx.AsyncClient

        def client(**kwargs: object) -> httpx.AsyncClient:
            kwargs.pop("limits", None)
            return original(transport=httpx.MockTransport(handler), **kwargs)  # type: ignore[arg-type]

        monkeypatch.setattr(httpx, "AsyncClient", client)
        monkeypatch.setattr(check_module, "RETRY_DELAY_SECONDS", 0.0)
        return asyncio.run(run_live_check(corpus))

    return run


def test_anchors_are_read_from_headings_outside_fences(corpus: Path) -> None:
    pages = collect_anchors(corpus)
    assert [page.anchors for page in pages] == [("before-you-start", "five-steps")]


def test_a_200_page_with_both_ids_passes(corpus: Path, run_check: RunCheck) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "HEAD":
            return httpx.Response(200)
        return httpx.Response(200, text='<h2 id="before-you-start"></h2><h2 id="five-steps"></h2>')

    report = run_check(corpus, handler)
    assert report.passed
    assert [r.status for r in report.urls] == [200]
    assert len(report.anchor_failures) == 0


def test_a_redirect_fails_but_keeps_its_target(corpus: Path, run_check: RunCheck) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "HEAD":
            return httpx.Response(308, headers={"location": "https://docs.mistral.ai/moved"})
        return httpx.Response(200, text='<h2 id="before-you-start"></h2><h2 id="five-steps"></h2>')

    report = run_check(corpus, handler)
    assert not report.passed
    assert report.url_failures == report.redirects
    assert report.redirects[0].redirect_target == "https://docs.mistral.ai/moved"
    assert "https://docs.mistral.ai/moved" in format_report(report)


def test_a_404_fails(corpus: Path, run_check: RunCheck) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "HEAD":
            return httpx.Response(404)
        return httpx.Response(404)

    report = run_check(corpus, handler)
    assert not report.passed
    assert [r.status for r in report.not_found] == [404]


def test_an_anchor_only_in_the_rsc_toc_fails(corpus: Path, run_check: RunCheck) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "HEAD":
            return httpx.Response(200)
        if request.headers.get("RSC") == "1":
            return httpx.Response(200, text='{"id":"before-you-start"},{"id":"five-steps"}')
        return httpx.Response(200, text="<h2>no ids here</h2>")

    report = run_check(corpus, handler)
    assert not report.passed
    assert len(report.anchor_failures) == 2
    assert all(r.found_in_toc and not r.found_in_html for r in report.anchors)


def test_one_retry_after_a_429(corpus: Path, run_check: RunCheck) -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.method)
        if request.method == "HEAD" and calls.count("HEAD") == 1:
            return httpx.Response(429)
        if request.method == "HEAD":
            return httpx.Response(200)
        return httpx.Response(200, text='<h2 id="before-you-start"></h2><h2 id="five-steps"></h2>')

    report = run_check(corpus, handler)
    assert calls.count("HEAD") == 2
    assert report.passed


def test_a_transport_error_is_a_failure(corpus: Path, run_check: RunCheck) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route to host")

    report = run_check(corpus, handler)
    assert not report.passed
    assert report.urls[0].error is not None
    assert all(result.error is not None for result in report.anchors)


def test_url_result_only_passes_on_200() -> None:
    assert UrlResult("u", 200).ok
    assert not UrlResult("u", 301).ok
    assert not UrlResult("u", 404).ok
    assert not UrlResult("u", 0, error="boom").ok


def test_anchor_result_needs_the_dom_id() -> None:
    assert AnchorResult("u", "a", found_in_html=True, found_in_toc=False).ok
    assert not AnchorResult("u", "a", found_in_html=False, found_in_toc=True).ok
