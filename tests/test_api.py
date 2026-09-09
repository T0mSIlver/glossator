"""HTTP route, validation, typed-error, and request-ID tests."""

import asyncio
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from httpx import ASGITransport
from mistralai.search.toolkit.retrieval.errors import RetrieverException

from entrypoints.api import app, registry
from glossator.answer import service as answer_service
from glossator.answer.citations import Answer, Citation, Trace
from glossator.answer.llm import TokenUsage
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
    assert body["corpus"]["pages"] == 411
    assert body["corpus"]["source_commit"].startswith("2e094f7")
    assert body["corpus"]["kinds"]["doc"] == 296
    assert body["embedding_probe"]["status"] in {"not_run", "passed"}


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


def test_unhandled_failures_keep_the_typed_shape() -> None:
    _engine().fail = RuntimeError("boom")

    response = _request("POST", "/search", json={"query": "streaming"}, raise_app_exceptions=False)

    assert response.status_code == 500
    error = response.json()["error"]
    assert error["code"] == "E_INTERNAL"
    assert error["next"]
