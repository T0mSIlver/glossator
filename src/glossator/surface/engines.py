"""One search engine per index variant, for the API, which serves every variant."""

from typing import Any

from glossator.index.variants import VARIANTS, get_variant
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import SearchEngine
from glossator.surface.errors import bad_param


class EngineRegistry:
    """Engines are cheap to hold and expensive to rebuild; one per variant.

    ``engines`` is the injection seam the tests use: a pre-built (fake) engine
    under a variant name is served as-is and the real one is never built.
    """

    def __init__(self) -> None:
        self.engines: dict[str, Any] = {}

    def get(self, variant: str) -> SearchEngine:
        require_variant(variant)
        engine = self.engines.get(variant)
        if engine is None:
            engine = SearchEngine(RetrievalConfig.shipped(variant=variant))
            self.engines[variant] = engine
        return engine


def require_variant(variant: str) -> None:
    try:
        get_variant(variant)
    except ValueError as exc:
        raise bad_param(str(exc), f"use one of {sorted(VARIANTS)}") from exc


__all__ = ["EngineRegistry", "require_variant"]
