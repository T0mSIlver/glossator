---
url: https://docs.mistral.ai/api/endpoint/beta/admin/scim
title: Beta Admin Scim API
breadcrumbs: [API, Beta Admin Scim]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: /tmp/claude-1000/-home-dev-work-glossator--claude-worktrees-valiant-hugging-codd/6d539ee6-ce5b-457d-adc5-7e53a6f3c066/scratchpad/corpus/live-openapi.yaml
---

# Beta Admin Scim API

Reference for the Beta Admin Scim endpoints of the Mistral API, generated from the OpenAPI specification.

## Trigger Scim Sync {#operation-users_api_admin_scim_sync_trigger_scim_sync}

`POST /v1/admin/scim/sync`

Trigger an on-demand SCIM synchronization for the Organization.

Requires SAML authentication to be enabled and the Organization to be in SCIM
user provisioning mode. A dry run previews every change without applying it;
a real run applies the categories selected in `sync_config`. Only one run may
be active at a time — a conflicting request returns the already-active run.

- Operation id: `users_api_admin_scim_sync_trigger_scim_sync`
- Tag: beta/admin/scim

### Request body

`application/json` (required), schema `AdminScimSyncTriggerIN`

- `dry_run` (boolean, optional) — Preview all synchronization changes without applying them.
- `sync_config` (object or null, optional) — Categories to synchronize. Required when dry_run is false; ignored for dry runs.
  - `delete_missing_groups` (boolean, optional) — Delete Organization groups that are absent from the SCIM provider.
  - `deprovision_users` (boolean, optional) — Remove Organization users that are inactive or absent from the SCIM provider.
  - `sync_users` (boolean, required) — Add users found in the SCIM provider to the Organization.
  - `sync_groups` (boolean, required) — Synchronize group metadata from the SCIM provider.
  - `sync_memberships` (boolean, required) — Synchronize additions and removals of users in SCIM groups.

### Responses

- `202` — Accepted (application/json, schema AdminScimSyncTriggerOUT)
- `409` — Conflict (application/json, schema AdminScimSyncActiveRunOUT)

## Get Scim Sync Run {#operation-users_api_admin_scim_sync_get_scim_sync_run}

`GET /v1/admin/scim/sync/{run_id}`

Retrieve an on-demand SCIM synchronization run for the Organization.

Returns the run's lifecycle status along with the preview or result summary
once the synchronization plan has been built.

- Operation id: `users_api_admin_scim_sync_get_scim_sync_run`
- Tag: beta/admin/scim

### Parameters

- `run_id` (string (uuid), required, in path) — Identifier of the SCIM synchronization run.

### Responses

- `200` — OK (application/json, schema AdminScimSyncRunOUT)
