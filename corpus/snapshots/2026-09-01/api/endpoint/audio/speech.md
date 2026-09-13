---
url: https://docs.mistral.ai/api/endpoint/audio/speech
title: Audio Speech API
breadcrumbs: [API, Audio Speech]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Audio Speech API

Reference for the Audio Speech endpoints of the Mistral API, generated from the OpenAPI specification.

## Speech {#operation-speech_v1_audio_speech_post}

`POST /v1/audio/speech`

- Operation id: `speech_v1_audio_speech_post`
- Tag: audio/speech

### Request body

`application/json` (required), schema `SpeechRequest`

- `model` (string or null, optional)
- `metadata` (object or null, optional) — Custom type for metadata with embedded validation.
- `stream` (boolean, optional)
- `prompt_cache_key` (string or null, optional)
- `voice_id` (string or null, optional) — The preset or custom voice to use for generating the speech.
- `ref_audio` (object, optional) — The audio reference for generating the speech.
  - one of 3 (anyOf):
    - string
    - string
    - null
- `input` (string, required) — Text to generate a speech from
- `response_format` (enum: 'pcm', 'wav', 'mp3', 'flac', 'opus', optional) — Output audio format. Defaults to mp3.

### Responses

- `200` — Speech audio data. (application/json, text/event-stream)
- `422` — Validation Error (application/json, schema HTTPValidationError)
