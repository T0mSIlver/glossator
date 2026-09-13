---
url: https://docs.mistral.ai/api/endpoint/audio/transcriptions
title: Audio Transcriptions API
breadcrumbs: [API, Audio Transcriptions]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Audio Transcriptions API

Reference for the Audio Transcriptions endpoints of the Mistral API, generated from the OpenAPI specification.

## Create Transcription {#operation-audio_api_v1_transcriptions_post}

`POST /v1/audio/transcriptions`

- Operation id: `audio_api_v1_transcriptions_post`
- Tag: audio/transcriptions

### Request body

`multipart/form-data` (required), schema `AudioTranscriptionRequest`

- `model` (string, required) — ID of the model to be used.
- `file` (string (binary) or null, optional) — The File object (not file name) to be uploaded. To upload a file and specify a custom file name you should format your request as such:

  ```bash
  file=@path/to/your/file.jsonl;filename=custom_name.jsonl
  ```
  Otherwise, you can just keep the original file name:
  ```bash
  file=@path/to/your/file.jsonl
  ```

- `file_url` (string (uri) or null, optional) — Url of a file to be transcribed
- `file_id` (string or null, optional) — ID of a file uploaded to /v1/files
- `language` (string or null, optional) — Language of the audio, e.g. 'en'. Providing the language can boost accuracy.
- `temperature` (number or null, optional)
- `stream` (boolean, optional)
- `diarize` (boolean, optional)
- `context_bias` (array of string, optional)
- `timestamp_granularities` (array of TimestampGranularity, optional) — Granularities of timestamps to include in the response.

### Responses

- `200` — Successful Response (application/json, schema TranscriptionResponse)

## Create Streaming Transcription (SSE) {#operation-audio_api_v1_transcriptions_post_stream}

`POST /v1/audio/transcriptions`

- Operation id: `audio_api_v1_transcriptions_post_stream`
- Tag: audio/transcriptions

### Request body

`multipart/form-data` (required), schema `AudioTranscriptionRequestStream`

- `model` (string, required)
- `file` (string (binary) or null, optional) — The File object (not file name) to be uploaded. To upload a file and specify a custom file name you should format your request as such:

  ```bash
  file=@path/to/your/file.jsonl;filename=custom_name.jsonl
  ```
  Otherwise, you can just keep the original file name:
  ```bash
  file=@path/to/your/file.jsonl
  ```

- `file_url` (string (uri) or null, optional) — Url of a file to be transcribed
- `file_id` (string or null, optional) — ID of a file uploaded to /v1/files
- `language` (string or null, optional) — Language of the audio, e.g. 'en'. Providing the language can boost accuracy.
- `temperature` (number or null, optional)
- `stream` (boolean, optional)
- `diarize` (boolean, optional)
- `context_bias` (array of string, optional)
- `timestamp_granularities` (array of TimestampGranularity, optional) — Granularities of timestamps to include in the response.

### Responses

- `200` — Stream of transcription events (text/event-stream, schema TranscriptionStreamEvents)
