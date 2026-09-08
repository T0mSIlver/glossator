---
url: https://docs.mistral.ai/api/endpoint/workflows/schedules
title: Workflows Schedules API
breadcrumbs: [API, Workflows Schedules]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Workflows Schedules API

Reference for the Workflows Schedules endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Schedules {#operation-get_schedules_v1_workflows_schedules_get}

`GET /v1/workflows/schedules`

- Operation id: `get_schedules_v1_workflows_schedules_get`
- Tag: workflows/schedules

### Parameters

- `workflow_name` (string or null, optional, in query) — Filter by exact workflow name
- `user_id` (string or null, optional, in query) — Filter by user ID. Pass 'current' to resolve to the authenticated user's ID.
- `status` (enum: 'active', 'paused', optional, in query) — Filter by schedule status: 'active' or 'paused'
- `search` (string or null, optional, in query) — Prefix search query for workflow name
- `page_size` (integer or null, optional, in query) — Number of items per page. Omitting this parameter fetches all results at once (deprecated — pass page_size to use pagination).
- `next_page_token` (string or null, optional, in query) — Token for the next page of results

### Responses

- `200` — Successful Response (application/json, schema WorkflowScheduleListResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Schedule Workflow {#operation-schedule_workflow_v1_workflows_schedules_post}

`POST /v1/workflows/schedules`

- Operation id: `schedule_workflow_v1_workflows_schedules_post`
- Tag: workflows/schedules

### Request body

`application/json` (required), schema `WorkflowScheduleRequest`

- `schedule` (ScheduleDefinition, required) — The schedule definition
  - `input` (Input, required) — Input to provide to the workflow when starting it.
  - `calendars` (array of ScheduleCalendar, optional) — Calendar-based specification of times.
    - `second` (array of ScheduleRange, optional)
    - `minute` (array of ScheduleRange, optional)
    - `hour` (array of ScheduleRange, optional)
    - `day_of_month` (array of ScheduleRange, optional)
    - `month` (array of ScheduleRange, optional)
    - `year` (array of ScheduleRange, optional)
    - `day_of_week` (array of ScheduleRange, optional)
    - `comment` (string or null, optional)
  - `intervals` (array of ScheduleInterval, optional) — Interval-based specification of times.
    - `every` (string (duration), required)
    - `offset` (string (duration) or null, optional)
  - `cron_expressions` (array of string, optional) — Cron-based specification of times.
  - `skip` (array of ScheduleCalendar, optional) — Set of calendar times to skip.
    - `second` (array of ScheduleRange, optional)
    - `minute` (array of ScheduleRange, optional)
    - `hour` (array of ScheduleRange, optional)
    - `day_of_month` (array of ScheduleRange, optional)
    - `month` (array of ScheduleRange, optional)
    - `year` (array of ScheduleRange, optional)
    - `day_of_week` (array of ScheduleRange, optional)
    - `comment` (string or null, optional)
  - `start_at` (string (date-time) or null, optional) — Time after which the first action may be run.
  - `end_at` (string (date-time) or null, optional) — Time after which no more actions will be run.
  - `jitter` (string (duration) or null, optional) — Jitter to apply each action. An action's scheduled time will be incremented by a random value between 0 and this value if present (but not past the next schedule).
  - `time_zone_name` (string or null, optional) — IANA time zone name, for example ``US/Central``.
  - `policy` (SchedulePolicy, optional) — Policy for the schedule.
    - `catchup_window_seconds` (integer, optional) — After a Temporal server is unavailable, amount of time in seconds in the past to execute missed actions.
    - `overlap` (enum: 1, 2, 3, 4, 5, 6, optional) — Policy controlling what to do when a workflow is already running.
    - `pause_on_failure` (boolean, optional) — Whether to pause the schedule after a workflow failure.
  - `max_executions` (integer or null, optional) — Maximum number of times this schedule will trigger a workflow execution. Once this limit is reached, no further executions are triggered automatically. null means unlimited.
  - `schedule_id` (string or null, optional) — Unique identifier for the schedule.
- `workflow_registration_id` (string (uuid) or null, optional) — The ID of the workflow registration to schedule
- `workflow_version_id` (string (uuid) or null, optional) — Deprecated: use workflow_registration_id
- `workflow_identifier` (string or null, optional) — The name or ID of the workflow to schedule
- `workflow_task_queue` (string or null, optional) — Deprecated. Use deployment_name instead.
- `schedule_id` (string or null, optional) — Allows you to specify a custom schedule ID. If not provided, a random ID will be generated.
- `deployment_name` (string or null, optional) — Name of the deployment to route this schedule to

### Responses

- `201` — Successful Response (application/json, schema WorkflowScheduleResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get Schedule {#operation-get_schedule_v1_workflows_schedules_schedule_id_get}

`GET /v1/workflows/schedules/{schedule_id}`

- Operation id: `get_schedule_v1_workflows_schedules__schedule_id__get`
- Tag: workflows/schedules

### Parameters

- `schedule_id` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema ScheduleDefinitionOutput)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Unschedule Workflow {#operation-unschedule_workflow_v1_workflows_schedules_schedule_id_delete}

`DELETE /v1/workflows/schedules/{schedule_id}`

- Operation id: `unschedule_workflow_v1_workflows_schedules__schedule_id__delete`
- Tag: workflows/schedules

### Parameters

- `schedule_id` (string, required, in path)

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update Schedule {#operation-update_schedule_v1_workflows_schedules_schedule_id_patch}

`PATCH /v1/workflows/schedules/{schedule_id}`

- Operation id: `update_schedule_v1_workflows_schedules__schedule_id__patch`
- Tag: workflows/schedules

### Parameters

- `schedule_id` (string, required, in path)

### Request body

`application/json` (required), schema `WorkflowScheduleUpdateRequest`

- `schedule` (PartialScheduleDefinition, required) — Partial schedule definition to update. Unset fields preserve existing values.
  - `input` (Input, optional) — Input to provide to the workflow when starting it.
  - `calendars` (array of ScheduleCalendar, optional) — Calendar-based specification of times.
    - `second` (array of ScheduleRange, optional)
    - `minute` (array of ScheduleRange, optional)
    - `hour` (array of ScheduleRange, optional)
    - `day_of_month` (array of ScheduleRange, optional)
    - `month` (array of ScheduleRange, optional)
    - `year` (array of ScheduleRange, optional)
    - `day_of_week` (array of ScheduleRange, optional)
    - `comment` (string or null, optional)
  - `intervals` (array of ScheduleInterval, optional) — Interval-based specification of times.
    - `every` (string (duration), required)
    - `offset` (string (duration) or null, optional)
  - `cron_expressions` (array of string, optional) — Cron-based specification of times.
  - `skip` (array of ScheduleCalendar, optional) — Set of calendar times to skip.
    - `second` (array of ScheduleRange, optional)
    - `minute` (array of ScheduleRange, optional)
    - `hour` (array of ScheduleRange, optional)
    - `day_of_month` (array of ScheduleRange, optional)
    - `month` (array of ScheduleRange, optional)
    - `year` (array of ScheduleRange, optional)
    - `day_of_week` (array of ScheduleRange, optional)
    - `comment` (string or null, optional)
  - `start_at` (string (date-time) or null, optional) — Time after which the first action may be run.
  - `end_at` (string (date-time) or null, optional) — Time after which no more actions will be run.
  - `jitter` (string (duration) or null, optional) — Jitter to apply each action. An action's scheduled time will be incremented by a random value between 0 and this value if present (but not past the next schedule).
  - `time_zone_name` (string or null, optional) — IANA time zone name, for example ``US/Central``.
  - `policy` (SchedulePolicy, optional) — Policy for the schedule.
    - `catchup_window_seconds` (integer, optional) — After a Temporal server is unavailable, amount of time in seconds in the past to execute missed actions.
    - `overlap` (enum: 1, 2, 3, 4, 5, 6, optional) — Policy controlling what to do when a workflow is already running.
    - `pause_on_failure` (boolean, optional) — Whether to pause the schedule after a workflow failure.
  - `max_executions` (integer or null, optional) — Maximum number of times this schedule will trigger a workflow execution. Once this limit is reached, no further executions are triggered automatically. null means unlimited.

### Responses

- `200` — Successful Response (application/json, schema WorkflowScheduleResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Pause Schedule {#operation-pause_schedule_v1_workflows_schedules_schedule_id_pause_post}

`POST /v1/workflows/schedules/{schedule_id}/pause`

- Operation id: `pause_schedule_v1_workflows_schedules__schedule_id__pause_post`
- Tag: workflows/schedules

### Parameters

- `schedule_id` (string, required, in path)

### Request body

`application/json`

- `note` (string or null, optional) — Optional note recorded in Temporal when pausing or resuming a schedule

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Resume Schedule {#operation-resume_schedule_v1_workflows_schedules_schedule_id_resume_post}

`POST /v1/workflows/schedules/{schedule_id}/resume`

- Operation id: `resume_schedule_v1_workflows_schedules__schedule_id__resume_post`
- Tag: workflows/schedules

### Parameters

- `schedule_id` (string, required, in path)

### Request body

`application/json`

- `note` (string or null, optional) — Optional note recorded in Temporal when pausing or resuming a schedule

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Trigger Schedule {#operation-trigger_schedule_v1_workflows_schedules_schedule_id_trigger_post}

`POST /v1/workflows/schedules/{schedule_id}/trigger`

- Operation id: `trigger_schedule_v1_workflows_schedules__schedule_id__trigger_post`
- Tag: workflows/schedules

### Parameters

- `schedule_id` (string, required, in path)

### Request body

`application/json`

- `overlap` (enum: 1, 2, 3, 4, 5, 6, optional) — Optional overlap policy override to use for the immediate trigger.

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)
