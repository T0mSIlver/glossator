---
url: https://docs.mistral.ai/api/endpoint/classifiers
title: Classifiers API
breadcrumbs: [API, Classifiers]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
openapi_md5: 1ae55facb05ef4d5bf803842b3033337
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Classifiers API

Reference for the Classifiers endpoints of the Mistral API, generated from the OpenAPI specification.

## Moderations {#operation-moderations_v1_moderations_post}

`POST /v1/moderations`

- Operation id: `moderations_v1_moderations_post`
- Tag: classifiers

### Request body

`application/json` (required), schema `ClassificationRequest`

- `model` (string, required) — ID of the model to use.
- `metadata` (object or null, optional)
- `input` (object, required) — Text to classify.
  - one of 2 (anyOf):
    - string
    - array of string

### Responses

- `200` — Successful Response (application/json, schema ModerationResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Chat Moderations {#operation-chat_moderations_v1_chat_moderations_post}

`POST /v1/chat/moderations`

- Operation id: `chat_moderations_v1_chat_moderations_post`
- Tag: classifiers

### Request body

`application/json` (required), schema `ChatModerationRequest`

- `input` (object, required) — Chat to classify
  - one of 2 (anyOf):
    - array of object
    - array of array of object
- `model` (string, required)

### Responses

- `200` — Successful Response (application/json, schema ModerationResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Classifications {#operation-classifications_v1_classifications_post}

`POST /v1/classifications`

- Operation id: `classifications_v1_classifications_post`
- Tag: classifiers

### Request body

`application/json` (required), schema `ClassificationRequest`

- `model` (string, required) — ID of the model to use.
- `metadata` (object or null, optional)
- `input` (object, required) — Text to classify.
  - one of 2 (anyOf):
    - string
    - array of string

### Responses

- `200` — Successful Response (application/json, schema ClassificationResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Chat Classifications {#operation-chat_classifications_v1_chat_classifications_post}

`POST /v1/chat/classifications`

- Operation id: `chat_classifications_v1_chat_classifications_post`
- Tag: classifiers

### Request body

`application/json` (required), schema `ChatClassificationRequest`

- `model` (string, required)
- `input` (ChatClassificationRequestInputs, required) — Chat to classify
  - one of 2 (anyOf):
    - InstructRequest
      - `messages` (array of object, required)
    - array of InstructRequest

### Responses

- `200` — Successful Response (application/json, schema ClassificationResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)
