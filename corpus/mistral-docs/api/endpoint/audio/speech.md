---
url: https://docs.mistral.ai/api/endpoint/audio/speech
title: Audio Speech API
breadcrumbs: [API, Audio Speech]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
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
  - one of (anyOf):
    - string
    - string
    - null
- `input` (string, required) — Text to generate a speech from
- `response_format` (enum: 'pcm', 'wav', 'mp3', 'flac', 'opus', optional) — Output audio format. Defaults to mp3.

### Responses

- `200` — Speech audio data. (application/json, text/event-stream)
- `422` — Validation Error (application/json, schema HTTPValidationError)
