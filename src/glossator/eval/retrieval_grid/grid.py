"""The grid's rows, expanded from the spec and optionally narrowed by name."""

from collections.abc import Iterable, Sequence

from glossator.eval.retrieval_grid.models import GridEntry, GridSpec
from glossator.retrieval.config import RetrievalConfig


def expand(spec: GridSpec) -> list[GridEntry]:
    """The grid's rows, in a stable order: the cross product, then the reranked rows.

    A reranked row is a copy of the row it names rather than a row of its own, so
    "reranking is worth this much" is a comparison between two rows that differ in
    one field and share everything else.
    """
    entries: list[GridEntry] = []
    excluded = {tuple(sorted(rule.items())) for rule in spec.exclude}
    for variant in spec.axes.get("variant", []):
        for weights in spec.axes.get("weights", []):
            if tuple(sorted({"variant": variant, "weights": weights}.items())) in excluded:
                continue
            entries.append(
                GridEntry(
                    name=f"{variant}-{weights}",
                    variant=variant,
                    weights=weights,
                    config=RetrievalConfig(
                        variant=variant,
                        top_k=spec.top_k,
                        ranking_weights=spec.weight_sets[weights],
                    ),
                )
            )

    by_name = {entry.name: entry for entry in entries}
    for name in spec.rerank.configurations:
        base = by_name.get(name)
        if base is None:
            raise ValueError(
                f"rerank names configuration {name!r}, which the grid does not contain; "
                f"available: {sorted(by_name)}"
            )
        entries.append(
            GridEntry(
                name=f"{name}+rerank",
                variant=base.variant,
                weights=base.weights,
                config=base.config.model_copy(
                    update={
                        "rerank": True,
                        "rerank_candidates": spec.rerank.candidates,
                        "rerank_model": spec.rerank.model,
                        "rerank_temperature": spec.rerank.temperature,
                    }
                ),
            )
        )
    return entries


def select(entries: Sequence[GridEntry], names: Iterable[str] | None) -> list[GridEntry]:
    """The named rows, in the grid's own order. ``None`` means every row."""
    if names is None:
        return list(entries)
    wanted = {name.strip() for name in names if name.strip()}
    unknown = sorted(wanted - {entry.name for entry in entries})
    if unknown:
        raise ValueError(
            f"unknown configuration(s) {unknown}; the grid holds "
            f"{sorted(entry.name for entry in entries)}"
        )
    return [entry for entry in entries if entry.name in wanted]
