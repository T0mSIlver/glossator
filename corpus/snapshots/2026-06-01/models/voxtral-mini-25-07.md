---
url: https://docs.mistral.ai/models/voxtral-mini-25-07
title: Voxtral Mini
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/voxtral-mini-25-07.ts
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# Voxtral Mini

A mini version of our first audio input model.

## Overview

| Field | Value |
| --- | --- |
| API names | `voxtral-mini-2507`, `voxtral-mini-latest` |
| Slug | `voxtral-mini-25-07` |
| Status | Deprecated |
| Release date | 2025-07-15 |
| Version | 25.07 |
| Type | Open |
| Class | Specialist |
| Context length | 32k |
| Legacy | yes |

## Modalities

- Input: Audio, Text
- Output: Text

## Features

- [Structured Outputs](https://docs.mistral.ai/studio-api/conversations/structured-output) (`structured-outputs`)
- [Document QnA](https://docs.mistral.ai/studio-api/document-processing/document_qna) (`document-qna`)
- [Prefix](https://docs.mistral.ai/studio-api/conversations/chat-completion#other-useful-features) (`prefix`)
- [Chat Completions](https://docs.mistral.ai/studio-api/conversations/chat-completion) (`chat-completions`)
- [Batching](https://docs.mistral.ai/studio-api/batch-processing) (`batching`)

## Pricing

- Input: 0.001 USD/Min; 0.04 USD/M Tokens
- Output: 0.04 USD/M Tokens

## Weights

- Weights, 4B parameters, license Apache 2.0, context 32k — [weights](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507)

## Lifecycle

- Deprecation date: 2026-02-27
- Retirement date: 2026-05-31
- Replacement: Voxtral Mini Transcribe 2

## Links

- [Blog post](https://mistral.ai/news/voxtral)
- [Paper](https://arxiv.org/pdf/2507.13264)
- [Playground](https://console.mistral.ai/build/playground)

## Capability matrix

See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
