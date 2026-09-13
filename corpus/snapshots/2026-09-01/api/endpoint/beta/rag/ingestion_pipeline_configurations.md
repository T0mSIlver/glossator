---
url: https://docs.mistral.ai/api/endpoint/beta/rag/ingestion_pipeline_configurations
title: Beta Rag Ingestion Pipeline Configurations API
breadcrumbs: [API, Beta Rag Ingestion Pipeline Configurations]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Rag Ingestion Pipeline Configurations API

Reference for the Beta Rag Ingestion Pipeline Configurations endpoints of the Mistral API, generated from the OpenAPI specification.

## List ingestion pipeline configurations {#operation-get_configs_v1_rag_ingestion_pipeline_configurations_get}

`GET /v1/rag/ingestion_pipeline_configurations`

For the current workspace, lists all of the registered ingestion pipeline configurations.

- Operation id: `get_configs_v1_rag_ingestion_pipeline_configurations_get`
- Tag: beta/rag/ingestion_pipeline_configurations

### Responses

- `200` — Successful Response (application/json)

## Register Config {#operation-register_config_v1_rag_ingestion_pipeline_configurations_put}

`PUT /v1/rag/ingestion_pipeline_configurations`

Register an ingestion configuration.

- Operation id: `register_config_v1_rag_ingestion_pipeline_configurations_put`
- Tag: beta/rag/ingestion_pipeline_configurations

### Request body

`application/json` (required), schema `CreateIngestionPipelineConfigurationRequest`

- `name` (string, required)
- `pipeline_composition` (object or null, optional)

### Responses

- `200` — Successful Response (application/json, schema IngestionPipelineConfiguration)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update Run Info {#operation-update_run_info_v1_rag_ingestion_pipeline_configurations_id_run_info_put}

`PUT /v1/rag/ingestion_pipeline_configurations/{id}/run_info`

- Operation id: `update_run_info_v1_rag_ingestion_pipeline_configurations__id__run_info_put`
- Tag: beta/rag/ingestion_pipeline_configurations

### Parameters

- `id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `UpdateRunInfo`

- `execution_time` (string (date-time), required)
- `chunks_count` (integer, required)

### Responses

- `200` — Successful Response (application/json, schema IngestionPipelineConfiguration)
- `422` — Validation Error (application/json, schema HTTPValidationError)
