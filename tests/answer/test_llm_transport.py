"""Failures that never produce a response, and the repair round that follows one.

A connection that dies and a body that will not validate are the two ways a call
costs money without returning an answer. Both have to reach the recorder: a
request that was sent and left no line in `calls.jsonl` is a hole in the record
(D-023).
"""

import httpx
import pytest
from mistralai.client.errors import NoResponseError

from glossator.answer.config import AnswerConfig
from tests.answer.conftest import Collector
from tests.answer.test_llm import Shape, build, complete, response


def test_a_read_timeout_is_retried_and_recorded() -> None:
    """The SDK re-raises httpx's own exceptions, which are not MistralError."""
    recorder = Collector()
    llm, client = build([httpx.ReadTimeout("timed out"), response()], recorder)

    completion = complete(llm)

    assert completion.text == "hello"
    assert len(client.chat.requests) == 2
    assert recorder.calls[0].error == "ReadTimeout: timed out"
    assert recorder.calls[0].response is None


def test_a_connection_error_is_retried() -> None:
    llm, client = build([httpx.ConnectError("refused"), response()])

    assert complete(llm).text == "hello"
    assert len(client.chat.requests) == 2


def test_a_no_response_error_is_retried() -> None:
    llm, client = build([NoResponseError("nothing came back"), response()])

    assert complete(llm).text == "hello"
    assert len(client.chat.requests) == 2


def test_a_transport_failure_that_never_clears_raises_with_both_attempts_recorded() -> None:
    recorder = Collector()
    llm, _ = build(
        [httpx.ReadTimeout("t1"), httpx.ReadTimeout("t2")],
        recorder,
        config=AnswerConfig(max_attempts=2, retry_base_seconds=0.0),
    )

    with pytest.raises(httpx.ReadTimeout):
        complete(llm)

    assert [call.attempt for call in recorder.calls] == [1, 2]
    assert all(call.error is not None for call in recorder.calls)


def test_the_repair_attempt_is_recorded_in_full() -> None:
    recorder = Collector()
    llm, _ = build([response(content="not json"), response(content='{"answer": "42"}')], recorder)

    complete(llm, response_schema=Shape, purpose="test:repair")

    first, second = recorder.calls
    assert first.parsed is None and first.error is not None
    assert first.text == "not json"
    assert first.response is not None and first.response["id"] == "cmpl-1"
    assert second.parsed == {"answer": "42"}
    assert second.response_schema == "Shape"
    assert second.purpose == "test:repair"
    # The repair request carries the failed answer and the validation error.
    assert second.messages[-2]["content"] == "not json"
    assert "not valid JSON" in second.messages[-1]["content"]


def test_cost_and_usage_are_summed_across_a_repair() -> None:
    llm, _ = build(
        [
            response(content="not json", prompt_tokens=1000, completion_tokens=200),
            response(content='{"answer": "42"}', prompt_tokens=1300, completion_tokens=50),
        ]
    )

    completion = complete(llm, response_schema=Shape)

    assert completion.usage.prompt_tokens == 2300
    assert completion.usage.completion_tokens == 250
    assert completion.cost_usd == pytest.approx((2300 * 1.50 + 250 * 7.50) / 1e6)
    assert len(completion.calls) == 2
