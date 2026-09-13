"""Check whether citation text fragments occur in the live documentation HTML."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import httpx

from glossator.answer.citations import fragment_link, matched_source_quote
from glossator.eval.answer_eval.judge import source_texts
from glossator.eval.answer_eval.models import QuestionRecord

DEFAULT_SAMPLE = 60
DEFAULT_SEED = 0
_DIRECTIVE = ":~:text="
_WHITESPACE = re.compile(r"\s+")
_TAB_LABEL = re.compile(
    r"(?m)^\*\*(?:Python|TypeScript|JavaScript|cURL|Bash|Shell|JSON|Go|Java|Rust|Ruby|PHP|C#|Output)\*\*\s*$"
)


@dataclass(frozen=True, slots=True)
class FragmentText:
    start: str
    end: str | None = None

    @property
    def json_value(self) -> str | dict[str, str]:
        return self.start if self.end is None else {"start": self.start, "end": self.end}


@dataclass(frozen=True, slots=True)
class CitationCheck:
    question_id: str
    question_type: str
    n: int
    url: str
    anchor: str | None
    fragment_url: str
    fragment: FragmentText
    quote: str
    source_text: str


@dataclass(frozen=True, slots=True)
class PageResponse:
    status_code: int
    content: bytes


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag.casefold() in {"script", "style"}:
            self._hidden += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in {"script", "style"} and self._hidden:
            self._hidden -= 1

    def handle_data(self, data: str) -> None:
        if not self._hidden:
            self.parts.append(data)


def visible_text(html: str) -> str:
    parser = _VisibleText()
    parser.feed(html)
    parser.close()
    return _WHITESPACE.sub(" ", "".join(parser.parts)).strip()


def parse_fragment_url(url: str) -> tuple[str | None, FragmentText]:
    fragment = urlsplit(url).fragment
    anchor, separator, directive = fragment.partition(_DIRECTIVE)
    if not separator:
        raise ValueError(f"URL has no text fragment directive: {url}")
    values = directive.split(",", 1)
    start = unquote(values[0])
    end = unquote(values[1]) if len(values) == 2 else None
    return anchor or None, FragmentText(start=start, end=end)


class PageCache:
    def __init__(
        self,
        directory: Path,
        *,
        fetch: Callable[[str], PageResponse] | None = None,
    ) -> None:
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self.index_path = directory / "index.json"
        self.entries: dict[str, dict[str, Any]] = {}
        if self.index_path.is_file():
            self.entries = json.loads(self.index_path.read_text())
        self.fetch = fetch or self._fetch

    def get(self, url: str) -> PageResponse:
        entry = self.entries.get(url)
        if entry is not None:
            content = (self.directory / entry["file"]).read_bytes()
            return PageResponse(status_code=int(entry["status_code"]), content=content)

        response = self.fetch(url)
        filename = f"{hashlib.sha256(url.encode()).hexdigest()}.html"
        (self.directory / filename).write_bytes(response.content)
        self.entries[url] = {"file": filename, "status_code": response.status_code}
        temporary = self.index_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.entries, indent=2, sort_keys=True) + "\n")
        temporary.replace(self.index_path)
        return response

    @staticmethod
    def _fetch(url: str) -> PageResponse:
        with httpx.Client(
            follow_redirects=True,
            timeout=30.0,
            headers={"User-Agent": "glossator-fragment-check/1"},
        ) as client:
            response = client.get(url)
        return PageResponse(status_code=response.status_code, content=response.content)


def _source_passages(record: QuestionRecord) -> dict[int, str]:
    passages = source_texts(record.trace)
    if record.trace is None:
        return passages
    for source in record.trace.sources:
        passage = passages.get(source.n)
        heading = " > ".join(source.heading_path)
        if passage is not None and heading and passage.startswith(f"{heading}\n"):
            passages[source.n] = passage[len(heading) + 1 :]
    return passages


def collect(run_dir: Path, *, fragment_field: str = "fragment_url") -> list[CitationCheck]:
    checks: list[CitationCheck] = []
    records_path = run_dir / "records.jsonl"
    for line in records_path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        record = QuestionRecord.model_validate(row)
        passages = _source_passages(record)
        for raw, citation in zip(row.get("citations", []), record.citations, strict=True):
            fragment_url = raw.get(fragment_field)
            if not citation.verified or not fragment_url:
                continue
            anchor, fragment = parse_fragment_url(str(fragment_url))
            checks.append(
                CitationCheck(
                    question_id=record.question_id,
                    question_type=record.question_type,
                    n=citation.n,
                    url=citation.url,
                    anchor=anchor,
                    fragment_url=str(fragment_url),
                    fragment=fragment,
                    quote=citation.quote,
                    source_text=passages.get(citation.n, ""),
                )
            )
    return checks


def _contains(page_text: str, fragment: FragmentText) -> tuple[bool, str | None]:
    page = _WHITESPACE.sub(" ", page_text).casefold()
    start = _WHITESPACE.sub(" ", fragment.start).strip().casefold()
    first = page.find(start)
    if first < 0:
        return False, "text absent"
    if fragment.end is None:
        return True, None
    end = _WHITESPACE.sub(" ", fragment.end).strip().casefold()
    if page.find(end) < 0:
        return False, "text absent"
    if page.find(end, first + len(start)) < 0:
        return False, "range order"
    return True, None


def _from_tab(check: CitationCheck) -> bool:
    source_match = matched_source_quote(check.quote, check.source_text, min_quote_chars=1)
    if source_match is None:
        prefix = check.source_text
    else:
        position = check.source_text.find(source_match)
        prefix = check.source_text[:position] if position >= 0 else check.source_text
    return _TAB_LABEL.search(prefix) is not None


def _metrics(
    rows: Sequence[Mapping[str, Any]], *, sample: int, seed: int, fragment_field: str
) -> dict[str, Any]:
    failures = Counter(str(row["failure"]) for row in rows if row.get("failure"))
    tab_excluded = sum(bool(row.get("tab_panel")) and not bool(row["found"]) for row in rows)
    found = sum(bool(row["found"]) for row in rows)
    eligible = len(rows) - tab_excluded
    by_type: dict[str, dict[str, Any]] = {}
    for question_type in sorted({str(row["question_type"]) for row in rows}):
        typed = [row for row in rows if row["question_type"] == question_type]
        typed_tab = sum(bool(row.get("tab_panel")) and not bool(row["found"]) for row in typed)
        typed_found = sum(bool(row["found"]) for row in typed)
        typed_eligible = len(typed) - typed_tab
        by_type[question_type] = {
            "checked": len(typed),
            "found": typed_found,
            "tab_panel_excluded": typed_tab,
            "html_eligible": typed_eligible,
            "share_found_among_html_eligible": (
                typed_found / typed_eligible if typed_eligible else None
            ),
        }
    return {
        "kind": "fragment_resolvability",
        "sample_requested": sample,
        "seed": seed,
        # Which generation of link was measured. D-036b reports a before and an
        # after row for the same run; without this the two numbers are
        # indistinguishable once the run directory is read back.
        "fragment_field": fragment_field,
        "checked": len(rows),
        "found": found,
        "share_found": found / len(rows) if rows else None,
        "tab_panel_excluded": tab_excluded,
        "html_eligible": eligible,
        "share_found_among_html_eligible": found / eligible if eligible else None,
        "failures": dict(sorted(failures.items())),
        "by_question_type": by_type,
    }


def render_readme(metrics: Mapping[str, Any]) -> str:
    failures = metrics["failures"]
    failure_rows = (
        "\n".join(f"| {reason} | {count} |" for reason, count in failures.items()) or "| none | 0 |"
    )
    type_rows = "\n".join(
        f"| {name} | {row['checked']} | {row['found']} | {row['tab_panel_excluded']} | "
        f"{_percent(row['share_found_among_html_eligible'])} |"
        for name, row in metrics["by_question_type"].items()
    )
    return f"""# Citation fragment resolvability

The check sampled {metrics["checked"]} verified citations from `records.jsonl` with
seed {metrics["seed"]}, reading the links stored under `{metrics["fragment_field"]}`.
It fetched each cited documentation page once, reduced the HTML to visible text, and
searched for the decoded text fragment without regard to case or whitespace runs.
Range directives pass only when both ends occur in order.

{metrics["found"]} of {metrics["checked"]} sampled fragments were present
({_percent(metrics["share_found"])}). {metrics["tab_panel_excluded"]} absent fragment(s)
came from tab-labelled source text. The live HTML omits non-default tab panels even
though a browser can render them after selecting the tab (D-003). After excluding
those citations, {metrics["found"]} of {metrics["html_eligible"]} fragments were found
({_percent(metrics["share_found_among_html_eligible"])}).

## Failures

| reason | citations |
|---|---:|
{failure_rows}

## Question types

| type | checked | found | tab exclusions | found in eligible HTML |
|---|---:|---:|---:|---:|
{type_rows}

## Files

`results.jsonl` has one row per sampled citation. `metrics.json` contains these
counts. `pages/` caches the HTTP responses, so repeating the command reads no
documentation pages from the network. This check calls no model, so it has no
`calls.jsonl`.
"""


def _percent(value: float | None) -> str:
    return "--" if value is None else f"{float(value):.1%}"


def check_run(
    run_dir: Path,
    *,
    sample: int = DEFAULT_SAMPLE,
    seed: int = DEFAULT_SEED,
    fetch: Callable[[str], PageResponse] | None = None,
    fragment_field: str = "fragment_url",
) -> dict[str, Any]:
    candidates = collect(run_dir, fragment_field=fragment_field)
    chosen = (
        random.Random(seed).sample(candidates, sample) if len(candidates) > sample else candidates
    )
    output_dir = run_dir / "fragments"
    output_dir.mkdir(parents=True, exist_ok=True)
    cache = PageCache(output_dir / "pages", fetch=fetch)
    page_text: dict[str, str] = {}
    rows: list[dict[str, Any]] = []
    for citation in chosen:
        failure: str | None = None
        text = page_text.get(citation.url)
        if text is None:
            try:
                response = cache.get(citation.url)
                if response.status_code != 200:
                    failure = "page fetch"
                else:
                    text = visible_text(response.content.decode("utf-8", errors="replace"))
                    page_text[citation.url] = text
            except httpx.HTTPError:
                failure = "page fetch"
        found = False
        if failure is None and text is not None:
            found, failure = _contains(text, citation.fragment)
        tab_panel = bool(failure in {"text absent", "range order"} and _from_tab(citation))
        rows.append(
            {
                "question_id": citation.question_id,
                "question_type": citation.question_type,
                "citation_number": citation.n,
                "url": citation.url,
                "anchor": citation.anchor,
                "fragment_url": citation.fragment_url,
                "fragment_text": citation.fragment.json_value,
                "found": found,
                "failure": failure,
                "tab_panel": tab_panel,
            }
        )
    metrics = _metrics(rows, sample=sample, seed=seed, fragment_field=fragment_field)
    (output_dir / "results.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    (output_dir / "README.md").write_text(render_readme(metrics))
    return metrics


def refragment(run_dir: Path) -> dict[str, int]:
    path = run_dir / "records.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    changed = 0
    citations = 0
    for row in rows:
        record = QuestionRecord.model_validate(row)
        passages = _source_passages(record)
        for raw, citation in zip(row.get("citations", []), record.citations, strict=True):
            if not citation.verified:
                continue
            citations += 1
            source_quote = matched_source_quote(citation.quote, passages.get(citation.n, ""))
            if source_quote is None:
                raise ValueError(
                    f"could not relocate citation {citation.n} for {record.question_id}"
                )
            old = raw.get("fragment_url")
            new = fragment_link(citation.url, citation.anchor, source_quote)
            if "fragment_url_v1" not in raw:
                raw["fragment_url_v1"] = old
            raw["fragment_url"] = new
            changed += old != new
    temporary = path.with_suffix(".tmp")
    temporary.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    temporary.replace(path)
    return {"records": len(rows), "citations": citations, "changed": changed}


def _parse_check_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check citation text fragments against page HTML")
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--sample", type=int, default=DEFAULT_SAMPLE)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--fragment-field",
        default="fragment_url",
        help=(
            "Which stored link to check: fragment_url (current) or fragment_url_v1 "
            "(the links a run carried before it was refragmented)"
        ),
    )
    return parser.parse_args(argv)


def _parse_refragment_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild stored citation fragment URLs")
    parser.add_argument("--run", type=Path, required=True)
    return parser.parse_args(argv)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "refragment":
        args = _parse_refragment_args(sys.argv[2:])
        print(json.dumps(refragment(args.run), indent=2))
        return
    args = _parse_check_args(sys.argv[1:])
    print(
        json.dumps(
            check_run(
                args.run,
                sample=args.sample,
                seed=args.seed,
                fragment_field=args.fragment_field,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "DEFAULT_SAMPLE",
    "DEFAULT_SEED",
    "FragmentText",
    "PageResponse",
    "check_run",
    "collect",
    "parse_fragment_url",
    "refragment",
    "render_readme",
    "visible_text",
]
