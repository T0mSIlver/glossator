---
url: https://docs.mistral.ai/api/endpoint/beta/admin/vibe-code-analytics
title: Beta Admin Vibe Code Analytics API
breadcrumbs: [API, Beta Admin Vibe Code Analytics]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Admin Vibe Code Analytics API

Reference for the Beta Admin Vibe Code Analytics endpoints of the Mistral API, generated from the OpenAPI specification.

## Usage by workspace {#operation-get_workspace_stats_v1_admin_analytics_vibe_code_usage_by_workspace}

`GET /v1/admin/analytics/vibe/code/usage/by_workspace`

Get Vibe Code usage for a Workspace.

- Operation id: `get_workspace_stats_v1_admin_analytics_vibe_code_usage_by_workspace`
- Tag: beta/admin/vibe-code-analytics

### Parameters

- `start_time` (integer, required, in query) — Start of the queried window, as a Unix timestamp in seconds.
- `end_time` (integer, required, in query) — End of the queried window, as a Unix timestamp in seconds.
- `workspace_id` (string or null, optional, in query) — Workspace ID to filter results.

### Responses

- `200` — Successful Response (application/json, schema VibeWorkspaceStatsOUT)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Usage by organization {#operation-get_organization_stats_v1_admin_analytics_vibe_code_usage_by_organization}

`GET /v1/admin/analytics/vibe/code/usage/by_organization`

Get Vibe Code usage for the Organization.

- Operation id: `get_organization_stats_v1_admin_analytics_vibe_code_usage_by_organization`
- Tag: beta/admin/vibe-code-analytics

### Parameters

- `start_time` (integer, required, in query) — Start of the queried window, as a Unix timestamp in seconds.
- `end_time` (integer, required, in query) — End of the queried window, as a Unix timestamp in seconds.

### Responses

- `200` — Successful Response (application/json, schema VibeOrganizationStatsOUT)
- `422` — Validation Error (application/json, schema HTTPValidationError)
