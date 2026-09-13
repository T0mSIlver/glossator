---
url: https://docs.mistral.ai/api/endpoint/deprecated/agents
title: Deprecated Agents API
breadcrumbs: [API, Deprecated Agents]
kind: api
locale: en
source_path: openapi.yaml
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
openapi_md5: 3c3c0d6b147730e71376c46aaca996cc
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Deprecated Agents API

Reference for the Deprecated Agents endpoints of the Mistral API, generated from the OpenAPI specification.

## Agents Completion {#operation-agents_completion_v1_agents_completions_post}

`POST /v1/agents/completions`

- Operation id: `agents_completion_v1_agents_completions_post`
- Tag: deprecated/agents
- Deprecated: yes

### Request body

`application/json` (required), schema `AgentsCompletionRequest`

- `max_tokens` (integer or null, optional) — The maximum number of tokens to generate in the completion. The token count of your prompt plus `max_tokens` cannot exceed the model's context length.
- `stream` (boolean, optional) — Whether to stream back partial progress. If set, tokens will be sent as data-only server-side events as they become available, with the stream terminated by a data: [DONE] message. Otherwise, the server will hold the request open until the timeout or until completion, with the response containing the full result as JSON.
- `stop` (object, optional) — Stop generation if this token is detected. Or if one of these tokens is detected when providing an array
  - one of 2 (anyOf):
    - string
    - array of string
- `random_seed` (integer or null, optional) — The seed to use for random sampling. If set, different calls will generate deterministic results.
- `metadata` (object or null, optional)
- `messages` (array of object, required) — The prompt(s) to generate completions for, encoded as a list of dict with role and content.
  - one of 4 (oneOf):
    - SystemMessage
    - UserMessage
    - AssistantMessage
    - ToolMessage
- `response_format` (ResponseFormat, optional) — Specify the format that the model must output. By default it will use `{ "type": "text" }`. Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is in JSON. When using JSON mode you MUST also instruct the model to produce JSON yourself with a system or a user message. Setting to `{ "type": "json_schema" }` enables JSON schema mode, which guarantees the message the model generates is in JSON and follows the schema you provide.
  - `type` (enum: 'text', 'json_object', 'json_schema', optional)
  - `json_schema` (object or null, optional)
    - `name` (string, required)
    - `description` (string or null, optional)
    - `schema` (object, required)
    - `strict` (boolean, optional)
- `tools` (array of Tool or null, optional)
  - `type` (enum: 'function', optional)
  - `function` (Function, required)
- `tool_choice` (object, optional)
  - one of 2 (anyOf):
    - ToolChoice
      - `type` (enum: 'function', optional)
      - `function` (FunctionName, required) — this restriction of `Function` is used to select a specific function to call
    - ToolChoiceEnum
- `presence_penalty` (number, optional) — The `presence_penalty` determines how much the model penalizes the repetition of words or phrases. A higher presence penalty encourages the model to use a wider variety of words and phrases, making the output more diverse and creative.
- `frequency_penalty` (number, optional) — The `frequency_penalty` penalizes the repetition of words based on their frequency in the generated text. A higher frequency penalty discourages the model from repeating words that have already appeared frequently in the output, promoting diversity and reducing repetition.
- `n` (integer or null, optional) — Number of completions to return for each request, input tokens are only billed once.
- `prediction` (Prediction, optional) — Enable users to specify expected results, optimizing response times by leveraging known or predictable content. This approach is especially effective for updating text documents or code files with minimal changes, reducing latency while maintaining high-quality results.
  - `type` (string, optional)
  - `content` (string, optional)
- `parallel_tool_calls` (boolean, optional)
- `prompt_mode` (enum: 'reasoning', optional) — Allows toggling between the reasoning mode and no system prompt. When set to `reasoning` the system prompt for reasoning models will be used. **Deprecated for reasoning models - use `reasoning_effort` parameter instead.**
- `reasoning_effort` (enum: 'high', 'none', optional) — Controls the reasoning effort level for reasoning models. "high" enables comprehensive reasoning traces, "none" disables reasoning effort.
- `prompt_cache_key` (string or null, optional) — A cache key to enable prompt caching. When provided, the API will attempt to reuse previously computed tokens for requests sharing the same prefix (e.g. multi-turn conversations or requests with a similar system prompt). Cached tokens are billed at 10% of the standard input token price.
- `agent_id` (string, required) — The ID of the agent to use for this completion.

### Responses

- `200` — Successful Response (application/json, schema ChatCompletionResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)
