"""Retrieval configuration validation.

A weight naming a feature the schema does not generate is silently ignored by
Vespa, and a filter value is interpolated into YQL, so both are checked here
rather than discovered as a query that quietly returns the wrong thing.
"""

import pytest
from pydantic import ValidationError

from glossator.index.variants import VARIANTS
from glossator.retrieval.config import RetrievalConfig


def test_defaults_name_a_real_variant() -> None:
    config = RetrievalConfig()
    assert config.variant in VARIANTS
    assert config.index_variant.schema_name.startswith("docs_")


def test_every_declared_variant_is_configurable() -> None:
    for name, variant in VARIANTS.items():
        config = RetrievalConfig(variant=name)
        assert config.index_variant is variant


def test_an_unknown_variant_is_rejected() -> None:
    with pytest.raises(ValidationError, match="unknown index variant"):
        RetrievalConfig(variant="sec2048")


def test_known_ranking_features_are_accepted() -> None:
    config = RetrievalConfig(
        ranking_weights={"bm25_content": 1.0, "content_embedding_closeness": 5.0}
    )
    assert config.ranking_weights["content_embedding_closeness"] == 5.0


def test_an_unknown_ranking_feature_is_rejected() -> None:
    with pytest.raises(ValidationError, match="unknown ranking feature"):
        RetrievalConfig(ranking_weights={"bm25_body": 1.0})


def test_an_unknown_kind_is_rejected() -> None:
    with pytest.raises(ValidationError, match="unknown page kind"):
        RetrievalConfig(kinds=frozenset({"cookbook"}))


def test_a_malformed_locale_is_rejected() -> None:
    """Filter values reach YQL, so the vocabulary is closed by shape."""
    with pytest.raises(ValidationError, match="malformed locale"):
        RetrievalConfig(locales=frozenset({'en" or true or "'}))


def test_top_k_is_bounded() -> None:
    with pytest.raises(ValidationError):
        RetrievalConfig(top_k=0)
    with pytest.raises(ValidationError):
        RetrievalConfig(top_k=1000)


def test_no_filter_means_no_yql_predicate() -> None:
    assert RetrievalConfig().yql_filter() is None


def test_filters_become_a_conjunction_of_in_clauses() -> None:
    config = RetrievalConfig(kinds=frozenset({"api", "doc"}), locales=frozenset({"en"}))
    assert config.yql_filter() == 'kind in ("api", "doc") and locale in ("en")'


def test_the_config_is_frozen() -> None:
    config = RetrievalConfig()
    with pytest.raises(ValidationError):
        config.top_k = 3
