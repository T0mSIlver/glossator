"""Whether each documentation link in a consumer answer supports the claim it is attached to.

The consumer judge sees no passages, so its groundedness fields say nothing, and
`links_on_gold` only asks whether one link names the single page a question's gold
lists; the documentation often states a fact on two pages (a guide and the API
reference), and a correct citation of the other one counts as a miss. This check
reads the link itself: the page from the vendored corpus, the section the anchor
names with its subsections, and asks a judge whether that passage, and nothing
else, states the claim the answer attached the link to.

One judge call per distinct documentation URL in an answer. Results go to
`citations.jsonl` in the run directory and are resumable; `citations.md` holds
the per-arm summary.
"""

from __future__ import annotations

import asyncio
import statistics
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import unquote, urlsplit

from pydantic import BaseModel, ConfigDict

from glossator.eval.answer_eval.models import JudgeModel
from glossator.eval.answer_eval.quota import wait_for_quota
from glossator.eval.consumer.judge import _CallsRecorder
from glossator.eval.consumer.models import ConsumerRecord, load_records
from glossator.eval.providers.client import OpenAICompatibleProvider
from glossator.eval.providers.models import ProviderCallError
from glossator.eval.providers.scopes import call_scope, candidate_scope
from glossator.ingest.pages import iter_page_paths, load_page
from glossator.ingest.sections import Section, parse_sections

CITATION_CHECK_VERSION = "citation-support/v1"

SECTION_CHAR_CAP = 16_000
PAGE_CHAR_CAP = 24_000
MARK = "⟦CITED⟧"
_LINK_END = " )\n>]\"'`,;"

CITATION_SYSTEM = f"""\
You check one citation in an answer about Mistral's documentation.

The answer marks every place it cites one URL with {MARK}. You are given the text \
that URL points to: the section its anchor names, with its subsections, or the \
whole page when the link has no anchor.

1. Identify the claims that citation is attached to: the sentence, list item or \
table row the link sits in or directly follows. When the link stands alone on its \
own line, it is attached to the statement just before it.
2. Judge from the passage alone whether it states those claims.
   - supported: the passage states every attached claim, or it follows directly \
from what the passage says.
   - partial: the passage states part of it, or the general point but not the \
specific value, name or limit the answer gives.
   - unsupported: the passage does not state the claim, or contradicts it.

Do not use outside knowledge, and do not judge whether the claim is true: only \
whether this passage says it. Navigation, link lists and headings that merely \
name a topic do not support a claim about that topic's content. Code in the \
passage counts as stating what it plainly shows.

Answer with JSON only."""


class CitationVerdict(BaseModel):
    model_config = ConfigDict(frozen=True)

    claims: str
    """The attached claims, quoted or closely paraphrased from the answer."""
    support: Literal["supported", "partial", "unsupported"]
    reason: str


Resolution = Literal["section", "page", "anchor_missing", "snapshot_page", "not_in_corpus"]


class CitationCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    consumer: str
    arm: str
    question_id: str
    question_type: str
    url: str
    page_url: str
    anchor: str | None
    resolution: Resolution
    passage_chars: int
    truncated: bool
    support: Literal["supported", "partial", "unsupported"] | None
    """None when the link resolves to nothing, which scores as unsupported."""
    claims: str = ""
    reason: str = ""
    judge_model: str = ""
    prompt_version: str = CITATION_CHECK_VERSION
    error: str | None = None

    @property
    def key(self) -> tuple[str, str, str, str]:
        return (self.consumer, self.arm, self.question_id, self.url)


@dataclass(frozen=True, slots=True)
class _Page:
    url: str
    title: str
    body: str
    sections: list[Section]


class Corpus:
    """Pages by URL: the served corpus first, then the dated snapshots, newest first."""

    def __init__(self, corpus_dir: Path, snapshots_dir: Path | None) -> None:
        self.current = self._load(corpus_dir)
        self.snapshots: dict[str, _Page] = {}
        if snapshots_dir is not None and snapshots_dir.is_dir():
            for snapshot in sorted(snapshots_dir.iterdir(), reverse=True):
                for url, page in self._load(snapshot).items():
                    self.snapshots.setdefault(url, page)

    @staticmethod
    def _load(directory: Path) -> dict[str, _Page]:
        pages: dict[str, _Page] = {}
        if not directory.is_dir():
            return pages
        for path in iter_page_paths(directory):
            page = load_page(path)
            pages[page.url] = _Page(
                url=page.url,
                title=page.title,
                body=page.body,
                sections=parse_sections(page.body, page_title=page.title),
            )
        return pages


def docs_links(answer: str, links: Sequence[str]) -> list[str]:
    """The documentation URLs of an answer, deduplicated after dropping a text fragment."""
    seen: list[str] = []
    for link in links:
        parts = urlsplit(link)
        if parts.netloc != "docs.mistral.ai":
            continue
        url = link.split(":~:text=")[0].rstrip("#")
        if url not in seen:
            seen.append(url)
    return seen


def _page_url(url: str) -> tuple[str, str | None]:
    parts = urlsplit(url)
    path = parts.path.rstrip("/") or ""
    return f"https://{parts.netloc}{path}", (unquote(parts.fragment) or None)


def _section_with_children(page: _Page, anchor: str) -> Section | None:
    for section in page.sections:
        if section.own_anchor == anchor:
            return section
    return None


def resolve_passage(corpus: Corpus, url: str) -> tuple[str, str, str | None, Resolution, bool]:
    """(page URL, passage, anchor, how it resolved, truncated)."""
    page_url, anchor = _page_url(url)
    resolution: Resolution
    page = corpus.current.get(page_url)
    if page is None:
        page = corpus.snapshots.get(page_url)
        if page is None:
            return page_url, "", anchor, "not_in_corpus", False
        resolution = "snapshot_page"
    else:
        resolution = "page"
    if anchor:
        section = _section_with_children(page, anchor)
        if section is not None:
            end = len(page.body)
            for later in page.sections[section.index + 1 :]:
                if later.level <= section.level:
                    end = later.start_offset
                    break
            text = page.body[section.start_offset : end]
            header = " > ".join(section.heading_path)
            passage = f"{header}\n\n{text}"
            truncated = len(passage) > SECTION_CHAR_CAP
            if resolution == "page":
                resolution = "section"
            return page_url, passage[:SECTION_CHAR_CAP], anchor, resolution, truncated
        if resolution == "page":
            resolution = "anchor_missing"
    passage = f"{page.title}\n\n{page.body}"
    truncated = len(passage) > PAGE_CHAR_CAP
    return page_url, passage[:PAGE_CHAR_CAP], anchor, resolution, truncated


def marked_answer(answer: str, url: str) -> str:
    """The answer with every occurrence of ``url`` (with or without a fragment directive) marked."""
    out: list[str] = []
    position = 0
    search_from = 0
    while True:
        found = answer.find(url, search_from)
        if found == -1:
            out.append(answer[position:])
            break
        end = found + len(url)
        rest = answer[end:]
        # The same URL, not a longer one it prefixes: a page link must not mark
        # that page's anchored links, which are checked on their own.
        if rest and rest[0] not in _LINK_END and not rest.startswith((":~:", "#:~:")):
            search_from = end
            continue
        while end < len(answer) and answer[end] not in _LINK_END:
            end += 1
        out.append(answer[position:end])
        out.append(f" {MARK}")
        position = search_from = end
    return "".join(out)


def render_input(record: ConsumerRecord, url: str, passage: str, resolution: Resolution) -> str:
    note = {
        "anchor_missing": "The anchor does not exist on the page; the passage is the whole page.",
        "snapshot_page": (
            "The page is not in the current documentation; the passage is its last dated version."
        ),
    }.get(resolution, "")
    return "\n\n".join(
        part
        for part in (
            f"QUESTION\n{record.question}",
            f"ANSWER\n{marked_answer(record.answer_text, url)}",
            f"CITED URL\n{url}",
            note,
            f"PASSAGE\n{passage}",
        )
        if part
    )


def load_checks(path: Path) -> list[CitationCheck]:
    if not path.is_file():
        return []
    return [
        CitationCheck.model_validate_json(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


async def _judge_link(
    provider: OpenAICompatibleProvider,
    judge: JudgeModel,
    record: ConsumerRecord,
    url: str,
    passage: str,
    resolution: Resolution,
    base: CitationCheck,
) -> CitationCheck:
    with (
        candidate_scope(f"{record.consumer}:{record.arm}:{record.question_id}"),
        call_scope("citation-support"),
    ):
        try:
            completion = await provider.complete(
                [
                    {"role": "system", "content": CITATION_SYSTEM},
                    {"role": "user", "content": render_input(record, url, passage, resolution)},
                ],
                model=judge.model,
                temperature=0.0,
                max_tokens=800,
                response_schema=CitationVerdict,
                thinking="disabled" if provider.name == "zai" else None,
            )
        except ProviderCallError as error:
            return base.model_copy(update={"error": str(error)})
    verdict = completion.parsed if isinstance(completion.parsed, CitationVerdict) else None
    if verdict is None:
        return base.model_copy(update={"error": "judge output did not validate"})
    return base.model_copy(
        update={"support": verdict.support, "claims": verdict.claims, "reason": verdict.reason}
    )


async def run_citation_check(
    run_dir: Path,
    judge: JudgeModel,
    *,
    corpus_dir: Path,
    snapshots_dir: Path | None,
    quota_ceiling: int = 80,
) -> dict[str, int]:
    records = load_records(run_dir / "records.jsonl")
    out_path = run_dir / "citations.jsonl"
    done = {
        check.key
        for check in load_checks(out_path)
        if check.error is None and check.prompt_version == CITATION_CHECK_VERSION
    }
    corpus = Corpus(corpus_dir, snapshots_dir)
    counts = {"checked": 0, "skipped": 0, "unresolved": 0, "errors": 0}
    pending: list[tuple[ConsumerRecord, str]] = []
    for record in records:
        for url in docs_links(record.answer_text, record.links):
            if (record.consumer, record.arm, record.question_id, url) in done:
                counts["skipped"] += 1
            else:
                pending.append((record, url))
    if not pending:
        return counts
    await wait_for_quota(quota_ceiling)
    recorder = _CallsRecorder(run_dir)
    recorder.path = run_dir / "citation-calls.jsonl"
    lock = asyncio.Lock()
    async with OpenAICompatibleProvider(
        judge.provider,
        asyncio.Semaphore(4 if judge.provider == "zai" else 1),
        caller_tag="eval.consumer.citations",
        recorder=recorder,
        seed=0,
    ) as provider:

        async def one(record: ConsumerRecord, url: str) -> None:
            page_url, passage, anchor, resolution, truncated = resolve_passage(corpus, url)
            base = CitationCheck(
                consumer=record.consumer,
                arm=record.arm,
                question_id=record.question_id,
                question_type=record.question_type,
                url=url,
                page_url=page_url,
                anchor=anchor,
                resolution=resolution,
                passage_chars=len(passage),
                truncated=truncated,
                support=None,
                judge_model=judge.identifier,
            )
            if resolution == "not_in_corpus":
                check = base.model_copy(update={"reason": "the page is not in the corpus"})
                counts["unresolved"] += 1
            else:
                check = await _judge_link(provider, judge, record, url, passage, resolution, base)
                counts["checked"] += 1
                if check.error is not None:
                    counts["errors"] += 1
            async with lock:
                with out_path.open("a") as handle:
                    handle.write(check.model_dump_json() + "\n")

        await asyncio.gather(*(one(record, url) for record, url in pending))
    return counts


SUPPORT_SCORE = {"supported": 1.0, "partial": 0.5, "unsupported": 0.0, None: 0.0}


def summarize(
    records: Sequence[ConsumerRecord], checks: Sequence[CitationCheck]
) -> dict[str, dict[str, float]]:
    """Per (consumer, arm): how answers cite and whether the citations hold."""
    latest: dict[tuple[str, str, str, str], CitationCheck] = {}
    for check in checks:
        if check.error is None and check.prompt_version == CITATION_CHECK_VERSION:
            latest[check.key] = check
    by_answer: dict[tuple[str, str, str], list[CitationCheck]] = defaultdict(list)
    for check in latest.values():
        by_answer[(check.consumer, check.arm, check.question_id)].append(check)
    cells: dict[str, dict[str, float]] = {}
    grouped: dict[str, list[ConsumerRecord]] = defaultdict(list)
    for record in records:
        grouped[f"{record.consumer} / {record.arm}"].append(record)
    for name, rows in sorted(grouped.items()):
        link_scores: list[float] = []
        resolutions: dict[str, int] = defaultdict(int)
        cited = supported_answer = supported_answerable = answerable = 0
        missing = 0
        for record in rows:
            wanted = docs_links(record.answer_text, record.links)
            found = by_answer.get(record.key, [])
            missing += len(wanted) - len(found)
            if wanted:
                cited += 1
            has_support = any(check.support == "supported" for check in found)
            supported_answer += has_support
            # A history answer's dates come from the snapshots; no page states when
            # it was added, so its citations cannot support that claim.
            if record.question_type not in ("unanswerable", "history"):
                answerable += 1
                supported_answerable += has_support
            for check in found:
                link_scores.append(SUPPORT_SCORE[check.support])
                resolutions[check.resolution] += 1
        total_links = sum(resolutions.values())
        cells[name] = {
            "answers": float(len(rows)),
            "answers_citing": cited / len(rows),
            "links": float(total_links),
            "links_per_answer": total_links / len(rows),
            "link_support": statistics.fmean(link_scores) if link_scores else 0.0,
            "links_supported": (
                sum(1 for s in link_scores if s == 1.0) / len(link_scores) if link_scores else 0.0
            ),
            "answers_with_supported_link": supported_answer / len(rows),
            "answerable_with_supported_link": supported_answerable / answerable
            if answerable
            else 0.0,
            "links_to_section": resolutions["section"] / total_links if total_links else 0.0,
            "links_anchor_missing": resolutions["anchor_missing"] / total_links
            if total_links
            else 0.0,
            "links_not_in_corpus": resolutions["not_in_corpus"] / total_links
            if total_links
            else 0.0,
            "links_unchecked": float(missing),
        }
    return cells


def render_summary(cells: dict[str, dict[str, float]], judge: str) -> str:
    lines = [
        "# Citation support",
        "",
        f"Each documentation link in an answer, resolved to the section its anchor names "
        f"(with subsections) or the whole page, judged by `{judge}` against the claim the "
        f"answer attached it to (`{CITATION_CHECK_VERSION}`). A link to a page outside the "
        "corpus scores as unsupported.",
        "",
        "| cell | answers citing | links / answer | link support | links supported | "
        "answerable with a supported link | to a section | anchor missing | not in corpus |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, cell in cells.items():
        lines.append(
            f"| {name} | {cell['answers_citing']:.2f} | {cell['links_per_answer']:.2f} | "
            f"{cell['link_support']:.2f} | {cell['links_supported']:.2f} | "
            f"{cell['answerable_with_supported_link']:.2f} | {cell['links_to_section']:.2f} | "
            f"{cell['links_anchor_missing']:.2f} | {cell['links_not_in_corpus']:.2f} |"
        )
    lines += [
        "",
        "`link support` scores supported 1, partial 0.5, unsupported 0 over links; "
        "`answerable with a supported link` is the share of answerable questions whose "
        "answer carries at least one fully supported link, the page-agnostic replacement "
        "for `on gold`. It counts answerable questions other than history rows: a history "
        "answer's dates come from the dated snapshots, and no page states when it was "
        "added, so every surface scores unsupported there.",
        "",
    ]
    return "\n".join(lines)
