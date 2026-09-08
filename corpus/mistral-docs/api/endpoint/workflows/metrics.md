---
url: https://docs.mistral.ai/api/endpoint/workflows/metrics
title: Workflows Metrics API
breadcrumbs: [API, Workflows Metrics]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Workflows Metrics API

Reference for the Workflows Metrics endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Workflow Metrics {#operation-get_workflow_metrics_v1_workflows_workflow_name_metrics_get}

`GET /v1/workflows/{workflow_name}/metrics`

Get comprehensive metrics for a specific workflow.

Args:
    workflow_name: The name of the workflow type to get metrics for
    start_time: Optional start time filter (ISO 8601 format)
    end_time: Optional end time filter (ISO 8601 format)

Returns:
    WorkflowMetrics: Dictionary containing metrics:
        - execution_count: Total number of executions
        - success_count: Number of successful executions
        - error_count: Number of failed/terminated executions
        - average_latency_ms: Average execution duration in milliseconds
        - retry_rate: Proportion of workflows with retries
        - latency_over_time: Time-series data of execution durations

Example:
    GET /v1/workflows/MyWorkflow/metrics
    GET /v1/workflows/MyWorkflow/metrics?start_time=2025-01-01T00:00:00Z
    GET /v1/workflows/MyWorkflow/metrics?start_time=2025-01-01T00:00:00Z&end_time=2025-12-31T23:59:59Z

- Operation id: `get_workflow_metrics_v1_workflows__workflow_name__metrics_get`
- Tag: workflows/metrics

### Parameters

- `workflow_name` (string, required, in path)
- `start_time` (string (date-time) or null, optional, in query) — Filter workflows started after this time (ISO 8601)
- `end_time` (string (date-time) or null, optional, in query) — Filter workflows started before this time (ISO 8601)

### Responses

- `200` — Successful Response (application/json, schema WorkflowMetrics)
- `422` — Validation Error (application/json, schema HTTPValidationError)
