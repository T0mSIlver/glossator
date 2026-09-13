"""Offline checks for stored citation text-fragment links."""

import json
from pathlib import Path

from glossator.answer.citations import Citation, Trace, TracedSource
from glossator.answer.llm import TokenUsage
from glossator.eval.answer_eval.models import QuestionRecord
from glossator.eval.fragments import PageResponse, check_run, refragment
from glossator.eval.page_text import (
    FragmentText,
    fragment_found,
    parse_fragment_url,
    visible_text,
)

PAGE = "https://docs.mistral.ai/example"


def _write_run(path: Path) -> None:
    path.mkdir()
    source = "Use **`tool_call_id`** when appending the result & response."
    citation = Citation(
        n=1,
        url=PAGE,
        anchor="tools",
        chunk_id="chunk",
        quote="Use tool_call_id when appending the result & response.",
        verified=True,
        reason="verified after emphasis normalization",
        fragment_url=(
            f"{PAGE}#tools:~:text=Use%20toolcallid%20when%20appending%20the%20result%20%26%20response."
        ),
    )
    trace = Trace(
        strategy="single_pass",
        variant="sec1024",
        prompt_version="v1",
        sources=[
            TracedSource(
                n=1,
                citation_url=f"{PAGE}#tools",
                heading_path=["Tools"],
                chunk_ids=["chunk"],
                tokens=10,
            )
        ],
        context_text=f"[1] {PAGE}#tools\nTools\n{source}",
    )
    record = QuestionRecord(
        question_id="q1",
        question="Which field?",
        question_type="single_page",
        language="en",
        reference_answer="Use the identifier.",
        strategy="single_pass",
        variant="sec1024",
        model="ministral-14b-2512",
        citations=[citation],
        trace=trace,
        usage=TokenUsage(),
    )
    (path / "records.jsonl").write_text(record.model_dump_json() + "\n")


def test_fragment_parser_distinguishes_exact_and_range_forms() -> None:
    anchor, exact = parse_fragment_url(f"{PAGE}#tools:~:text=one%2C%20two")
    _, ranged = parse_fragment_url(f"{PAGE}#:~:text=first%20words,last%20words")

    assert anchor == "tools"
    assert (exact.start, exact.end) == ("one, two", None)
    assert (ranged.start, ranged.end) == ("first words", "last words")


def test_visible_text_drops_scripts_styles_tags_and_decodes_entities() -> None:
    body = visible_text(
        "<style>hidden</style><main>One&nbsp; <b>visible</b> &amp; useful</main>"
        "<script>also hidden</script>"
    )

    assert body == ["One visible & useful"]


RERANKER_HTML = (
    "<h3 id='llm-reranker'>LLM Reranker</h3>"
    "<ul><li>After initial retrieval to <code>improve</code> quality</li></ul>"
    "<p><strong>Cost optimization</strong>:</p>\n"
    "<p>LLM reranking is expensive (1 LLM call per chunk). Reduce cost by:</p>"
)


def test_visible_text_cuts_the_page_at_block_boundaries() -> None:
    assert visible_text(RERANKER_HTML) == [
        "LLM Reranker",
        "After initial retrieval to improve quality",
        "Cost optimization:",
        "LLM reranking is expensive (1 LLM call per chunk). Reduce cost by:",
    ]


def test_a_plain_fragment_across_two_paragraphs_is_not_found() -> None:
    blocks = visible_text(RERANKER_HTML)

    assert fragment_found(blocks, FragmentText("Cost optimization: LLM")) == (
        False,
        "across blocks",
    )
    assert fragment_found([" ".join(blocks)], FragmentText("Cost optimization: LLM")) == (
        True,
        None,
    )
    assert fragment_found(blocks, FragmentText("LLM reranking is expensive")) == (True, None)
    assert fragment_found(blocks, FragmentText("no such words")) == (False, "text absent")


def test_a_range_may_span_blocks_when_each_end_sits_in_one() -> None:
    blocks = visible_text(RERANKER_HTML)

    assert fragment_found(blocks, FragmentText("Cost optimization:", "LLM")) == (True, None)
    assert fragment_found(blocks, FragmentText("Reduce cost by", "Cost optimization")) == (
        False,
        "range order",
    )
    assert fragment_found(blocks, FragmentText("LLM Reranker", "quality Cost")) == (
        False,
        "across blocks",
    )


def test_check_writes_results_and_fetches_each_page_once(tmp_path: Path) -> None:
    run = tmp_path / "run"
    _write_run(run)
    calls: list[str] = []

    def fetch(url: str) -> PageResponse:
        calls.append(url)
        return PageResponse(
            status_code=200,
            content=(
                b"<html><body>Use tool_call_id when appending the result "
                b"&amp; response.</body></html>"
            ),
        )

    refragment(run)
    metrics = check_run(run, fetch=fetch)
    check_run(run, fetch=lambda url: (_ for _ in ()).throw(AssertionError(url)))
    result = json.loads((run / "fragments" / "results.jsonl").read_text())

    assert calls == [PAGE]
    assert metrics["share_found_among_html_eligible"] == 1.0
    assert result["fragment_text"] == "Use tool_call_id when appending the result & response."
    assert "calls no model" in (run / "fragments" / "README.md").read_text()


def test_refragment_uses_source_text_and_archives_the_old_url(tmp_path: Path) -> None:
    run = tmp_path / "run"
    _write_run(run)

    result = refragment(run)
    citation = json.loads((run / "records.jsonl").read_text())["citations"][0]

    assert result == {"records": 1, "citations": 1, "changed": 1}
    assert citation["fragment_url_v1"].endswith(
        "text=Use%20toolcallid%20when%20appending%20the%20result%20%26%20response."
    )
    assert citation["fragment_url"].endswith(
        "text=Use%20tool_call_id%20when%20appending%20the%20result%20%26%20response."
    )


def test_refragment_adds_a_missing_url_and_records_that_it_was_absent(tmp_path: Path) -> None:
    run = tmp_path / "run"
    _write_run(run)
    row = json.loads((run / "records.jsonl").read_text())
    row["citations"][0].pop("fragment_url")
    (run / "records.jsonl").write_text(json.dumps(row) + "\n")

    first = refragment(run)
    second = refragment(run)
    citation = json.loads((run / "records.jsonl").read_text())["citations"][0]

    assert first["changed"] == 1
    assert second["changed"] == 0
    assert citation["fragment_url_v1"] is None
    assert citation["fragment_url"].endswith(
        "text=Use%20tool_call_id%20when%20appending%20the%20result%20%26%20response."
    )
