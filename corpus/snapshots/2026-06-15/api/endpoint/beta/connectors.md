---
url: https://docs.mistral.ai/api/endpoint/beta/connectors
title: Beta Connectors API
breadcrumbs: [API, Beta Connectors]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
openapi_md5: bdb780fc2046eadc8ab1125990abd435
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Beta Connectors API

Reference for the Beta Connectors endpoints of the Mistral API, generated from the OpenAPI specification.

## List all connectors. {#operation-connector_list_v1}

`GET /v1/connectors`

List all your custom connectors with keyset pagination and filters.

- Operation id: `connector_list_v1`
- Tag: beta/connectors

### Parameters

- `query_filters` (object, optional, in query)
- `cursor` (string or null, optional, in query)
- `page_size` (integer, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema PaginatedConnectors)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create a new connector. {#operation-connector_create_v1}

`POST /v1/connectors`

Create a new MCP connector. You can customize its visibility, url and auth type.

- Operation id: `connector_create_v1`
- Tag: beta/connectors

### Request body

`application/json` (required), schema `ConnectorMCPCreate`

- `name` (string, required) — The name of the connector. Should be 64 char length maximum, alphanumeric, only underscores/dashes.
- `description` (string, required) — The description of the connector.
- `icon_url` (string or null, optional) — The optional url of the icon you want to associate to the connector.
- `visibility` (enum: 'shared_global', 'shared_org', 'shared_workspace', 'private', optional) — Visibility of the connector. Use 'shared_workspace' for workspace scoped connectors, or 'private' for private connectors.
- `server` (string (uri), required) — The url of the MCP server.
- `headers` (object or null, optional) — Optional organization-level headers to be sent with the request to the mcp server.
- `auth_data` (object or null, optional) — Optional additional authentication data for the connector.
  - `client_id` (string, required)
  - `client_secret` (string, required)
- `system_prompt` (string or null, optional) — Optional system prompt for the connector.

### Responses

- `201` — Successful Response (application/json, schema Connector)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get the auth URL for a connector. {#operation-connector_get_auth_url_v1}

`GET /v1/connectors/{connector_id_or_name}/auth_url`

Get the OAuth2 authorization URL for a connector to initiate user authentication.

- Operation id: `connector_get_auth_url_v1`
- Tag: beta/connectors

### Parameters

- `app_return_url` (string or null, optional, in query)
- `credentials_name` (string or null, optional, in query)
- `connector_id_or_name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema AuthUrlResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Call Connector Tool {#operation-connector_call_tool_v1}

`POST /v1/connectors/{connector_id_or_name}/tools/{tool_name}/call`

Call a tool on an MCP connector.

- Operation id: `connector_call_tool_v1`
- Tag: beta/connectors

### Parameters

- `tool_name` (string, required, in path)
- `credentials_name` (string or null, optional, in query)
- `connector_id_or_name` (string, required, in path)

### Request body

`application/json` (required), schema `MCPToolCallRequest`

- `arguments` (object, optional)

### Responses

- `200` — Successful Response (application/json, schema MCPToolCallResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List tools for a connector. {#operation-connector_list_tools_v1}

`GET /v1/connectors/{connector_id_or_name}/tools`

List all tools available for an MCP connector.

- Operation id: `connector_list_tools_v1`
- Tag: beta/connectors

### Parameters

- `page` (integer, optional, in query)
- `page_size` (integer, optional, in query)
- `refresh` (boolean, optional, in query)
- `pretty` (boolean, optional, in query) — Return a simplified payload with only name, description, annotations, and a compact inputSchema.
- `credentials_name` (string or null, optional, in query)
- `connector_id_or_name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get authentication methods for a connector. {#operation-connector_get_authentication_methods_v1}

`GET /v1/connectors/{connector_id_or_name}/authentication_methods`

Get the authentication schema for a connector. Returns the list of supported authentication methods and their required headers.

- Operation id: `connector_get_authentication_methods_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json)

## List organization credentials for a connector. {#operation-connector_list_organization_credentials_v1}

`GET /v1/connectors/{connector_id_or_name}/organization/credentials`

List all credentials configured at the organization level for a given connector.

- Operation id: `connector_list_organization_credentials_v1`
- Tag: beta/connectors

### Parameters

- `auth_type` (enum: 'oauth2', 'bearer', 'none', optional, in query)
- `fetch_default` (boolean, optional, in query)
- `connector_id_or_name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema CredentialsResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create or update organization credentials for a connector. {#operation-connector_create_or_update_organization_credentials_v1}

`POST /v1/connectors/{connector_id_or_name}/organization/credentials`

Create or update credentials at the organization level for a given connector.

- Operation id: `connector_create_or_update_organization_credentials_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (string, required, in path)

### Request body

`application/json` (required), schema `CredentialsCreateOrUpdate`

- `name` (string, required) — Name of the credentials. Use this name to access or modify your credentials.
- `is_default` (boolean or null, optional) — Controls whether this credential is the default for its auth method. On creation: if no credential exists yet for this auth method, the credential is automatically set as default when is_default is true or omitted; setting is_default to false is rejected because a default must exist. If other credentials already exist, setting is_default to true promotes this credential (demoting the previous default); false or omitted creates it as non-default. On update: true promotes this credential, false is rejected if it is currently the default (promote another credential first), omitted leaves the default status unchanged.
- `credentials` (object or null, optional) — The credential data (headers, bearer_token).
  - `oauth` (object or null, optional)
    - `access_token` (string, required)
    - `token_type` (string, optional)
    - `expires_in` (integer or null, optional)
    - `scope` (string or null, optional)
    - `refresh_token` (string or null, optional)
    - `expires_at` (string (date-time) or null, optional)
  - `headers` (object or null, optional)
  - `bearer_token` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List workspace credentials for a connector. {#operation-connector_list_workspace_credentials_v1}

`GET /v1/connectors/{connector_id_or_name}/workspace/credentials`

List all credentials configured at the workspace level for a given connector.

- Operation id: `connector_list_workspace_credentials_v1`
- Tag: beta/connectors

### Parameters

- `auth_type` (enum: 'oauth2', 'bearer', 'none', optional, in query)
- `fetch_default` (boolean, optional, in query)
- `connector_id_or_name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema CredentialsResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create or update workspace credentials for a connector. {#operation-connector_create_or_update_workspace_credentials_v1}

`POST /v1/connectors/{connector_id_or_name}/workspace/credentials`

Create or update credentials at the workspace level for a given connector.

- Operation id: `connector_create_or_update_workspace_credentials_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (string, required, in path)

### Request body

`application/json` (required), schema `CredentialsCreateOrUpdate`

- `name` (string, required) — Name of the credentials. Use this name to access or modify your credentials.
- `is_default` (boolean or null, optional) — Controls whether this credential is the default for its auth method. On creation: if no credential exists yet for this auth method, the credential is automatically set as default when is_default is true or omitted; setting is_default to false is rejected because a default must exist. If other credentials already exist, setting is_default to true promotes this credential (demoting the previous default); false or omitted creates it as non-default. On update: true promotes this credential, false is rejected if it is currently the default (promote another credential first), omitted leaves the default status unchanged.
- `credentials` (object or null, optional) — The credential data (headers, bearer_token).
  - `oauth` (object or null, optional)
    - `access_token` (string, required)
    - `token_type` (string, optional)
    - `expires_in` (integer or null, optional)
    - `scope` (string or null, optional)
    - `refresh_token` (string or null, optional)
    - `expires_at` (string (date-time) or null, optional)
  - `headers` (object or null, optional)
  - `bearer_token` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List user credentials for a connector. {#operation-connector_list_user_credentials_v1}

`GET /v1/connectors/{connector_id_or_name}/user/credentials`

List all credentials configured at the user level for a given connector.

- Operation id: `connector_list_user_credentials_v1`
- Tag: beta/connectors

### Parameters

- `auth_type` (enum: 'oauth2', 'bearer', 'none', optional, in query)
- `fetch_default` (boolean, optional, in query)
- `connector_id_or_name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema CredentialsResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create or update user credentials for a connector. {#operation-connector_create_or_update_user_credentials_v1}

`POST /v1/connectors/{connector_id_or_name}/user/credentials`

Create or update credentials at the user level for a given connector.

- Operation id: `connector_create_or_update_user_credentials_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (string, required, in path)

### Request body

`application/json` (required), schema `CredentialsCreateOrUpdate`

- `name` (string, required) — Name of the credentials. Use this name to access or modify your credentials.
- `is_default` (boolean or null, optional) — Controls whether this credential is the default for its auth method. On creation: if no credential exists yet for this auth method, the credential is automatically set as default when is_default is true or omitted; setting is_default to false is rejected because a default must exist. If other credentials already exist, setting is_default to true promotes this credential (demoting the previous default); false or omitted creates it as non-default. On update: true promotes this credential, false is rejected if it is currently the default (promote another credential first), omitted leaves the default status unchanged.
- `credentials` (object or null, optional) — The credential data (headers, bearer_token).
  - `oauth` (object or null, optional)
    - `access_token` (string, required)
    - `token_type` (string, optional)
    - `expires_in` (integer or null, optional)
    - `scope` (string or null, optional)
    - `refresh_token` (string or null, optional)
    - `expires_at` (string (date-time) or null, optional)
  - `headers` (object or null, optional)
  - `bearer_token` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete organization credentials for a connector. {#operation-connector_delete_organization_credentials_v1}

`DELETE /v1/connectors/{connector_id_or_name}/organization/credentials/{credentials_name}`

Delete credentials at the organization level for a given connector.

- Operation id: `connector_delete_organization_credentials_v1`
- Tag: beta/connectors

### Parameters

- `credentials_name` (string, required, in path)
- `connector_id_or_name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete workspace credentials for a connector. {#operation-connector_delete_workspace_credentials_v1}

`DELETE /v1/connectors/{connector_id_or_name}/workspace/credentials/{credentials_name}`

Delete credentials at the workspace level for a given connector.

- Operation id: `connector_delete_workspace_credentials_v1`
- Tag: beta/connectors

### Parameters

- `credentials_name` (string, required, in path)
- `connector_id_or_name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete user credentials for a connector. {#operation-connector_delete_user_credentials_v1}

`DELETE /v1/connectors/{connector_id_or_name}/user/credentials/{credentials_name}`

Delete credentials at the user level for a given connector.

- Operation id: `connector_delete_user_credentials_v1`
- Tag: beta/connectors

### Parameters

- `credentials_name` (string, required, in path)
- `connector_id_or_name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get a connector. {#operation-connector_get_v1}

`GET /v1/connectors/{connector_id_or_name}`

Get a connector by its ID or name.

- Operation id: `connector_get_v1`
- Tag: beta/connectors

### Parameters

- `fetch_customer_data` (boolean, optional, in query) — Fetch the customer data associated with the connector (e.g. customer secrets / config).
- `fetch_connection_secrets` (boolean, optional, in query) — Fetch the general connection secrets associated with the connector.
- `connector_id_or_name` (string, required, in path)

### Responses

- `200` — Successful Response (application/json, schema Connector)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete a connector. {#operation-connector_delete_v1}

`DELETE /v1/connectors/{connector_id}`

Delete a connector by its ID.

- Operation id: `connector_delete_v1`
- Tag: beta/connectors

### Parameters

- `connector_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Update a connector. {#operation-connector_update_v1}

`PATCH /v1/connectors/{connector_id}`

Update a connector by its ID.

- Operation id: `connector_update_v1`
- Tag: beta/connectors

### Parameters

- `connector_id` (string (uuid), required, in path)

### Request body

`application/json` (required), schema `ConnectorMCPUpdate`

- `name` (string or null, optional) — The name of the connector.
- `description` (string or null, optional) — The description of the connector.
- `icon_url` (string or null, optional) — The optional url of the icon you want to associate to the connector.
- `system_prompt` (string or null, optional) — Optional system prompt for the connector.
- `connection_config` (object or null, optional) — Optional new connection config.
- `connection_secrets` (object or null, optional) — Optional new connection secrets
- `server` (string (uri) or null, optional) — New server url for your mcp connector.
- `headers` (object or null, optional) — New headers for your mcp connector.
- `auth_data` (object or null, optional) — New authentication data for your mcp connector.
  - `client_id` (string, required)
  - `client_secret` (string, required)

### Responses

- `200` — Successful Response (application/json, schema Connector)
- `422` — Validation Error (application/json, schema HTTPValidationError)
