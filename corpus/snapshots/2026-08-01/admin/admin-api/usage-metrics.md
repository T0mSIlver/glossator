---
url: https://docs.mistral.ai/admin/admin-api/usage-metrics
title: Usage metrics
breadcrumbs: [Admin, Admin API]
kind: doc
locale: en
source_path: src/content/en/docs/admin/admin-api/usage-metrics/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Usage metrics with the Admin API

The Admin API exposes two kinds of consumption data:

- **Billing usage**: cost and consumption for your Organization over a billing period.
- **Product analytics**: le Chat activity and Vibe Code usage metrics over a time range.

## Before you start {#before-you-start}

You need an Admin API key created in the Backoffice. Every request uses the base URL `https://api.mistral.ai/v1/admin` and the `x-api-key` header. See [Admin API authentication](https://docs.mistral.ai/admin/admin-api/authentication).

## Billing usage {#billing-usage}

Retrieve cost and consumption for the Organization. The `month`, `year`, and `workspace_id` parameters are optional. `month` and `year` are whole numbers, so `5` and `05` both work.

```bash
curl "https://api.mistral.ai/v1/admin/usage?month=5&year=2026" \
  -H "x-api-key: $ADMIN_API_KEY"
```

The response breaks consumption down by category (`chat`, `completion`, `ocr`, `audio`, `connectors`, `libraries_api`, `fine_tuning`, and `vibe_usage`), together with the period (`start_date`, `end_date`) and the `currency`.

## Spending and rate limits {#limits}

Read the current Organization limits:

```bash
# Spend limits
curl https://api.mistral.ai/v1/admin/spend-limit \
  -H "x-api-key: $ADMIN_API_KEY"

# Rate limits (requests per second and per-model token limits)
curl https://api.mistral.ai/v1/admin/rate-limit \
  -H "x-api-key: $ADMIN_API_KEY"
```

Set the Organization's monthly spending limit:

```bash
curl -X POST https://api.mistral.ai/v1/admin/spend-limit \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ADMIN_API_KEY" \
  -d '{"amount": 500, "no_monthly_limit": false}'
```

- `amount`: the monthly limit, as a whole number in your Organization's billing currency (`500` means 500, not 500 cents).
- `no_monthly_limit`: set to `true` to remove the cap.

See [Usage limits](https://docs.mistral.ai/admin/billing-usage/usage-limits) for the concept.

## le Chat analytics {#lechat-analytics}

The `/analytics/lechat` endpoints report le Chat messaging activity. All of them take `start_time` and `end_time` as Unix timestamps in seconds.

### By user {#lechat-by-user}

```bash
curl "https://api.mistral.ai/v1/admin/analytics/lechat/usage/by_user_stats?start_time=1704067200&end_time=1706745600" \
  -H "x-api-key: $ADMIN_API_KEY"
```

Returns, per user: message, file, image, and spreadsheet counts; unique conversations; unique agents; messages sent to agents; and the last message timestamp.

### By agent {#lechat-by-agent}

```bash
curl "https://api.mistral.ai/v1/admin/analytics/lechat/usage/by_agent_stats?start_time=1704067200&end_time=1706745600" \
  -H "x-api-key: $ADMIN_API_KEY"
```

Returns the same activity counts grouped by agent, plus the number of unique users per agent.

### Over time {#lechat-by-time}

Add `granularity` (`hour`, `day`, `week`, or `month`) to bucket the results.

```bash
curl "https://api.mistral.ai/v1/admin/analytics/lechat/usage/by_time_stats?start_time=1704067200&end_time=1706745600&granularity=day" \
  -H "x-api-key: $ADMIN_API_KEY"
```

Returns activity counts per time bucket, including unique users and unique agents.

## Vibe Code analytics {#vibe-code-analytics}

The `/analytics/vibe` endpoints report Vibe Code activity. They take `start_time` and `end_time` as Unix timestamps in seconds.

### By workspace {#vibe-by-workspace}

Pass `workspace_id` to scope the report to a single workspace, or omit it for all workspaces.

```bash
curl "https://api.mistral.ai/v1/admin/analytics/vibe/usage/by_workspace?start_time=1704067200&end_time=1706745600" \
  -H "x-api-key: $ADMIN_API_KEY"
```

Returns daily series for sessions (CLI, ACP, programmatic), active users, consumed tokens (input, output, and cached, per model), tool calls, and session durations.

### By Organization {#vibe-by-organization}

```bash
curl "https://api.mistral.ai/v1/admin/analytics/vibe/usage/by_organization?start_time=1704067200&end_time=1706745600" \
  -H "x-api-key: $ADMIN_API_KEY"
```

Returns daily series for next-edit suggestions (by outcome), next-edit active users, and modified lines of code.

## Next steps {#next-steps}

- [User provisioning](https://docs.mistral.ai/admin/admin-api/user-provisioning)

- [Usage limits](https://docs.mistral.ai/admin/billing-usage/usage-limits)
