# gen-0bce71927bac60e9 (single_page)

## Question

When querying the Admin API audit logs endpoint, what query parameters can I use to filter by actor, event, or target, and what is the default limit and sort order?

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Admin API audit logs query parameters for filtering by actor, event, or target", "max_hits": 5}
```

Result:

```
q: "Admin API audit logs query parameters for filtering by actor, event, or target"

[1] https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs | section: operation-users_api_admin_audit_logs_get_audit_logs/parameters
    Beta Admin Audit Logs API > Get Audit Logs > Parameters
    - `actor_type` (array of ActorType or null, optional, in query) — Actor types to include in the audit log results. - `event_type` (array of AuditLogEventType or null, optional, in query) — Event types to include in the audit log results. - `target_type` (array of TargetType or null, optional, in query) — Target resource types to include in the audit log results. - `actor_user_uuid` (string or null …
    cite: https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs#operation-users_api_admin_audit_logs_get_audit_logs

[2] https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | section: filters
    Audit logs reference > Filters
    Use these query parameters with the [Admin API audit logs endpoint](https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs). | Filter | Type | Default | Meaning | |---|---|---|---| | `actor_type` | `ActorType[]` or `null` | `None` | Actor types to include in the audit log results. | | `event_type` | `EventType[]` or `null` | `None` | Event types to include in the audit log results. | | `target …
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#:~:text=Use%20these%20query

[3] https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | section: audit-logs-reference
    Audit logs reference
    This reference lists the fields, filters, actor types, target types, and events that can appear in audit logs. Audit log entries are generated from the Admin API schema and dashboard audit log constants. Metadata fields vary by event and resource type.
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference

[4] https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | section: response-fields
    Audit logs reference > Response fields
    | Field | Type | Required | Meaning | |---|---|---|---| | `created_at` | `date-time string` | Yes | Time when the audit log entry was created. | | `actor_type` | `ActorType` | Yes | Type of actor that performed the action. | | `actor_metadata` | `object<string, string>` | Yes | Details about who performed the action. | | `event_type` | `EventType` | Yes | Type of action recorded in the audit log. …
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference

[5] https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | section: metadata-fields
    Audit logs reference > Metadata fields
    `actor_metadata`, `event_metadata`, and `target_metadata` are objects. They contain extra data about the actor, action, and affected resource. The raw API schema accepts string values. The dashboard can enrich known IDs into objects for display. | Key | Appears in | Meaning | |---|---|---| | `user_uuid` | Actor metadata | User ID for the human actor. The dashboard can enrich this value with `uuid` …
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs") to read hit 1 on its page
```

### 2. mistral_docs_search

```json
{"q": "Admin API audit logs default limit and sort order", "max_hits": 5}
```

Result:

```
q: "Admin API audit logs default limit and sort order"

[1] https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | section: filters
    Audit logs reference > Filters
    Use these query parameters with the [Admin API audit logs endpoint](https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs). | Filter | Type | Default | Meaning | |---|---|---|---| | `actor_type` | `ActorType[]` or `null` | `None` | Actor types to include in the audit log results. | | `event_type` | `EventType[]` or `null` | `None` | Event types to include in the audit log results. | | `target …
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#:~:text=Use%20these%20query

[2] https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs | section: operation-users_api_admin_audit_logs_get_audit_logs/parameters
    Beta Admin Audit Logs API > Get Audit Logs > Parameters
    - `actor_type` (array of ActorType or null, optional, in query) — Actor types to include in the audit log results. - `event_type` (array of AuditLogEventType or null, optional, in query) — Event types to include in the audit log results. - `target_type` (array of TargetType or null, optional, in query) — Target resource types to include in the audit log results. - `actor_user_uuid` (string or null …
    cite: https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs#operation-users_api_admin_audit_logs_get_audit_logs

[3] https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs | section: operation-users_api_admin_audit_logs_get_audit_logs
    Beta Admin Audit Logs API > Get Audit Logs
    `GET /v1/admin/audit-logs` List audit log entries for the Organization. - Operation id: `users_api_admin_audit_logs_get_audit_logs` - Tag: beta/admin/audit-logs
    cite: https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs#operation-users_api_admin_audit_logs_get_audit_logs

[4] https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | section: audit-logs-reference
    Audit logs reference
    This reference lists the fields, filters, actor types, target types, and events that can appear in audit logs. Audit log entries are generated from the Admin API schema and dashboard audit log constants. Metadata fields vary by event and resource type.
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference

[5] https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs | section: beta-admin-audit-logs-api
    Beta Admin Audit Logs API
    Reference for the Beta Admin Audit Logs endpoints of the Mistral API, generated from the OpenAPI specification.
    cite: https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference") to read hit 1 on its page
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference", "section": "filters"}
```

Result:

```
page: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference | "Audit logs reference" | section: filters

## section: filters
    Audit logs reference > Filters
    cite: https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#:~:text=Use%20these%20query
## Filters

Use these query parameters with the [Admin API audit logs endpoint](https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs).

| Filter | Type | Default | Meaning |
|---|---|---|---|
| `actor_type` | `ActorType[]` or `null` | `None` | Actor types to include in the audit log results. |
| `event_type` | `EventType[]` or `null` | `None` | Event types to include in the audit log results. |
| `target_type` | `TargetType[]` or `null` | `None` | Target resource types to include in the audit log results. |
| `actor_user_uuid` | `string` or `null` | `None` | Filter logs by the UUID of the user who performed the action. |
| `sort` | `ascending` or `descending` | `descending` | Sort order for audit log entries. |
| `after` | `date-time string` or `null` | `None` | Return audit log entries after this time. |
| `before` | `date-time string` or `null` | `None` | Return audit log entries before this time. |
| `limit` | `integer` | `20` | Maximum number of results to return. |

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference", section="actor-types") for the section after it
```

### 4. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs", "section": "operation-users_api_admin_audit_logs_get_audit_logs"}
```

Result:

```
page: https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs | "Beta Admin Audit Logs API" | section: operation-users_api_admin_audit_logs_get_audit_logs

## section: operation-users_api_admin_audit_logs_get_audit_logs
    Beta Admin Audit Logs API > Get Audit Logs
    cite: https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs#operation-users_api_admin_audit_logs_get_audit_logs
## Get Audit Logs {#operation-users_api_admin_audit_logs_get_audit_logs}

`GET /v1/admin/audit-logs`

List audit log entries for the Organization.

- Operation id: `users_api_admin_audit_logs_get_audit_logs`
- Tag: beta/admin/audit-logs

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs", section="operation-users_api_admin_audit_logs_get_audit_logs/parameters") for the section after it
```

## Answer

Here are the query parameters you can use to filter audit logs by **actor**, **event**, or **target**, along with the **default limit** and **sort order**:

---

### **Filtering Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| `actor_type` | `ActorType[]` or `null` | Filter by actor types (e.g., `user`, `service_account`). |
| `event_type` | `AuditLogEventType[]` or `null` | Filter by event types (e.g., `create`, `update`, `delete`). |
| `target_type` | `TargetType[]` or `null` | Filter by target resource types (e.g., `model`, `dataset`, `organization`). |
| `actor_user_uuid` | `string` or `null` | Filter logs by the UUID of the user who performed the action. |

---
### **Default Values**
| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `limit` | `20` | Maximum number of results returned per request. |
| `sort` | `descending` | Sort order for audit log entries (newest first). |

---
### **Additional Parameters**
You can also use:
- `after`: Return logs **after** a specific timestamp.
- `before`: Return logs **before** a specific timestamp.

For more details, refer to the [Admin API Audit Logs reference](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#filters)
[Filters](https://docs.mistral.ai/admin/monitor-comply/audit-logs/reference#:~:text=Use%20these%20query) and the [API endpoint documentation](https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs#operation-users_api_admin_audit_logs_get_audit_logs)
[Get Audit Logs](https://docs.mistral.ai/api/endpoint/beta/admin/audit-logs#operation-users_api_admin_audit_logs_get_audit_logs).

