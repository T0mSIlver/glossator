---
url: https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs
title: Beta Admin Audit Logs API
breadcrumbs: [API, Beta Admin Audit Logs]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Beta Admin Audit Logs API

Reference for the Beta Admin Audit Logs endpoints of the Mistral API, generated from the OpenAPI specification.

## Get Audit Logs {#operation-users_api_admin_audit_logs_get_audit_logs}

`GET /v1/admin/audit-logs`

List audit log entries for the Organization.

- Operation id: `users_api_admin_audit_logs_get_audit_logs`
- Tag: beta/admin/audit-logs

### Parameters

- `actor_type` (array of ActorType or null, optional, in query) — Actor types to include in the audit log results.
- `event_type` (array of AuditLogEventType or null, optional, in query) — Event types to include in the audit log results.
- `target_type` (array of TargetType or null, optional, in query) — Target resource types to include in the audit log results.
- `actor_user_uuid` (string or null, optional, in query) — Filter logs by the UUID of the user who performed the action.
- `sort` (object, optional, in query) — Sort order for audit log entries.
- `after` (string (date-time) or null, optional, in query) — Return audit log entries after this time.
- `before` (string (date-time) or null, optional, in query) — Return audit log entries before this time.
- `limit` (integer, optional, in query) — Maximum number of results to return.

### Responses

- `200` — OK (application/json)
