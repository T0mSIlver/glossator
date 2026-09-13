---
url: https://docs.mistral.ai/api/endpoint/deprecated/fine-tuning
title: Deprecated Fine Tuning API
breadcrumbs: [API, Deprecated Fine Tuning]
kind: api
locale: en
source_path: openapi.yaml
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
openapi_md5: 3c3c0d6b147730e71376c46aaca996cc
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Deprecated Fine Tuning API

Reference for the Deprecated Fine Tuning endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Fine Tuning Jobs {#operation-jobs_api_routes_fine_tuning_get_fine_tuning_jobs}

`GET /v1/fine_tuning/jobs`

Get a list of fine-tuning jobs for your organization and user.

- Operation id: `jobs_api_routes_fine_tuning_get_fine_tuning_jobs`
- Tag: deprecated/fine-tuning

### Parameters

- `page` (integer, optional, in query) — The page number of the results to be returned.
- `page_size` (integer, optional, in query) — The number of items to return per page.
- `model` (string or null, optional, in query) — The model name used for fine-tuning to filter on. When set, the other results are not displayed.
- `created_after` (string (date-time) or null, optional, in query) — The date/time to filter on. When set, the results for previous creation times are not displayed.
- `created_before` (string (date-time) or null, optional, in query)
- `created_by_me` (boolean, optional, in query) — When set, only return results for jobs created by the API caller. Other results are not displayed.
- `status` (enum: 'QUEUED', 'STARTED', 'VALIDATING', 'VALIDATED', 'RUNNING', 'FAILED_VALIDATION', 'FAILED', 'SUCCESS', 'CANCELLED', 'CANCELLATION_REQUESTED', optional, in query) — The current job state to filter on. When set, the other results are not displayed.
- `wandb_project` (string or null, optional, in query) — The Weights and Biases project to filter on. When set, the other results are not displayed.
- `wandb_name` (string or null, optional, in query) — The Weight and Biases run name to filter on. When set, the other results are not displayed.
- `suffix` (string or null, optional, in query) — The model suffix to filter on. When set, the other results are not displayed.

### Responses

- `200` — OK (application/json, schema JobsOut)

## Create Fine Tuning Job {#operation-jobs_api_routes_fine_tuning_create_fine_tuning_job}

`POST /v1/fine_tuning/jobs`

Create a new fine-tuning job, it will be queued for processing.

- Operation id: `jobs_api_routes_fine_tuning_create_fine_tuning_job`
- Tag: deprecated/fine-tuning

### Parameters

- `dry_run` (boolean or null, optional, in query) — * If `true` the job is not spawned, instead the query returns a handful of useful metadata for the user to perform sanity checks (see `LegacyJobMetadataOut` response). * Otherwise, the job is started and the query returns the job ID along with some of the input parameters (see `JobOut` response).

### Request body

`application/json` (required), schema `JobIn`

- `model` (string, required)
- `training_files` (array of TrainingFile, optional)
  - `file_id` (string (uuid), required)
  - `weight` (number, optional)
- `validation_files` (array of string (uuid) or null, optional) — A list containing the IDs of uploaded files that contain validation data. If you provide these files, the data is used to generate validation metrics periodically during fine-tuning. These metrics can be viewed in `checkpoints` when getting the status of a running fine-tuning job. The same data should not be present in both train and validation files.
- `suffix` (string or null, optional) — A string that will be added to your fine-tuning model name. For example, a suffix of "my-great-model" would produce a model name like `ft:open-mistral-7b:my-great-model:xxx...`
- `integrations` (array of object or null, optional) — A list of integrations to enable for your fine-tuning job.
- `auto_start` (boolean, optional) — This field will be required in a future release.
- `invalid_sample_skip_percentage` (number, optional)
- `job_type` (enum: 'completion', 'classifier', optional)
- `hyperparameters` (object, required)
  - one of 2 (anyOf):
    - CompletionTrainingParametersIn
      - `training_steps` (integer or null, optional) — The number of training steps to perform. A training step refers to a single update of the model weights during the fine-tuning process. This update is typically calculated using a batch of samples from the training dataset.
      - `learning_rate` (number, optional) — A parameter describing how much to adjust the pre-trained model's weights in response to the estimated error each time the weights are updated during the fine-tuning process.
      - `weight_decay` (number or null, optional) — (Advanced Usage) Weight decay adds a term to the loss function that is proportional to the sum of the squared weights. This term reduces the magnitude of the weights and prevents them from growing too large.
      - `warmup_fraction` (number or null, optional) — (Advanced Usage) A parameter that specifies the percentage of the total training steps at which the learning rate warm-up phase ends. During this phase, the learning rate gradually increases from a small value to the initial learning rate, helping to stabilize the training process and improve convergence. Similar to `pct_start` in [mistral-finetune](https://github.com/mistralai/mistral-finetune)
      - `epochs` (number or null, optional)
      - `seq_len` (integer or null, optional)
      - `fim_ratio` (number or null, optional)
    - ClassifierTrainingParametersIn
      - `training_steps` (integer or null, optional) — The number of training steps to perform. A training step refers to a single update of the model weights during the fine-tuning process. This update is typically calculated using a batch of samples from the training dataset.
      - `learning_rate` (number, optional) — A parameter describing how much to adjust the pre-trained model's weights in response to the estimated error each time the weights are updated during the fine-tuning process.
      - `weight_decay` (number or null, optional) — (Advanced Usage) Weight decay adds a term to the loss function that is proportional to the sum of the squared weights. This term reduces the magnitude of the weights and prevents them from growing too large.
      - `warmup_fraction` (number or null, optional) — (Advanced Usage) A parameter that specifies the percentage of the total training steps at which the learning rate warm-up phase ends. During this phase, the learning rate gradually increases from a small value to the initial learning rate, helping to stabilize the training process and improve convergence. Similar to `pct_start` in [mistral-finetune](https://github.com/mistralai/mistral-finetune)
      - `epochs` (number or null, optional)
      - `seq_len` (integer or null, optional)
- `repositories` (array of object or null, optional)
- `classifier_targets` (array of ClassifierTargetIn or null, optional)
  - `name` (string, required)
  - `labels` (array of string, required)
  - `weight` (number, optional)
  - `loss_function` (enum: 'single_class', 'multi_class', optional)

### Responses

- `200` — OK (application/json)

## Get Fine Tuning Job {#operation-jobs_api_routes_fine_tuning_get_fine_tuning_job}

`GET /v1/fine_tuning/jobs/{job_id}`

Get a fine-tuned job details by its UUID.

- Operation id: `jobs_api_routes_fine_tuning_get_fine_tuning_job`
- Tag: deprecated/fine-tuning

### Parameters

- `job_id` (string (uuid), required, in path) — The ID of the job to analyse.

### Responses

- `200` — OK (application/json)

## Cancel Fine Tuning Job {#operation-jobs_api_routes_fine_tuning_cancel_fine_tuning_job}

`POST /v1/fine_tuning/jobs/{job_id}/cancel`

Request the cancellation of a fine tuning job.

- Operation id: `jobs_api_routes_fine_tuning_cancel_fine_tuning_job`
- Tag: deprecated/fine-tuning

### Parameters

- `job_id` (string (uuid), required, in path) — The ID of the job to cancel.

### Responses

- `200` — OK (application/json)

## Start Fine Tuning Job {#operation-jobs_api_routes_fine_tuning_start_fine_tuning_job}

`POST /v1/fine_tuning/jobs/{job_id}/start`

Request the start of a validated fine tuning job.

- Operation id: `jobs_api_routes_fine_tuning_start_fine_tuning_job`
- Tag: deprecated/fine-tuning

### Parameters

- `job_id` (string (uuid), required, in path)

### Responses

- `200` — OK (application/json)
