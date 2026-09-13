---
url: https://docs.mistral.ai/api/endpoint/beta/libraries
title: Beta Libraries API
breadcrumbs: [API, Beta Libraries]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
openapi_md5: bdb780fc2046eadc8ab1125990abd435
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Libraries API

Reference for the Beta Libraries endpoints of the Mistral API, generated from the OpenAPI specification.

## List all libraries you have access to. {#operation-libraries_list_v1}

`GET /v1/libraries`

List all libraries that you have created or have been shared with you.

- Operation id: `libraries_list_v1`
- Tag: beta/libraries

### Responses

- `200` — Successful Response (application/json, schema ListLibraryOut)

## Create a new Library. {#operation-libraries_create_v1}

`POST /v1/libraries`

Create a new Library, you will be marked as the owner and only you will have the possibility to share it with others. When first created this will only be accessible by you.

- Operation id: `libraries_create_v1`
- Tag: beta/libraries

### Request body

`application/json` (required), schema `LibraryIn`

- `name` (string, required)
- `description` (string or null, optional)
- `chunk_size` (integer or null, optional)

### Responses

- `201` — Successful Response (application/json, schema LibraryOut)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Detailed information about a specific Library. {#operation-libraries_get_v1}

`GET /v1/libraries/{library_id}`

Given a library id, details information about that Library.

- Operation id: `libraries_get_v1`
- Tag: beta/libraries

### Parameters

- `library_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema LibraryOut)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update a library. {#operation-libraries_update_v1}

`PUT /v1/libraries/{library_id}`

Given a library id, you can update the name and description.

- Operation id: `libraries_update_v1`
- Tag: beta/libraries

### Parameters

- `library_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `LibraryInUpdate`

- `name` (string or null, optional)
- `description` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema LibraryOut)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete a library and all of it's document. {#operation-libraries_delete_v1}

`DELETE /v1/libraries/{library_id}`

Given a library id, deletes it together with all documents that have been uploaded to that library.

- Operation id: `libraries_delete_v1`
- Tag: beta/libraries

### Parameters

- `library_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema LibraryOut)
- `422` — Validation Error (application/json, schema HTTPValidationError)
