"""A small in-process BM25 over corpus sections.

Used to decide whether an "unanswerable" candidate is really unanswerable: the
question has to miss the whole corpus, not just the section it was written from.
Deliberately independent of Vespa, so that generating a dataset needs no running
index, and lexical rather than semantic so that it costs nothing to run.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from glossator.eval.corpus import CorpusDocument
from glossator.ingest.sections import Section

_TOKEN = re.compile(r"[a-z0-9]+")

_K1 = 1.5
_B = 0.75


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.casefold())


@dataclass(frozen=True, slots=True)
class SearchHit:
    document: CorpusDocument
    section: Section
    score: float

    @property
    def label(self) -> str:
        """How the hit is named when it is shown to a model or recorded."""
        return f"{self.document.title} > {' > '.join(self.section.heading_path)}"


class LexicalIndex:
    """BM25 over every non-empty section of the corpus."""

    def __init__(self, documents: Sequence[CorpusDocument]) -> None:
        self.entries: list[tuple[CorpusDocument, Section]] = [
            (document, section)
            for document in documents
            for section in document.sections
            if section.body.strip()
        ]
        self._counts = [
            Counter(tokenize(f"{' '.join(section.heading_path)} {section.body}"))
            for _document, section in self.entries
        ]
        self._lengths = [sum(counts.values()) for counts in self._counts]
        self._average_length = (sum(self._lengths) / len(self._lengths)) if self._lengths else 0.0
        document_frequency: Counter[str] = Counter()
        for counts in self._counts:
            document_frequency.update(counts.keys())
        total = max(len(self._counts), 1)
        self._idf = {
            term: math.log(1 + (total - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }

    def search(self, query: str, *, top_k: int = 5) -> list[SearchHit]:
        terms = tokenize(query)
        if not terms or not self.entries:
            return []
        scored: list[tuple[float, int]] = []
        for index, counts in enumerate(self._counts):
            score = 0.0
            for term in terms:
                frequency = counts.get(term)
                if not frequency:
                    continue
                norm = 1 - _B + _B * (self._lengths[index] / (self._average_length or 1))
                score += self._idf[term] * frequency * (_K1 + 1) / (frequency + _K1 * norm)
            if score > 0:
                scored.append((score, index))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [
            SearchHit(
                document=self.entries[index][0],
                section=self.entries[index][1],
                score=round(score, 4),
            )
            for score, index in scored[:top_k]
        ]
