---
url: https://docs.mistral.ai/models/devstral-2-25-12
title: Devstral 2
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/devstral-2-25-12.ts
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Devstral 2

Our frontier code agents model for solving software engineering tasks; excels at using tools to explore codebases, editing multiple files and power software engineering agents.

## Overview

| Field | Value |
| --- | --- |
| API names | `devstral-2512`, `devstral-latest`, `devstral-medium-latest` |
| Slug | `devstral-2-25-12` |
| Status | Deprecated |
| Release date | 2025-12-09 |
| Version | 25.12 |
| Type | Open |
| Class | Specialist |
| Context length | 256k |
| Legacy | yes |

## Modalities

- Input: Text
- Output: Text

## Features

- [Structured Outputs](https://docs.mistral.ai/studio-api/conversations/structured-output) (`structured-outputs`)
- [Function Calling](https://docs.mistral.ai/studio-api/conversations/function-calling) (`function-calling`)
- [Document QnA](https://docs.mistral.ai/studio-api/document-processing/document_qna) (`document-qna`)
- [Prefix](https://docs.mistral.ai/studio-api/conversations/chat-completion#other-useful-features) (`prefix`)
- [Chat Completions](https://docs.mistral.ai/studio-api/conversations/chat-completion) (`chat-completions`)
- [Batching](https://docs.mistral.ai/studio-api/batch-processing) (`batching`)

## Pricing

- Input: 0.4 USD/M Tokens
- Output: 2.0 USD/M Tokens

## Weights

- Weights, 123B parameters, license Modified MIT, context 256k — [weights](https://huggingface.co/mistralai/Devstral-2-123B-Instruct-2512)

## Lifecycle

- Deprecation date: 2026-05-22
- Retirement date: 2026-07-31
- Replacement: Mistral Medium 3.5

## Links

- [Blog post](https://mistral.ai/news/devstral-2-vibe-cli)
- [Playground](https://console.mistral.ai/build/playground)

## Capability matrix

See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
