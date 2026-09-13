---
url: https://docs.mistral.ai/models/voxtral-tts-26-03
title: Voxtral TTS
breadcrumbs: [Models]
kind: model
locale: en
source_path: src/schema/models/models/voxtral-tts-26-03.ts
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Voxtral TTS

Our state-of-the-art text-to-speech model with zero-shot voice cloning. Supports 9 languages, streaming with ~90ms time-to-first-audio, and no transcript required for voice prompts.

## Overview

| Field | Value |
| --- | --- |
| API names | `voxtral-mini-tts-2603`, `voxtral-mini-tts-latest` |
| Slug | `voxtral-tts-26-03` |
| Status | GA |
| Release date | 2026-03-23 |
| Version | 26.03 |
| Type | Open |
| Class | Specialist |
| Legacy | no |

## Modalities

- Input: Text, Audio
- Output: Audio

## Features

- [Text to Speech](https://docs.mistral.ai/studio-api/audio/text_to_speech) (`tts`)
- [Voice Cloning](https://docs.mistral.ai/studio-api/audio/text_to_speech/voices) (`voice-cloning`)

## Pricing

- Input: 0.0 USD/M Chars
- Output: 16.0 USD/M Chars

## Weights

- Weights, 4B parameters, license CC BY-NC 4.0 — [weights](https://huggingface.co/mistralai/Voxtral-4B-TTS-2603)

## Links

- [Playground](https://console.mistral.ai/build/audio/text-to-speech)

## Capability matrix

See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
