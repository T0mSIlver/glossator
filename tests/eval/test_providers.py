"""The chat client: caching, retries, structured output, and what gets recorded."""

import asyncio
import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from pydantic import BaseModel

from glossator.eval.providers.client import OpenAICompatibleProvider
from glossator.eval.providers.models import ProviderCallError
from glossator.eval.providers.scopes import candidate_scope
from glossator.eval.providers.structured import extract_json_object
from glossator.eval.run_records.recorder import RunRecorder

CONFIG = {
    "model": "glm-test",
    "corpus": "fixture",
    "prompt_version": "test",
    "provider": "zai",
    "thinking": "disabled",
    "seed": 0,
    "corpus_commit": "fixture",
    "n": 6,
}


class Answer(BaseModel):
    value: int


class OtherAnswer(BaseModel):
    value: int
    note: str = ""


def response(
    content: str,
    *,
    prompt: int = 4,
    completion: int = 2,
    finish_reason: str = "stop",
) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "choices": [{"message": {"content": content}, "finish_reason": finish_reason}],
            "usage": {
                "prompt_tokens": prompt,
                "completion_tokens": completion,
                "completion_tokens_details": {"reasoning_tokens": 1},
            },
        },
    )


def make_provider(
    tmp_path: Path,
    handler: Any,
    *,
    name: str = "zai",
    recorder: RunRecorder | None = None,
    semaphore: asyncio.Semaphore | None = None,
    seed: int | None = None,
) -> tuple[OpenAICompatibleProvider, httpx.AsyncClient]:
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://example.test/v1/"
    )
    provider = OpenAICompatibleProvider(
        name,  # type: ignore[arg-type]
        semaphore or asyncio.Semaphore(1),
        cache_dir=tmp_path / "cache",
        caller_tag="test",
        client=client,
        recorder=recorder,
        seed=seed,
    )
    return provider, client


BASE_CALL: dict[str, Any] = {
    "model": "glm-test",
    "temperature": 0.0,
    "max_tokens": 20,
    "response_schema": Answer,
    "thinking": "disabled",
}


@pytest.mark.asyncio
async def test_cache_miss_then_hit_skips_transport(tmp_path: Path) -> None:
    calls = 0
    run_dir = tmp_path / "run"
    recorder = RunRecorder.start(run_dir, CONFIG)

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        body = json.loads(request.content)
        assert body["thinking"] == {"type": "disabled"}
        assert body["response_format"] == {"type": "json_object"}
        assert body["seed"] == 7
        assert "JSON Schema" in body["messages"][0]["content"]
        return response('{"value": 7}')

    provider, client = make_provider(tmp_path, handler, recorder=recorder, seed=7)
    with candidate_scope("cand-1"):
        first = await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)
        second = await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)

    assert calls == 1
    assert first.cached is False
    assert second.cached is True
    assert isinstance(second.parsed, Answer)
    assert second.parsed.value == 7
    assert second.usage.reasoning_tokens == 1

    recorder.finalize(dataset_path=None, error=None)
    rows = [json.loads(row) for row in (run_dir / "calls.jsonl").read_text().splitlines()]
    assert [row["cached"] for row in rows] == [False, True]
    assert rows[0]["candidate_id"] == "cand-1"
    assert rows[0]["temperature"] == 0.0
    assert rows[0]["max_tokens"] == 20
    assert rows[0]["seed"] == 7
    assert rows[0]["endpoint"] == "https://example.test/v1/"
    assert rows[0]["schema_name"] == "Answer"
    assert rows[0]["schema_hash"]
    assert rows[0]["finish_reason"] == "stop"
    assert rows[0]["response_format"] == {"type": "json_object"}
    await client.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "override",
    [
        {"temperature": 0.7},
        {"max_tokens": 40},
        {"model": "glm-other"},
        {"thinking": "enabled"},
        {"response_schema": OtherAnswer},
    ],
    ids=["temperature", "max_tokens", "model", "thinking", "schema"],
)
async def test_cache_key_separates_call_parameters(
    tmp_path: Path, override: dict[str, Any]
) -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return response('{"value": 7}')

    provider, client = make_provider(tmp_path, handler)
    await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)
    await provider.complete([{"role": "user", "content": "answer"}], **{**BASE_CALL, **override})

    assert calls == 2
    await client.aclose()


@pytest.mark.asyncio
async def test_a_changed_schema_shape_is_a_miss_even_under_the_same_name(
    tmp_path: Path,
) -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return response('{"value": 7}')

    class Answer(BaseModel):  # noqa: F811 - deliberately shadows the module-level schema
        value: int
        extra: int = 0

    provider, client = make_provider(tmp_path, handler)
    await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)
    await provider.complete(
        [{"role": "user", "content": "answer"}], **{**BASE_CALL, "response_schema": Answer}
    )

    assert calls == 2
    await client.aclose()


@pytest.mark.asyncio
async def test_a_cache_nonce_separates_two_identical_requests(tmp_path: Path) -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return response('{"value": 7}')

    provider, client = make_provider(tmp_path, handler)
    await provider.complete(
        [{"role": "user", "content": "answer"}], **BASE_CALL, cache_nonce="cand-1"
    )
    await provider.complete(
        [{"role": "user", "content": "answer"}], **BASE_CALL, cache_nonce="cand-2"
    )

    assert calls == 2
    await client.aclose()


@pytest.mark.asyncio
async def test_a_corrupt_cache_file_is_a_miss(tmp_path: Path) -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return response('{"value": 7}')

    provider, client = make_provider(tmp_path, handler)
    await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)
    entry = next((tmp_path / "cache").glob("*.json"))
    entry.write_text('{"text": "{\\"value\\": 7}", "usage"')

    result = await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)

    assert calls == 2
    assert result.cached is False
    await client.aclose()


@pytest.mark.asyncio
async def test_a_stale_cache_file_is_a_miss(tmp_path: Path) -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return response('{"value": 7}')

    provider, client = make_provider(tmp_path, handler)
    await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)
    entry = next((tmp_path / "cache").glob("*.json"))
    entry.write_text(json.dumps({"text": "{}", "parsed": {"value": "not an int"}}))

    result = await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)

    assert calls == 2
    assert result.parsed == Answer(value=7)
    await client.aclose()


@pytest.mark.asyncio
async def test_structured_output_retries_once_after_validation_failure(tmp_path: Path) -> None:
    requests: list[dict[str, Any]] = []
    replies = iter([response('{"value":"wrong"}'), response('{"value": 9}')])

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content))
        return next(replies)

    provider, client = make_provider(tmp_path, handler)
    result = await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)

    assert len(requests) == 2
    retry_messages = requests[1]["messages"]
    assert retry_messages[-2]["content"] == '{"value":"wrong"}'
    assert "failed JSON validation" in retry_messages[-1]["content"]
    assert result.parsed == Answer(value=9)
    assert result.usage.prompt_tokens == 8
    await client.aclose()


@pytest.mark.asyncio
async def test_a_second_validation_failure_raises_without_a_third_call(tmp_path: Path) -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return response('{"value":"wrong"}')

    provider, client = make_provider(tmp_path, handler)
    with pytest.raises(ProviderCallError, match="Answer did not validate"):
        await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)

    assert calls == 2
    await client.aclose()


@pytest.mark.asyncio
async def test_json_wrapped_in_a_fence_or_followed_by_prose_needs_no_repair(
    tmp_path: Path,
) -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return response('```json\n{"value": 3}\n```\nThat is the answer.')

    provider, client = make_provider(tmp_path, handler)
    result = await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)

    assert calls == 1
    assert result.parsed == Answer(value=3)
    await client.aclose()


def test_extract_json_object_keeps_braces_inside_strings() -> None:
    assert extract_json_object('prefix {"a": "}{"} suffix') == '{"a": "}{"}'
    assert extract_json_object("no object here") == "no object here"


@pytest.mark.asyncio
async def test_a_truncated_answer_is_retried_with_double_the_budget(tmp_path: Path) -> None:
    budgets: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        budgets.append(body["max_tokens"])
        if len(budgets) == 1:
            return response('{"value": 7', finish_reason="length")
        return response('{"value": 7}')

    provider, client = make_provider(tmp_path, handler)
    result = await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)

    assert budgets == [20, 40]
    assert result.parsed == Answer(value=7)
    assert result.finish_reason == "stop"
    await client.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [429, 503])
async def test_retryable_statuses_are_retried(tmp_path: Path, status: int) -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls < 3:
            return httpx.Response(status)
        return response("done")

    provider, client = make_provider(tmp_path, handler, name="mistral")
    result = await provider.complete(
        [{"role": "user", "content": "answer"}],
        model="mistral-test",
        temperature=0,
        max_tokens=20,
    )

    assert calls == 3
    assert result.text == "done"
    await client.aclose()


@pytest.mark.asyncio
async def test_a_client_error_is_not_retried(tmp_path: Path) -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(400, json={"error": "bad request"})

    provider, client = make_provider(tmp_path, handler)
    with pytest.raises(ProviderCallError, match="HTTP 400"):
        await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)

    assert calls == 1
    await client.aclose()


@pytest.mark.asyncio
async def test_a_transport_error_is_retried_then_reported(tmp_path: Path) -> None:
    calls = 0
    run_dir = tmp_path / "run"
    recorder = RunRecorder.start(run_dir, CONFIG)

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ConnectError("connection refused", request=request)

    provider, client = make_provider(tmp_path, handler, recorder=recorder)
    with pytest.raises(ProviderCallError, match="connection refused"):
        await provider.complete([{"role": "user", "content": "answer"}], **BASE_CALL)

    assert calls == 3
    rows = [json.loads(row) for row in (run_dir / "calls.jsonl").read_text().splitlines()]
    assert len(rows) == 3
    assert all(row["error"] == "connection refused" for row in rows)
    await client.aclose()


@pytest.mark.asyncio
async def test_the_semaphore_bounds_concurrency(tmp_path: Path) -> None:
    in_flight = 0
    peak = 0

    async def handler(_: httpx.Request) -> httpx.Response:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.01)
        in_flight -= 1
        return response('{"value": 1}')

    provider, client = make_provider(tmp_path, handler, semaphore=asyncio.Semaphore(2))
    await asyncio.gather(
        *(
            provider.complete([{"role": "user", "content": f"answer {index}"}], **BASE_CALL)
            for index in range(6)
        )
    )

    assert peak <= 2
    await client.aclose()


@pytest.mark.asyncio
async def test_thinking_is_rejected_for_the_mistral_provider(tmp_path: Path) -> None:
    provider, client = make_provider(tmp_path, lambda _: response("x"), name="mistral")
    with pytest.raises(ValueError, match="only by the zai provider"):
        await provider.complete(
            [{"role": "user", "content": "answer"}],
            model="mistral-test",
            temperature=0,
            max_tokens=20,
            thinking="disabled",
        )
    await client.aclose()


@pytest.mark.asyncio
async def test_the_mistral_path_builds_a_request(tmp_path: Path) -> None:
    seen: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content))
        seen["url"] = str(request.url)
        return response('{"value": 5}')

    provider, client = make_provider(tmp_path, handler, name="mistral", seed=3)
    result = await provider.complete(
        [{"role": "user", "content": "answer"}],
        model="mistral-medium-3-5",
        temperature=0.0,
        max_tokens=20,
        response_schema=Answer,
        thinking=None,
    )

    assert "thinking" not in seen
    # Mistral names the determinism parameter differently; sending "seed" would
    # be ignored and the run would look reproducible when it is not.
    assert seen["random_seed"] == 3
    assert seen["model"] == "mistral-medium-3-5"
    assert seen["url"] == "https://example.test/v1/chat/completions"
    assert result.parsed == Answer(value=5)
    assert result.provider == "mistral"
    await client.aclose()


@pytest.mark.asyncio
async def test_a_null_usage_block_is_read_as_zero(tmp_path: Path) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "done"}}], "usage": None},
        )

    provider, client = make_provider(tmp_path, handler)
    result = await provider.complete(
        [{"role": "user", "content": "answer"}],
        model="glm-test",
        temperature=0,
        max_tokens=20,
    )

    assert result.usage.prompt_tokens == 0
    await client.aclose()
