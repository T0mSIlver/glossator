---
url: https://docs.mistral.ai/api/endpoint/beta/admin/api-keys
title: Beta Admin Api Keys API
breadcrumbs: [API, Beta Admin Api Keys]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
openapi_md5: 1ae55facb05ef4d5bf803842b3033337
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Admin Api Keys API

Reference for the Beta Admin Api Keys endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Api Keys {#operation-users_api_admin_api_keys_get_api_keys}

`GET /v1/admin/api-keys`

List API keys for the Organization.

- Operation id: `users_api_admin_api_keys_get_api_keys`
- Tag: beta/admin/api-keys

### Parameters

- `limit` (integer, optional, in query) — Maximum number of results to return.
- `offset` (integer, optional, in query) — Number of results to skip before returning results.

### Responses

- `200` — OK (application/json, schema APIKeysExtendedOUT)

## Create Api Key {#operation-users_api_admin_api_keys_create_api_key}

`POST /v1/admin/api-keys`

Create a Workspace API key.

- Operation id: `users_api_admin_api_keys_create_api_key`
- Tag: beta/admin/api-keys

### Request body

`application/json` (required), schema `AdminCreateAPIKeyIN`

- `name` (string or null, optional) — Optional name for the API key.
- `expiration` (string (date) or null, optional) — Date when the API key should expire.
- `workspace_uuid` (string (uuid), required) — Workspace ID for the API key.
- `user_id` (string (uuid), required) — ID of the user the API key is created for.

### Responses

- `200` — OK (application/json, schema APIKeyOUT)

## Delete Api Key {#operation-users_api_admin_api_keys_delete_api_key}

`DELETE /v1/admin/api-keys/{key_id}`

Delete an API key.

- Operation id: `users_api_admin_api_keys_delete_api_key`
- Tag: beta/admin/api-keys

### Parameters

- `key_id` (string (uuid), required, in path) — API key ID.

### Responses

- `200` — OK (application/json, schema DeleteAPIKeyOUT)
