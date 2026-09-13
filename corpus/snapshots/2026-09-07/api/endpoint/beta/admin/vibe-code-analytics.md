---
url: https://docs.mistral.ai/api/endpoint/beta/admin/vibe-code-analytics
title: Beta Admin Vibe Code Analytics API
breadcrumbs: [API, Beta Admin Vibe Code Analytics]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
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
