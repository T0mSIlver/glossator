---
url: https://docs.mistral.ai/api/endpoint/beta/workflows/schedules
title: Beta Workflows Schedules API
breadcrumbs: [API, Beta Workflows Schedules]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
openapi_md5: bdb780fc2046eadc8ab1125990abd435
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Workflows Schedules API

Reference for the Beta Workflows Schedules endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Schedules {#operation-get_schedules_v1_workflows_schedules_get}

`GET /v1/workflows/schedules`

- Operation id: `get_schedules_v1_workflows_schedules_get`
- Tag: beta/workflows/schedules

### Responses

- `200` — Successful Response (application/json, schema WorkflowScheduleListResponse)

## Schedule Workflow {#operation-schedule_workflow_v1_workflows_schedules_post}

`POST /v1/workflows/schedules`

- Operation id: `schedule_workflow_v1_workflows_schedules_post`
- Tag: beta/workflows/schedules

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
  - `jitter` (string (duration) or null, optional) — Jitter to apply each action.

    An action's scheduled time will be incremented by a random value between 0
    and this value if present (but not past the next schedule).

  - `time_zone_name` (string or null, optional) — IANA time zone name, for example ``US/Central``.
  - `policy` (SchedulePolicy, optional) — Policy for the schedule.
    - `catchup_window_seconds` (integer, optional) — After a Temporal server is unavailable, amount of time in seconds in the past to execute missed actions.
    - `overlap` (enum: 1, 2, 3, 4, 5, 6, optional) — Policy controlling what to do when a workflow is already running.
    - `pause_on_failure` (boolean, optional) — Whether to pause the schedule after a workflow failure.
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

## Unschedule Workflow {#operation-unschedule_workflow_v1_workflows_schedules_schedule_id_delete}

`DELETE /v1/workflows/schedules/{schedule_id}`

- Operation id: `unschedule_workflow_v1_workflows_schedules__schedule_id__delete`
- Tag: beta/workflows/schedules

### Parameters

- `schedule_id` (string, required, in path)

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)
