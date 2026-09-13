---
url: https://docs.mistral.ai/api/endpoint/chat
title: Chat API
breadcrumbs: [API, Chat]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
openapi_md5: a48c7e7248a7d23ff0ece7147ffa1a80
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Chat API

Reference for the Chat endpoints of the Mistral API, generated from the OpenAPI specification.

## Chat Completion {#operation-chat_completion_v1_chat_completions_post}

`POST /v1/chat/completions`

- Operation id: `chat_completion_v1_chat_completions_post`
- Tag: chat

### Request body

`application/json` (required), schema `ChatCompletionRequest`

- `model` (string, required) — ID of the model to use. You can use the [List Available Models](https://docs.mistral.ai/api/#tag/models/operation/list_models_v1_models_get) API to see all of your available models, or see our [Model overview](https://docs.mistral.ai/models) for model descriptions.
- `temperature` (number or null, optional) — What sampling temperature to use, we recommend between 0.0 and 0.7. Higher values like 0.7 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or `top_p` but not both. The default value varies depending on the model you are targeting. Call the `/models` endpoint to retrieve the appropriate value.
- `top_p` (number or null, optional) — Nucleus sampling, where the model considers the results of the tokens with `top_p` probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or `temperature` but not both.
- `max_tokens` (integer or null, optional) — The maximum number of tokens to generate in the completion. The token count of your prompt plus `max_tokens` cannot exceed the model's context length.
- `stream` (boolean, optional) — Whether to stream back partial progress. If set, tokens will be sent as data-only server-side events as they become available, with the stream terminated by a data: [DONE] message. Otherwise, the server will hold the request open until the timeout or until completion, with the response containing the full result as JSON.
- `stop` (object, optional) — Stop generation if this token is detected. Or if one of these tokens is detected when providing an array
  - one of 3 (anyOf):
    - string
    - array of string
    - null
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
- `tools` (array of object or null, optional) — A list of tools the model may call. Use this to provide a list of functions the model may generate JSON inputs for.
  - one of 7 (oneOf):
    - Tool
    - WebSearchTool
    - WebSearchPremiumTool
    - CodeInterpreterTool
    - ImageGenerationTool
    - DocumentLibraryTool
    - CustomConnector
- `tool_choice` (object, optional) — Controls which (if any) tool is called by the model. `none` means the model will not call any tool and instead generates a message. `auto` means the model can pick between generating a message or calling one or more tools. `any` or `required` means the model must call one or more tools. Specifying a particular tool via `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool.
  - one of 2 (anyOf):
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
- `parallel_tool_calls` (boolean, optional) — Whether to enable parallel function calling during tool use, when enabled the model can call multiple tools in parallel.
- `reasoning_effort` (enum: 'none', 'minimal', 'low', 'medium', 'high', 'xhigh', optional)
- `prompt_mode` (enum: 'reasoning', optional) — Allows toggling between the reasoning mode and no system prompt. When set to `reasoning` the system prompt for reasoning models will be used.
- `guardrails` (array of GuardrailConfig or null, optional)
  - `block_on_error` (boolean, optional) — If true, return HTTP 403 and block request in the event of a server-side error
  - `moderation_llm_v1` (object or null, optional)
  - `moderation_llm_v2` (object or null, optional)
- `prompt_cache_key` (string or null, optional)
- `safe_prompt` (boolean, optional) — Whether to inject a safety prompt before all conversations.

### Responses

- `200` — Successful Response (application/json, text/event-stream, schema ChatCompletionResponse, CompletionEvent)
- `422` — Validation Error (application/json, schema HTTPValidationError)
