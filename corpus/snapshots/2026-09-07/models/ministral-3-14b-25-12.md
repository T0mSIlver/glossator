---
url: https://docs.mistral.ai/models/ministral-3-14b-25-12
title: Ministral 3 14B
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/ministral-3-14b-25-12.ts
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Ministral 3 14B

Ministral 3 14B is the largest model in the Ministral 3 family, offering state-of-the-art capabilities and performance comparable to its larger Mistral Small 3.2 24B counterpart. Optimized for local deployment, it delivers high performance across diverse hardware, including local setups.

## Overview

| Field | Value |
| --- | --- |
| API names | `ministral-14b-2512`, `ministral-14b-latest` |
| Slug | `ministral-3-14b-25-12` |
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

- Input: 0.2 USD/M Tokens (0.18 EUR/M Tokens)
- Output: 0.2 USD/M Tokens (0.18 EUR/M Tokens)

## Weights

- Instruct Weights, 14B parameters, license Apache 2.0, context 256k — [weights](https://huggingface.co/mistralai/Ministral-3-14B-Instruct-2512)
- Reasoning Weights, 14B parameters, license Apache 2.0, context 256k — [weights](https://huggingface.co/mistralai/Ministral-3-14B-Reasoning-2512)
- Base Weights, 14B parameters, license Apache 2.0, context 256k — [weights](https://huggingface.co/mistralai/Ministral-3-14B-Base-2512)

## Links

- [Blog post](https://mistral.ai/news/mistral-3)
- [Paper](https://arxiv.org/abs/2601.08584)
- [Playground](https://console.mistral.ai/build/playground)

## Capability matrix

See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
