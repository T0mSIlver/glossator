---
url: https://docs.mistral.ai/models/mistral-small-3-2-25-06
title: Mistral Small 3.2
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/mistral-small-3-2-25-06.ts
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Mistral Small 3.2

An update to our previous small model, released June 2025.

## Overview

| Field | Value |
| --- | --- |
| API names | `mistral-small-2506` |
| Slug | `mistral-small-3-2-25-06` |
| Status | Deprecated |
| Release date | 2025-06-20 |
| Version | 25.06 |
| Type | Open |
| Class | Generalist |
| Context length | 128k |
| Legacy | yes |

## Modalities

- Input: Text, Image
- Output: Text

## Features

- [Structured Outputs](https://docs.mistral.ai/studio-api/conversations/structured-output) (`structured-outputs`)
- [Function Calling](https://docs.mistral.ai/studio-api/conversations/function-calling) (`function-calling`)
- [Document QnA](https://docs.mistral.ai/studio-api/document-processing/document_qna) (`document-qna`)
- [Prefix](https://docs.mistral.ai/studio-api/conversations/chat-completion#other-useful-features) (`prefix`)
- [Chat Completions](https://docs.mistral.ai/studio-api/conversations/chat-completion) (`chat-completions`)
- [Agents & Conversations](https://docs.mistral.ai/studio-api/agents/agents-api) (`agents-conversations`)
- [Batching](https://docs.mistral.ai/studio-api/batch-processing) (`batching`)
- [Built-In Tools](https://docs.mistral.ai/studio-api/agents/agent-tools) (`connectors`)
- [Predicted Outputs](https://docs.mistral.ai/studio-api/conversations/advanced/predicted-outputs) (`predicted-outputs`)

## Pricing

- Input: 0.1 USD/M Tokens
- Output: 0.3 USD/M Tokens

## Weights

- Weights, 24B parameters, license Apache 2.0, context 128k — [weights](https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506)

## Lifecycle

- Deprecation date: 2026-04-30
- Retirement date: 2026-07-31
- Replacement: Mistral Small 4

## Links

- [Playground](https://console.mistral.ai/build/playground)

## Capability matrix

See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
