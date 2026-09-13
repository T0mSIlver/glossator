"""Grid expansion from YAML, and the completeness of what a run records.

The engine is a stand-in: a grid run is a loop over configurations and questions
plus a run directory, and none of that needs Vespa or a model to be exercised.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from glossator.eval.datasets import read_jsonl
from glossator.eval.retrieval_grid.grid import expand, select
from glossator.eval.retrieval_grid.metrics import recompute
from glossator.eval.retrieval_grid.models import RUN_KIND, GridSpec
from glossator.eval.retrieval_grid.run import GridRun
from glossator.eval.retrieval_report import render_readme, write_report
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import Hit, SearchTrace
from glossator.retrieval.reranker import RerankTrace

FIXTURE_DATASET = Path(__file__).parent.parent / "fixtures" / "retrieval-dev.jsonl"
SHIPPED_GRID = Path("eval/configs/retrieval-grid.yaml")

GRID: dict[str, Any] = {
    "name": "test-grid",
    "top_k": 5,
    "weight_sets": {
        "shipped": {},
        "vector-heavy": {"content_embedding_closeness": 8.0, "bm25_content": 0.3},
    },
    "axes": {"variant": ["sec128", "sec1024"], "weights": ["shipped", "vector-heavy"]},
    "exclude": [{"variant": "sec128", "weights": "vector-heavy"}],
    "rerank": {
        "model": "ministral-8b-2512",
        "candidates": 8,
        "max_calls": 2,
        "configurations": ["sec1024-shipped"],
    },
}


def spec(**overrides: Any) -> GridSpec:
    return GridSpec.model_validate({**GRID, **overrides})


def test_the_grid_is_the_cross_product_minus_the_exclusions() -> None:
    names = [entry.name for entry in expand(spec())]
    assert names == [
        "sec128-shipped",
        "sec1024-shipped",
        "sec1024-vector-heavy",
        "sec1024-shipped+rerank",
    ]


def test_a_row_carries_the_weight_set_it_names() -> None:
    entries = {entry.name: entry for entry in expand(spec())}
    assert entries["sec1024-vector-heavy"].config.ranking_weights == {
        "content_embedding_closeness": 8.0,
        "bm25_content": 0.3,
    }
    assert entries["sec1024-shipped"].config.ranking_weights == {}
    assert entries["sec128-shipped"].config.top_k == 5


def test_a_reranked_row_differs_from_its_base_in_the_reranking_only() -> None:
    entries = {entry.name: entry for entry in expand(spec())}
    base = entries["sec1024-shipped"].config
    reranked = entries["sec1024-shipped+rerank"].config
    assert reranked.rerank and not base.rerank
    assert reranked.rerank_model == "ministral-8b-2512"
    assert reranked.rerank_candidates == 8
    assert (
        reranked.model_copy(
            update={"rerank": False, "rerank_model": base.rerank_model, "rerank_candidates": 20}
        )
        == base
    )


def test_a_weight_set_the_axes_name_must_be_defined() -> None:
    with pytest.raises(ValueError, match="no definition"):
        spec(axes={"variant": ["sec1024"], "weights": ["invented"]})


def test_an_unknown_axis_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown grid axis"):
        spec(axes={"chunker": ["section"]})


def test_reranking_a_row_the_grid_does_not_hold_is_refused() -> None:
    with pytest.raises(ValueError, match="does not contain"):
        expand(spec(rerank={**GRID["rerank"], "configurations": ["page128-shipped"]}))


def test_selecting_names_keeps_the_grid_order() -> None:
    entries = expand(spec())
    assert [
        entry.name for entry in select(entries, ["sec1024-vector-heavy", "sec128-shipped"])
    ] == [
        "sec128-shipped",
        "sec1024-vector-heavy",
    ]
    assert select(entries, None) == entries
    with pytest.raises(ValueError, match="unknown configuration"):
        select(entries, ["nope"])


def test_the_shipped_grid_expands_and_keeps_the_reranker_under_its_budget() -> None:
    shipped = GridSpec.load(SHIPPED_GRID)
    entries = expand(shipped)
    reranked = [entry for entry in entries if entry.reranked]
    assert {entry.variant for entry in reranked} == {"sec1024"}
    assert len(reranked) == 2
    assert shipped.rerank.max_calls == 600
    assert all(entry.config.top_k == 20 for entry in entries)
    assert all(entry.config.rerank_candidates == 20 for entry in reranked)


class StubEngine:
    """Returns fixed hits and a trace, and counts what it was asked."""

    def __init__(self, config: RetrievalConfig, fail: set[str] | None = None) -> None:
        self.config = config
        self.fail = fail or set()
        self.context = None
        self.retriever = self
        self.queries: list[str] = []

    async def embed_query(self, query: str, context: object = None) -> list[float]:
        return [0.1, 0.2, 0.3]

    async def search_with_trace(
        self,
        query: str,
        rerank: bool = False,
        embedding: list[float] | None = None,
    ) -> tuple[list[Hit], SearchTrace]:
        self.queries.append(query)
        if query in self.fail:
            raise RuntimeError("Vespa said no")
        hits = [
            Hit(
                chunk_id=f"chunk-{rank}",
                score=1.0 if rerank else 5.0 - rank,
                url="https://docs.mistral.ai/capabilities/function-calling",
                anchor="tool-choice",
                heading_path=("Function calling", "Tool choice"),
                page_title="Function calling",
                kind="doc",
                locale="en",
                section_index=rank,
                content="body",
                source_id="https://docs.mistral.ai/capabilities/function-calling",
                start_offset=0,
                end_offset=4,
                rerank_score=1.0 if rerank else None,
                retrieval_score=5.0 - rank,
            )
            for rank in range(3)
        ]
        trace = SearchTrace(
            query=query,
            variant=self.config.variant,
            considered=3,
            kept=3,
            latency_ms=12.5,
            lexical_footing=True,
            rerank=RerankTrace(
                model=self.config.rerank_model,
                candidates=3,
                applied=True,
                cost_usd=0.0008,
            )
            if rerank
            else None,
        )
        return hits, trace


def run_grid(tmp_path: Path, *, limit: int = 3, fail: set[str] | None = None) -> dict[str, Any]:
    questions = read_jsonl(FIXTURE_DATASET)[:limit]
    entries = expand(spec())
    run = GridRun(
        entries,
        questions,
        tmp_path / "run",
        spec=spec(),
        dataset_path=FIXTURE_DATASET,
        request_interval=0.0,
        engine_factory=lambda config, _recorder: StubEngine(config, fail),
    )
    return asyncio.run(run.run())


def test_a_run_writes_every_file_the_record_contract_asks_for(tmp_path: Path) -> None:
    run_grid(tmp_path)
    run_dir = tmp_path / "run"
    assert {path.name for path in run_dir.iterdir()} == {
        "config.json",
        "records.jsonl",
        "calls.jsonl",
        "metrics.json",
        "figures",
    }


def test_a_record_carries_the_ranked_hits_and_the_question_it_answers(tmp_path: Path) -> None:
    run_grid(tmp_path)
    rows = [
        json.loads(line) for line in (tmp_path / "run" / "records.jsonl").read_text().splitlines()
    ]
    # Four configurations over three questions.
    assert len(rows) == 12
    row = rows[0]
    assert row["question_id"] == "fx-001"
    assert row["gold"] == [
        {
            "url": "https://docs.mistral.ai/capabilities/function-calling",
            "anchor": "tool-choice",
        }
    ]
    assert [hit["rank"] for hit in row["hits"]] == [1, 2, 3]
    assert row["hits"][0]["chunk_id"] == "chunk-0"
    assert row["hits"][0]["retrieval_score"] == 5.0
    assert row["lexical_footing"] is True
    assert row["considered"] == 3 and row["kept"] == 3
    assert row["latency_ms"] == 12.5


def test_the_config_records_every_parameter_of_the_run(tmp_path: Path) -> None:
    run_grid(tmp_path)
    config = json.loads((tmp_path / "run" / "config.json").read_text())
    assert config["kind"] == RUN_KIND
    assert config["dataset_sha256"]
    assert config["questions"] == 3
    assert [row["name"] for row in config["grid"]] == [
        "sec128-shipped",
        "sec1024-shipped",
        "sec1024-vector-heavy",
        "sec1024-shipped+rerank",
    ]
    assert config["rerank"]["prompt_sha256"]
    assert config["rerank"]["model"] == "ministral-8b-2512"


def test_the_reranker_stops_at_its_call_budget(tmp_path: Path) -> None:
    metrics = run_grid(tmp_path)
    # max_calls is 2 in the test grid, over three questions.
    assert metrics["rerank_calls"] == 2
    rows = [
        json.loads(line)
        for line in (tmp_path / "run" / "records.jsonl").read_text().splitlines()
        if json.loads(line)["configuration"].endswith("+rerank")
    ]
    assert [row["reranked"] for row in rows] == [True, True, False]
    assert "budget" in rows[-1]["rerank_error"]


def test_a_call_the_budget_stopped_is_not_counted_as_a_fallback(tmp_path: Path) -> None:
    """A row past the budget sent nothing, so it neither cost anything nor
    returned a ranking that could not be used."""
    metrics = run_grid(tmp_path)
    assert metrics["rerank_billed_calls"] == 2
    assert metrics["rerank_fallbacks"] == 0
    assert metrics["rerank_skipped"] == 1
    reranked = metrics["configurations"]["sec1024-shipped+rerank"]
    assert reranked["rerank_billed_calls"] == 2
    assert reranked["rerank_fallbacks"] == 0
    assert reranked["rerank_skipped"] == 1

    readme = render_readme(json.loads((tmp_path / "run" / "config.json").read_text()), metrics)
    assert "The reranker made 2 calls" in readme
    assert "1 question of a reranked configuration ran without the reranker" in readme
    assert "fell back to retrieval order" not in readme


def test_the_winner_is_ranked_over_the_questions_its_matching_can_score(tmp_path: Path) -> None:
    """The section level scores fewer questions than the page level, so a single
    dataset-wide count under both would overstate one of them."""
    metrics = run_grid(tmp_path, limit=12)
    assert metrics["best"]["page"]["questions"] == metrics["page_scoreable"] == 11
    assert metrics["best"]["section"]["questions"] == metrics["section_scoreable"] == 9
    assert metrics["best"]["ranked_on"] == "recall@5 over the questions each matching can score"


def test_a_question_that_fails_is_recorded_rather_than_aborting_the_run(tmp_path: Path) -> None:
    questions = read_jsonl(FIXTURE_DATASET)[:3]
    metrics = run_grid(tmp_path, fail={questions[1].question})
    assert len(metrics["errors"]) == 4
    assert metrics["errors"][0]["error"] == "Vespa said no"
    # The failed question drops out of the common set but not out of the run.
    assert metrics["common_questions"] == 2
    assert metrics["questions"] == 3


def test_unanswerable_questions_are_reported_rather_than_scored(tmp_path: Path) -> None:
    metrics = run_grid(tmp_path, limit=12)
    unanswerable = metrics["unanswerable"]
    assert unanswerable["questions"] == 1
    assert unanswerable["with_a_top_hit"] == 4
    assert unanswerable["rows"][0]["top_hit"]["chunk_id"] == "chunk-0"
    for row in metrics["configurations"].values():
        assert "unanswerable" not in row["metrics"]["page"]["common"]


def test_metrics_and_the_readme_regenerate_from_the_records_alone(tmp_path: Path) -> None:
    first = run_grid(tmp_path, limit=12)
    run_dir = tmp_path / "run"
    (run_dir / "metrics.json").unlink()
    again = asyncio.run(recompute(run_dir))
    assert again == first
    write_report(run_dir, json.loads((run_dir / "config.json").read_text()), again)
    readme = (run_dir / "README.md").read_text()
    assert "# Retrieval grid" in readme
    assert "recall@5" in readme
    assert sorted(path.name for path in (run_dir / "figures").glob("*.svg")) == [
        "best-two-by-type-page.svg",
        "best-two-by-type-section.svg",
        "recall-at-k-page.svg",
        "recall-at-k-section.svg",
    ]


def test_the_shipped_grid_file_parses(tmp_path: Path) -> None:
    raw = yaml.safe_load(SHIPPED_GRID.read_text())
    assert raw["top_k"] == 20
    assert set(raw["axes"]["variant"]) == {"page128", "sec128", "sec1024"}
