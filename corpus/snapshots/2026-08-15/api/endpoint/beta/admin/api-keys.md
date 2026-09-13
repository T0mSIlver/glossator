---
url: https://docs.mistral.ai/api/endpoint/beta/admin/api-keys
title: Beta Admin Api Keys API
breadcrumbs: [API, Beta Admin Api Keys]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
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
- `name` (string or null, optional, in query) — Filter API keys by name substring or the last 4 characters of the key. Matching is case-insensitive and accent-insensitive.

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
