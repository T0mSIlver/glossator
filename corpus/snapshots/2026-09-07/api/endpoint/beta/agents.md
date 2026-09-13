---
url: https://docs.mistral.ai/api/endpoint/beta/agents
title: Beta Agents API
breadcrumbs: [API, Beta Agents]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Agents API

Reference for the Beta Agents endpoints of the Mistral API, generated from the OpenAPI specification.

## List agent entities. {#operation-agents_api_v1_agents_list}

`GET /v1/agents`

Retrieve a list of agent entities sorted by creation time. Deprecated: some features such as agent sharing are not supported by this endpoint. Use the cursor-paginated `GET /v1/agents/pages` instead.

- Operation id: `agents_api_v1_agents_list`
- Tag: beta/agents
- Deprecated: yes

### Parameters

- `page` (integer, optional, in query) — Page number (0-indexed)
- `page_size` (integer, optional, in query) — Number of agents per page
- `deployment_chat` (boolean or null, optional, in query)
- `sources` (array of RequestSource or null, optional, in query)
- `name` (string or null, optional, in query) — Filter by agent name
- `search` (string or null, optional, in query) — Search agents by name or ID
- `id` (string or null, optional, in query)
- `metadata` (object, optional, in query)

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create a agent that can be used within a conversation. {#operation-agents_api_v1_agents_create}

`POST /v1/agents`

Create a new agent giving it instructions, tools, description. The agent is then available to be used as a regular assistant in a conversation or as part of an agent pool from which it can be used.

- Operation id: `agents_api_v1_agents_create`
- Tag: beta/agents

### Request body

`application/json` (required), schema `CreateAgentRequest`

- `instructions` (string or null, optional) — Instruction prompt the model will follow during the conversation.
- `tools` (array of object, optional) — List of tools which are available to the model during the conversation.
  - one of 7 (oneOf):
    - FunctionTool
    - WebSearchTool
    - WebSearchPremiumTool
    - CodeInterpreterTool
    - ImageGenerationTool
    - DocumentLibraryTool
    - CustomConnector
- `completion_args` (CompletionArgs, optional) — Completion arguments that will be used to generate assistant responses. Can be overridden at each message request.
  - `stop` (CompletionArgsStop, optional)
    - one of 3 (anyOf):
      - string
      - array of string
      - null
  - `presence_penalty` (number or null, optional)
  - `frequency_penalty` (number or null, optional)
  - `temperature` (number or null, optional)
  - `top_p` (number or null, optional)
  - `max_tokens` (integer or null, optional)
  - `random_seed` (integer or null, optional)
  - `prediction` (object or null, optional) — Enable users to specify an expected completion, optimizing response times by leveraging known or predictable content.
    - `type` (string, optional)
    - `content` (string, optional)
  - `response_format` (object or null, optional) — Specify the format that the model must output. By default it will use `{ "type": "text" }`. Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is in JSON. When using JSON mode you MUST also instruct the model to produce JSON yourself with a system or a user message. Setting to `{ "type": "json_schema" }` enables JSON schema mode, which guarantees the message the model generates is in JSON and follows the schema you provide.
    - `type` (enum: 'text', 'json_object', 'json_schema', optional)
    - `json_schema` (object or null, optional)
  - `tool_choice` (enum: 'auto', 'none', 'any', 'required', optional)
  - `reasoning_effort` (enum: 'none', 'minimal', 'low', 'medium', 'high', 'xhigh', optional)
- `guardrails` (array of GuardrailConfig or null, optional)
  - `block_on_error` (boolean, optional) — If true, return HTTP 403 and block request in the event of a server-side error
  - `moderation_llm_v1` (object or null, optional)
  - `moderation_llm_v2` (object or null, optional)
- `model` (string, required)
- `name` (string, required)
- `description` (string or null, optional)
- `handoffs` (array of string or null, optional)
- `metadata` (object or null, optional) — Custom type for metadata with embedded validation.
- `version_message` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema Agent)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List agent entities, cursor-paginated. {#operation-agents_api_v1_agents_list_pages}

`GET /v1/agents/pages`

Retrieve a page of agent entities. Unlike the deprecated `GET /v1/agents`, this endpoint paginates by opaque cursor and honors per-agent sharing, returning only agents the caller is authorized to see.

- Operation id: `agents_api_v1_agents_list_pages`
- Tag: beta/agents

### Parameters

- `page_size` (integer, optional, in query) — Number of agents per page
- `deployment_chat` (boolean or null, optional, in query)
- `sources` (array of RequestSource or null, optional, in query)
- `name` (string or null, optional, in query) — Filter by agent name
- `search` (string or null, optional, in query) — Search agents by name or ID
- `id` (string or null, optional, in query)
- `metadata` (object, optional, in query)
- `page_token` (string or null, optional, in query) — Opaque cursor from a previous response's next_page_token. When set, results page forward from the cursor.

### Responses

- `200` — Successful Response (application/json, schema AgentListPage)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Retrieve an agent entity. {#operation-agents_api_v1_agents_get}

`GET /v1/agents/{agent_id}`

Given an agent, retrieve an agent entity with its attributes. The agent_version parameter can be an integer version number or a string alias.

- Operation id: `agents_api_v1_agents_get`
- Tag: beta/agents

### Parameters

- `agent_id` (string, required, in path)
- `agent_version` (object, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema Agent)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete an agent entity. {#operation-agents_api_v1_agents_delete}

`DELETE /v1/agents/{agent_id}`

- Operation id: `agents_api_v1_agents_delete`
- Tag: beta/agents

### Parameters

- `agent_id` (string, required, in path)

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update an agent entity. {#operation-agents_api_v1_agents_update}

`PATCH /v1/agents/{agent_id}`

Update an agent attributes and create a new version.

- Operation id: `agents_api_v1_agents_update`
- Tag: beta/agents

### Parameters

- `agent_id` (string, required, in path)

### Request body

`application/json` (required), schema `UpdateAgentRequest`

- `instructions` (string or null, optional) — Instruction prompt the model will follow during the conversation.
- `tools` (array of object, optional) — List of tools which are available to the model during the conversation.
  - one of 7 (oneOf):
    - FunctionTool
    - WebSearchTool
    - WebSearchPremiumTool
    - CodeInterpreterTool
    - ImageGenerationTool
    - DocumentLibraryTool
    - CustomConnector
- `completion_args` (CompletionArgs, optional) — Completion arguments that will be used to generate assistant responses. Can be overridden at each message request.
  - `stop` (CompletionArgsStop, optional)
    - one of 3 (anyOf):
      - string
      - array of string
      - null
  - `presence_penalty` (number or null, optional)
  - `frequency_penalty` (number or null, optional)
  - `temperature` (number or null, optional)
  - `top_p` (number or null, optional)
  - `max_tokens` (integer or null, optional)
  - `random_seed` (integer or null, optional)
  - `prediction` (object or null, optional) — Enable users to specify an expected completion, optimizing response times by leveraging known or predictable content.
    - `type` (string, optional)
    - `content` (string, optional)
  - `response_format` (object or null, optional) — Specify the format that the model must output. By default it will use `{ "type": "text" }`. Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is in JSON. When using JSON mode you MUST also instruct the model to produce JSON yourself with a system or a user message. Setting to `{ "type": "json_schema" }` enables JSON schema mode, which guarantees the message the model generates is in JSON and follows the schema you provide.
    - `type` (enum: 'text', 'json_object', 'json_schema', optional)
    - `json_schema` (object or null, optional)
  - `tool_choice` (enum: 'auto', 'none', 'any', 'required', optional)
  - `reasoning_effort` (enum: 'none', 'minimal', 'low', 'medium', 'high', 'xhigh', optional)
- `guardrails` (array of GuardrailConfig or null, optional)
  - `block_on_error` (boolean, optional) — If true, return HTTP 403 and block request in the event of a server-side error
  - `moderation_llm_v1` (object or null, optional)
  - `moderation_llm_v2` (object or null, optional)
- `model` (string or null, optional)
- `name` (string or null, optional)
- `description` (string or null, optional)
- `handoffs` (array of string or null, optional)
- `deployment_chat` (boolean or null, optional)
- `metadata` (object or null, optional) — Custom type for metadata with embedded validation.
- `version_message` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema Agent)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update an agent version. {#operation-agents_api_v1_agents_update_version}

`PATCH /v1/agents/{agent_id}/version`

Switch the version of an agent.

- Operation id: `agents_api_v1_agents_update_version`
- Tag: beta/agents

### Parameters

- `agent_id` (string, required, in path)
- `version` (integer, required, in query)

### Responses

- `200` — Successful Response (application/json, schema Agent)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List all versions of an agent. {#operation-agents_api_v1_agents_list_versions}

`GET /v1/agents/{agent_id}/versions`

Retrieve all versions for a specific agent with full agent context. Supports pagination.

- Operation id: `agents_api_v1_agents_list_versions`
- Tag: beta/agents

### Parameters

- `agent_id` (string, required, in path)
- `page` (integer, optional, in query) — Page number (0-indexed)
- `page_size` (integer, optional, in query) — Number of versions per page

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Retrieve a specific version of an agent. {#operation-agents_api_v1_agents_get_version}

`GET /v1/agents/{agent_id}/versions/{version}`

Get a specific agent version by version number.

- Operation id: `agents_api_v1_agents_get_version`
- Tag: beta/agents

### Parameters

- `agent_id` (string, required, in path)
- `version` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema Agent)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List all aliases for an agent. {#operation-agents_api_v1_agents_list_version_aliases}

`GET /v1/agents/{agent_id}/aliases`

Retrieve all version aliases for a specific agent.

- Operation id: `agents_api_v1_agents_list_version_aliases`
- Tag: beta/agents

### Parameters

- `agent_id` (string, required, in path)

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create or update an agent version alias. {#operation-agents_api_v1_agents_create_or_update_alias}

`PUT /v1/agents/{agent_id}/aliases`

Create a new alias or update an existing alias to point to a specific version. Aliases are unique per agent and can be reassigned to different versions.

- Operation id: `agents_api_v1_agents_create_or_update_alias`
- Tag: beta/agents

### Parameters

- `agent_id` (string, required, in path)
- `alias` (string, required, in query)
- `version` (integer, required, in query)

### Responses

- `200` — Successful Response (application/json, schema AgentAliasResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete an agent version alias. {#operation-agents_api_v1_agents_delete_alias}

`DELETE /v1/agents/{agent_id}/aliases`

Delete an existing alias for an agent.

- Operation id: `agents_api_v1_agents_delete_alias`
- Tag: beta/agents

### Parameters

- `agent_id` (string, required, in path)
- `alias` (string, required, in query)

### Responses

- `204` — Successful Response
- `422` — Validation Error (application/json, schema HTTPValidationError)
