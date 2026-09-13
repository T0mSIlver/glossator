"""The generated-answer path behind ``POST /ask`` and ``POST /cite``: the model
choice, the failures that are upstream's fault, and the response payload."""

import os
from typing import Any

from mistralai.search.toolkit.retrieval.errors import RetrieverException
from mistralai.search.toolkit.search.errors import IndexException
from pydantic import ValidationError

from glossator.answer import cite as cite_engine
from glossator.answer import service as answer_service
from glossator.answer.citations import Answer
from glossator.answer.cite import (
    CiteInputError,
    CiteQuote,
    CiteResult,
    SourceEntry,
    entries_with_headings,
    sources_markdown,
)
from glossator.answer.config import PRICES, AnswerConfig, known_serving_model
from glossator.answer.llm import CALL_ERRORS
from glossator.surface.engines import EngineRegistry
from glossator.surface.errors import SurfaceError, bad_param

_ASK_UPSTREAM_ERRORS: tuple[type[Exception], ...] = (
    RetrieverException,
    IndexException,
    RuntimeError,
    *CALL_ERRORS,
)
"""What the answer path fails with that is upstream's fault rather than a bug
here: retrieval and index errors, a missing key, and every generation-client
error after the service layer has exhausted its own retries."""


def answer_config(model: str | None) -> AnswerConfig:
    """Build a validated answer configuration for one request.

    The request's model wins; otherwise ``GLOSSATOR_MODEL``, which deployment
    compose passes blank when unset, so a blank value means the shipped default.
    A model the price table does not know is refused at the door, unless a local
    chat server is configured, whose ids the table has never seen (D-035c).
    """
    chosen = model if model is not None else os.environ.get("GLOSSATOR_MODEL") or None
    if chosen is not None and not known_serving_model(chosen):
        raise ValueError(
            f"no price for model {chosen!r}; priced models: {sorted(PRICES)} "
            "(or set GLOSSATOR_CHAT_SERVER_URL to serve from a local server)"
        )
    return AnswerConfig(model=chosen) if chosen is not None else AnswerConfig()


async def ask(
    registry: EngineRegistry, question: str, *, strategy: str, variant: str, model: str | None
) -> Answer:
    if strategy not in answer_service.STRATEGIES:
        raise bad_param(
            f"unknown strategy {strategy!r}", f"use one of {sorted(answer_service.STRATEGIES)}"
        )
    engine = registry.get(variant)
    try:
        config = answer_config(model)
    except (ValidationError, ValueError) as exc:
        raise bad_param(
            str(exc),
            f"model must be one of {sorted(PRICES)} "
            "(or set GLOSSATOR_CHAT_SERVER_URL for a local server)",
        ) from exc
    try:
        return await answer_service.ask(
            question, strategy=strategy, variant=variant, engine=engine, config=config
        )
    except _ASK_UPSTREAM_ERRORS as exc:
        # CALL_ERRORS are the generation client's own failures (a zero-quota
        # 429 included, D-017a); they reach here only after the service layer
        # exhausted its retries, so the caller hears 503, not a 500 the
        # /health dashboard cannot explain.
        raise SurfaceError(
            "E_UPSTREAM",
            f"answer generation failed: {exc}",
            "retry the identical request; if it repeats, check GET /health",
        ) from exc


def _citation_url(url: str, anchor: str | None) -> str:
    return f"{url}#{anchor}" if anchor else url


def _deduped_sources(answer: Answer) -> list[SourceEntry]:
    """One source entry per distinct (url, anchor) over the verified citations.

    Markers keep their numbers; each entry lists the numbers that point at it
    (D-027b). The per-marker ``citations`` list is unchanged beside it.
    """
    headings = {source.n: " > ".join(source.heading_path) for source in answer.trace.sources}
    return entries_with_headings(answer.citations, headings)


def answer_payload(answer: Answer, request_id: str) -> dict[str, Any]:
    """The ``POST /ask`` body: the answer with citation links, deduplicated
    sources and their Markdown, and the trace summary."""
    payload: dict[str, Any] = answer.model_dump()
    for citation in payload["citations"]:
        citation["citation_url"] = _citation_url(citation["url"], citation["anchor"])
    for citation in payload["trace"]["unverified_citations"]:
        if citation["url"]:
            citation["citation_url"] = _citation_url(citation["url"], citation["anchor"])
    entries = _deduped_sources(answer)
    payload["sources"] = [entry.model_dump() for entry in entries]
    payload["sources_markdown"] = sources_markdown(entries)
    payload["trace_summary"] = answer.trace.summary()
    payload["request_id"] = request_id
    return payload


async def cite(
    registry: EngineRegistry, draft: str, quotes: list[CiteQuote], *, variant: str
) -> CiteResult:
    """The verdict on each quote; malformed quotes and index failures become typed errors."""
    engine = registry.get(variant)
    try:
        return await cite_engine.cite_draft(draft, quotes, engine=engine)
    except CiteInputError as exc:
        raise bad_param(
            str(exc),
            "each quote needs n, quote, and either chunk_id (exactly as a "
            "search hit printed it) or a page url with an optional #anchor",
        ) from exc
    except (RetrieverException, IndexException) as exc:
        raise SurfaceError(
            "E_UPSTREAM",
            f"citation check failed: {exc}",
            "retry the identical request; if it repeats, check GET /health",
        ) from exc


__all__ = ["answer_config", "answer_payload", "ask", "cite"]
