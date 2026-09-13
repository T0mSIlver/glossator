---
url: https://docs.mistral.ai/models/mistral-nemo-12b-24-07
title: Mistral Nemo 12B
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/mistral-nemo-12b-24-07.ts
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Mistral Nemo 12B

Our best multilingual open source model released July 2024.

## Overview

| Field | Value |
| --- | --- |
| API names | `open-mistral-nemo-2407`, `open-mistral-nemo` |
| Slug | `mistral-nemo-12b-24-07` |
| Status | Deprecated |
| Release date | 2024-07-18 |
| Version | 24.07 |
| Type | Open |
| Class | Generalist |
| Context length | 128k |
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

- Input: 0.15 USD/M Tokens
- Output: 0.15 USD/M Tokens

## Weights

- Instruct Weights, 12B parameters, license Apache 2.0, context 128k — [weights](https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407)
- Base Weights, 12B parameters, license Apache 2.0, context 128k — [weights](https://huggingface.co/mistralai/Mistral-Nemo-Base-2407)
- FP8 Instruct Weights, 12B parameters, license Apache 2.0, context 128k — [weights](https://huggingface.co/mistralai/Mistral-Nemo-Instruct-FP8-2407)

## Lifecycle

- Deprecation date: 2026-05-22
- Retirement date: 2026-07-31
- Replacement: Ministral 3 8B

## Links

- [Blog post](https://mistral.ai/news/mistral-nemo)

## Capability matrix

See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
