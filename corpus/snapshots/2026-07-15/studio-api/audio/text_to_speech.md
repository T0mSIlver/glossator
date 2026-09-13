---
url: https://docs.mistral.ai/studio-api/audio/text_to_speech
title: Text to Speech
breadcrumbs: [Studio, Audio]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/audio/text_to_speech/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Text to Speech

**Voxtral TTS** is Mistral's text-to-speech model with zero-shot voice cloning. It generates natural, expressive speech from text using a short audio prompt.

## Key Features

- **Zero-shot voice cloning**: Clone any voice from as little as 2–3 seconds of audio, capturing emotion, speaking style, and accent.
- **Voice-as-an-instruction**: The model follows the intonation, rhythm, and emotional rendering of the voice prompt — no prosody or emotion tags needed.
- **Multilingual support**: English, French, Spanish, Portuguese, Italian, Dutch, German, Hindi, Arabic. Supports cross-lingual voice cloning and code-mixing.
- **Streaming**: Low model latency (~90ms processing time). End-to-end API time-to-first-audio varies by format (~0.8s for `pcm`, ~3s for `mp3`), suitable for real-time voice agent applications.

## Text to Speech Services {#tts-services}

Explore our comprehensive TTS services to bring your applications to life with natural-sounding speech:
    - [Voices](https://docs.mistral.ai/studio-api/audio/text_to_speech/voices): Create and manage reusable voice profiles for consistent branding and personalization.
    - [Speech Generation](https://docs.mistral.ai/studio-api/audio/text_to_speech/speech): Generate speech using either saved voices or one-off reference audio clips with support for both basic and streaming delivery.
