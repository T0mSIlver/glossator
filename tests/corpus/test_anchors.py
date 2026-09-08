"""The slugify ports decide whether a citation anchor resolves on the live site."""

from __future__ import annotations

import pytest

from glossator.corpus.mistral_docs.anchors import (
    AnchorAllocator,
    faq_slugify,
    section_tab_level,
    slugify,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Available Models", "available-models"),
        ("Before You Start", "before-you-start"),
        ("What's next", "whats-next"),
        ("Step 1. Developer", "step-1-developer"),
        ("  Padded  Heading  ", "padded-heading"),
        ("Multiple   spaces", "multiple-spaces"),
        ("Hyphen -- collapse", "hyphen-collapse"),
        ("-leading and trailing-", "leading-and-trailing"),
        ("service_tier stays a word char", "service_tier-stays-a-word-char"),
        ("Café déjà vu", "caf-dj-vu"),
        ("", "heading"),
        ("!!!", ""),
    ],
)
def test_slugify_matches_the_site(text: str, expected: str) -> None:
    assert slugify(text) == expected


def test_allocator_dedupes_with_numeric_suffixes() -> None:
    allocator = AnchorAllocator()
    assert allocator.allocate("Overview") == "overview"
    assert allocator.allocate("Overview") == "overview-1"
    assert allocator.allocate("Overview") == "overview-2"
    assert allocator.allocate("Other") == "other"


def test_allocator_avoids_reserved_section_ids() -> None:
    allocator = AnchorAllocator()
    allocator.reserve("overview")
    assert allocator.allocate("Overview") == "overview-1"


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("What happens if I omit service_tier?", "what-happens-if-i-omit-servicetier"),
        (
            "Why did my request return service_tier: standard?",
            "why-did-my-request-return-servicetier-standard",
        ),
    ],
)
def test_faq_slugify_drops_underscores(question: str, expected: str) -> None:
    # The FAQ accordion uses its own slugify; the heading one would keep the underscore.
    assert faq_slugify(question) == expected
    assert slugify(question) != expected


def test_faq_slugify_agrees_with_headings_when_there_is_nothing_to_differ_on() -> None:
    question = "Can I use Priority Tier on every model?"
    assert faq_slugify(question) == "can-i-use-priority-tier-on-every-model"
    assert slugify(question) == faq_slugify(question)


@pytest.mark.parametrize(
    ("as_prop", "variant", "expected"),
    [
        ("h1", None, 2),
        ("h2", None, 2),
        ("h1", "secondary", 3),
        ("h2", "secondary", 3),
        ("h3", None, 3),
        ("h4", "secondary", 4),
        (None, None, 2),
        ("nonsense", None, 2),
    ],
)
def test_section_tab_level(as_prop: str | None, variant: str | None, expected: int) -> None:
    assert section_tab_level(as_prop, variant) == expected
