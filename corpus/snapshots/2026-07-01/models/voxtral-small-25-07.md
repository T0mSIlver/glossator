---
url: https://docs.mistral.ai/models/voxtral-small-25-07
title: Voxtral Small
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/voxtral-small-25-07.ts
source_commit: 30f0c7c655287852d745d191f05e68a99d7a5b89
---

# Voxtral Small

Our first model with audio input capabilities for instruct use cases.

## Overview

| Field | Value |
| --- | --- |
| API names | `voxtral-small-2507`, `voxtral-small-latest` |
| Slug | `voxtral-small-25-07` |
| Status | Active |
| Release date | 2025-07-15 |
| Version | 25.07 |
| Type | Open |
| Class | Specialist |
| Context length | 32k |
| Legacy | no |

## Modalities

- Input: Audio, Text
- Output: Text

## Features

- [Structured Outputs](https://docs.mistral.ai/studio-api/conversations/structured-output) (`structured-outputs`)
- [Document QnA](https://docs.mistral.ai/studio-api/document-processing/document_qna) (`document-qna`)
- [Prefix](https://docs.mistral.ai/studio-api/conversations/chat-completion#other-useful-features) (`prefix`)
- [Chat Completions](https://docs.mistral.ai/studio-api/conversations/chat-completion) (`chat-completions`)
- [Batching](https://docs.mistral.ai/studio-api/batch-processing) (`batching`)
- [Function Calling](https://docs.mistral.ai/studio-api/conversations/function-calling) (`function-calling`)

## Pricing

- Input: 0.004 USD/Min; 0.1 USD/M Tokens
- Output: 0.3 USD/M Tokens

## Weights

- Weights, 24B parameters, license Apache 2.0, context 32k — [weights](https://huggingface.co/mistralai/Voxtral-Small-24B-2507)

## Links

- [Blog post](https://mistral.ai/news/voxtral)
- [Paper](https://arxiv.org/pdf/2507.13264)
- [Playground](https://console.mistral.ai/build/playground)

## Capability matrix

See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
