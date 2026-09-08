"""Doubles for the answer layer: an index and a model that never touch the network."""

import json
from collections.abc import Callable, Sequence
from typing import Any

import pytest
from mistralai.search.toolkit.search import GrepMode
from pydantic import BaseModel

from glossator.answer.config import AnswerConfig
from glossator.answer.llm import Completion, LLMCall, Message, TokenUsage, ToolInvocation, ToolSpec
from glossator.retrieval.config import RetrievalConfig
from glossator.retrieval.engine import Hit

PAGE = "https://docs.mistral.ai/capabilities/function-calling"


def make_hit(
    chunk_id: str,
    content: str,
    *,
    start: int = 0,
    end: int | None = None,
    score: float = 1.0,
    source_id: str = PAGE,
    url: str | None = None,
    anchor: str | None = "tools",
    heading_path: tuple[str, ...] = ("Function calling",),
    page_title: str = "Function calling",
) -> Hit:
    """A hit shaped like the ones the index returns, offsets and all."""
    return Hit(
        chunk_id=chunk_id,
        score=score,
        url=url or source_id,
        anchor=anchor,
        heading_path=heading_path,
        page_title=page_title,
        kind="doc",
        locale="en",
        section_index=0,
        content=content,
        source_id=source_id,
        start_offset=start,
        end_offset=len(content) if end is None else end,
    )


def chunked_hit(
    chunk_id: str,
    body: str,
    *,
    start: int,
    end: int,
    heading_path: tuple[str, ...] = ("Function calling",),
    **kwargs: Any,
) -> Hit:
    """A hit whose content carries the heading prefix the chunker adds."""
    prefix = " > ".join(heading_path)
    return make_hit(
        chunk_id,
        f"{prefix}\n\n{body}",
        start=start,
        end=end,
        heading_path=heading_path,
        **kwargs,
    )


def word_tokens(text: str) -> int:
    """A stand-in tokenizer: budget tests want arithmetic, not BPE."""
    return len(text.split())


class FakePage:
    """One page's navigation operations, backed by a list of hits."""

    def __init__(self, hits: Sequence[Hit]) -> None:
        self.hits = list(hits)
        self.calls: list[tuple[str, object]] = []

    async def around(self, window: int = 2) -> list[Hit]:
        self.calls.append(("around", window))
        return self.hits

    async def read(
        self, start: int | None = None, end: int | None = None, top_k: int = 20
    ) -> list[Hit]:
        self.calls.append(("read", (start, end)))
        return [
            hit
            for hit in self.hits
            if (start is None or (hit.start_offset or 0) >= start)
            and (end is None or (hit.end_offset or 0) <= end)
        ][:top_k]

    async def grep(
        self, pattern: str, mode: GrepMode = GrepMode.PHRASE, top_k: int = 5
    ) -> list[Hit]:
        self.calls.append(("grep", pattern))
        return [hit for hit in self.hits if pattern.lower() in hit.content.lower()][:top_k]


class FakeIndex:
    """A `DocsIndex` over fixed results, recording what was asked of it."""

    def __init__(
        self,
        results: Sequence[Sequence[Hit]] | None = None,
        pages: dict[str, Sequence[Hit]] | None = None,
        variant: str = "sec1024",
    ) -> None:
        self.config = RetrievalConfig(variant=variant)
        self._results = [list(batch) for batch in (results or [])]
        self._pages = {url: FakePage(hits) for url, hits in (pages or {}).items()}
        self.queries: list[tuple[str, int | None, frozenset[str]]] = []

    async def search(
        self,
        query: str,
        exclude_ids: set[str] | None = None,
        top_k: int | None = None,
    ) -> list[Hit]:
        self.queries.append((query, top_k, frozenset(exclude_ids or ())))
        batch = self._results.pop(0) if self._results else []
        return [hit for hit in batch if hit.chunk_id not in (exclude_ids or set())]

    def navigation_at(self, source_id: str, start_offset: int = 0, end_offset: int = 0) -> FakePage:
        return self._pages.setdefault(source_id, FakePage([]))

    async def get_chunk(self, chunk_id: str) -> Hit | None:
        for page in self._pages.values():
            for hit in page.hits:
                if hit.chunk_id == chunk_id:
                    return hit
        return None

    def page(self, source_id: str) -> FakePage:
        return self._pages[source_id]


class FakeLLM:
    """Replays scripted completions and remembers what it was sent."""

    def __init__(
        self, script: Sequence[Completion | Callable[[list[Message]], Completion]]
    ) -> None:
        self.script = list(script)
        self.requests: list[dict[str, Any]] = []

    async def complete(
        self,
        messages: list[Message],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[ToolSpec] | None = None,
        tool_choice: str | None = None,
        response_schema: type[BaseModel] | None = None,
        purpose: str = "",
    ) -> Completion:
        self.requests.append(
            {
                "messages": [dict(message) for message in messages],
                "tools": tools,
                "response_schema": response_schema,
                "purpose": purpose,
            }
        )
        if not self.script:
            raise AssertionError(f"FakeLLM ran out of scripted completions at {purpose!r}")
        entry = self.script.pop(0)
        return entry(messages) if callable(entry) else entry


def completion(
    *,
    text: str = "",
    parsed: BaseModel | None = None,
    tool_calls: Sequence[ToolInvocation] = (),
    prompt_tokens: int = 100,
    completion_tokens: int = 20,
    cost_usd: float = 0.001,
) -> Completion:
    usage = TokenUsage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
    return Completion(
        text=text,
        parsed=parsed,
        tool_calls=tuple(tool_calls),
        finish_reason="tool_calls" if tool_calls else "stop",
        usage=usage,
        latency_ms=12.0,
        cost_usd=cost_usd,
        calls=(
            LLMCall(
                call_id="test",
                purpose="test",
                started_at="2026-09-09T00:00:00+00:00",
                model="fake",
                temperature=0.2,
                max_tokens=100,
                attempt=1,
                messages=[],
                usage=usage,
                cost_usd=cost_usd,
            ),
        ),
    )


def invocation(name: str, **arguments: Any) -> ToolInvocation:
    return ToolInvocation(
        id=f"call_{name}",
        name=name,
        arguments=arguments,
        raw_arguments=json.dumps(arguments),
    )


@pytest.fixture
def config() -> AnswerConfig:
    return AnswerConfig(top_k=4, context_token_budget=4000, round_cap=2, page_cap=2)
