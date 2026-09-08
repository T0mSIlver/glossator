"""The corpus as the generators see it: a page paired with its sections.

Reading and section splitting belong to ``glossator.ingest``; this only holds the
two together so that a sampler can move between a section and the page it came
from, and adds the rough token size the samplers filter on.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from glossator.ingest.pages import CorpusPage, iter_page_paths, load_page
from glossator.ingest.sections import Section, parse_sections

# Pages under these prefixes describe products released after the generating
# model's training cutoff, which is what makes them worth asking about (D-020).
POST_CUTOFF_PREFIXES = ("/studio/search/", "/vibe/")


@dataclass(frozen=True, slots=True)
class CorpusDocument:
    """One page with its sections already parsed."""

    page: CorpusPage
    sections: tuple[Section, ...]

    @property
    def url(self) -> str:
        return self.page.url

    @property
    def title(self) -> str:
        return self.page.title

    @property
    def path(self) -> str:
        """The page's site path, e.g. ``/studio/conversations``."""
        return urlparse(self.page.url).path

    @property
    def top_level(self) -> str:
        """First path segment, used to keep one area of the site from dominating."""
        return self.path.strip("/").split("/", maxsplit=1)[0] or "root"

    @property
    def is_post_cutoff(self) -> bool:
        return self.path.startswith(POST_CUTOFF_PREFIXES)


def load_documents(corpus_dir: Path) -> list[CorpusDocument]:
    """Every page of a corpus directory, in path order, with its sections."""
    documents = []
    for path in iter_page_paths(corpus_dir):
        page = load_page(path)
        sections = tuple(parse_sections(page.body, page_title=page.title))
        documents.append(CorpusDocument(page=page, sections=sections))
    return documents


def block_text(document: CorpusDocument, section: Section) -> str:
    """A section together with its subsections.

    An API operation is one heading with ``Request body`` and ``Responses``
    underneath it; a question about a parameter needs all of them, and the
    section parser deliberately keeps each heading's own text separate.
    """
    body = document.page.body
    end = len(body)
    for candidate in document.sections:
        if candidate.start_offset > section.start_offset and candidate.level <= section.level:
            end = candidate.start_offset
            break
    return body[section.start_offset : end]


def estimate_tokens(text: str) -> int:
    """Rough token count, four characters to the token.

    Only used to skip sections too small to hold a question. The exact Mistral
    tokenizer the chunker uses would be more accurate and far slower over a
    corpus this size, and no decision here turns on a few tokens.
    """
    return math.ceil(len(text) / 4)
