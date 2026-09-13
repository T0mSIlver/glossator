---
url: https://docs.mistral.ai/api/endpoint/ocr
title: Ocr API
breadcrumbs: [API, Ocr]
kind: api
locale: en
source_path: openapi.yaml
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
openapi_md5: 3c3c0d6b147730e71376c46aaca996cc
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Ocr API

Reference for the Ocr endpoints of the Mistral API, generated from the OpenAPI specification.

## OCR {#operation-ocr_v1_ocr_post}

`POST /v1/ocr`

- Operation id: `ocr_v1_ocr_post`
- Tag: ocr

### Request body

`application/json` (required), schema `OCRRequest`

- `model` (string or null, required)
- `id` (string, optional)
- `document` (object, required) — Document to run OCR on
  - one of 3 (anyOf):
    - FileChunk
      - `type` (string, optional)
      - `file_id` (string (uuid), required)
    - DocumentURLChunk
      - `type` (string, optional)
      - `document_url` (string, required)
      - `document_name` (string or null, optional) — The filename of the document
    - ImageURLChunk
      - `type` (string, optional)
      - `image_url` (object, required)
- `pages` (array of integer or null, optional) — Specific pages user wants to process in various formats: single number, range, or list of both. Starts from 0
- `include_image_base64` (boolean or null, optional) — Include image URLs in response
- `image_limit` (integer or null, optional) — Max images to extract
- `image_min_size` (integer or null, optional) — Minimum height and width of image to extract
- `bbox_annotation_format` (object or null, optional) — Structured output class for extracting useful information from each extracted bounding box / image from document. Only json_schema is valid for this field
  - `type` (enum: 'text', 'json_object', 'json_schema', optional)
  - `json_schema` (object or null, optional)
    - `name` (string, required)
    - `description` (string or null, optional)
    - `schema` (object, required)
    - `strict` (boolean, optional)
- `document_annotation_format` (object or null, optional) — Structured output class for extracting useful information from the entire document. Only json_schema is valid for this field
  - `type` (enum: 'text', 'json_object', 'json_schema', optional)
  - `json_schema` (object or null, optional)
    - `name` (string, required)
    - `description` (string or null, optional)
    - `schema` (object, required)
    - `strict` (boolean, optional)
- `document_annotation_prompt` (string or null, optional) — Optional prompt to guide the model in extracting structured output from the entire document. A document_annotation_format must be provided.
- `table_format` (enum: 'markdown', 'html', optional)
- `extract_header` (boolean, optional)
- `extract_footer` (boolean, optional)
- `confidence_scores_granularity` (enum: 'word', 'page', optional) — Granularity for confidence scores: 'word' (per-word scores) or 'page' (aggregate only). Defaults to None (no confidence scores) to keep response payload small.

### Responses

- `200` — Successful Response (application/json, schema OCRResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)
