"""The populations, the recorded depths, the junk questions, and one query's profile."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

RUN_KIND = "floor-calibration"

POPULATIONS = ("real", "junk", "unanswerable")
"""``real`` is an answerable dataset question, ``junk`` a question about another
subject entirely. ``unanswerable`` is the dataset's own unanswerable type: written
in the corpus's vocabulary, not answered by it. It is reported separately and
never used to set the floor -- a floor low enough to accept a question the corpus
cannot answer accepts everything, which is exactly the failure D-030 is about."""

DEPTHS = (1, 5, 20, 50)
"""Where the similarity is read. 1 is the number a floor is compared against, 5
is roughly what an answer reads, 20 is the reranker's window, and 50 is deep
enough to show where the tail flattens."""

TOP_K = 50

JUNK_QUESTIONS: tuple[str, ...] = (
    # Cooking
    "how long should I proof a sourdough starter before the first bake",
    "what temperature should a rib of beef reach for medium rare",
    "why does my hollandaise split when I add the butter too quickly",
    "which flour makes the chewiest neapolitan pizza base",
    # Veterinary
    "what causes feline hyperthyroidism and how is it treated",
    "how often should a border collie puppy be wormed",
    "is xylitol dangerous for dogs in small quantities",
    "what are the early signs of laminitis in a horse",
    # Astronomy
    "why does the moon appear larger near the horizon",
    "how do astronomers measure the distance to a cepheid variable",
    "what is the difference between a meteor and a meteorite",
    "when is the next total solar eclipse visible from northern europe",
    # Sport
    "what is the offside rule in rugby union",
    "how many sets does a player need to win a grand slam final",
    "what gear ratio suits a steep alpine climb on a road bike",
)


class QuerySimilarities(BaseModel):
    """One query's similarity profile through the index."""

    model_config = ConfigDict(frozen=True)

    query: str
    population: str
    """``real`` or ``junk``."""

    question_id: str | None = None
    question_type: str | None = None
    lexical_footing: bool | None = None
    hits: int = 0
    at_depth: dict[str, float | None] = Field(default_factory=dict)
    """Similarity at each depth in ``DEPTHS``, keyed by the depth as a string."""

    error: str | None = None

    @property
    def best(self) -> float | None:
        return self.at_depth.get("1")
