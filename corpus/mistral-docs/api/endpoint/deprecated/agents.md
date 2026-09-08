---
url: https://docs.mistral.ai/api/endpoint/deprecated/agents
title: Deprecated Agents API
breadcrumbs: [API, Deprecated Agents]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Deprecated Agents API

Reference for the Deprecated Agents endpoints of the Mistral API, generated from the OpenAPI specification.

## Agents Completion {#operation-agents_completion_v1_agents_completions_post}

`POST /v1/agents/completions`

- Operation id: `agents_completion_v1_agents_completions_post`
- Tag: deprecated/agents

### Request body

`application/json` (required), schema `AgentsCompletionRequest`

- `max_tokens` (integer or null, optional) — The maximum number of tokens to generate in the completion. The token count of your prompt plus `max_tokens` cannot exceed the model's context length.
- `stream` (boolean, optional) — Whether to stream back partial progress. If set, tokens will be sent as data-only server-side events as they become available, with the stream terminated by a data: [DONE] message. Otherwise, the server will hold the request open until the timeout or until completion, with the response containing the full result as JSON.
- `stop` (object, optional) — Stop generation if this token is detected. Or if one of these tokens is detected when providing an array
  - one of (anyOf):
    - string
    - array of string
    - null
- `random_seed` (integer or null, optional) — The seed to use for random sampling. If set, different calls will generate deterministic results.
- `metadata` (object or null, optional)
- `messages` (array of object, required) — The prompt(s) to generate completions for, encoded as a list of dict with role and content.
  - one of (oneOf):
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
- `tools` (array of object or null, optional)
  - one of (oneOf):
    - Tool
    - WebSearchTool
    - WebSearchPremiumTool
    - CodeInterpreterTool
    - ImageGenerationTool
    - DocumentLibraryTool
- `tool_choice` (object, optional)
  - one of (anyOf):
    - ToolChoice
      - `type` (enum: 'function', optional)
      - `function` (FunctionName, required) — this restriction of `Function` is used to select a specific function to call
    - ToolChoiceEnum
- `presence_penalty` (number or null, optional) — The `presence_penalty` determines how much the model penalizes the repetition of words or phrases. A higher presence penalty encourages the model to use a wider variety of words and phrases, making the output more diverse and creative.
- `frequency_penalty` (number or null, optional) — The `frequency_penalty` penalizes the repetition of words based on their frequency in the generated text. A higher frequency penalty discourages the model from repeating words that have already appeared frequently in the output, promoting diversity and reducing repetition.
- `n` (integer or null, optional) — Number of completions to return for each request, input tokens are only billed once.
- `prediction` (Prediction, optional) — Enable users to specify expected results, optimizing response times by leveraging known or predictable content. This approach is especially effective for updating text documents or code files with minimal changes, reducing latency while maintaining high-quality results.
  - `type` (string, optional)
  - `content` (string, optional)
- `parallel_tool_calls` (boolean, optional)
- `reasoning_effort` (enum: 'none', 'minimal', 'low', 'medium', 'high', 'xhigh', optional)
- `prompt_mode` (enum: 'reasoning', optional) — Allows toggling between the reasoning mode and no system prompt. When set to `reasoning` the system prompt for reasoning models will be used.
- `guardrails` (array of GuardrailConfig or null, optional)
  - `block_on_error` (boolean, optional) — If true, return HTTP 403 and block request in the event of a server-side error
  - `moderation_llm_v1` (object or null, optional)
  - `moderation_llm_v2` (object or null, optional)
- `prompt_cache_key` (string or null, optional)
- `service_tier` (enum: 'auto', 'standard_only', optional) — Determines whether to serve the request using priority or standard capacity.
- `agent_id` (string, required) — The ID of the agent to use for this completion.

### Responses

- `200` — Successful Response (application/json, schema ChatCompletionResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)
