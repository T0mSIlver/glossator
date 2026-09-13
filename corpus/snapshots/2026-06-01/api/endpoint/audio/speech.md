---
url: https://docs.mistral.ai/api/endpoint/audio/speech
title: Audio Speech API
breadcrumbs: [API, Audio Speech]
kind: api
locale: en
source_path: openapi.yaml
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
openapi_md5: 3c3c0d6b147730e71376c46aaca996cc
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Audio Speech API

Reference for the Audio Speech endpoints of the Mistral API, generated from the OpenAPI specification.

## Speech {#operation-speech_v1_audio_speech_post}

`POST /v1/audio/speech`

Generate speech from text using a saved voice or a reference audio clip.

- Operation id: `speech_v1_audio_speech_post`
- Tag: audio/speech

### Request body

`application/json` (required), schema `SpeechRequest`

- `model` (string or null, optional)
- `stream` (boolean, optional)
- `voice_id` (string or null, optional) — The preset or custom voice to use for generating the speech.
- `ref_audio` (string or null, optional) — The base64-encoded audio reference for zero-shot voice cloning.
- `input` (string, required) — Text to generate speech from.
- `response_format` (enum: 'pcm', 'wav', 'mp3', 'flac', 'opus', optional) — Output audio format. Defaults to mp3.

### Responses

- `200` — Speech audio data. (application/json, text/event-stream, schema SpeechResponse, SpeechStreamEvents)
- `422` — Validation Error (application/json, schema HTTPValidationError)
