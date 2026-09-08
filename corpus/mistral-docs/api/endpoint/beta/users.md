---
url: https://docs.mistral.ai/api/endpoint/beta/users
title: Beta Users API
breadcrumbs: [API, Beta Users]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Beta Users API

Reference for the Beta Users endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Identity {#operation-users_api_get_identity}

`GET /v1/users/me`

- Operation id: `users_api_get_identity`
- Tag: beta/users

### Responses

- `200` — OK (application/json, schema UserIdentity)

## List Organizations {#operation-users_api_list_organizations}

`GET /v1/users/me/organizations`

List every organization the authenticated user is a member of.

Identity-only: the caller need not have selected an organization, so this
reads only the user and never scopes by the active org.

- Operation id: `users_api_list_organizations`
- Tag: beta/users

### Parameters

- `offset` (integer, optional, in query) — Number of organizations to skip before returning results.
- `limit` (integer, optional, in query) — Maximum number of organizations to return.

### Responses

- `200` — OK (application/json, schema ListOrganizationsResponse)

## List Workspaces {#operation-users_api_list_workspaces}

`GET /v1/users/me/workspaces`

List every workspace the authenticated user is a member of, across all
their organizations, each tagged with the organization it belongs to.

- Operation id: `users_api_list_workspaces`
- Tag: beta/users

### Parameters

- `organization_id` (string (uuid) or null, optional, in query) — Return only workspaces belonging to this organization.
- `offset` (integer, optional, in query) — Number of workspaces to skip before returning results.
- `limit` (integer, optional, in query) — Maximum number of workspaces to return.

### Responses

- `200` — OK (application/json, schema ListWorkspacesResponse)
