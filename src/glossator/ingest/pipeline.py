"""Ingest a corpus directory into one index variant.

Re-running is safe: a document's chunk ids are derived from its URL and its span,
and the store deletes a document's previous chunks before writing the new ones,
so a second run over an unchanged corpus leaves the index exactly as it was.
"""

import asyncio
import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

import structlog
from mistralai.client import Mistral
from mistralai.search.toolkit.embedding import MistralEmbedder
from mistralai.search.toolkit.ingestion.pipelines import Pipeline

from glossator.index import get_index, get_variant
from glossator.index.variants import IndexVariant
from glossator.ingest.chunker import build_chunker
from glossator.ingest.extractor import CorpusPageExtractor, page_file
from glossator.ingest.pages import (
    CorpusError,
    iter_page_paths,
    load_page,
    verify_manifest,
)

logger = structlog.get_logger(__name__)

DEFAULT_CONCURRENCY = 4

# The embedding API rate-limits a full-corpus run. The toolkit's embedder retries a
# 429 with exponential backoff, but only three times by default, which a handful of
# concurrent pages exhaust -- and a page that runs out of retries is a page missing
# from the index. More attempts cost wall-clock time on a run that happens rarely.
_EMBEDDER_MAX_RETRY = 8

# USD per million input tokens for mistral-embed (pricing page, 2026-09-08). The
# smaller-dimension variants have no published price; they are billed as embeddings,
# so the same rate is the honest estimate to report rather than a silent zero.
_EMBEDDING_USD_PER_MTOK = 0.10


class PartialIngestError(RuntimeError):
    """Some pages did not reach the index.

    Raised rather than returned because a caller that does not look at
    ``IngestReport.failures`` -- the eval grid, a script -- would otherwise measure
    a corpus with holes in it and never know. Pass ``allow_partial=True`` to get the
    report back instead.
    """

    def __init__(self, report: "IngestReport") -> None:
        super().__init__(
            f"{len(report.failures)} of {len(report.failures) + report.pages} page(s) "
            f"failed to index into {report.variant!r}: {', '.join(report.failures)}"
        )
        self.report = report


@dataclass(frozen=True, slots=True)
class IngestReport:
    """What one ingest run did, for the CLI and for the cost log."""

    variant: str
    pages: int
    chunks: int
    embedding_tokens: int
    failures: tuple[str, ...]

    @property
    def estimated_usd(self) -> float:
        return self.embedding_tokens / 1_000_000 * _EMBEDDING_USD_PER_MTOK


def _mistral_client() -> Mistral:
    api_key = os.environ.get("MISTRAL_API_KEY", "")
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY is not set. Check your .env file.")
    return Mistral(
        api_key=api_key,
        server_url=os.getenv("MISTRAL_API_URL", "https://api.mistral.ai"),
    )


async def _run_batch(
    paths: list[Path],
    ingest_one: Callable[[Path], Awaitable[None]],
    sequential: bool = False,
) -> list[Path]:
    """Ingest every path, returning the ones that raised.

    ``sequential`` drops all concurrency, which is what a retry after a rate limit
    wants: the page's own semaphore slot is not the constraint, the account's
    request rate is.
    """
    failed: list[Path] = []
    if sequential:
        for path in paths:
            try:
                await ingest_one(path)
            except Exception as exc:  # noqa: BLE001 - reported per page, never fatal
                failed.append(path)
                logger.error("Failed to ingest page", path=str(path), error=str(exc))
        return failed

    results = await asyncio.gather(
        *(ingest_one(path) for path in paths), return_exceptions=True
    )
    for path, result in zip(paths, results, strict=True):
        if isinstance(result, BaseException):
            failed.append(path)
            logger.error("Failed to ingest page", path=str(path), error=str(result))
    return failed


def build_pipeline(variant: IndexVariant, client: Mistral | None = None) -> Pipeline:
    """The ingestion pipeline for one variant.

    ``loader=None`` because pages are fed as in-memory ``File``s through
    ``run_file``: the corpus is already on disk in the shape we want, so there is
    nothing for a loader to decide.
    """
    return Pipeline(
        loader=None,
        extractor=CorpusPageExtractor(),
        text_splitter=build_chunker(variant.chunking),
        embedder=MistralEmbedder(
            client=client or _mistral_client(),
            model_name=variant.embedding_model_name,
            max_retry=_EMBEDDER_MAX_RETRY,
        ),
        stores=get_index(variant),
    )


async def ingest_corpus(
    corpus_dir: Path,
    variant: IndexVariant | str,
    concurrency: int = DEFAULT_CONCURRENCY,
    client: Mistral | None = None,
    allow_partial: bool = False,
) -> IngestReport:
    """Index every page of ``corpus_dir`` into ``variant``'s schema.

    Raises ``PartialIngestError`` if any page fails, unless ``allow_partial`` is set.
    """
    resolved = get_variant(variant) if isinstance(variant, str) else variant
    paths = list(iter_page_paths(corpus_dir))
    if not paths:
        raise CorpusError(f"{corpus_dir}: no markdown pages found")
    verified = verify_manifest(corpus_dir)

    pipeline = build_pipeline(resolved, client=client)
    semaphore = asyncio.Semaphore(concurrency)
    log = logger.bind(
        variant=resolved.name, schema=resolved.schema_name, pages=len(paths)
    )
    log.info("Ingesting corpus", corpus_dir=str(corpus_dir), manifest_pages=verified)

    chunks = 0
    tokens = 0

    async def ingest_one(path: Path) -> None:
        nonlocal chunks, tokens
        async with semaphore:
            page = load_page(path)
            # No checkpoint key: extraction here is a frontmatter split, so caching
            # it would cost more than it saves and would hide corpus edits.
            document = await pipeline.run_file(page_file(page))
            chunks += len(document.chunks)
            tokens += int(document.metadata.get("embed_total_tokens") or 0)
            logger.debug("Indexed page", url=page.url, chunks=len(document.chunks))

    failed = await _run_batch(paths, ingest_one)
    if failed:
        # One sequential retry pass. What fails here is a rate limit the embedder's
        # own backoff ran out of attempts on, and a corpus indexed except for the
        # pages that happened to collide is worse than a slower run.
        log.info("Retrying pages that failed", count=len(failed))
        failed = await _run_batch(failed, ingest_one, sequential=True)
    failures = [str(path) for path in failed]

    report = IngestReport(
        variant=resolved.name,
        pages=len(paths) - len(failures),
        chunks=chunks,
        embedding_tokens=tokens,
        failures=tuple(failures),
    )
    log.info(
        "Ingest complete",
        chunks=report.chunks,
        embedding_tokens=report.embedding_tokens,
        estimated_usd=round(report.estimated_usd, 6),
        failures=len(report.failures),
    )
    if report.failures and not allow_partial:
        raise PartialIngestError(report)
    return report
