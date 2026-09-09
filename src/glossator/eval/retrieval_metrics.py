"""Ranked hits and gold sources in, recall and nDCG out.

The arithmetic is the toolkit's: ``RetrieverEvaluator`` walks the dataset and
``MetricsCalculator`` computes recall@k, MRR and nDCG@k, so nothing here reimplements
a metric that a reviewer would then have to check twice. What this module owns is
the part the toolkit leaves open -- what counts as a hit.

Two answers, because they measure different things:

- **page**: the hit's URL is one of the question's gold URLs. This is what a
  reader needs to be able to find the answer at all.
- **section**: the hit's URL *and* anchor match a gold URL and anchor. This is
  what a citation needs to deep-link (D-003a), and it is the number that separates
  a chunker that keeps a section together from one that does not.

A question whose gold carries no anchor cannot be scored at the section level --
most of the corpus's markdown headings have none -- so it is scored at the page
level only and counted separately, rather than being scored as a miss.

Matching goes through the harness's ``relevant_reference_ids`` proxies rather
than through chunk ids: gold is written as a URL and an anchor, chunk ids are
derived from a page's span and change whenever the chunker does.

One list is de-duplicated before it is scored. Several chunks of one page are one
result to a reader, and to the harness they are several: its ideal DCG assumes
each relevant id appears once, so four chunks of the right page in the top four
produce an nDCG of 2.13. Collapsing the ranked list to distinct proxies, each at
its best rank, fixes that and turns recall@k into "the answer was among the first
k *pages*", which is the number D-012a's "several chunks of one section crowd the
top" is about.
"""

from collections.abc import Mapping, Sequence
from enum import StrEnum

import structlog
from mistralai.search.toolkit.evals import (
    EvaluationDataset,
    EvaluationQuery,
    MetricsCalculator,
    RetrievalMetrics,
    RetrievalStepResult,
    RetrieverEvaluator,
    generate_proxy,
)
from mistralai.search.toolkit.search import SearchResult

from glossator.eval.datasets import EvalQuestion, QuestionType

logger = structlog.get_logger(__name__)

K_VALUES = [1, 3, 5, 10]

STEP_NAME = "retrieval"
"""The harness reports metrics per workflow step; there is one step per row here,
because the grid varies the configuration and not the pipeline shape."""


class Matching(StrEnum):
    """How closely a hit has to agree with the gold source to count."""

    PAGE = "page"
    SECTION = "section"

    @property
    def metadata_keys(self) -> list[str]:
        """Chunk metadata the harness builds a hit's proxy id from."""
        return ["url"] if self is Matching.PAGE else ["url", "anchor"]


def gold_proxies(question: EvalQuestion, matching: Matching) -> list[str] | None:
    """The question's gold sources as harness proxy ids, or ``None`` when it
    cannot be scored at this matching.

    The proxy spelling is the harness's own (``generate_proxy`` joins ``key_value``
    pairs with underscores), so gold and hits are built the same way and a change
    to one side cannot silently stop matching the other.
    """
    if question.type is QuestionType.UNANSWERABLE:
        return None
    if matching is Matching.PAGE:
        return [f"url_{gold.url}" for gold in question.gold]
    if any(gold.anchor is None for gold in question.gold):
        return None
    return [f"url_{gold.url}_anchor_{gold.anchor}" for gold in question.gold]


def scoreable(questions: Sequence[EvalQuestion], matching: Matching) -> list[EvalQuestion]:
    """The questions that have gold to be scored against at this matching."""
    return [question for question in questions if gold_proxies(question, matching) is not None]


def deduplicate(results: Sequence[SearchResult], matching: Matching) -> list[SearchResult]:
    """One entry per distinct page (or section), at the best rank it reached.

    The proxy is rebuilt with the harness's own ``generate_proxy`` so the key this
    collapses on is exactly the key the harness will match on.
    """
    seen: set[str] = set()
    kept: list[SearchResult] = []
    for result in results:
        proxy = generate_proxy(result.chunk, matching.metadata_keys)
        if proxy in seen:
            continue
        seen.add(proxy)
        kept.append(result)
    return kept


async def evaluate(
    questions: Sequence[EvalQuestion],
    results: Mapping[str, list[SearchResult]],
    matching: Matching,
    top_k: int,
) -> dict[str, RetrievalMetrics]:
    """Per-question metrics for one configuration, keyed by question id.

    ``results`` holds the ranked hits each question already produced, so the
    harness scores a run that has happened rather than driving one: the reranker's
    calls are made once, recorded once, and paid for once.
    """
    included = [question for question in scoreable(questions, matching) if question.id in results]
    if not included:
        return {}

    by_query: dict[str, list[SearchResult]] = {}
    for question in included:
        # The harness's workflow callable receives only the query string, so two
        # questions with the same text would be indistinguishable inside it.
        if question.question in by_query:
            raise ValueError(
                f"dataset has two questions with identical text ({question.id!r} repeats it); "
                "the harness keys its workflow on the query string"
            )
        by_query[question.question] = deduplicate(results[question.id], matching)

    async def workflow(query: str) -> list[RetrievalStepResult]:
        # Never raises: the harness aborts the whole run on the first workflow
        # exception, and a lookup miss is a fact about one question, not a reason
        # to lose the other 299.
        return [
            RetrievalStepResult(
                step_name=STEP_NAME,
                results=by_query.get(query, []),
                top_k=top_k,
                k_values=K_VALUES,
            )
        ]

    dataset = EvaluationDataset(
        name=f"{matching}-matching",
        queries=[
            EvaluationQuery(
                query=question.question,
                relevant_ids=[],
                relevant_reference_ids=gold_proxies(question, matching),
                metadata={"question_id": question.id, "type": str(question.type)},
            )
            for question in included
        ],
    )
    evaluator = RetrieverEvaluator(k_values=K_VALUES, metadata_keys=matching.metadata_keys)
    _summary, per_query = await evaluator.evaluate_workflow_dataset_batch_with_results(
        dataset=dataset,
        workflow=workflow,
        # One batch, in order: the results are already in hand, so batching would
        # only make the returned order harder to pair back with the questions.
        batch_size=max(len(included), 1),
        max_concurrent_batches=1,
    )
    return {
        question.id: result.workflow_metrics[STEP_NAME]
        for question, result in zip(included, per_query, strict=True)
        if STEP_NAME in result.workflow_metrics
    }


def aggregate(metrics: Sequence[RetrievalMetrics]) -> RetrievalMetrics | None:
    """The mean of a group of per-question metrics, or ``None`` for an empty group."""
    if not metrics:
        return None
    return MetricsCalculator.aggregate_metrics(list(metrics))


def as_row(metrics: RetrievalMetrics | None, questions: int) -> dict[str, float | int | None]:
    """One aggregate as the flat numbers a table and a figure both read."""
    if metrics is None:
        return {"questions": questions}
    return {
        "questions": questions,
        "recall@1": _round(metrics.recall_at_k.get(1)),
        "recall@3": _round(metrics.recall_at_k.get(3)),
        "recall@5": _round(metrics.recall_at_k.get(5)),
        "recall@10": _round(metrics.recall_at_k.get(10)),
        "mrr": _round(metrics.mrr),
        "ndcg@10": _round(metrics.ndcg_at_k.get(10)),
    }


METRIC_NAMES = ("recall@1", "recall@3", "recall@5", "recall@10", "mrr", "ndcg@10")


def _round(value: float | None) -> float | None:
    return None if value is None else round(value, 4)


__all__ = [
    "K_VALUES",
    "METRIC_NAMES",
    "STEP_NAME",
    "Matching",
    "aggregate",
    "as_row",
    "deduplicate",
    "evaluate",
    "gold_proxies",
    "scoreable",
]
