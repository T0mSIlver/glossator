---
url: https://docs.mistral.ai/api/endpoint/embeddings
title: Embeddings API
breadcrumbs: [API, Embeddings]
kind: api
locale: en
source_path: openapi.yaml
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
openapi_md5: 3c3c0d6b147730e71376c46aaca996cc
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Embeddings API

Reference for the Embeddings endpoints of the Mistral API, generated from the OpenAPI specification.

## Embeddings {#operation-embeddings_v1_embeddings_post}

`POST /v1/embeddings`

- Operation id: `embeddings_v1_embeddings_post`
- Tag: embeddings

### Request body

`application/json` (required), schema `EmbeddingRequest`

- `model` (string, required) — ID of the model to use.
- `metadata` (object or null, optional)
- `input` (object, required) — Text to embed.
  - one of 2 (anyOf):
    - string
    - array of string
- `output_dimension` (integer or null, optional) — The dimension of the output embeddings when feature available. If not provided, a default output dimension will be used.
- `output_dtype` (enum: 'float', 'int8', 'uint8', 'binary', 'ubinary', optional) — The data type of the output embeddings when feature available. If not provided, a default output data type will be used.
- `encoding_format` (enum: 'float', 'base64', optional) — The format of embeddings in the response.

### Responses

- `200` — Successful Response (application/json, schema EmbeddingResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)
