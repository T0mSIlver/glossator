"""Score floors, the lexical-footing gate, and the embedding probe's arithmetic.

All offline: the floors are applied to hits the engine already has, and the probe
runs against a stand-in embedder whose geometry is chosen by hand.
"""

import asyncio
from pathlib import Path

import pytest

from glossator.retrieval.config import RetrievalConfig, cosine_only_weights, query_weights
from glossator.retrieval.probe import (
    MIN_SEPARATION,
    PROBE_PAIRS,
    UNRELATED_PASSAGES,
    EmbeddingProbeError,
    ProbeResult,
    cosine,
    probe_embedding,
)
from glossator.retrieval.vocabulary import STOPWORDS, corpus_vocabulary, load_vocabulary, tokenize

FIXTURE_CORPUS = Path(__file__).parent / "fixtures" / "corpus"


def test_the_floors_are_off_until_they_are_calibrated() -> None:
    config = RetrievalConfig()
    assert config.similarity_floor is None
    assert config.similarity_margin is None
    assert not config.scores_similarity


def test_setting_either_floor_asks_for_the_similarity_read_out() -> None:
    assert RetrievalConfig(similarity_floor=0.7).scores_similarity
    assert RetrievalConfig(similarity_margin=0.1).scores_similarity


def test_a_floor_outside_the_cosine_range_is_refused() -> None:
    with pytest.raises(ValueError):
        RetrievalConfig(similarity_floor=1.5)
    with pytest.raises(ValueError):
        RetrievalConfig(similarity_margin=-0.1)


def test_reranking_fewer_candidates_than_are_returned_is_refused() -> None:
    with pytest.raises(ValueError, match="rerank_candidates"):
        RetrievalConfig(rerank=True, top_k=10, rerank_candidates=5)


def test_the_cosine_read_out_zeroes_every_weight_but_the_cosine_term() -> None:
    weights = cosine_only_weights()
    assert weights["content_embedding_cosine_similarity_score"] == 1.0
    assert set(weights.values()) == {0.0, 1.0}
    assert sum(weights.values()) == 1.0
    # The query inputs Vespa reads carry the `_weight` suffix (D-025).
    assert "content_embedding_cosine_similarity_score_weight" in query_weights(weights)


def test_cosine_is_computed_without_assuming_unit_length() -> None:
    """Mistral's embeddings are not normalised, so a dot product is a different
    number; the embeddings page says so."""
    assert cosine([3.0, 0.0], [10.0, 0.0]) == pytest.approx(1.0)
    assert cosine([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    assert cosine([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_the_vocabulary_holds_the_words_of_the_corpus() -> None:
    vocabulary = corpus_vocabulary(FIXTURE_CORPUS)
    assert vocabulary.pages == 9
    assert "streaming" in vocabulary.words
    assert "tool_choice" not in vocabulary.words and "tool" in vocabulary.words
    # French pages are in the corpus, so French words are in the vocabulary.
    assert "vecteurs" in vocabulary.words


def test_a_documentation_question_has_lexical_footing() -> None:
    vocabulary = corpus_vocabulary(FIXTURE_CORPUS)
    assert vocabulary.has_footing("how do I stream a chat completion")
    assert vocabulary.missing_terms("how do I stream a chat completion") == []


def test_a_question_about_another_subject_has_none() -> None:
    vocabulary = corpus_vocabulary(FIXTURE_CORPUS)
    assert not vocabulary.has_footing("what causes feline hyperthyroidism in cats")
    assert "hyperthyroidism" in vocabulary.missing_terms("what causes feline hyperthyroidism")


def test_scaffolding_words_alone_do_not_give_footing() -> None:
    """Every English question contains "how" and "do"; a gate that counted them
    would answer yes for every query ever asked."""
    vocabulary = corpus_vocabulary(FIXTURE_CORPUS)
    assert "how" in STOPWORDS and "comment" in STOPWORDS
    assert not vocabulary.has_footing("how do I braise a shin of beef")


def test_a_question_with_no_content_words_is_given_the_benefit_of_the_doubt() -> None:
    vocabulary = corpus_vocabulary(FIXTURE_CORPUS)
    assert vocabulary.has_footing("how do I do this?")


def test_accented_words_stay_whole() -> None:
    assert tokenize("Les modèles d'embeddings") == ["les", "modèles", "d", "embeddings"]


def test_a_corpus_that_is_not_on_disk_makes_footing_unknown_rather_than_false() -> None:
    assert load_vocabulary(Path("corpus/does-not-exist")) is None


class StubEmbedder:
    """Returns a vector per text from a table, so the probe's geometry is chosen."""

    def __init__(self, vectors: dict[str, list[float]]) -> None:
        self.model_name = "stub-embed"
        self.vectors = vectors

    async def embed(self, texts: list[str], context: object = None) -> object:
        class Result:
            embeddings = [self.vectors[text] for text in texts]
            total_tokens = 0

        return Result()

    async def embed_query(self, text: str, context: object = None) -> list[float]:
        return self.vectors[text]


def basis(index: int, size: int) -> list[float]:
    return [1.0 if position == index else 0.0 for position in range(size)]


def honest_vectors() -> dict[str, list[float]]:
    """Each question sits nearly on its own passage's axis and nowhere else."""
    size = len(PROBE_PAIRS) + len(UNRELATED_PASSAGES)
    vectors: dict[str, list[float]] = {}
    for index, (question, passage) in enumerate(PROBE_PAIRS):
        vectors[passage] = basis(index, size)
        near = basis(index, size)
        near[(index + 1) % size] = 0.2
        vectors[question] = near
    for offset, passage in enumerate(UNRELATED_PASSAGES):
        vectors[passage] = basis(len(PROBE_PAIRS) + offset, size)
    return vectors


def probe(vectors: dict[str, list[float]]) -> ProbeResult:
    async def run() -> ProbeResult:
        return await probe_embedding("sec1024", embedder=StubEmbedder(vectors))  # type: ignore[arg-type]

    return asyncio.run(run())


def test_an_honest_embedding_model_passes_the_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("glossator.retrieval.probe._round_trip", _no_round_trip)
    result = probe(honest_vectors())
    assert result.passed
    assert result.round_trip is None
    assert result.lowest_separation >= MIN_SEPARATION
    # The summary names the variant and the model the variant is built with, which
    # is what a failure message has to say for a reader to act on it.
    assert "sec1024 on mistral-embed" in result.summary()


def test_a_model_with_collapsed_geometry_fails_on_separation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Random weights leave every text at roughly the same distance from every
    other: the similarities stay high and the separation goes to zero (D-031)."""
    monkeypatch.setattr("glossator.retrieval.probe._round_trip", _no_round_trip)
    vectors = {text: [1.0, 1.0, 1.0] for text in _all_probe_texts()}
    with pytest.raises(EmbeddingProbeError) as error:
        probe(vectors)
    assert "sec1024" in str(error.value)
    assert "mistral-embed" in str(error.value)


def test_a_question_closer_to_the_wrong_passage_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("glossator.retrieval.probe._round_trip", _no_round_trip)
    vectors = honest_vectors()
    first_question, _first_passage = PROBE_PAIRS[0]
    _second_question, second_passage = PROBE_PAIRS[1]
    vectors[first_question] = list(vectors[second_passage])
    with pytest.raises(EmbeddingProbeError, match="closer to another probe passage"):
        probe(vectors)


def test_a_stored_vector_that_disagrees_with_a_fresh_one_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def drifted(_variant: object, _embedder: object) -> float:
        return 0.42

    monkeypatch.setattr("glossator.retrieval.probe._round_trip", drifted)
    with pytest.raises(EmbeddingProbeError, match="built by a different model"):
        probe(honest_vectors())


async def _no_round_trip(_variant: object, _embedder: object) -> None:
    return None


def _all_probe_texts() -> list[str]:
    return (
        [question for question, _passage in PROBE_PAIRS]
        + [passage for _question, passage in PROBE_PAIRS]
        + list(UNRELATED_PASSAGES)
    )
