---
url: https://docs.mistral.ai/studio/observability/traces/explorer
title: Explore traces
breadcrumbs: [Studio, Observability, Distributed tracing]
kind: doc
locale: en
source_path: src/content/en/docs/studio/observability/traces/explorer/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
hidden: true
---

# Explore traces

The Trace Explorer is where you search, filter, and inspect every trace flowing through your AI applications. It's available in Studio at [Observability → Traces](https://console.mistral.ai/observability/traces).

Before you can explore traces, your application needs to be instrumented. See [Send traces](https://docs.mistral.ai/studio/observability/traces/send-traces) for setup instructions.

## What traces contain {#what-traces-contain}

Every trace is a tree of spans. Each span represents one operation in the execution chain.

| Field | Description |
|-------|-------------|
| **Trace ID** | Unique identifier for the full execution chain |
| **Spans** | Individual operations: LLM calls, tool calls, workflow steps |
| **Duration** | Time taken for each span and the total trace |
| **Token counts** | Input and output tokens per LLM call |
| **Status** | Success or error, with error messages when applicable |
| **Source** | Which product generated the trace (SDK, Workflows, Vibe Code CLI, Vibe Code Web, Vibe Work) |
| **Tags** | Custom tags from SDK usage, plus automatic metadata such as model name |

Click any trace in the list to open the span tree. Expand individual spans to inspect inputs, outputs, latency, and token usage at each step.

## Search and filter {#searching-traces}

Explorer accepts a **search expression language**: write conditions on trace fields and combine them with `AND`, `OR`, and `NOT`.

### Operators {#operators}

| Category | Operators | Example |
|----------|-----------|---------|
| Comparison | `=`, `!=`, `<`, `<=`, `>`, `>=` | `duration_ns > 5000000000` |
| Pattern matching | `LIKE`, `ILIKE`, `NOT LIKE` | `service_name LIKE '%agent%'` |
| Substring | `CONTAINS`, `NOT CONTAINS` | `service_name CONTAINS 'sdk'` |
| Regex | `REGEXP`, `NOT REGEXP` | `service_name REGEXP '^my-'` |
| Range | `BETWEEN ... AND ...` | `duration_ns BETWEEN 1000000 AND 5000000000` |
| List | `IN (...)`, `NOT IN (...)` | `status_code IN ('Error', 'Ok')` |
| Null check | `EXISTS`, `NOT EXISTS` | `error_message EXISTS` |
| Boolean | `AND`, `OR`, `NOT`, `()` | `status_code = 'Error' AND duration_ns > 1000000` |

### Available fields {#available-fields}

| Field | Type | Description |
|-------|------|-------------|
| `service_name` | string | Name of the service that produced the trace |
| `status_code` | string | Trace status: `Ok` or `Error` |
| `duration_ns` | number | Total trace duration in nanoseconds |
| `error_message` | string | Error message if the trace failed |
| `start_time` | timestamp | When the trace started (ISO 8601) |
| `models_used` | array | Models called within the trace |
| `span_attributes['key']` | map value | Any span attribute, using bracket syntax |

### Span attribute queries {#span-attribute-queries}

Use bracket syntax to filter on any OpenTelemetry span attribute:

```
span_attributes['gen_ai.request.model'] CONTAINS 'mistral-large'
span_attributes['gen_ai.operation.name'] = 'chat'
span_attributes['custom.tag'] EXISTS
```

### Array fields {#array-fields}

For array fields like `models_used`:

| Function | Example |
|----------|---------|
| `CONTAINS` | `models_used CONTAINS 'mistral-medium-latest'` |
| `has(field, value)` | `has(models_used, 'mistral-medium-latest')` |
| `hasany(field, [values])` | `hasany(models_used, ['mistral-large-latest', 'mistral-small-latest'])` |
| `hasall(field, [values])` | `hasall(models_used, ['mistral-large-latest', 'mistral-small-latest'])` |

### Common examples {#common-examples}

```
# All failed traces from a specific service
service_name = 'my-agent' AND status_code = 'Error'

# Traces slower than 5 seconds
duration_ns > 5000000000

# Traces using a specific model
span_attributes['gen_ai.request.model'] CONTAINS 'mistral-large'
```

## Query traces programmatically {#api-access}

All trace data is accessible via the REST API. The endpoints are documented in the API reference:

- [Traces](https://docs.mistral.ai/api/endpoint/beta/observability/traces): search traces, get a single trace, list fields and field options.
- [Spans](https://docs.mistral.ai/api/endpoint/beta/observability/spans): list spans for a trace, query span evaluations.

## Access {#access}

Reading traces requires an Enterprise organization and one of the following roles:

| Role | Access |
|------|--------|
| Org Admin | All traces across all workspaces |
| Workspace Admin | All traces in their workspace |
| Observability Viewer | All traces in their workspace (read-only) |

A Workspace Admin or Org Admin can assign the Observability Viewer role to grant read-only access without admin privileges.

## FAQ {#faq}

### I enabled the SDK but don't see any traces {#i-enabled-the-sdk-but-dont-see-any-traces}

Make sure you called `configure_telemetry(client)` before making any API calls. Make at least one request, then wait a few seconds. Check that your workspace has Observability enabled and that you have one of the required roles.

### My search returns no results {#my-search-returns-no-results}

Start by removing all conditions except a time range, then add filters one at a time. A common mistake is filtering on `status_code = 'Error'` when most traces are successful. Try removing that condition first.

### I can't see the Trace Explorer in Studio {#i-cant-see-the-trace-explorer-in-studio}

Explorer requires the Org Admin, Workspace Admin, or Observability Viewer role in an Enterprise organization. Check with your workspace admin if you don't have access.
