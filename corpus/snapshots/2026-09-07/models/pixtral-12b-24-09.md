---
url: https://docs.mistral.ai/models/pixtral-12b-24-09
title: Pixtral 12B
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/pixtral-12b-24-09.ts
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Pixtral 12B

A 12B model with image understanding capabilities in addition to text.

## Overview

| Field | Value |
| --- | --- |
| API names | `pixtral-12b-2409` |
| Slug | `pixtral-12b-24-09` |
| Status | Deprecated |
| Release date | 2024-09-11 |
| Version | 24.09 |
| Type | Open |
| Class | Generalist |
| Context length | 128k |
| Legacy | yes |

## Modalities

- Input: Text, Image
- Output: Text

## Features

- [Structured Outputs](https://docs.mistral.ai/studio/conversations/structured-output) (`structured-outputs`)
- [Function Calling](https://docs.mistral.ai/studio/conversations/function-calling) (`function-calling`)
- [Document QnA](https://docs.mistral.ai/studio/document-processing/document_qna) (`document-qna`)
- [Prefix](https://docs.mistral.ai/studio/conversations/chat-completion#other-useful-features) (`prefix`)
- [Chat Completions](https://docs.mistral.ai/studio/conversations/chat-completion) (`chat-completions`)
- [Batching](https://docs.mistral.ai/studio/batch-processing) (`batching`)

## Pricing

- Input: 0.15 USD/M Tokens (0.13 EUR/M Tokens)
- Output: 0.15 USD/M Tokens (0.13 EUR/M Tokens)

## Weights

- Instruct Weights, 12B parameters, license Apache 2.0, context 128k — [weights](https://huggingface.co/mistralai/Pixtral-12B-2409)
- Base Weights, 12B parameters, license Apache 2.0, context 128k — [weights](https://huggingface.co/mistralai/Pixtral-12B-Base-2409)

## Lifecycle

- Deprecation date: 2025-12-02
- Retirement date: 2025-12-31
- Replacement: Ministral 3 14B

## Links

- [Blog post](https://mistral.ai/news/pixtral-12b)
- [Paper](https://arxiv.org/pdf/2410.07073)
- [Playground](https://console.mistral.ai/build/playground)

## Capability matrix

See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
