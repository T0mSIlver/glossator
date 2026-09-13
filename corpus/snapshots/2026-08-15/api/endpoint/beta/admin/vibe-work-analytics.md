---
url: https://docs.mistral.ai/api/endpoint/beta/admin/vibe-work-analytics
title: Beta Admin Vibe Work Analytics API
breadcrumbs: [API, Beta Admin Vibe Work Analytics]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Admin Vibe Work Analytics API

Reference for the Beta Admin Vibe Work Analytics endpoints of the Mistral API, generated from the OpenAPI specification.

## Usage by user {#operation-get_by_user_stats_v1_admin_analytics_vibe_work_usage_by_user_stats}

`GET /v1/admin/analytics/vibe/work/usage/by_user_stats`

Get Vibe Work usage by user for a time range.

- Operation id: `get_by_user_stats_v1_admin_analytics_vibe_work_usage_by_user_stats`
- Tag: beta/admin/vibe-work-analytics

### Parameters

- `start_time` (integer, required, in query) — Start of the queried window, as a Unix timestamp in seconds.
- `end_time` (integer, required, in query) — End of the queried window, as a Unix timestamp in seconds.

### Responses

- `200` — Successful Response (application/json, schema VibeWorkByUserStatsOUT)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Usage by agent {#operation-get_by_agent_stats_v1_admin_analytics_vibe_work_usage_by_agent_stats}

`GET /v1/admin/analytics/vibe/work/usage/by_agent_stats`

Get Vibe Work usage by agent for a time range.

- Operation id: `get_by_agent_stats_v1_admin_analytics_vibe_work_usage_by_agent_stats`
- Tag: beta/admin/vibe-work-analytics

### Parameters

- `start_time` (integer, required, in query) — Start of the queried window, as a Unix timestamp in seconds.
- `end_time` (integer, required, in query) — End of the queried window, as a Unix timestamp in seconds.

### Responses

- `200` — Successful Response (application/json, schema VibeWorkByAgentStatsOUT)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Usage over time {#operation-get_by_time_stats_v1_admin_analytics_vibe_work_usage_by_time_stats}

`GET /v1/admin/analytics/vibe/work/usage/by_time_stats`

Get Vibe Work usage over time.

- Operation id: `get_by_time_stats_v1_admin_analytics_vibe_work_usage_by_time_stats`
- Tag: beta/admin/vibe-work-analytics

### Parameters

- `start_time` (integer, required, in query) — Start of the queried window, as a Unix timestamp in seconds.
- `end_time` (integer, required, in query) — End of the queried window, as a Unix timestamp in seconds.
- `granularity` (enum: 'hour', 'day', 'week', 'month', optional, in query) — Time interval used to group usage results.

### Responses

- `200` — Successful Response (application/json, schema VibeWorkByTimeStatsOUT)
- `422` — Validation Error (application/json, schema HTTPValidationError)
