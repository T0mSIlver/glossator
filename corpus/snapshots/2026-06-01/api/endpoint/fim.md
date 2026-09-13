---
url: https://docs.mistral.ai/api/endpoint/fim
title: Fim API
breadcrumbs: [API, Fim]
kind: api
locale: en
source_path: openapi.yaml
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
openapi_md5: 3c3c0d6b147730e71376c46aaca996cc
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Fim API

Reference for the Fim endpoints of the Mistral API, generated from the OpenAPI specification.

## Fim Completion {#operation-fim_completion_v1_fim_completions_post}

`POST /v1/fim/completions`

FIM completion.

- Operation id: `fim_completion_v1_fim_completions_post`
- Tag: fim

### Request body

`application/json` (required), schema `FIMCompletionRequest`

- `model` (string, required) — ID of the model with FIM to use.
- `temperature` (number or null, optional) — What sampling temperature to use, we recommend between 0.0 and 0.7. Higher values like 0.7 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or `top_p` but not both. The default value varies depending on the model you are targeting. Call the `/models` endpoint to retrieve the appropriate value.
- `top_p` (number, optional) — Nucleus sampling, where the model considers the results of the tokens with `top_p` probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or `temperature` but not both.
- `max_tokens` (integer or null, optional) — The maximum number of tokens to generate in the completion. The token count of your prompt plus `max_tokens` cannot exceed the model's context length.
- `stream` (boolean, optional) — Whether to stream back partial progress. If set, tokens will be sent as data-only server-side events as they become available, with the stream terminated by a data: [DONE] message. Otherwise, the server will hold the request open until the timeout or until completion, with the response containing the full result as JSON.
- `stop` (object, optional) — Stop generation if this token is detected. Or if one of these tokens is detected when providing an array
  - one of 2 (anyOf):
    - string
    - array of string
- `random_seed` (integer or null, optional) — The seed to use for random sampling. If set, different calls will generate deterministic results.
- `metadata` (object or null, optional)
- `prompt` (string, required) — The text/code to complete.
- `suffix` (string or null, optional) — Optional text/code that adds more context for the model. When given a `prompt` and a `suffix` the model will fill what is between them. When `suffix` is not provided, the model will simply execute completion starting with `prompt`.
- `min_tokens` (integer or null, optional) — The minimum number of tokens to generate in the completion.
- `prompt_cache_key` (string or null, optional) — A cache key to enable prompt caching. When provided, the API will attempt to reuse previously computed tokens for requests sharing the same prefix (e.g. multi-turn conversations or requests with a similar system prompt). Cached tokens are billed at 10% of the standard input token price.

### Responses

- `200` — Successful Response (application/json, text/event-stream, schema FIMCompletionResponse, CompletionEvent)
- `422` — Validation Error (application/json, schema HTTPValidationError)
