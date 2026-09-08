import asyncio
import json
from pathlib import Path

import httpx
import pytest
from pydantic import BaseModel

from glossator.eval.providers import OpenAICompatibleProvider
from glossator.eval.run_records import RunRecorder


class Answer(BaseModel):
    value: int


def response(content: str, *, prompt: int = 4, completion: int = 2) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "choices": [{"message": {"content": content}}],
            "usage": {
                "prompt_tokens": prompt,
                "completion_tokens": completion,
                "completion_tokens_details": {"reasoning_tokens": 1},
            },
        },
    )


@pytest.mark.asyncio
async def test_cache_miss_then_hit_skips_transport(tmp_path: Path) -> None:
    calls = 0
    run_dir = tmp_path / "run"
    recorder = RunRecorder(
        run_dir,
        {
            "model": "glm-test",
            "corpus": "fixture",
            "prompt_version": "test",
            "provider": "zai",
            "thinking": "disabled",
            "seed": 0,
            "corpus_commit": "fixture",
            "n": 1,
        },
    )

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        body = json.loads(request.content)
        assert body["thinking"] == {"type": "disabled"}
        assert body["response_format"] == {"type": "json_object"}
        assert "JSON Schema" in body["messages"][0]["content"]
        return response('{"value": 7}')

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://example.test/v1/"
    )
    provider = OpenAICompatibleProvider(
        "zai",
        asyncio.Semaphore(1),
        cache_dir=tmp_path / "cache",
        caller_tag="test",
        client=client,
        recorder=recorder,
    )
    kwargs = {
        "model": "glm-test",
        "temperature": 0.0,
        "max_tokens": 20,
        "response_schema": Answer,
        "thinking": "disabled",
    }
    first = await provider.complete([{"role": "user", "content": "answer"}], **kwargs)
    second = await provider.complete([{"role": "user", "content": "answer"}], **kwargs)

    assert calls == 1
    assert first.cached is False
    assert second.cached is True
    assert isinstance(second.parsed, Answer)
    assert second.parsed.value == 7
    assert second.usage.reasoning_tokens == 1
    usage_rows = (tmp_path / "cache" / "usage.jsonl").read_text().splitlines()
    assert [json.loads(row)["cached"] for row in usage_rows] == [False, True]
    recorder.finalize(dataset_path=None, error=None)
    call_rows = [
        json.loads(row) for row in (run_dir / "calls.jsonl").read_text().splitlines()
    ]
    assert [row["cached"] for row in call_rows] == [False, True]
    assert call_rows[0]["parsed_result"] == {"value": 7}
    assert call_rows[0]["usage"]["reasoning_tokens"] == 1
    assert call_rows[0]["latency_ms"] >= 0
    assert call_rows[0]["error"] is None
    await client.aclose()


@pytest.mark.asyncio
async def test_structured_output_retries_once_after_validation_failure(
    tmp_path: Path,
) -> None:
    requests: list[dict[str, object]] = []
    replies = iter([response('{"value":"wrong"}'), response('{"value": 9}')])

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content))
        return next(replies)

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://example.test/v1/"
    )
    provider = OpenAICompatibleProvider(
        "zai", asyncio.Semaphore(1), cache_dir=tmp_path, client=client
    )
    result = await provider.complete(
        [{"role": "user", "content": "answer"}],
        model="glm-test",
        temperature=0,
        max_tokens=20,
        response_schema=Answer,
        thinking=None,
    )

    assert len(requests) == 2
    retry_messages = requests[1]["messages"]
    assert isinstance(retry_messages, list)
    assert retry_messages[-2]["content"] == '{"value":"wrong"}'
    assert "failed JSON validation" in retry_messages[-1]["content"]
    assert result.parsed == Answer(value=9)
    assert result.usage.prompt_tokens == 8
    assert result.usage.completion_tokens == 4
    await client.aclose()


@pytest.mark.asyncio
async def test_retries_retryable_statuses(tmp_path: Path) -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls < 3:
            return httpx.Response(503)
        return response("done")

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://example.test/v1/"
    )
    provider = OpenAICompatibleProvider(
        "mistral", asyncio.Semaphore(1), cache_dir=tmp_path, client=client
    )
    result = await provider.complete(
        [{"role": "user", "content": "answer"}],
        model="mistral-test",
        temperature=0,
        max_tokens=20,
    )
    assert calls == 3
    assert result.text == "done"
    await client.aclose()
