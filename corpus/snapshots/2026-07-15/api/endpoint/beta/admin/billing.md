---
url: https://docs.mistral.ai/api/endpoint/beta/admin/billing
title: Beta Admin Billing API
breadcrumbs: [API, Beta Admin Billing]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
openapi_md5: c28e3a674c73b4319d99305d173a6656
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Admin Billing API

Reference for the Beta Admin Billing endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Rate Limits {#operation-users_api_admin_rate_limits_get_rate_limits}

`GET /api/admin/rate-limit`

- Operation id: `users_api_admin_rate_limits_get_rate_limits`
- Tag: beta/admin/billing

### Responses

- `200` — OK (application/json, schema RateLimitsOUT)

## Get Spend Limits {#operation-users_api_admin_spend_limits_get_spend_limits}

`GET /api/admin/spend-limit`

Get usage, rate, and job limits for the Organization.

- Operation id: `users_api_admin_spend_limits_get_spend_limits`
- Tag: beta/admin/billing

### Responses

- `200` — OK (application/json, schema LimitsOUT)

## Update Spend Limits {#operation-users_api_admin_spend_limits_update_spend_limits}

`POST /api/admin/spend-limit`

Update the Organization usage limit.

- Operation id: `users_api_admin_spend_limits_update_spend_limits`
- Tag: beta/admin/billing

### Request body

`application/json` (required), schema `NewUsageLimitIN`

- `amount` (integer, required) — New monthly usage limit amount.
- `no_monthly_limit` (boolean, optional) — Whether to remove the monthly usage limit.

### Responses

- `200` — OK (application/json, schema LimitsOUT)

## Get Usage {#operation-users_api_admin_usage_get_usage}

`GET /api/admin/usage`

Get usage and cost data for the Organization.

- Operation id: `users_api_admin_usage_get_usage`
- Tag: beta/admin/billing

### Parameters

- `month` (string or null, optional, in query) — Month to return usage for.
- `year` (string or null, optional, in query) — Year to return usage for.
- `workspace_id` (string (uuid) or null, optional, in query) — Workspace ID to filter results.
- `api_zone` (enum: 'global', 'us', 'eu', optional, in query) — Regional inference zone to filter results.

### Responses

- `200` — OK (application/json, schema UsageOUTJSON)
