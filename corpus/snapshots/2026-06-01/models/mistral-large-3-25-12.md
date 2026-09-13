---
url: https://docs.mistral.ai/models/mistral-large-3-25-12
title: Mistral Large 3
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/mistral-large-3-25-12.ts
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Mistral Large 3

Mistral Large 3, is a state-of-the-art, open-weight, general-purpose multimodal model with a granular Mixture-of-Experts architecture. It features 41B active parameters and 675B total parameters.

## Overview

| Field | Value |
| --- | --- |
| API names | `mistral-large-2512`, `mistral-large-latest` |
| Slug | `mistral-large-3-25-12` |
| Status | Active |
| Release date | 2025-12-02 |
| Version | 25.12 |
| Type | Open |
| Class | Generalist |
| Context length | 256k |
| Legacy | no |

## Modalities

- Input: Text, Image
- Output: Text

## Features

- [Structured Outputs](https://docs.mistral.ai/studio-api/conversations/structured-output) (`structured-outputs`)
- [Function Calling](https://docs.mistral.ai/studio-api/conversations/function-calling) (`function-calling`)
- [Document QnA](https://docs.mistral.ai/studio-api/document-processing/document_qna) (`document-qna`)
- [Prefix](https://docs.mistral.ai/studio-api/conversations/chat-completion#other-useful-features) (`prefix`)
- [Chat Completions](https://docs.mistral.ai/studio-api/conversations/chat-completion) (`chat-completions`)
- [Batching](https://docs.mistral.ai/studio-api/batch-processing) (`batching`)
- [Agents & Conversations](https://docs.mistral.ai/studio-api/agents/agents-api) (`agents-conversations`)
- [Built-In Tools](https://docs.mistral.ai/studio-api/agents/agent-tools) (`connectors`)

## Pricing

- Input: 0.5 USD/M Tokens
- Output: 1.5 USD/M Tokens

## Weights

- Weights, 675B parameters, license Apache 2.0, context 256k — [weights](https://huggingface.co/mistralai/Mistral-Large-3-675B-Instruct-2512)

## Links

- [Blog post](https://mistral.ai/news/mistral-3)
- [Playground](https://console.mistral.ai/build/playground)

## Capability matrix

See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
