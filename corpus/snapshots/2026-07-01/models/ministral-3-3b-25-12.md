---
url: https://docs.mistral.ai/models/ministral-3-3b-25-12
title: Ministral 3 3B
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/ministral-3-3b-25-12.ts
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Ministral 3 3B

Ministral 3 3B is the smallest and most efficient model in the Ministral 3 family, offering robust language and vision capabilities in a compact package. Designed for edge deployment, it delivers high performance across diverse hardware, including local setups.

## Overview

| Field | Value |
| --- | --- |
| API names | `ministral-3b-2512`, `ministral-3b-latest` |
| Slug | `ministral-3-3b-25-12` |
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

## Pricing

- Input: 0.1 USD/M Tokens
- Output: 0.1 USD/M Tokens

## Weights

- Instruct Weights, 3B parameters, license Apache 2.0, context 256k — [weights](https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512)
- Reasoning Weights, 3B parameters, license Apache 2.0, context 256k — [weights](https://huggingface.co/mistralai/Ministral-3-3B-Reasoning-2512)
- Base Weights, 3B parameters, license Apache 2.0, context 256k — [weights](https://huggingface.co/mistralai/Ministral-3-3B-Base-2512)

## Links

- [Blog post](https://mistral.ai/news/mistral-3)
- [Paper](https://arxiv.org/abs/2601.08584)
- [Playground](https://console.mistral.ai/build/playground)

## Capability matrix

See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
