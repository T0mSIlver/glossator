---
url: https://docs.mistral.ai/api/endpoint/audio/voices
title: Audio Voices API
breadcrumbs: [API, Audio Voices]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Audio Voices API

Reference for the Audio Voices endpoints of the Mistral API, generated from the OpenAPI specification.

## List all voices {#operation-list_voices_v1_audio_voices_get}

`GET /v1/audio/voices`

List all voices (excluding sample data)

- Operation id: `list_voices_v1_audio_voices_get`
- Tag: audio/voices

### Parameters

- `limit` (integer, optional, in query) — Maximum number of voices to return
- `offset` (integer, optional, in query) — Offset for pagination
- `type` (enum: 'all', 'custom', 'preset', optional, in query) — Filter the voices between customs and presets

### Responses

- `200` — Successful Response (application/json, schema VoiceListResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create a new voice {#operation-create_voice_v1_audio_voices_post}

`POST /v1/audio/voices`

Create a new voice with a base64-encoded audio sample

- Operation id: `create_voice_v1_audio_voices_post`
- Tag: audio/voices

### Request body

`application/json` (required), schema `VoiceCreateRequest`

- `name` (string, required)
- `slug` (string or null, optional)
- `languages` (array of string, optional)
- `gender` (string or null, optional)
- `age` (integer or null, optional)
- `tags` (array of string or null, optional)
- `color` (string or null, optional)
- `description` (string or null, optional)
- `retention_notice` (integer, optional)
- `sample_audio` (string, required) — Base64-encoded audio file
- `sample_filename` (string or null, optional) — Original filename for extension detection

### Responses

- `200` — Successful Response (application/json, schema VoiceResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get voice details {#operation-get_voice_v1_audio_voices_voice_id_get}

`GET /v1/audio/voices/{voice_id}`

Get voice details (excluding sample)

- Operation id: `get_voice_v1_audio_voices__voice_id__get`
- Tag: audio/voices

### Parameters

- `voice_id` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema VoiceResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete a custom voice {#operation-delete_voice_v1_audio_voices_voice_id_delete}

`DELETE /v1/audio/voices/{voice_id}`

- Operation id: `delete_voice_v1_audio_voices__voice_id__delete`
- Tag: audio/voices

### Parameters

- `voice_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema VoiceResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update voice metadata {#operation-update_voice_v1_audio_voices_voice_id_patch}

`PATCH /v1/audio/voices/{voice_id}`

Update voice metadata (name, gender, languages, age, tags).

- Operation id: `update_voice_v1_audio_voices__voice_id__patch`
- Tag: audio/voices

### Parameters

- `voice_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `VoiceUpdateRequest`

- `name` (string or null, optional)
- `languages` (array of string or null, optional)
- `gender` (string or null, optional)
- `age` (integer or null, optional)
- `tags` (array of string or null, optional)
- `description` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema VoiceResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get voice sample audio {#operation-get_voice_sample_audio_v1_audio_voices_voice_id_sample_get}

`GET /v1/audio/voices/{voice_id}/sample`

Get the audio sample for a voice

- Operation id: `get_voice_sample_audio_v1_audio_voices__voice_id__sample_get`
- Tag: audio/voices

### Parameters

- `voice_id` (string, required, in path)

### Responses

- `200` — Successful Response (audio/wav)
- `422` — Validation Error (application/json, schema HTTPValidationError)
