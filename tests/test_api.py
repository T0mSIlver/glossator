"""HTTP route, validation, typed-error, and request-ID tests."""

import asyncio
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from httpx import ASGITransport
from mistralai.client.errors import MistralError
from mistralai.search.toolkit.retrieval.errors import RetrieverException
from structlog.testing import capture_logs

from entrypoints import api as api_module
from entrypoints.api import app, registry
from glossator.answer import service as answer_service
from glossator.answer.citations import Answer, Citation, Trace
from glossator.answer.config import AnswerConfig
from glossator.answer.llm import TokenUsage
from glossator.corpus.snapshots import SnapshotUnavailableError
from glossator.index.variants import VARIANTS

URL = "https://docs.mistral.ai/api/endpoint/chat"
ANCHOR = "streaming-responses"


def _hit(n: int = 1) -> Any:
    return SimpleNamespace(
        chunk_id=f"c{n}",
        score=0.831,
        url=URL,
        anchor=ANCHOR,
        citation_url=f"{URL}#{ANCHOR}",
        heading_path=("Chat completions", "Streaming"),
        heading_line="Chat completions > Streaming",
        page_title="Chat completions",
        kind="doc",
        locale="en",
        preview=lambda chars=240: "Server-sent events carry the response.",
        source_id=URL,
        start_offset=100 * n,
        end_offset=100 * n + 80,
        content="Server-sent events carry the response.",
        section_index=n,
    )


class FakeNavigation:
    def __init__(self, sections: list[Any]) -> None:
        self.sections = sections

    async def read(
        self, start: int | None = None, end: int | None = None, top_k: int = 20
    ) -> list[Any]:
        if start is not None:
            return [s for s in self.sections if (s.start_offset or 0) >= start][:top_k]
        return self.sections[:top_k]


class FakeEngine:
    def __init__(
        self,
        hits: list[Any] | None = None,
        sections: list[Any] | None = None,
        count: int = 4430,
        fail: Exception | None = None,
    ) -> None:
        self.config = SimpleNamespace(variant="sec1024")
        self.hits = hits if hits is not None else [_hit()]
        self.sections = sections if sections is not None else self.hits
        self.count = count
        self.fail = fail
        self.search_calls: list[dict[str, Any]] = []

    async def search(
        self,
        query: str,
        exclude_ids: set[str] | None = None,
        top_k: int | None = None,
        kinds: frozenset[str] | None = None,
        locales: frozenset[str] | None = None,
    ) -> list[Any]:
        self.search_calls.append(
            {
                "query": query,
                "exclude_ids": exclude_ids,
                "top_k": top_k,
                "kinds": kinds,
                "locales": locales,
            }
        )
        if self.fail:
            raise self.fail
        return self.hits

    def navigation_at(self, source_id: str, start: int = 0, end: int = 0) -> FakeNavigation:
        return FakeNavigation(self.sections)

    async def get_chunk(self, chunk_id: str) -> Any | None:
        return next((s for s in self.sections if s.chunk_id == chunk_id), None)

    async def document_count(self) -> int:
        if self.fail:
            raise self.fail
        return self.count


def _request(
    method: str,
    path: str,
    json: Any = None,
    headers: dict[str, str] | None = None,
    *,
    raise_app_exceptions: bool = True,
) -> httpx.Response:
    """One request through the real ASGI stack, in the repo's asyncio.run style."""

    async def run() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=raise_app_exceptions),
            base_url="http://test",
        ) as client:
            return await client.request(method, path, json=json, headers=headers)

    return asyncio.run(run())


@pytest.fixture(autouse=True)
def fresh_registry() -> Any:
    registry.engines.clear()
    engine = FakeEngine()
    registry.engines["sec1024"] = engine
    yield registry
    registry.engines.clear()


def _engine() -> FakeEngine:
    engine = registry.engines["sec1024"]
    assert isinstance(engine, FakeEngine)
    return engine


@pytest.fixture
def fake_ask(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Patch the service seam; record what the route forwarded."""
    calls: list[dict[str, Any]] = []

    async def _ask(
        question: str,
        *,
        strategy: str = "single_pass",
        variant: str = "sec1024",
        recorder: object = None,
        config: object = None,
        engine: object = None,
        llm: object = None,
    ) -> Answer:
        calls.append(
            {
                "question": question,
                "strategy": strategy,
                "variant": variant,
                "config": config,
                "engine": engine,
            }
        )
        return Answer(
            question=question,
            strategy=strategy,
            model="mistral-medium-2604",
            answer_markdown="It streams via server-sent events [1], [2].",
            citations=[
                Citation(
                    n=1,
                    url=URL,
                    anchor=ANCHOR,
                    chunk_id="c1",
                    quote="Server-sent events carry the response.",
                    verified=True,
                    fragment_url=(
                        f"{URL}#{ANCHOR}:~:text=Server%2Dsent%20events%20carry%20the%20response."
                    ),
                )
            ],
            trace=Trace(strategy=strategy, variant=variant, prompt_version="v1"),
            usage=TokenUsage(prompt_tokens=120, completion_tokens=30),
            latency_ms=1500.0,
            cost_usd=0.0004,
        )

    monkeypatch.setattr(answer_service, "ask", _ask)
    return calls


def test_ask_returns_the_answer_contract_with_trace_summary(
    fake_ask: list[dict[str, Any]],
) -> None:
    response = _request(
        "POST",
        "/ask",
        json={"question": "how do I stream a chat completion?", "strategy": "search_loop"},
        headers={"X-Request-Id": "req-42"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer_markdown"].startswith("It streams")
    assert body["citations"][0]["citation_url"] == f"{URL}#{ANCHOR}"
    assert body["citations"][0]["fragment_url"] == (
        f"{URL}#{ANCHOR}:~:text=Server%2Dsent%20events%20carry%20the%20response."
    )
    assert body["citations"][0]["verified"] is True
    assert body["trace"]["strategy"] == "search_loop"
    assert "search_loop on" in body["trace_summary"]
    assert body["usage"]["prompt_tokens"] == 120
    assert body["cost_usd"] == pytest.approx(0.0004)
    assert body["latency_ms"] == pytest.approx(1500.0)
    assert response.headers["X-Request-Id"] == "req-42"
    assert body["request_id"] == "req-42"
    assert fake_ask[0]["strategy"] == "search_loop"
    # The route reuses the registry's engine rather than building a new one.
    assert isinstance(fake_ask[0]["engine"], FakeEngine)


def test_ask_rejects_an_unknown_strategy_with_a_typed_error(
    fake_ask: list[dict[str, Any]],
) -> None:
    response = _request("POST", "/ask", json={"question": "q", "strategy": "teleport"})

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "E_BAD_PARAM"
    assert "teleport" in error["message"]
    assert "single_pass" in error["next"]


def test_ask_rejects_an_unknown_variant_with_a_typed_error(
    fake_ask: list[dict[str, Any]],
) -> None:
    response = _request("POST", "/ask", json={"question": "q", "variant": "sec2048"})

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "E_BAD_PARAM"
    assert "sec2048" in error["message"]
    assert "sec1024" in error["next"]


def test_ask_rejects_an_unpriced_model_with_a_typed_error(
    fake_ask: list[dict[str, Any]],
) -> None:
    response = _request("POST", "/ask", json={"question": "q", "model": "latest-maybe"})

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "E_BAD_PARAM"
    assert "latest-maybe" in error["message"]
    assert "ministral-14b-2512" in error["next"]


def test_ask_validation_errors_use_the_typed_shape() -> None:
    response = _request("POST", "/ask", json={"question": ""})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "E_BAD_PARAM"
    assert "question" in error["message"]
    assert error["next"]


def test_search_returns_hits_with_citation_fields() -> None:
    response = _request("POST", "/search", json={"query": "streaming", "top_k": 3})

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "streaming"
    assert body["variant"] == "sec1024"
    hit = body["hits"][0]
    assert hit["url"] == URL
    assert hit["anchor"] == ANCHOR
    assert hit["citation_url"] == f"{URL}#{ANCHOR}"
    assert hit["heading_path"] == ["Chat completions", "Streaming"]
    assert "Server-sent events" in hit["preview"]
    assert hit["score"] == pytest.approx(0.831)


def test_search_forwards_filters_and_exclusions() -> None:
    _request(
        "POST",
        "/search",
        json={
            "query": "streaming",
            "kinds": ["api"],
            "locales": ["en"],
            "exclude_ids": ["c1", "c2", "c1"],
            "top_k": 7,
        },
    )

    call = _engine().search_calls[0]
    assert call["kinds"] == frozenset({"api"})
    assert call["locales"] == frozenset({"en"})
    assert call["exclude_ids"] == {"c1", "c2"}
    assert call["top_k"] == 7


def test_search_rejects_an_unknown_kind() -> None:
    response = _request("POST", "/search", json={"query": "streaming", "kinds": ["tutorial"]})

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "E_BAD_PARAM"
    assert "tutorial" in error["message"]


def test_search_rejects_a_malformed_locale() -> None:
    response = _request("POST", "/search", json={"query": "streaming", "locales": ["english"]})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "E_BAD_PARAM"


def test_pages_returns_sections_in_reading_order() -> None:
    _engine().sections = [_hit(1), _hit(2), _hit(3)]

    response = _request("GET", "/pages/api/endpoint/chat")

    assert response.status_code == 200
    body = response.json()
    assert body["url"] == URL
    assert body["title"] == "Chat completions"
    assert [s["section_index"] for s in body["sections"]] == [1, 2, 3]
    first = body["sections"][0]
    assert first["citation_url"] == f"{URL}#{ANCHOR}"
    assert first["heading_path"] == ["Chat completions", "Streaming"]
    assert "Server-sent events" in first["content"]
    assert body["truncated"] is False


def test_pages_unknown_path_is_a_typed_404() -> None:
    _engine().sections = []

    response = _request("GET", "/pages/no/such/page")

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "E_UNKNOWN_PAGE"
    assert "no indexed page" in error["message"]
    assert "search" in error["next"]


def test_health_reports_counts_and_corpus() -> None:
    registry.engines.clear()
    for name in VARIANTS:
        registry.engines[name] = FakeEngine(count=len(VARIANTS[name].schema_name))

    response = _request("GET", "/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["vespa"] == "reachable"
    assert set(body["variants"]) == set(VARIANTS)
    assert body["variants"]["sec1024"]["documents"] == len(VARIANTS["sec1024"].schema_name)
    # Shape only: the vendored corpus is refreshed independently of these routes.
    corpus = body["corpus"]
    assert corpus is not None
    assert corpus["pages"] > 0
    assert corpus["source_commit"]
    assert corpus["kinds"]
    assert body["snapshots"] == {"readable": 8, "total": 8}
    assert body["embedding_probe"]["status"] in {"not_run", "passed"}


def test_health_is_degraded_when_one_variant_is_down() -> None:
    registry.engines.clear()
    names = sorted(VARIANTS)
    for name in names:
        registry.engines[name] = FakeEngine(
            fail=RuntimeError("connection refused") if name == names[0] else None
        )

    response = _request("GET", "/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["vespa"] == "reachable"
    assert body["variants"][names[0]]["documents"] is None
    assert body["variants"][names[1]]["documents"] is not None


def test_a_failed_startup_probe_degrades_health(monkeypatch: pytest.MonkeyPatch) -> None:
    registry.engines.clear()
    for name in VARIANTS:
        registry.engines[name] = FakeEngine(count=len(VARIANTS[name].schema_name))

    async def failing(variant: str) -> Any:
        raise RuntimeError("embeddings unreachable")

    monkeypatch.setattr(api_module, "check_embedding_once", failing)

    async def run() -> None:
        async with api_module.lifespan(api_module.app):
            pass

    asyncio.run(run())
    try:
        assert api_module.app.state.embedding_probe["status"] == "failed"
        response = _request("GET", "/health")
        assert response.status_code == 200
        assert response.json()["status"] == "degraded"
    finally:
        del api_module.app.state.embedding_probe


def test_health_is_a_typed_503_when_no_variant_answers() -> None:
    registry.engines.clear()
    for name in VARIANTS:
        registry.engines[name] = FakeEngine(fail=RuntimeError("connection refused"))

    response = _request("GET", "/health")

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "E_UPSTREAM"
    assert "setup-vespa" in error["next"]


def test_version_names_the_variants_and_models() -> None:
    response = _request("GET", "/version")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "glossator"
    assert body["version"]
    assert body["variants"] == sorted(VARIANTS)
    assert "mistral-medium-2604" in body["generation_models"]


def test_request_id_is_minted_when_absent_and_echoed_when_sent() -> None:
    minted = _request("GET", "/version")
    echoed = _request("GET", "/version", headers={"X-Request-Id": "abc-123"})

    assert minted.headers["X-Request-Id"]
    assert echoed.headers["X-Request-Id"] == "abc-123"


def test_minted_request_id_is_in_the_ask_body(fake_ask: list[dict[str, Any]]) -> None:
    response = _request("POST", "/ask", json={"question": "how do I stream?"})

    assert response.json()["request_id"] == response.headers["X-Request-Id"]


def test_search_upstream_failures_are_a_typed_503() -> None:
    _engine().fail = RetrieverException("vespa down")

    response = _request("POST", "/search", json={"query": "streaming"})

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "E_UPSTREAM"
    assert "retry the identical request" in error["next"]


def test_search_upstream_failures_are_logged() -> None:
    _engine().fail = RetrieverException("vespa down")

    with capture_logs() as logs:
        response = _request("POST", "/search", json={"query": "streaming"})

    assert response.status_code == 503
    warnings = [log for log in logs if log["event"] == "Upstream failure"]
    assert warnings == [
        {
            "event": "Upstream failure",
            "log_level": "warning",
            "operation": "search",
            "error": "vespa down",
        }
    ]


def test_unhandled_failures_keep_the_typed_shape() -> None:
    _engine().fail = RuntimeError("boom")

    response = _request("POST", "/search", json={"query": "streaming"}, raise_app_exceptions=False)

    assert response.status_code == 500
    error = response.json()["error"]
    assert error["code"] == "E_INTERNAL"
    assert error["next"]


def test_error_bodies_carry_the_request_id() -> None:
    response = _request(
        "POST",
        "/ask",
        json={"question": "q", "strategy": "teleport"},
        headers={"X-Request-Id": "err-17"},
    )

    error = response.json()["error"]
    assert error["request_id"] == "err-17"
    assert response.headers["X-Request-Id"] == "err-17"


def test_ask_forwards_the_requested_model(fake_ask: list[dict[str, Any]]) -> None:
    _request("POST", "/ask", json={"question": "q", "model": "ministral-14b-2512"})

    assert fake_ask[0]["config"].model == "ministral-14b-2512"


def test_ask_defaults_to_the_configured_model(
    fake_ask: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GLOSSATOR_MODEL", "ministral-14b-2512")
    _request("POST", "/ask", json={"question": "q"})
    _request("POST", "/ask", json={"question": "q", "model": "mistral-medium-2604"})
    # Compose passes the variable blank when the operator leaves it unset.
    monkeypatch.setenv("GLOSSATOR_MODEL", "")
    _request("POST", "/ask", json={"question": "q"})

    assert [call["config"].model for call in fake_ask] == [
        "ministral-14b-2512",
        "mistral-medium-2604",
        AnswerConfig().model,
    ]


def test_ask_generation_failures_are_a_typed_503_upstream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def quota_blocked(*args: Any, **kwargs: Any) -> Answer:
        raise MistralError(
            "quota exceeded",
            httpx.Response(
                429, request=httpx.Request("POST", "https://api.mistral.ai/v1/chat/completions")
            ),
        )

    monkeypatch.setattr(answer_service, "ask", quota_blocked)

    response = _request("POST", "/ask", json={"question": "how do I stream?"})

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "E_UPSTREAM"
    assert "quota exceeded" in error["message"]
    assert "retry the identical request" in error["next"]


def test_search_unknown_variant_hint_names_the_variants() -> None:
    response = _request("POST", "/search", json={"query": "streaming", "variant": "sec2048"})

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "E_BAD_PARAM"
    assert "sec2048" in error["message"]
    assert error["next"] == f"use one of {sorted(VARIANTS)}"
    # The hint must not send the client rewriting locales instead.
    assert "locales" not in error["next"]


def test_search_unknown_field_is_rejected_with_a_suggestion() -> None:
    response = _request("POST", "/search", json={"query": "streaming", "limit": 5})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "E_BAD_PARAM"
    assert "limit" in error["message"]
    assert "did you mean limit= → top_k=?" in error["next"]
    assert "/search accepts:" in error["next"]
    assert "query" in error["next"] and "top_k" in error["next"]


def test_pages_truncation_is_recoverable_by_offset() -> None:
    _engine().sections = [_hit(n) for n in range(1, 151)]

    first = _request("GET", "/pages/api/endpoint/chat")

    assert first.status_code == 200
    body = first.json()
    assert len(body["sections"]) == 100
    assert body["truncated"] is True

    resume_at = body["sections"][-1]["end_offset"]
    second = _request("GET", f"/pages/api/endpoint/chat?start_offset={resume_at}")

    assert second.status_code == 200
    rest = second.json()
    assert len(rest["sections"]) == 50
    assert rest["truncated"] is False
    assert rest["sections"][0]["section_index"] == 101


def test_pages_honours_a_smaller_top_k() -> None:
    _engine().sections = [_hit(n) for n in range(1, 6)]

    response = _request("GET", "/pages/api/endpoint/chat?top_k=2")

    assert response.status_code == 200
    body = response.json()
    assert [s["section_index"] for s in body["sections"]] == [1, 2]
    assert body["truncated"] is True


def test_cite_verifies_a_chunk_quote_with_a_fragment_link() -> None:
    response = _request(
        "POST",
        "/cite",
        json={
            "draft": "It streams via server-sent events [1].",
            "quotes": [
                {
                    "n": 1,
                    "chunk_id": "c1",
                    "quote": "Server-sent events carry the response.",
                }
            ],
        },
        headers={"X-Request-Id": "cite-1"},
    )

    assert response.status_code == 200
    body = response.json()
    (item,) = body["quotes"]
    assert item["verified"] is True
    assert item["url"] == URL
    assert item["anchor"] == ANCHOR
    assert item["chunk_id"] == "c1"
    assert item["fragment_url"] == (
        f"{URL}#{ANCHOR}:~:text=Server%2Dsent%20events%20carry%20the%20response."
    )
    assert body["unverified_markers"] == []
    assert body["sources"] == [
        {
            "url": URL,
            "anchor": ANCHOR,
            "citation_url": f"{URL}#{ANCHOR}",
            "numbers": [1],
            "quotes": [
                {
                    "n": 1,
                    "fragment_url": (
                        f"{URL}#{ANCHOR}:~:text=Server%2Dsent%20events%20carry%20the%20response."
                    ),
                    "text": "Server-sent events carry the response.",
                }
            ],
            "heading": "Chat completions > Streaming",
        }
    ]
    assert body["sources_markdown"].startswith("Sources (1 verified):")
    assert "[1] [Chat completions > Streaming](" in body["sources_markdown"]
    assert body["request_id"] == "cite-1"
    assert response.headers["X-Request-Id"] == "cite-1"


def test_cite_collapses_duplicate_sources_and_names_uncovered_markers() -> None:
    response = _request(
        "POST",
        "/cite",
        json={
            "draft": "It streams [1] and again [2], plus pixels [3].",
            "quotes": [
                {
                    "n": 1,
                    "chunk_id": "c1",
                    "quote": "Server-sent events carry the response.",
                },
                {
                    "n": 2,
                    "url": URL,
                    "quote": "Server-sent events carry the response.",
                },
                {"n": 3, "chunk_id": "c1", "quote": "pixels are delicious"},
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert [item["verified"] for item in body["quotes"]] == [True, True, False]
    assert body["unverified_markers"] == [3]
    assert len(body["sources"]) == 1
    assert body["sources"][0]["numbers"] == [1, 2]


def test_cite_rejects_a_quote_naming_both_chunk_and_url() -> None:
    response = _request(
        "POST",
        "/cite",
        json={
            "draft": "It streams [1].",
            "quotes": [{"n": 1, "chunk_id": "c1", "url": URL, "quote": "Server-sent events"}],
        },
    )

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "E_BAD_PARAM"
    assert "exactly one" in error["message"]
    assert "chunk_id" in error["next"]


def test_cite_rejects_an_unknown_variant() -> None:
    response = _request(
        "POST",
        "/cite",
        json={"draft": "It streams [1].", "quotes": [], "variant": "sec2048"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "E_BAD_PARAM"


def test_history_text_form_returns_the_service_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def phrase_history(text: str, manifest: object, **scope: object) -> dict[str, object]:
        del manifest, scope
        calls.append(text)
        return {"form": "text", "text": text, "first": None, "last": None}

    monkeypatch.setattr("glossator.history.phrase_history", phrase_history)

    response = _request("GET", "/history?text=rate+limits")

    assert response.status_code == 200
    assert response.json()["form"] == "text"
    assert calls == ["rate limits"]


def test_history_rejects_zero_or_two_forms() -> None:
    for path in (
        "/history",
        "/history?page_url=/page&under=/vibe",
        "/history?text=a&since=2026-07-01",
    ):
        response = _request("GET", path)

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "E_BAD_PARAM"


def test_history_under_returns_grouped_intervals(monkeypatch: pytest.MonkeyPatch) -> None:
    def history_under(under: str, since: str | None, manifest: object) -> dict[str, object]:
        del manifest
        return {"form": "under", "under": under, "since": since, "intervals": []}

    monkeypatch.setattr("glossator.changelog.history_under", history_under)
    response = _request("GET", "/history?under=/vibe&since=2026-07-01")

    assert response.status_code == 200
    assert response.json()["form"] == "under"


def test_history_rejects_an_empty_form() -> None:
    response = _request("GET", "/history?text=++")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "E_BAD_PARAM"


def test_cite_validation_errors_use_the_typed_shape() -> None:
    response = _request("POST", "/cite", json={"draft": "It streams [1].", "limit": 5})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "E_BAD_PARAM"
    assert "limit" in error["message"]


def test_ask_lists_one_source_entry_per_url_and_anchor(
    fake_ask: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    answer = Answer(
        question="q",
        strategy="single_pass",
        model="mistral-medium-2604",
        answer_markdown="It streams [1] and again [2].",
        citations=[
            Citation(
                n=1,
                url=URL,
                anchor=ANCHOR,
                chunk_id="c1",
                quote="Server-sent events carry the response.",
                verified=True,
                fragment_url=f"{URL}#{ANCHOR}:~:text=Server.",
            ),
            Citation(
                n=2,
                url=URL,
                anchor=ANCHOR,
                chunk_id="c1",
                quote="Server-sent events carry the response.",
                verified=True,
                fragment_url=f"{URL}#{ANCHOR}:~:text=Server.",
            ),
        ],
        trace=Trace(strategy="single_pass", variant="sec1024", prompt_version="v1"),
        usage=TokenUsage(prompt_tokens=10, completion_tokens=5),
    )

    async def _ask(question: str, **kwargs: Any) -> Answer:
        return answer

    monkeypatch.setattr(answer_service, "ask", _ask)

    response = _request("POST", "/ask", json={"question": "how do I stream?"})

    assert response.status_code == 200
    body = response.json()
    assert len(body["citations"]) == 2
    assert body["sources"] == [
        {
            "url": URL,
            "anchor": ANCHOR,
            "citation_url": f"{URL}#{ANCHOR}",
            "numbers": [1, 2],
            "quotes": [
                {
                    "n": 1,
                    "fragment_url": f"{URL}#{ANCHOR}:~:text=Server.",
                    "text": "Server-sent events carry the response.",
                },
                {
                    "n": 2,
                    "fragment_url": f"{URL}#{ANCHOR}:~:text=Server.",
                    "text": "Server-sent events carry the response.",
                },
            ],
            "heading": "",
        }
    ]
    assert body["sources_markdown"].splitlines()[1].startswith("[1][2] [")


def test_history_section_errors_become_bad_param(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def section_history(page_url: str, section: str | None, manifest: object) -> dict[str, object]:
        raise ValueError("section must be on docs.mistral.ai")

    monkeypatch.setattr("glossator.history.section_history", section_history)

    response = _request("GET", "/history?page_url=https://example.com/page")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "E_BAD_PARAM"


def test_missing_history_snapshot_is_a_typed_503(monkeypatch: pytest.MonkeyPatch) -> None:
    def phrase_history(text: str, manifest: object, **scope: object) -> dict[str, object]:
        raise SnapshotUnavailableError("snapshot is missing")

    monkeypatch.setattr("glossator.history.phrase_history", phrase_history)

    response = _request("GET", "/history?text=rate+limits")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "E_UPSTREAM"
