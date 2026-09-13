---
url: https://docs.mistral.ai/api/endpoint/beta/workflows/deployments
title: Beta Workflows Deployments API
breadcrumbs: [API, Beta Workflows Deployments]
kind: api
locale: en
source_path: openapi.yaml
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
openapi_md5: 3c3c0d6b147730e71376c46aaca996cc
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Workflows Deployments API

Reference for the Beta Workflows Deployments endpoints of the Mistral API, generated from the OpenAPI specification.

## List Deployments {#operation-list_deployments_v1_workflows_deployments_get}

`GET /v1/workflows/deployments`

- Operation id: `list_deployments_v1_workflows_deployments_get`
- Tag: beta/workflows/deployments

### Parameters

- `active_only` (boolean, optional, in query)
- `workflow_name` (string or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema DeploymentListResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Deployment {#operation-get_deployment_v1_workflows_deployments_name_get}

`GET /v1/workflows/deployments/{name}`

- Operation id: `get_deployment_v1_workflows_deployments__name__get`
- Tag: beta/workflows/deployments

### Parameters

- `name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema DeploymentDetailResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)
