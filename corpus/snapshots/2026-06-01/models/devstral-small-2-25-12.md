---
url: https://docs.mistral.ai/models/devstral-small-2-25-12
title: Devstral Small 2
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/devstral-small-2-25-12.ts
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Devstral Small 2

Our open source model that excels at using tools to explore codebases, editing multiple files and power software engineering agents.

## Overview

| Field | Value |
| --- | --- |
| API names | `labs-devstral-small-2512`, `devstral-small-latest` |
| Slug | `devstral-small-2-25-12` |
| Status | Deprecated |
| Release date | 2025-12-09 |
| Version | 25.12 |
| Type | Labs |
| Class | Specialist |
| Context length | 256k |
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
- [Batching](https://docs.mistral.ai/studio-api/batch-processing) (`batching`)

## Pricing

- Input: 0.1 USD/M Tokens
- Output: 0.3 USD/M Tokens

## Weights

- Weights, 24B parameters, license Apache 2.0, context 256k — [weights](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512)

## Lifecycle

- Deprecation date: 2026-02-27
- Retirement date: 2026-03-31
- Replacement: Devstral 2

## Links

- [Blog post](https://mistral.ai/news/devstral-2-vibe-cli)
- [Playground](https://console.mistral.ai/build/playground)

## Capability matrix

See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
