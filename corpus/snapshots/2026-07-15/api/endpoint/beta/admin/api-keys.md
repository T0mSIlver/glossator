---
url: https://docs.mistral.ai/api/endpoint/beta/admin/api-keys
title: Beta Admin Api Keys API
breadcrumbs: [API, Beta Admin Api Keys]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
openapi_md5: c28e3a674c73b4319d99305d173a6656
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Admin Api Keys API

Reference for the Beta Admin Api Keys endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Api Keys {#operation-users_api_admin_api_keys_get_api_keys}

`GET /api/admin/api-keys`

List API keys for the Organization.

- Operation id: `users_api_admin_api_keys_get_api_keys`
- Tag: beta/admin/api-keys

### Parameters

- `limit` (integer, optional, in query) — Maximum number of results to return.
- `offset` (integer, optional, in query) — Number of results to skip before returning results.

### Responses

- `200` — OK (application/json, schema APIKeysExtendedOUT)

## Create Api Key {#operation-users_api_admin_api_keys_create_api_key}

`POST /api/admin/api-keys`

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

`DELETE /api/admin/api-keys/{key_id}`

Delete an API key.

- Operation id: `users_api_admin_api_keys_delete_api_key`
- Tag: beta/admin/api-keys

### Parameters

- `key_id` (string (uuid), required, in path) — API key ID.

### Responses

- `200` — OK (application/json, schema DeleteAPIKeyOUT)
