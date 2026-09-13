---
url: https://docs.mistral.ai/resources/known-limitations
title: Known limitations
breadcrumbs: [Resources]
kind: doc
locale: en
source_path: src/content/en/docs/resources/known-limitations/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Known limitations

This page documents current limitations of the Mistral platform. We actively work to address these. Check the [changelogs](https://docs.mistral.ai/resources/changelogs) for updates.

## Context window {#context-window}

| Model | Max context length |
|-------|-------------------|
| Mistral Large 3 | 256k tokens |
| Mistral Medium 3.5 | 256k tokens |
| Mistral Medium 3.1 | 128k tokens |
| Mistral Small 4 | 256k tokens |
| Codestral | 128k tokens |
| Devstral 2 | 256k tokens |
| Magistral Medium 1.2 | 128k tokens |
| Ministral 3 (3B / 8B / 14B) | 256k tokens |
| Mistral Nemo 12B | 128k tokens |

For the full and up-to-date list, see the [model cards](https://docs.mistral.ai/models).

- Requests exceeding the model's context window return a `400 Bad Request` error.
- Token counts include both input and output tokens. Plan your `max_tokens` accordingly.

## Rate limits {#rate-limits}

Rate limits vary by subscription tier and model. When exceeded, the API returns `429 Too Many Requests`.

- **Requests per second** and **tokens per minute** are enforced independently.
- Limits apply per organization.
- You can check your current rate limits in the [limits page](https://admin.mistral.ai/plateforme/limits).
- [Batch processing](https://docs.mistral.ai/studio/batch-processing) does not count against real-time rate limits.

> **Tip**
>
> Check the `X-RateLimit-Remaining` response header to monitor your usage before hitting the limit.

## File uploads {#file-uploads}

- Maximum file size: **512 MB**
- Supported formats for OCR: PDF, PNG, JPG, JPEG, TIFF, BMP, GIF, WEBP
- Uploaded files are retained for 30 days unless deleted earlier.

## Batch processing {#batch-processing}

- Maximum batch file size: **512 MB**.
- Maximum requests per batch: **100,000**.
- Batch jobs are processed asynchronously; completion time depends on queue depth and request complexity.
- Batch results are available for download for **24 hours** after completion.

## Streaming {#streaming}

- Streaming connections time out after **10 minutes** of inactivity.
- `stream_options.include_usage` must be explicitly set to receive token usage in stream events.
- Some client HTTP libraries may buffer streamed responses; ensure chunked transfer encoding is handled correctly.

## Function calling {#function-calling}

- Maximum number of tools per request: **128**.
- Tool descriptions are included in the token count. Long descriptions reduce available context for messages.
- Parallel function calls are supported but may return calls in any order.
- `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected.

## JSON mode {#json-mode}

- When `response_format: {"type": "json_object"}` is set, the model always returns valid JSON.
- You must include "JSON" in the system or user prompt. Otherwise the model may produce an infinite whitespace stream.
- JSON mode does not guarantee adherence to a specific schema. Use function calling for structured outputs.

## Vision {#vision}

- Maximum image size: **20 MB** per image.
- Supported formats: PNG, JPG, JPEG, GIF, WEBP.
- Maximum images per request depends on the model and total token budget.
- Images are resized internally; very small images may lose detail.

## Audio transcription {#audio}

- Supported formats: WAV, MP3, FLAC, OGG, WEBM.
- Maximum audio duration: **60 minutes**.
- Maximum file size: **500 MB**.
- Transcription is optimized for clear speech; heavy background noise reduces accuracy.

## Regional availability {#regional-availability}

- The Mistral API is served from EU data centers by default.
- Some models may not be available in all regions. Check the [models page](https://docs.mistral.ai/models) for details.
