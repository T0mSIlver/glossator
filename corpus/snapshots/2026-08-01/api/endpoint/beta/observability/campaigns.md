---
url: https://docs.mistral.ai/api/endpoint/beta/observability/campaigns
title: Beta Observability Campaigns API
breadcrumbs: [API, Beta Observability Campaigns]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
openapi_md5: 1ae55facb05ef4d5bf803842b3033337
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Observability Campaigns API

Reference for the Beta Observability Campaigns endpoints of the Mistral API, generated from the OpenAPI specification.

## Get all campaigns {#operation-get_campaigns_v1_observability_campaigns_get}

`GET /v1/observability/campaigns`

- Operation id: `get_campaigns_v1_observability_campaigns_get`
- Tag: beta/observability/campaigns

### Parameters

- `page_size` (integer, optional, in query)
- `page` (integer, optional, in query)
- `q` (string or null, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema ListCampaignsResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Create and start a new campaign {#operation-create_campaign_v1_observability_campaigns_post}

`POST /v1/observability/campaigns`

- Operation id: `create_campaign_v1_observability_campaigns_post`
- Tag: beta/observability/campaigns

### Request body

`application/json` (required), schema `CreateCampaignRequest`

- `search_params` (FilterPayload, required)
  - `filters` (object, required)
    - one of 3 (anyOf):
      - FilterGroup
      - FilterCondition
      - null
- `judge_id` (string (uuid), required)
- `name` (string, required)
- `description` (string, required)
- `max_nb_events` (integer, required)

### Responses

- `201` — Successful Response (application/json, schema Campaign)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get campaign by id {#operation-get_campaign_by_id_v1_observability_campaigns_campaign_id_get}

`GET /v1/observability/campaigns/{campaign_id}`

- Operation id: `get_campaign_by_id_v1_observability_campaigns__campaign_id__get`
- Tag: beta/observability/campaigns

### Parameters

- `campaign_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema Campaign)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Delete a campaign {#operation-delete_campaign_v1_observability_campaigns_campaign_id_delete}

`DELETE /v1/observability/campaigns/{campaign_id}`

- Operation id: `delete_campaign_v1_observability_campaigns__campaign_id__delete`
- Tag: beta/observability/campaigns

### Parameters

- `campaign_id` (string (uuid), required, in path)

### Responses

- `204` — Successful Response
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get campaign status by campaign id {#operation-get_campaign_status_by_id_v1_observability_campaigns_campaign_id_status_get}

`GET /v1/observability/campaigns/{campaign_id}/status`

- Operation id: `get_campaign_status_by_id_v1_observability_campaigns__campaign_id__status_get`
- Tag: beta/observability/campaigns

### Parameters

- `campaign_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema FetchCampaignStatusResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)

## Get event ids that were selected by the given campaign {#operation-get_campaign_selected_events_v1_observability_campaigns_campaign_id_selected_events_get}

`GET /v1/observability/campaigns/{campaign_id}/selected-events`

- Operation id: `get_campaign_selected_events_v1_observability_campaigns__campaign_id__selected_events_get`
- Tag: beta/observability/campaigns

### Parameters

- `campaign_id` (string (uuid), required, in path)
- `page_size` (integer, optional, in query)
- `page` (integer, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema ListCampaignSelectedEventsResponse)
- `400` — Bad Request - Invalid request parameters or data (application/json, schema ObservabilityError)
- `404` — Not Found - Resource does not exist (application/json, schema ObservabilityError)
- `408` — Request Timeout - Operation timed out (application/json, schema ObservabilityError)
- `409` — Conflict - Resource conflict (application/json, schema ObservabilityError)
- `422` — Unprocessable Entity - Validation error (application/json, schema ObservabilityError)
