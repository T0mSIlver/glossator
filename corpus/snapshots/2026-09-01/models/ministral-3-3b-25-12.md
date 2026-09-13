---
url: https://docs.mistral.ai/models/ministral-3-3b-25-12
title: Ministral 3 3B
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/ministral-3-3b-25-12.ts
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Ministral 3 3B

Ministral 3 3B is the smallest and most efficient model in the Ministral 3 family, offering robust language and vision capabilities in a compact package. Designed for edge deployment, it delivers high performance across diverse hardware, including local setups.

## Overview

| Field | Value |
| --- | --- |
| API names | `ministral-3b-2512`, `ministral-3b-latest` |
| Slug | `ministral-3-3b-25-12` |
| Status | GA |
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

- [Structured Outputs](https://docs.mistral.ai/studio/conversations/structured-output) (`structured-outputs`)
- [Function Calling](https://docs.mistral.ai/studio/conversations/function-calling) (`function-calling`)
- [Document QnA](https://docs.mistral.ai/studio/document-processing/document_qna) (`document-qna`)
- [Prefix](https://docs.mistral.ai/studio/conversations/chat-completion#other-useful-features) (`prefix`)
- [Chat Completions](https://docs.mistral.ai/studio/conversations/chat-completion) (`chat-completions`)
- [Batching](https://docs.mistral.ai/studio/batch-processing) (`batching`)

## Pricing

- Input: 0.1 USD/M Tokens (0.088 EUR/M Tokens)
- Output: 0.1 USD/M Tokens (0.088 EUR/M Tokens)

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
