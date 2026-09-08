---
url: https://docs.mistral.ai/api/endpoint/chat-completions
title: Create chat completion
breadcrumbs: [API reference, Chat]
kind: api
locale: en
source_path: openapi-public-doc.yaml#/paths/~1v1~1chat~1completions/post
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---
# Create chat completion {#create-chat-completion}

Creates a model response from a list of input messages.

## Request fields {#request-fields}

Send a model identifier and an ordered messages array. Each message has a role and content. Temperature changes sampling randomness, while max_tokens limits the generated continuation. Setting stream to true returns server-sent events whose data fields contain incremental deltas. Tools are supplied as function definitions with JSON Schema parameters. A response format of json_object asks supported models to produce valid JSON, but the prompt must still tell the model which object to return. The optional random seed can improve repeatability without guaranteeing byte-identical output. Unknown model identifiers and malformed message roles return a client error before generation begins.

## Response usage {#response-usage}

Non-streaming responses contain a choices array and token usage. Prompt tokens count the submitted context, completion tokens count generated output, and completion details may report reasoning tokens for models that expose them. The finish reason says whether generation stopped naturally, reached a token limit, or requested a tool. A tool call appears on the assistant message rather than as executed output. Streaming clients receive usage only when the request asks for the usage-bearing final event. Billing and evaluation tools should store the model returned by the service because aliases may resolve to a dated model version.
