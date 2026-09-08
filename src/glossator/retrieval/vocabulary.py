"""Does the corpus contain any of the words the question is made of?

With k-nearest-neighbour search there is no such thing as no result: every query
lands somewhere, and "feline hyperthyroidism" comes back with a confident page
about something else (D-030). A vector score cannot say "not covered" on its own,
because it is only meaningful relative to other scores from the same model. A
word can: if no content word of the question occurs anywhere in the corpus, the
corpus does not discuss the subject, and the engine can say so.

The vocabulary is built once from the same section text ingestion embeds, so it
answers for the corpus that was indexed rather than for the pages on the site.
"""

import re
from functools import lru_cache
from pathlib import Path

import structlog

from glossator.ingest.pages import CorpusError, iter_page_paths, load_page
from glossator.ingest.sections import parse_sections

logger = structlog.get_logger(__name__)

_TOKEN = re.compile(r"[^\W_]+")


def tokenize(text: str) -> list[str]:
    """Casefolded runs of letters and digits, underscores excluded.

    Accented letters are kept rather than stripped, so ``modèles`` stays one word:
    the corpus is part French (D-008) and both sides of the comparison go through
    this function, so a French question is tested against French text.
    """
    return _TOKEN.findall(text.casefold())


# Words that occur in any English or French question regardless of its subject. A
# footing test that counted them would answer "yes" for every query ever asked,
# which is the failure mode this check exists to avoid. Kept short and closed:
# the only job is to strip question scaffolding, not to do linguistics.
STOPWORDS = frozenset(
    (
        # English
        "a", "about", "all", "also", "am", "an", "and", "any", "are", "as", "at", "be", "been",
        "but", "by", "can", "cannot", "could", "do", "does", "doing", "done", "for", "from",
        "get", "give", "got", "had", "has", "have", "how", "i", "if", "in", "into", "is", "it",
        "its", "me", "my", "no", "not", "of", "on", "one", "only", "or", "our", "out", "over",
        "should", "so", "some", "such", "than", "that", "the", "their", "them", "then", "there",
        "these", "they", "this", "those", "to", "up", "us", "use", "used", "using", "was", "way",
        "we", "what", "when", "where", "which", "while", "who", "why", "will", "with", "within",
        "would", "you", "your",
        # French
        "avec", "chez", "comment", "dans", "de", "des", "du", "en", "est", "et", "je", "la",
        "le", "les", "moins", "ne", "pas", "plus", "pour", "que", "quel", "quelle", "quelles",
        "quels", "qui", "quoi", "sans", "sur", "un", "une",
    )
)  # fmt: skip


class Vocabulary:
    """Every word the indexed corpus contains, and the footing test over it."""

    def __init__(self, words: frozenset[str], pages: int) -> None:
        self.words = words
        self.pages = pages

    def content_terms(self, query: str) -> list[str]:
        """The query's words with the scaffolding removed, in order, de-duplicated."""
        seen: dict[str, None] = {}
        for term in tokenize(query):
            if term not in STOPWORDS and not term.isdigit():
                seen.setdefault(term, None)
        return list(seen)

    def has_footing(self, query: str) -> bool:
        """True when at least one content word of the query occurs in the corpus.

        A query with no content words at all ("how do I do this?") has nothing to
        test and is given the benefit of the doubt: the gate exists to catch a
        question about another subject, not to refuse a vague one.
        """
        terms = self.content_terms(query)
        if not terms:
            return True
        return any(term in self.words for term in terms)

    def missing_terms(self, query: str) -> list[str]:
        """The query's content words the corpus does not contain, for the trace."""
        return [term for term in self.content_terms(query) if term not in self.words]


@lru_cache(maxsize=4)
def corpus_vocabulary(corpus_dir: Path) -> Vocabulary:
    """The corpus's words, read once per directory per process.

    Cached because an engine is built per request in some entrypoints and the walk
    is a few hundred files; the corpus is vendored and does not change under a
    running process.
    """
    words: set[str] = set()
    pages = 0
    for path in iter_page_paths(corpus_dir):
        page = load_page(path)
        pages += 1
        words.update(tokenize(page.title))
        for section in parse_sections(page.body, page_title=page.title):
            words.update(tokenize(" ".join(section.heading_path)))
            words.update(tokenize(section.body))
    logger.info(
        "Built corpus vocabulary", corpus_dir=str(corpus_dir), pages=pages, words=len(words)
    )
    return Vocabulary(frozenset(words), pages)


def load_vocabulary(corpus_dir: Path) -> Vocabulary | None:
    """The corpus's vocabulary, or ``None`` when the corpus is not on disk.

    A missing corpus makes the footing test unanswerable rather than false: an
    engine served from an index whose corpus directory was not shipped should
    report "unknown" and keep searching, not refuse everything.
    """
    try:
        return corpus_vocabulary(corpus_dir)
    except CorpusError as error:
        logger.warning(
            "No corpus to build a vocabulary from; lexical footing will be unknown",
            corpus_dir=str(corpus_dir),
            error=str(error),
        )
        return None


__all__ = ["STOPWORDS", "Vocabulary", "corpus_vocabulary", "load_vocabulary"]
