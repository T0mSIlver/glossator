"""The chat wrapper: retries, schema repair, recording, and what a call costs.

The client is a double, so nothing here reaches the network; the responses it
returns are the SDK's own models, so the real parsing path is what is exercised.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, cast

import httpx
import pytest
from mistralai.client import Mistral
from mistralai.client.errors import SDKError
from mistralai.client.models import (
    AssistantMessage,
    ChatCompletionChoice,
    ChatCompletionChoiceFinishReason,
    ChatCompletionResponse,
    FunctionCall,
    ToolCall,
    UsageInfo,
)
from pydantic import BaseModel, ConfigDict

from glossator.answer.config import MISTRAL_MEDIUM_3_5, AnswerConfig, ModelPrice
from glossator.answer.llm import Completion, JsonlCallRecorder, Message, MistralLLM
from tests.answer.conftest import Collector


class Shape(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    answer: str


HELLO: list[Message] = [{"role": "user", "content": "hi"}]


def response(
    *,
    content: str | None = "hello",
    tool_calls: list[ToolCall] | None = None,
    prompt_tokens: int = 1000,
    completion_tokens: int = 200,
    finish_reason: ChatCompletionChoiceFinishReason = "stop",
    model: str = MISTRAL_MEDIUM_3_5,
) -> ChatCompletionResponse:
    return ChatCompletionResponse(
        id="cmpl-1",
        object="chat.completion",
        model=model,
        created=0,
        usage=UsageInfo(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
        choices=[
            ChatCompletionChoice(
                index=0,
                finish_reason=finish_reason,
                message=AssistantMessage(content=content, tool_calls=tool_calls),
            )
        ],
    )


def sdk_error(status: int) -> SDKError:
    request = httpx.Request("POST", "https://api.mistral.ai/v1/chat/completions")
    return SDKError("boom", httpx.Response(status, request=request, text="boom"))


class FakeChat:
    def __init__(self, script: list[Any]) -> None:
        self.script = script
        self.requests: list[dict[str, Any]] = []

    async def complete_async(self, **kwargs: Any) -> ChatCompletionResponse:
        self.requests.append(kwargs)
        entry = self.script.pop(0)
        if isinstance(entry, Exception):
            raise entry
        return cast(ChatCompletionResponse, entry)


class FakeClient:
    def __init__(self, script: list[Any]) -> None:
        self.chat = FakeChat(script)


def build(
    script: list[Any],
    recorder: Collector | None = None,
    config: AnswerConfig | None = None,
) -> tuple[MistralLLM, FakeClient]:
    client = FakeClient(script)
    llm = MistralLLM(
        config or AnswerConfig(retry_base_seconds=0.0),
        client=cast(Mistral, client),
        recorder=recorder,
    )
    return llm, client


def complete(llm: MistralLLM, **kwargs: Any) -> Completion:
    return asyncio.run(llm.complete(HELLO, **kwargs))


def test_plain_completion_carries_text_usage_and_cost() -> None:
    llm, _ = build([response()])

    completion = complete(llm)

    assert completion.text == "hello"
    assert completion.finish_reason == "stop"
    assert completion.usage.prompt_tokens == 1000
    assert completion.usage.total_tokens == 1200
    # 1000 in at 1.50/M plus 200 out at 7.50/M.
    assert completion.cost_usd == pytest.approx(0.0015 + 0.0015)


def test_a_structured_response_is_parsed() -> None:
    llm, client = build([response(content=json.dumps({"answer": "42"}))])

    completion = complete(llm, response_schema=Shape)

    assert isinstance(completion.parsed, Shape)
    assert completion.parsed.answer == "42"
    assert client.chat.requests[0]["response_format"]["type"] == "json_schema"


def test_json_object_mode_sends_the_bare_type_and_still_validates() -> None:
    """The fallback for a server that does not honour a JSON schema (D-035c):
    the request asks only for a JSON object, the schema lives in the prompt's
    words, and the response is validated and repaired exactly as before."""
    llm, client = build(
        [response(content="prose first"), response(content='{"answer": "42"}')],
        config=AnswerConfig(retry_base_seconds=0.0, response_format="json_object"),
    )

    completion = complete(llm, response_schema=Shape)

    assert client.chat.requests[0]["response_format"] == {"type": "json_object"}
    assert isinstance(completion.parsed, Shape)
    # The mode is part of the call record, so a run on a fallback is never silent.
    assert completion.calls[0].response_format == "json_object"


def test_a_fenced_json_object_response_parses_without_repair() -> None:
    """llama.cpp serves ``json_object`` inside a ```json fence (D-035c): the
    fence is stripped before parsing, so the fallback needs no repair call."""
    llm, client = build(
        [response(content='```json\n{"answer": "42"}\n```')],
        config=AnswerConfig(retry_base_seconds=0.0, response_format="json_object"),
    )

    completion = complete(llm, response_schema=Shape)

    assert isinstance(completion.parsed, Shape)
    assert completion.parsed.answer == "42"
    assert len(completion.calls) == 1


def test_the_mode_a_structured_call_ran_under_is_recorded() -> None:
    recorder = Collector()
    llm, _client = build([response(content='{"answer": "42"}')], recorder)

    complete(llm, response_schema=Shape)

    assert recorder.calls[0].response_format == "json_schema"


def test_invalid_json_is_repaired_once() -> None:
    llm, client = build([response(content="not json"), response(content='{"answer": "42"}')])

    completion = complete(llm, response_schema=Shape)

    assert isinstance(completion.parsed, Shape)
    assert len(completion.calls) == 2
    # The repair shows the model its own output and the validation error.
    repair_messages = client.chat.requests[1]["messages"]
    assert repair_messages[-2] == {"role": "assistant", "content": "not json"}
    assert "not valid JSON" in repair_messages[-1]["content"]


def test_a_response_that_never_parses_leaves_parsed_empty() -> None:
    llm, _ = build([response(content="not json"), response(content="still not json")])

    completion = complete(llm, response_schema=Shape)

    assert completion.parsed is None
    assert completion.calls[-1].error is not None


def test_rate_limits_and_server_errors_are_retried() -> None:
    llm, client = build([sdk_error(429), sdk_error(503), response()])

    completion = complete(llm)

    assert completion.text == "hello"
    assert len(client.chat.requests) == 3
    assert [call.attempt for call in completion.calls] == [1, 2, 3]


def test_a_client_error_is_not_retried() -> None:
    llm, client = build([sdk_error(400), response()])

    with pytest.raises(SDKError):
        complete(llm)

    assert len(client.chat.requests) == 1


def test_retries_give_up_after_the_configured_attempts() -> None:
    llm, client = build(
        [sdk_error(429), sdk_error(429)],
        config=AnswerConfig(max_attempts=2, retry_base_seconds=0.0),
    )

    with pytest.raises(SDKError):
        complete(llm)

    assert len(client.chat.requests) == 2


def test_tool_calls_are_returned_parsed_and_raw() -> None:
    call = ToolCall(
        id="call_1",
        function=FunctionCall(name="search", arguments='{"query": "how to stream"}'),
    )
    llm, _ = build([response(content=None, tool_calls=[call], finish_reason="tool_calls")])

    completion = complete(llm)

    assert completion.tool_calls[0].name == "search"
    assert completion.tool_calls[0].arguments == {"query": "how to stream"}
    assert completion.tool_calls[0].raw_arguments == '{"query": "how to stream"}'


def test_every_field_of_every_call_reaches_the_recorder(tmp_path: Path) -> None:
    path = tmp_path / "calls.jsonl"
    recorder = JsonlCallRecorder(path)
    llm = MistralLLM(
        AnswerConfig(retry_base_seconds=0.0),
        client=cast(Mistral, FakeClient([sdk_error(429), response(content='{"answer": "42"}')])),
        recorder=recorder,
    )

    asyncio.run(llm.complete(HELLO, response_schema=Shape, purpose="test:grounded_answer"))
    recorder.close()

    lines = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(lines) == 2

    failed, succeeded = lines
    assert failed["error"].startswith("SDKError: boom")
    assert failed["attempt"] == 1
    assert failed["response"] is None

    assert succeeded["purpose"] == "test:grounded_answer"
    assert succeeded["model"] == MISTRAL_MEDIUM_3_5
    assert succeeded["temperature"] == 0.2
    assert succeeded["max_tokens"] == 1600
    assert succeeded["messages"] == [{"role": "user", "content": "hi"}]
    assert succeeded["response_schema"] == "Shape"
    assert succeeded["text"] == '{"answer": "42"}'
    assert succeeded["parsed"] == {"answer": "42"}
    assert succeeded["response"]["id"] == "cmpl-1"
    assert succeeded["finish_reason"] == "stop"
    assert succeeded["usage"] == {"prompt_tokens": 1000, "completion_tokens": 200}
    assert succeeded["cost_usd"] == pytest.approx(0.003)
    assert succeeded["latency_ms"] >= 0
    assert succeeded["error"] is None
    assert succeeded["tools"] is None
    assert succeeded["started_at"].startswith("20")


def test_tools_and_tool_choice_reach_the_api_and_the_record() -> None:
    recorder = Collector()
    tools: list[dict[str, Any]] = [
        {"type": "function", "function": {"name": "search", "parameters": {}}}
    ]
    llm, client = build([response()], recorder)

    complete(llm, tools=tools, tool_choice="auto")

    assert client.chat.requests[0]["tools"] == tools
    assert client.chat.requests[0]["tool_choice"] == "auto"
    assert recorder.calls[0].tools == tools
    assert recorder.calls[0].tool_choice == "auto"


def test_cost_is_the_price_table_applied_to_the_token_counts() -> None:
    config = AnswerConfig()

    assert config.cost_usd(MISTRAL_MEDIUM_3_5, 1_000_000, 0) == pytest.approx(1.50)
    assert config.cost_usd(MISTRAL_MEDIUM_3_5, 0, 1_000_000) == pytest.approx(7.50)
    assert config.cost_usd(MISTRAL_MEDIUM_3_5, 12_345, 678) == pytest.approx(
        12_345 * 1.50 / 1e6 + 678 * 7.50 / 1e6
    )


def test_an_unpriced_model_costs_zero_rather_than_a_guess() -> None:
    assert AnswerConfig().cost_usd("some-future-model", 1_000_000, 1_000_000) == 0.0


def test_an_unpriced_model_is_allowed_and_warns_once_not_per_call() -> None:
    """A local server reports ids the price list has never seen (D-035c): the
    run proceeds, the tokens are recorded, and the warning says so once per
    model per process. The warned set is the log's gate, so asserting on it is
    asserting on the once-ness."""
    import glossator.answer.config as config_module

    config_module._WARNED_UNPRICED.discard("some-future-model")
    settings = AnswerConfig(model="some-future-model")

    assert settings.cost_usd("some-future-model", 1_000, 100) == 0.0
    assert settings.cost_usd("some-future-model", 1_000, 100) == 0.0
    assert "some-future-model" in config_module._WARNED_UNPRICED


def test_a_price_override_is_honoured() -> None:
    config = AnswerConfig(
        model="house-model",
        prices={"house-model": ModelPrice(input_usd_per_mtok=2.0, output_usd_per_mtok=4.0)},
    )

    assert config.cost_usd("house-model", 500_000, 250_000) == pytest.approx(1.0 + 1.0)
