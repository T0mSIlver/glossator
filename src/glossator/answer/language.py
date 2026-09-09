"""The question's language, and the English wording retrieval is run with.

The index holds English pages, so a French question meets a hybrid ranking whose
BM25 half has no term in common with any page, and a reranker reading French
against English (D-008a). Rendering the question in English before retrieval
fixes the query side without touching the index; the answer is still generated
from the original question, so it comes back in the language it was asked in.

Detection is deterministic and free: an English question must not pay a model
call to learn that it is English. The rendering is one short structured call,
recorded like every other call in the run.
"""

import re
import unicodedata

import structlog
from pydantic import BaseModel, ConfigDict

from glossator.answer.config import AnswerConfig
from glossator.answer.llm import LLM, Completion
from glossator.answer.prompts import RETRIEVAL_QUERY_SYSTEM, RETRIEVAL_QUERY_USER

logger = structlog.get_logger(__name__)

ENGLISH = "en"
FRENCH = "fr"
UNKNOWN = "und"
"""Text in a script English never uses. The language is not identified, but it is
certainly not English, so it is rendered like any other non-English question."""

RETRIEVAL_QUERY_PURPOSE = "retrieval_query"
"""The call kind a rendering is recorded under, prefixed by the strategy that
asked for it."""

# Elisions split apart, so "l'API" contributes the French marker "l" and the
# identifier "api"; digits and underscores stay inside a token, so `safe_prompt`
# survives as one word and can never look like a stopword.
_WORD = re.compile(r"[^\W\d_][\w]*", re.UNICODE)

_FRENCH_MARKER_WORDS = """
    le la les un une des du au aux de d l qu que qui quoi quel quelle quels
    quelles comment pourquoi quand je tu il elle nous vous ils elles mon ma mes
    son sa ses notre votre leur ce cette ces dans avec pour sans sous entre chez
    vers depuis pendant contre selon ainsi afin lorsque meme tous toutes autre
    autres et ou mais donc car ne pas plus jamais rien aucun toujours
    est sont etre suis fait faire faut peut peux peuvent dois doit doivent
    utiliser configurer appeler renvoie renvoyer definir activer parametre
"""

_FRENCH_MARKERS = frozenset(_FRENCH_MARKER_WORDS.split())

_ENGLISH_MARKER_WORDS = """
    the a an this that these those how what why when where which who whom
    do does did is are was were be been being have has had can could should
    would will shall may might must
    i you he she we they my your our their its it
    in with for on to of and or but from into about between over under
    use using set setting call calling return returns define defining enable
    there here not no any all each every other another same
"""

_ENGLISH_MARKERS = frozenset(_ENGLISH_MARKER_WORDS.split())

# A word in both lists is evidence of neither. Subtracting the overlap once, here,
# is what keeps a word like "on" from tilting a short question either way.
_SHARED = _FRENCH_MARKERS & _ENGLISH_MARKERS
FRENCH_MARKERS = _FRENCH_MARKERS - _SHARED
ENGLISH_MARKERS = _ENGLISH_MARKERS - _SHARED

FRENCH_LETTERS = frozenset("àâäçéèêëîïôöùûüÿœæ")
"""Letters French writes and English does not."""

ACCENT_CAP = 2
"""Accents count for at most this much, so one borrowed word does not outweigh a
sentence of English, while an unaccented French question still has its words."""


class EnglishRendering(BaseModel):
    """The structured output the rendering prompt asks for."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    english_question: str


class RetrievalQuery(BaseModel):
    """What retrieval should be run with, and where it came from.

    ``question`` is always the original: generation reads it from here, so no
    caller can accidentally answer the rendering instead of the question.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    question: str
    language: str
    text: str
    completion: Completion | None = None
    """The rendering call, for the run to charge and record. ``None`` when the
    question needed no call."""

    note: str | None = None

    @property
    def translated(self) -> bool:
        return self.text != self.question


def detect_language(question: str) -> str:
    """``en``, ``fr`` or ``und``, from the words and the letters alone.

    Unsure means English: the corpus is English, so a wrong ``en`` costs the
    retrieval this project already measured (D-008a), while a wrong ``fr`` spends
    a call rewriting a question that needed no rewriting.
    """
    text = question.strip()
    if not text:
        return ENGLISH
    if _mostly_non_latin(text):
        return UNKNOWN

    words = [_fold(word) for word in _WORD.findall(text)]
    french = sum(word in FRENCH_MARKERS for word in words)
    english = sum(word in ENGLISH_MARKERS for word in words)
    accents = min(sum(letter in FRENCH_LETTERS for letter in text.lower()), ACCENT_CAP)
    return FRENCH if french + accents > english else ENGLISH


async def render_for_retrieval(
    question: str,
    *,
    llm: LLM,
    config: AnswerConfig,
    purpose: str = RETRIEVAL_QUERY_PURPOSE,
) -> RetrievalQuery:
    """The question as retrieval should see it: English, identifiers untouched.

    An English question is returned as it came, with no model call. A rendering
    that fails to parse or comes back empty falls back to the original question
    and says so in ``note``: a broken rendering has to degrade to the measured
    French-over-English behaviour, not to an empty query.
    """
    language = detect_language(question)
    if language == ENGLISH or not config.translate_for_retrieval:
        return RetrievalQuery(question=question, language=language, text=question)

    completion = await llm.complete(
        [
            {"role": "system", "content": RETRIEVAL_QUERY_SYSTEM},
            {"role": "user", "content": RETRIEVAL_QUERY_USER.format(question=question)},
        ],
        temperature=0.0,
        max_tokens=config.render_max_tokens,
        response_schema=EnglishRendering,
        purpose=purpose,
    )

    rendering = completion.parsed
    if not isinstance(rendering, EnglishRendering) or not rendering.english_question.strip():
        logger.warning("Retrieval rendering unusable, keeping the original question")
        return RetrievalQuery(
            question=question,
            language=language,
            text=question,
            completion=completion,
            note="rendering failed; retrieved with the original question",
        )

    return RetrievalQuery(
        question=question,
        language=language,
        text=rendering.english_question.strip(),
        completion=completion,
    )


def _fold(word: str) -> str:
    """Lowercase without diacritics, so one spelling of a marker matches both.

    A question typed without its accents is still French, and a stopword list
    written once should cover "meme" and "même" alike.
    """
    stripped = unicodedata.normalize("NFD", word.lower())
    return "".join(character for character in stripped if not unicodedata.combining(character))


def _mostly_non_latin(text: str) -> bool:
    """Whether the letters are mostly from a script English does not use."""
    letters = [character for character in text if character.isalpha()]
    if not letters:
        return False
    latin = sum(unicodedata.name(letter, "").startswith("LATIN") for letter in letters)
    return latin * 2 < len(letters)


__all__ = [
    "ACCENT_CAP",
    "ENGLISH",
    "ENGLISH_MARKERS",
    "FRENCH",
    "FRENCH_LETTERS",
    "FRENCH_MARKERS",
    "RETRIEVAL_QUERY_PURPOSE",
    "UNKNOWN",
    "EnglishRendering",
    "RetrievalQuery",
    "detect_language",
    "render_for_retrieval",
]
