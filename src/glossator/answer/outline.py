"""The model picks pages from the site map, then reads them whole.

Search finds passages that look like the question; a table of contents finds the
page that is *about* it. That is the difference this strategy exists to measure --
for a question whose answer is spread over a page ("how do I set up X"), reading
the page beats reading its five best-matching paragraphs.

The outline is built from the corpus manifest, which is the same hash-checked file
the index was ingested from, so a page in the outline is a page in the index. API
reference pages are left out: there are 49 of them, one per endpoint, and their
titles carry no signal a picker can use. Pages are read back through the index by
their url, which is the chunks' ``source_id``, so no corpus file is opened at
answer time.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import structlog
from pydantic import BaseModel, ConfigDict, Field

from glossator.answer.citations import Answer
from glossator.answer.config import AnswerConfig
from glossator.answer.docs_index import DocsIndex
from glossator.answer.generation import AnswerRun
from glossator.answer.llm import LLM
from glossator.answer.prompts import OUTLINE_SYSTEM, OUTLINE_USER
from glossator.retrieval.engine import Hit

logger = structlog.get_logger(__name__)

NAME = "outline"

DEFAULT_MANIFEST = Path("corpus/mistral-docs/manifest.json")
OUTLINE_KINDS = frozenset({"doc", "model"})


class PagePick(BaseModel):
    """Which pages the model wants to read."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    page_numbers: list[int] = Field(default_factory=list)
    reason: str = ""


@dataclass(frozen=True, slots=True)
class OutlineEntry:
    """One page in the site map, as the model sees it and as the index knows it."""

    number: int
    title: str
    breadcrumbs: tuple[str, ...]
    url: str

    def render(self) -> str:
        trail = " > ".join(self.breadcrumbs)
        return f"{self.number}. {trail} > {self.title}" if trail else f"{self.number}. {self.title}"


def load_outline(manifest_path: Path = DEFAULT_MANIFEST) -> tuple[OutlineEntry, ...]:
    """The site map, numbered, in manifest (url) order so the tree reads top-down."""
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    pages = [entry for entry in entries if entry.get("kind") in OUTLINE_KINDS]
    return tuple(
        OutlineEntry(
            number=number,
            title=str(entry["title"]),
            breadcrumbs=_breadcrumbs(str(entry["path"])),
            url=str(entry["url"]),
        )
        for number, entry in enumerate(sorted(pages, key=lambda page: page["url"]), start=1)
    )


def render_outline(entries: tuple[OutlineEntry, ...]) -> str:
    return "\n".join(entry.render() for entry in entries)


async def answer(
    question: str,
    *,
    engine: DocsIndex,
    llm: LLM,
    config: AnswerConfig,
    manifest_path: Path = DEFAULT_MANIFEST,
) -> Answer:
    run = AnswerRun(strategy=NAME, variant=engine.config.variant)
    run.rounds = 1
    entries = load_outline(manifest_path)

    completion = await llm.complete(
        [
            {"role": "system", "content": OUTLINE_SYSTEM.format(page_cap=config.page_cap)},
            {
                "role": "user",
                "content": OUTLINE_USER.format(question=question, outline=render_outline(entries)),
            },
        ],
        response_schema=PagePick,
        max_tokens=300,
        purpose=f"{NAME}:pick_pages",
    )
    run.spent(completion)

    picked = _picked(completion.parsed, entries, config.page_cap)
    run.event(
        "outline",
        "pick_pages",
        arguments={"pages": len(entries), "cap": config.page_cap},
        result_ids=[entry.url for entry in picked],
        note=completion.parsed.reason if isinstance(completion.parsed, PagePick) else None,
    )

    hits: list[Hit] = []
    for entry in picked:
        # source_id is the page url for every chunk this project writes, so a page
        # is read straight out of the index rather than off disk.
        page = await engine.navigation_at(entry.url).read(None, None, top_k=config.page_read_top_k)
        hits.extend(page)
        run.event(
            "retrieval",
            "read",
            arguments={"source_id": entry.url},
            result_ids=[hit.chunk_id for hit in page],
            note=None if page else "page not in the index",
        )

    logger.info("Outline pages read", pages=len(picked), chunks=len(hits))
    return await run.finish(question, hits, llm=llm, config=config)


def _picked(
    parsed: BaseModel | None, entries: tuple[OutlineEntry, ...], cap: int
) -> list[OutlineEntry]:
    """The pages the model named, in its order, ignoring numbers that do not exist."""
    if not isinstance(parsed, PagePick):
        return []
    by_number = {entry.number: entry for entry in entries}
    seen: set[int] = set()
    picked: list[OutlineEntry] = []
    for number in parsed.page_numbers:
        entry = by_number.get(number)
        if entry is None or number in seen:
            continue
        seen.add(number)
        picked.append(entry)
        if len(picked) == cap:
            break
    return picked


def _breadcrumbs(path: str) -> tuple[str, ...]:
    """The page's place in the site tree, from its corpus path.

    The manifest carries no breadcrumb field; the path mirrors the url, which is
    the site's own hierarchy, so the directories above the file are the trail.
    """
    parts = Path(path).parts[:-1]
    return tuple(part.replace("-", " ") for part in parts)


__all__ = [
    "DEFAULT_MANIFEST",
    "NAME",
    "OUTLINE_KINDS",
    "OutlineEntry",
    "PagePick",
    "answer",
    "load_outline",
    "render_outline",
]
