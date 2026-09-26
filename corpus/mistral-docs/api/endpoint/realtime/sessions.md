---
url: https://docs.mistral.ai/api/endpoint/realtime/sessions
title: Realtime Sessions API
breadcrumbs: [API, Realtime Sessions]
kind: api
locale: en
source_path: openapi.yaml
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
openapi_md5: 71b15b9981e95fd9c3ab90aa80f2d1b6
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Realtime Sessions API

Reference for the Realtime Sessions endpoints of the Mistral API, generated from the OpenAPI specification.

## Create Client Session {#operation-create_client_session_v1_client_sessions_post}

`POST /v1/client/sessions`

Create a client session. Requires the `create_client_session` permission.

- Operation id: `create_client_session_v1_client_sessions_post`
- Tag: realtime/sessions

### Request body

`application/json` (required)

- Not documented.

### Responses

- `201` — Successful Response (application/json, schema CreateRealtimeSessionResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)
