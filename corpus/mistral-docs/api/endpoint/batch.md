---
url: https://docs.mistral.ai/api/endpoint/batch
title: Batch API
breadcrumbs: [API, Batch]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Batch API

Reference for the Batch endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Batch Jobs {#operation-jobs_api_routes_batch_get_batch_jobs}

`GET /v1/batch/jobs`

Get a list of batch jobs for your organization and user.

- Operation id: `jobs_api_routes_batch_get_batch_jobs`
- Tag: batch

### Parameters

- `page` (integer, optional, in query)
- `page_size` (integer, optional, in query)
- `model` (string or null, optional, in query)
- `agent_id` (string or null, optional, in query)
- `metadata` (object or null, optional, in query)
- `created_after` (string (date-time) or null, optional, in query)
- `created_by_me` (boolean, optional, in query)
- `status` (array of BatchJobStatus or null, optional, in query)
- `order_by` (enum: 'created', '-created', optional, in query)

### Responses

- `200` — OK (application/json, schema ListBatchJobsResponse)

## Create Batch Job {#operation-jobs_api_routes_batch_create_batch_job}

`POST /v1/batch/jobs`

Create a new batch job, it will be queued for processing.

- Operation id: `jobs_api_routes_batch_create_batch_job`
- Tag: batch

### Request body

`application/json` (required), schema `CreateBatchJobRequest`

- `input_files` (array of string (uuid) or null, optional) — A list of `.jsonl` files for batch inference. Each line must be a JSON object with a `body` field containing the request payload: ```json {"custom_id": "0", "body": {"max_tokens": 100, "messages": [{"role": "user", "content": "What is the best French cheese?"}]}} {"custom_id": "1", "body": {"max_tokens": 100, "messages": [{"role": "user", "content": "What is the best French wine?"}]}} ```
- `requests` (array of BatchRequest or null, optional)
  - `custom_id` (string or null, optional)
  - `body` (object, required)
- `endpoint` (enum: '/v1/chat/completions', '/v1/embeddings', '/v1/fim/completions', '/v1/moderations', '/v1/chat/moderations', '/v1/ocr', '/v1/classifications', '/v1/chat/classifications', '/v1/conversations', '/v1/audio/transcriptions', required) — The endpoint to be used for batch inference.
- `model` (string or null, optional) — The model to be used for batch inference.
- `agent_id` (string or null, optional) — In case you want to use a specific agent from the **deprecated** agents api for batch inference, you can specify the agent ID here.
- `metadata` (object or null, optional) — The metadata of your choice to be associated with the batch inference job.
- `timeout_hours` (integer, optional) — The timeout in hours for the batch inference job.

### Responses

- `200` — OK (application/json, schema BatchJob)

## Get Batch Job {#operation-jobs_api_routes_batch_get_batch_job}

`GET /v1/batch/jobs/{job_id}`

Get a batch job details by its UUID.

Args:
    inline: If True, return results inline in the response.

- Operation id: `jobs_api_routes_batch_get_batch_job`
- Tag: batch

### Parameters

- `job_id` (string (uuid), required, in path)
- `inline` (boolean or null, optional, in query)

### Responses

- `200` — OK (application/json, schema BatchJob)

## Delete Batch Job {#operation-jobs_api_routes_batch_delete_batch_job}

`DELETE /v1/batch/jobs/{job_id}`

Request the deletion of a batch job.

- Operation id: `jobs_api_routes_batch_delete_batch_job`
- Tag: batch

### Parameters

- `job_id` (string (uuid), required, in path)

### Responses

- `200` — OK (application/json, schema DeleteBatchJobResponse)

## Cancel Batch Job {#operation-jobs_api_routes_batch_cancel_batch_job}

`POST /v1/batch/jobs/{job_id}/cancel`

Request the cancellation of a batch job.

- Operation id: `jobs_api_routes_batch_cancel_batch_job`
- Tag: batch

### Parameters

- `job_id` (string (uuid), required, in path)

### Responses

- `200` — OK (application/json, schema BatchJob)
