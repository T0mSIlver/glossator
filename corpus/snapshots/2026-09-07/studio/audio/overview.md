---
url: https://docs.mistral.ai/studio/audio/overview
title: Audio
breadcrumbs: [Studio, Audio]
kind: doc
locale: en
source_path: src/content/en/docs/studio/audio/overview/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Audio

Transcribe speech to text, generate and clone voices from text, and build real-time voice agents with Mistral's **Voxtral** models.

Start with the outcome you want to build. Use the request-based audio APIs for files and bounded requests, the realtime API for live audio that needs low latency, and the full speech-to-speech pipeline for voice agents that listen, reason, and respond.

## Choose your path {#choose-your-path}

| Goal | Models | How to use |
| --- | --- | --- |
| Transcribe recordings, meetings, or call archives | [Voxtral Mini Transcribe 2](https://docs.mistral.ai/models/voxtral-mini-transcribe-26-02) | [Offline transcription](https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription) |
| Transcribe live audio with sub-200ms latency | [Voxtral Realtime](https://docs.mistral.ai/models/voxtral-mini-transcribe-realtime-26-02) | [Realtime transcription](https://docs.mistral.ai/studio/audio/speech_to_text/realtime_transcription) |
| Generate natural speech or clone a voice | [Voxtral TTS](https://docs.mistral.ai/models/voxtral-tts-26-03) | [Text to speech](https://docs.mistral.ai/studio/audio/text_to_speech) |
| Build a voice agent that listens, reasons, and speaks | [Voxtral Realtime](https://docs.mistral.ai/models/voxtral-mini-transcribe-realtime-26-02) + an LLM + [Voxtral TTS](https://docs.mistral.ai/models/voxtral-tts-26-03) | [Speech-to-speech pipeline](https://docs.mistral.ai/studio/audio/overview#speech-to-speech-pipeline) |

## Capabilities {#capabilities}

### Speech to text {#speech-to-text}

Convert speech to text with high accuracy and low latency. Two models cover batch and live workloads:

- **[Voxtral Mini Transcribe 2](https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription)** for batch transcription — speaker diarization, context biasing (up to 100 custom terms), word-level timestamps, recordings up to 3 hours per request, and noise-robust accuracy across 13 languages.
- **Voxtral Realtime** (`voxtral-mini-transcribe-realtime-2602`) for [live streaming](https://docs.mistral.ai/studio/audio/speech_to_text/realtime_transcription) — transcribes audio as it arrives with latency configurable down to sub-200ms, a 4B footprint for edge deployment, and open weights under Apache 2.0.

> **Note**
>
> Realtime transcription is not compatible with the `diarize` parameter. Use one or the other.

### Text to speech {#text-to-speech}

**Voxtral TTS** (`voxtral-mini-tts-2603`) generates expressive speech and clones any voice from a sample as short as 2–3 seconds, capturing tone, rhythm, and personality. The model treats the voice prompt as an instruction, so it follows the speaker's intonation and emotional rendering without separate prosody tags. It supports 9 languages with cross-lingual cloning and code-mixing, and streams with low processing latency (~90ms) for voice-agent use.

- [Voices](https://docs.mistral.ai/studio/audio/text_to_speech/voices): create and manage reusable voice profiles for consistent branding.
- [Speech generation](https://docs.mistral.ai/studio/audio/text_to_speech/speech): generate speech from saved voices or one-off reference clips, with basic or streaming delivery.

### Speech-to-speech pipeline {#speech-to-speech-pipeline}

Combine the models into a real-time voice-to-voice loop: **Voxtral Realtime** transcribes incoming speech, **an LLM** reasons over the transcript and decides a response, and **Voxtral TTS** speaks the reply.

![Speech-to-speech pipeline: speech in flows to Voxtral Realtime (transcribe speech), then an LLM (reason over transcript), then Voxtral TTS (speak the reply), producing speech out.](https://docs.mistral.ai/img/audio_speech_to_speech_pipeline.svg)

Each component is independently customizable and deployable. Cross-lingual voice adaptation lets the same pipeline handle live translation while preserving the speaker's accent and identity.

## Models {#models}

The Voxtral family covers transcription, speech generation, and audio understanding, available as Premier and open-weights models. Open a model card for capabilities, languages, pricing, and benchmarks.

> **Tip**
>
> Test transcription in the [speech-to-text playground](https://console.mistral.ai/build/audio/speech-to-text), and voice generation and cloning in the [text-to-speech playground](https://console.mistral.ai/build/audio/text-to-speech).

## How teams use audio {#use-cases}

- **Customer support**: voice agents that route and resolve queries with natural, brand-appropriate speech.
- **Financial services**: compliant voice AI for advisory, policy queries, and client onboarding.
- **Compliance and risk**: real-time call monitoring with speaker attribution and auditable interaction records.
- **Manufacturing and field operations**: voice interfaces for inspection and feedback in high-noise environments.
- **Meetings and sales**: meeting intelligence with speaker attribution and automated follow-ups.
- **Real-time translation**: cross-lingual voice adaptation for live translation that preserves speaker identity and accent.

## FAQ {#faq}

### Which transcription model should I use? {#which-transcription-model-should-i-use}

Use **Voxtral Mini Transcribe 2** for batch transcription with diarization, word-level timestamps, and long audio. Use **Voxtral Realtime** for live streaming with sub-200ms latency.

### Can I clone a voice? {#can-i-clone-a-voice}

Yes. Use the [API](https://docs.mistral.ai/studio/audio/text_to_speech/voices) and provide a sample as short as 2–3 seconds and Voxtral TTS adapts to its tone, rhythm, and personality. You can also use preset voices or build a reusable [voice library](https://docs.mistral.ai/studio/audio/text_to_speech/voices).

### Which languages are supported? {#which-languages-are-supported}

Transcription supports 13 languages and voice generation supports 9, with cross-lingual and dialect adaptation. See [supported languages](https://docs.mistral.ai/resources/languages).

### Can I deploy on-premises or in a VPC? {#can-i-deploy-on-premises-or-in-a-vpc}

Yes. The Voxtral models ship with open weights, so you can self-host or deploy them on your own infrastructure. See [deployment](https://docs.mistral.ai/inference/deployment).
