---
url: https://docs.mistral.ai/api/endpoint/chat-completions
title: Create chat completion
breadcrumbs:
  - API
  - Chat
  - Create chat completion
kind: api
locale: en
source_path: openapi-public-doc.yaml#/paths/~1v1~1chat~1completions/post
source_commit: 2e094f7
---

# Create chat completion

`POST https://api.mistral.ai/v1/chat/completions`

Generate an assistant message from a conversation. This is the endpoint behind
`client.chat.complete` and `client.chat.stream` in the official clients.

## Authentication {#authentication}

Send the API key as a bearer token:

```http
POST /v1/chat/completions HTTP/1.1
Host: api.mistral.ai
Authorization: Bearer $MISTRAL_API_KEY
Content-Type: application/json
```

## Request body {#request-body}

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `model` | string | yes | -- | Model id, e.g. `mistral-medium-latest`. |
| `messages` | array | yes | -- | Conversation so far, oldest first. |
| `temperature` | number | no | model default | Sampling temperature between 0.0 and 1.5. |
| `top_p` | number | no | 1.0 | Nucleus sampling mass. Change this or `temperature`, not both. |
| `max_tokens` | integer | no | null | Upper bound on generated tokens. |
| `stream` | boolean | no | false | Return server-sent events instead of one response. |
| `stop` | string or array | no | null | Up to four sequences that end generation. |
| `random_seed` | integer | no | null | Seed for reproducible sampling. |
| `tools` | array | no | null | Function definitions the model may call. |
| `tool_choice` | string or object | no | `auto` | `auto`, `any`, `none`, or a named tool. |
| `response_format` | object | no | null | `{"type": "json_object"}` or a JSON schema. |
| `safe_prompt` | boolean | no | false | Prepend a safety system prompt. |
| `presence_penalty` | number | no | 0.0 | Penalise tokens already present. |
| `frequency_penalty` | number | no | 0.0 | Penalise tokens by frequency. |
| `n` | integer | no | 1 | Number of completions to return. |
| `prediction` | object | no | null | Predicted output, for latency on edits. |
| `parallel_tool_calls` | boolean | no | true | Allow several tool calls per message. |

### Message objects {#message-objects}

Each element of `messages` has a `role` and content appropriate to that role.

| Role | Content | Notes |
| --- | --- | --- |
| `system` | string | Instructions. Usually the first message. |
| `user` | string or array | Text, or text plus image parts for vision models. |
| `assistant` | string or null | May carry `tool_calls` instead of content. |
| `tool` | string | Result of one tool call; requires `tool_call_id`. |

## Response {#response}

```json
{
  "id": "cmpl-e5cc70bb28c444948073e77776eb30ef",
  "object": "chat.completion",
  "model": "mistral-medium-latest",
  "created": 1775000000,
  "choices": [
    {
      "index": 0,
      "message": { "role": "assistant", "content": "Paris." },
      "finish_reason": "stop"
    }
  ],
  "usage": { "prompt_tokens": 14, "completion_tokens": 2, "total_tokens": 16 }
}
```

`finish_reason` is `stop` for a natural end, `length` when `max_tokens` was hit,
`tool_calls` when the model is waiting for tool results, and `model_length` when
the context window was exhausted.

## Errors {#errors}

| Status | Meaning | What to do |
| --- | --- | --- |
| 400 | Malformed request | Read `message`; the offending field is named. |
| 401 | Invalid API key | Check the `Authorization` header. |
| 422 | Valid JSON, invalid values | E.g. an unknown model id. |
| 429 | Rate limited | Back off exponentially and retry. |
| 500 | Server error | Retry with backoff; report if it persists. |

Only 429 and 5xx are worth retrying. Retrying a 422 produces the same 422.
