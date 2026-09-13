"""The one reading of a docs.mistral.ai location the three tools share."""

import pytest

from glossator.doc_paths import split_docs_location, under_prefix


@pytest.mark.parametrize(
    "value",
    [
        "https://docs.mistral.ai/studio/search#limits",
        "docs.mistral.ai/studio/search#limits",
        "/studio/search/#limits",
        "studio/search#limits",
        "site:docs.mistral.ai/studio/search#limits",
    ],
)
def test_every_form_names_the_same_path_and_fragment(value: str) -> None:
    assert split_docs_location(value, "page_url") == ("/studio/search", "limits")


@pytest.mark.parametrize("value", ["https://docs.mistral.ai/", "docs.mistral.ai", "/", "site:"])
def test_the_site_root_is_the_empty_path(value: str) -> None:
    assert split_docs_location(value, "under") == ("", "")


@pytest.mark.parametrize(
    "value", ["example.com/studio", "https://example.com/studio", "docs.mistral.ai.example.com/x"]
)
def test_another_host_is_refused_under_the_argument_name(value: str) -> None:
    with pytest.raises(ValueError, match="page_url must be on docs.mistral.ai"):
        split_docs_location(value, "page_url")


def test_under_prefix_is_the_page_url_without_a_trailing_slash() -> None:
    assert under_prefix("studio/search/") == "https://docs.mistral.ai/studio/search"
    assert under_prefix("/") == "https://docs.mistral.ai"


def test_under_prefix_refuses_an_empty_value() -> None:
    with pytest.raises(ValueError, match="under must contain a documentation path"):
        under_prefix("  ")
