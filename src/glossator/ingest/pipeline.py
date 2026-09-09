"""Ingest a corpus directory into one index variant.

Re-running is safe: a document's chunk ids are derived from its URL and its span,
and the store deletes a document's previous chunks before writing the new ones,
so a second run over an unchanged corpus leaves the index exactly as it was.
"""

import asyncio
import hashlib
import json
import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast
from uuid import uuid4

import structlog
from mistralai.client import Mistral
from mistralai.search.toolkit.context import IngestContext, RetrievalContext
from mistralai.search.toolkit.document import (
    Document,
    DocumentChunk,
    compute_char_locator,
    compute_id,
)
from mistralai.search.toolkit.embedding import Embedder, EmbeddingResult, MistralEmbedder
from mistralai.search.toolkit.ingestion.pipelines import Pipeline
from mistralai.search.toolkit.search.errors import IndexingError

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
DEFAULT_EMBEDDING_CACHE = Path.home() / ".cache" / "glossator" / "embeddings"

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


class IndexWritePreflightError(RuntimeError):
    """The target schema rejected a harmless write before ingestion started."""


class WritableIndex(Protocol):
    async def index_document(
        self, document: Document, context: IngestContext = IngestContext()
    ) -> None: ...

    async def delete_document(
        self, doc_id: str, context: IngestContext = IngestContext()
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class IngestReport:
    """What one ingest run did, for the CLI and for the cost log."""

    variant: str
    pages: int
    chunks: int
    embedding_tokens: int
    failures: tuple[str, ...]
    embedded_chunks: int = 0
    cached_chunks: int = 0

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


class CachedEmbedder(Embedder):
    """Cache embeddings by model, dimensions, and exact chunk content."""

    def __init__(self, inner: Embedder, dimensions: int, cache_dir: Path) -> None:
        super().__init__(inner.model_name)
        self.inner = inner
        self.dimensions = dimensions
        self.cache_dir = cache_dir
        self.embedded_chunks = 0
        self.cached_chunks = 0

    def _path(self, text: str) -> Path:
        content_sha256 = hashlib.sha256(text.encode()).hexdigest()
        material = f"{self.model_name}\0{self.dimensions}\0{content_sha256}".encode()
        key = hashlib.sha256(material).hexdigest()
        return self.cache_dir / self.model_name.replace("/", "_") / f"{key}.json"

    async def embed(
        self,
        texts: list[str],
        context: RetrievalContext = RetrievalContext(),
    ) -> EmbeddingResult:
        embeddings: list[list[float] | None] = [None] * len(texts)
        missing_positions: list[int] = []
        missing_texts: list[str] = []
        for position, text in enumerate(texts):
            path = self._path(text)
            try:
                cached = json.loads(path.read_text())
                if not isinstance(cached, list) or len(cached) != self.dimensions:
                    raise ValueError("wrong embedding dimensions")
                embeddings[position] = [float(value) for value in cached]
                self.cached_chunks += 1
            except (FileNotFoundError, OSError, TypeError, ValueError, json.JSONDecodeError):
                missing_positions.append(position)
                missing_texts.append(text)

        total_tokens = 0
        if missing_texts:
            result = await self.inner.embed(missing_texts, context=context)
            total_tokens = result.total_tokens
            for position, embedding in zip(missing_positions, result.embeddings, strict=True):
                if len(embedding) != self.dimensions:
                    raise ValueError(
                        f"{self.model_name} returned {len(embedding)} dimensions, "
                        f"expected {self.dimensions}"
                    )
                embeddings[position] = embedding
                path = self._path(texts[position])
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary = path.with_suffix(f".{uuid4().hex}.tmp")
                temporary.write_text(json.dumps(embedding, separators=(",", ":")))
                temporary.replace(path)
                self.embedded_chunks += 1

        if any(embedding is None for embedding in embeddings):
            raise RuntimeError("embedding cache left a chunk without an embedding")
        return EmbeddingResult(
            embeddings=cast(list[list[float]], embeddings), total_tokens=total_tokens
        )


class SnapshotStamp:
    """Attach the date and content digest after chunking and before embedding."""

    def __init__(self, snapshot: str) -> None:
        self.snapshot = snapshot

    async def process(
        self, document: Document, context: IngestContext = IngestContext()
    ) -> Document:
        del context
        chunks = []
        for chunk in document.chunks:
            digest = hashlib.sha256(chunk.content.encode()).hexdigest()
            metadata = chunk.metadata.model_copy(
                update={"snapshot": self.snapshot, "content_sha256": digest}
            )
            chunks.append(chunk.model_copy(update={"metadata": metadata}))
        return document.model_copy(update={"chunks": chunks})


async def _run_batch(
    paths: list[Path],
    ingest_one: Callable[[Path], Awaitable[None]],
    sequential: bool = False,
    stop_on_index_failure: bool = False,
    max_concurrency: int | None = None,
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
                if stop_on_index_failure and isinstance(exc, IndexingError):
                    break
        return failed

    async def attempt(path: Path) -> tuple[Path, Exception | None]:
        try:
            await ingest_one(path)
        except Exception as exc:  # noqa: BLE001 - returned with its page and reported below
            return path, exc
        return path, None

    if not stop_on_index_failure:
        results = await asyncio.gather(*(attempt(path) for path in paths))
        for path, error in results:
            if error is not None:
                failed.append(path)
                logger.error("Failed to ingest page", path=str(path), error=str(error))
        return failed

    waiting = iter(paths)
    active: set[asyncio.Task[tuple[Path, Exception | None]]] = set()
    for _ in range(max_concurrency or len(paths)):
        try:
            candidate = next(waiting)
        except StopIteration:
            break
        active.add(asyncio.create_task(attempt(candidate)))
    while active:
        done, active = await asyncio.wait(active, return_when=asyncio.FIRST_COMPLETED)
        stop = False
        for task in done:
            path, error = task.result()
            if error is None:
                continue
            failed.append(path)
            logger.error("Failed to ingest page", path=str(path), error=str(error))
            stop = stop or isinstance(error, IndexingError)
        if stop:
            for task in active:
                task.cancel()
            await asyncio.gather(*active, return_exceptions=True)
            break
        for _ in range(len(done)):
            try:
                candidate = next(waiting)
            except StopIteration:
                break
            active.add(asyncio.create_task(attempt(candidate)))
    return failed


async def _verify_index_writable(index: WritableIndex, variant: IndexVariant) -> None:
    """Feed and remove one small document before any corpus page can be deleted."""
    content = "glossator ingestion write probe"
    probe_id = f"glossator-write-probe-{uuid4().hex}"
    locator = compute_char_locator(0, len(content))
    probe = Document(
        id=probe_id,
        source_id=probe_id,
        content=content,
        chunks=[
            DocumentChunk(
                id=compute_id(probe_id, locator),
                source_id=probe_id,
                locator=locator,
                start_offset=0,
                end_offset=len(content),
                content=content,
                embedding=[1.0, *([0.0] * (variant.embedding_dimensions - 1))],
            )
        ],
    )
    try:
        await index.index_document(probe)
    except Exception as exc:  # noqa: BLE001 - backend failures share this safety message
        raise IndexWritePreflightError(
            f"Refusing to ingest into schema {variant.schema_name!r}: the write probe was "
            "rejected. Vespa may be blocking feeds because disk usage exceeds its resource limit."
        ) from exc
    try:
        await index.delete_document(probe.id)
    except Exception as exc:  # noqa: BLE001 - leaving the probe behind is not a safe start
        raise IndexWritePreflightError(
            f"Refusing to ingest into schema {variant.schema_name!r}: the write probe could not "
            "be removed after a successful feed."
        ) from exc


def build_pipeline(
    variant: IndexVariant,
    client: Mistral | None = None,
    *,
    snapshot: str | None = None,
    embedding_cache: Path = DEFAULT_EMBEDDING_CACHE,
) -> Pipeline:
    """The ingestion pipeline for one variant.

    ``loader=None`` because pages are fed as in-memory ``File``s through
    ``run_file``: the corpus is already on disk in the shape we want, so there is
    nothing for a loader to decide.
    """
    embedder: Embedder = MistralEmbedder(
        client=client or _mistral_client(),
        model_name=variant.embedding_model_name,
        max_retry=_EMBEDDER_MAX_RETRY,
    )
    if snapshot is not None:
        embedder = CachedEmbedder(embedder, variant.embedding_dimensions, embedding_cache)
    return Pipeline(
        loader=None,
        extractor=CorpusPageExtractor(),
        text_splitter=build_chunker(variant.chunking),
        embedder=embedder,
        processors=[SnapshotStamp(snapshot)] if snapshot is not None else None,
        stores=get_index(variant),
    )


async def ingest_corpus(
    corpus_dir: Path,
    variant: IndexVariant | str,
    concurrency: int = DEFAULT_CONCURRENCY,
    client: Mistral | None = None,
    allow_partial: bool = False,
    snapshot: str | None = None,
    embedding_cache: Path = DEFAULT_EMBEDDING_CACHE,
) -> IngestReport:
    """Index every page of ``corpus_dir`` into ``variant``'s schema.

    Raises ``PartialIngestError`` if any page fails, unless ``allow_partial`` is set.
    """
    resolved = get_variant(variant) if isinstance(variant, str) else variant
    if resolved.name == "snap1024" and snapshot is None:
        raise ValueError("snapshot is required for the snap1024 variant")
    if snapshot is not None and resolved.name != "snap1024":
        raise ValueError("snapshot may only be used with the snap1024 variant")
    paths = list(iter_page_paths(corpus_dir))
    if not paths:
        raise CorpusError(f"{corpus_dir}: no markdown pages found")
    verified = verify_manifest(corpus_dir)

    pipeline = build_pipeline(
        resolved,
        client=client,
        snapshot=snapshot,
        embedding_cache=embedding_cache,
    )
    await _verify_index_writable(pipeline.stores[0], resolved)
    semaphore = asyncio.Semaphore(concurrency)
    log = logger.bind(variant=resolved.name, schema=resolved.schema_name, pages=len(paths))
    log.info("Ingesting corpus", corpus_dir=str(corpus_dir), manifest_pages=verified)

    chunks = 0
    tokens = 0
    indexed_pages: set[Path] = set()
    index_failures: set[Path] = set()

    async def ingest_one(path: Path) -> None:
        nonlocal chunks, tokens
        async with semaphore:
            page = load_page(path)
            # No checkpoint key: extraction here is a frontmatter split, so caching
            # it would cost more than it saves and would hide corpus edits.
            try:
                source_id = f"{page.url}::__snapshot__:{snapshot}" if snapshot is not None else None
                document = await pipeline.run_file(page_file(page, source_id=source_id))
            except IndexingError:
                index_failures.add(path)
                raise
            chunks += len(document.chunks)
            tokens += int(document.metadata.get("embed_total_tokens") or 0)
            indexed_pages.add(path)
            logger.debug("Indexed page", url=page.url, chunks=len(document.chunks))

    failed = await _run_batch(
        paths,
        ingest_one,
        stop_on_index_failure=not allow_partial,
        max_concurrency=concurrency,
    )
    if failed and (allow_partial or not index_failures):
        # One sequential retry pass. What fails here is a rate limit the embedder's
        # own backoff ran out of attempts on, and a corpus indexed except for the
        # pages that happened to collide is worse than a slower run.
        log.info("Retrying pages that failed", count=len(failed))
        failed = await _run_batch(
            failed,
            ingest_one,
            sequential=True,
            stop_on_index_failure=not allow_partial,
        )
    failures = [str(path) for path in failed]
    embedder = getattr(pipeline, "embedder", None)

    report = IngestReport(
        variant=resolved.name,
        pages=len(indexed_pages),
        chunks=chunks,
        embedding_tokens=tokens,
        embedded_chunks=int(getattr(embedder, "embedded_chunks", 0)),
        cached_chunks=int(getattr(embedder, "cached_chunks", 0)),
        failures=tuple(failures),
    )
    log.info(
        "Ingest complete",
        chunks=report.chunks,
        embedding_tokens=report.embedding_tokens,
        embedded_chunks=report.embedded_chunks,
        cached_chunks=report.cached_chunks,
        estimated_usd=round(report.estimated_usd, 6),
        failures=len(report.failures),
    )
    if report.failures and not allow_partial:
        raise PartialIngestError(report)
    return report
