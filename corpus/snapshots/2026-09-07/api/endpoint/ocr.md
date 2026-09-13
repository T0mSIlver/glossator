---
url: https://docs.mistral.ai/api/endpoint/ocr
title: OCR API
breadcrumbs: [API, OCR]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# OCR API

Reference for the OCR endpoints of the Mistral API, generated from the OpenAPI specification.

## OCR {#operation-ocr_v1_ocr_post}

`POST /v1/ocr`

- Operation id: `ocr_v1_ocr_post`
- Tag: ocr

### Request body

`application/json` (required), schema `OCRRequest`

- `model` (string or null, required)
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
- `pages` (object, optional) — Specific pages to process. Accepts a list of integers or a string of comma-separated numbers and ranges (e.g. '0,1,2' or '0-5' or '0,2-4'). Page numbers start from 0.
  - one of 3 (anyOf):
    - string
    - array of integer
    - null
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
- `extract_header` (boolean, optional) — Extract the page header into the response's `header` field and remove it from the markdown content
- `extract_footer` (boolean, optional) — Extract the page footer into the response's `footer` field and remove it from the markdown content
- `include_blocks` (boolean, optional) — Return paragraph-level bounding boxes for all content blocks in the response
- `confidence_scores_granularity` (enum: 'word', 'page', 'block', optional) — Granularity for confidence scores: 'page' (aggregate only), 'word' (per-word scores), or 'block' (per-block scores). Defaults to None (no confidence scores) to keep response payload small.

### Responses

- `200` — Successful Response (application/json, schema OCRResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)
