---
url: https://docs.mistral.ai/api/endpoint/beta/admin/analytics
title: Beta Admin Analytics API
breadcrumbs: [API, Beta Admin Analytics]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
openapi_md5: c28e3a674c73b4319d99305d173a6656
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Admin Analytics API

Reference for the Beta Admin Analytics endpoints of the Mistral API, generated from the OpenAPI specification.

## Get By User Stats {#operation-get_by_user_stats_api_admin_analytics_vibe_usage_by_user_stats}

`GET /api/admin/analytics/vibe/usage/by_user_stats`

Get Le Chat usage by user for a time range.

- Operation id: `get_by_user_stats_api_admin_analytics_vibe_usage_by_user_stats`
- Tag: beta/admin/analytics

### Parameters

- `start_time` (integer, required, in query) — Start of the queried window, as a Unix timestamp in seconds.
- `end_time` (integer, required, in query) — End of the queried window, as a Unix timestamp in seconds.

### Responses

- `200` — Successful Response (application/json, schema LeChatByUserStatsOUT)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get By Agent Stats {#operation-get_by_agent_stats_api_admin_analytics_vibe_usage_by_agent_stats}

`GET /api/admin/analytics/vibe/usage/by_agent_stats`

Get Le Chat usage by agent for a time range.

- Operation id: `get_by_agent_stats_api_admin_analytics_vibe_usage_by_agent_stats`
- Tag: beta/admin/analytics

### Parameters

- `start_time` (integer, required, in query) — Start of the queried window, as a Unix timestamp in seconds.
- `end_time` (integer, required, in query) — End of the queried window, as a Unix timestamp in seconds.

### Responses

- `200` — Successful Response (application/json, schema LeChatByAgentStatsOUT)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get By Time Stats {#operation-get_by_time_stats_api_admin_analytics_vibe_usage_by_time_stats}

`GET /api/admin/analytics/vibe/usage/by_time_stats`

Get Le Chat usage over time.

- Operation id: `get_by_time_stats_api_admin_analytics_vibe_usage_by_time_stats`
- Tag: beta/admin/analytics

### Parameters

- `start_time` (integer, required, in query) — Start of the queried window, as a Unix timestamp in seconds.
- `end_time` (integer, required, in query) — End of the queried window, as a Unix timestamp in seconds.
- `granularity` (enum: 'hour', 'day', 'week', 'month', optional, in query) — Time interval used to group usage results.

### Responses

- `200` — Successful Response (application/json, schema LeChatByTimeStatsOUT)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Workspace Stats {#operation-get_workspace_stats_api_admin_analytics_vibe_usage_by_workspace}

`GET /api/admin/analytics/vibe/usage/by_workspace`

Get Vibe usage for a Workspace.

- Operation id: `get_workspace_stats_api_admin_analytics_vibe_usage_by_workspace`
- Tag: beta/admin/analytics

### Parameters

- `start_time` (integer, required, in query) — Start of the queried window, as a Unix timestamp in seconds.
- `end_time` (integer, required, in query) — End of the queried window, as a Unix timestamp in seconds.
- `workspace_id` (string or null, optional, in query) — Workspace ID to filter results.

### Responses

- `200` — Successful Response (application/json, schema VibeWorkspaceStatsOUT)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Organization Stats {#operation-get_organization_stats_api_admin_analytics_vibe_usage_by_organization}

`GET /api/admin/analytics/vibe/usage/by_organization`

Get Vibe usage for the Organization.

- Operation id: `get_organization_stats_api_admin_analytics_vibe_usage_by_organization`
- Tag: beta/admin/analytics

### Parameters

- `start_time` (integer, required, in query) — Start of the queried window, as a Unix timestamp in seconds.
- `end_time` (integer, required, in query) — End of the queried window, as a Unix timestamp in seconds.

### Responses

- `200` — Successful Response (application/json, schema VibeOrganizationStatsOUT)
- `422` — Validation Error (application/json, schema HTTPValidationError)
