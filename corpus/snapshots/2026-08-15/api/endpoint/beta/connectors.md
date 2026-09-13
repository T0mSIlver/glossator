---
url: https://docs.mistral.ai/api/endpoint/beta/connectors
title: Beta Connectors API
breadcrumbs: [API, Beta Connectors]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
openapi_md5: db1a4fa046d1b32a0c8dbb092f397986
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

`application/json` (required), schema `CreateConnectorRequest`

- `protocol` (string, optional) — Protocol of the connector. Only 'mcp' is supported on the public endpoint; creating HTTP connectors here is explicitly refused.
- `name` (string, required) — The name of the connector. Should be 64 char length maximum, alphanumeric, only underscores/dashes.
- `title` (string or null, optional) — Optional human-readable title for the connector.
- `description` (string, required) — The description of the connector.
- `icon_url` (string or null, optional) — The optional url of the icon you want to associate to the connector.
- `visibility` (enum: 'shared_org', 'shared_workspace', 'private', optional) — Visibility of the connector. Use 'shared_workspace' for workspace scoped connectors, or 'private' for private connectors.
- `server` (string (uri), required) — The url of the MCP server.
- `headers` (object or null, optional) — Optional organization-level headers to be sent with the request to the mcp server.
- `global_headers` (object, optional) — Optional connector-wide headers, keyed by header name, set at creation and applied to every credential. Secret values are encrypted at rest and never returned in clear.
- `auth_data` (object or null, optional) — Optional additional authentication data for the connector.
  - `client_id` (string, required)
  - `client_secret` (string (password) or null, optional)
- `oauth2_server_metadata` (object or null, optional) — Optional OAuth2 authorization server metadata (authorization_endpoint, token_endpoint, etc.). When provided, skips .well-known discovery and uses these endpoints directly.
  - `issuer` (string (uri), required)
  - `authorization_endpoint` (string (uri), required)
  - `token_endpoint` (string (uri), required)
  - `registration_endpoint` (string (uri) or null, optional)
  - `scopes_supported` (array of string or null, optional)
  - `response_types_supported` (array of string, optional)
  - `response_modes_supported` (array of string or null, optional)
  - `grant_types_supported` (array of string or null, optional)
  - `token_endpoint_auth_methods_supported` (array of string or null, optional)
  - `token_endpoint_auth_signing_alg_values_supported` (array of string or null, optional)
  - `service_documentation` (string (uri) or null, optional)
  - `ui_locales_supported` (array of string or null, optional)
  - `op_policy_uri` (string (uri) or null, optional)
  - `op_tos_uri` (string (uri) or null, optional)
  - `revocation_endpoint` (string (uri) or null, optional)
  - `revocation_endpoint_auth_methods_supported` (array of string or null, optional)
  - `revocation_endpoint_auth_signing_alg_values_supported` (array of string or null, optional)
  - `introspection_endpoint` (string (uri) or null, optional)
  - `introspection_endpoint_auth_methods_supported` (array of string or null, optional)
  - `introspection_endpoint_auth_signing_alg_values_supported` (array of string or null, optional)
  - `code_challenge_methods_supported` (array of string or null, optional)
  - `client_id_metadata_document_supported` (boolean or null, optional)
  - `x_source` (enum: 'autodiscovery', 'provided', optional) — How a connector's OAuth server metadata was obtained.
  - `x_resource_url` (string or null, optional)
  - `x_scope` (string or null, optional)
- `oauth2_server_metadata_url` (string (uri) or null, optional) — Optional URL to fetch OAuth2 authorization server metadata from (RFC 8414). When provided, the metadata is fetched from this URL and used instead of .well-known discovery. Mutually exclusive with oauth2_server_metadata.
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

- `connector_id_or_name` (object, required, in path)
- `app_return_url` (string or null, optional, in query)
- `method_type` (enum: 'oauth2', 'bearer', 'none', 'github_app', 'slack_app', optional, in query) — Auth method type to use for the authorization URL. Required when the connector supports multiple interactive auth methods; otherwise the sole method is selected automatically. Use this to pick a specific method (e.g. 'oauth2' vs 'github_app').
- `credentials_name` (string or null, optional, in query)
- `credentials_title` (string or null, optional, in query)
- `github_installation_link` (boolean, optional, in query) — Only valid with method_type=oauth2. When true, returns a GitHub App installation URL (https://github.com/apps/<slug>/installations/new) if the connector has the proper configuration The Github application needs to have 'Request user authorization (OAuth) during installation' enabled to perform the proper auth loop.

### Responses

- `200` — Successful Response (application/json, schema AuthUrlResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Share a private connector to the current workspace. {#operation-connector_share_v1}

`PUT /v1/connectors/{connector_id}/share`

Transfers ownership of a private user-owned connector to the current workspace, making it available to all workspace members. The creator can later revert this via the unshare endpoint. Any authentication flows that rely on the original owner's identity (e.g. OAuth on-behalf-of) will be affected and must be reconfigured after sharing. Only the connector's creator can call this endpoint. Requires the ShareConnectorToWorkspace workspace permission.

- Operation id: `connector_share_v1`
- Tag: beta/connectors

### Parameters

- `connector_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Unshare a connector from the current workspace. {#operation-connector_unshare_v1}

`DELETE /v1/connectors/{connector_id}/share`

Reverts a workspace-shared connector back to a private, creator-owned connector. Workspace-scoped connections and other members' connections are removed; the creator's own connection is preserved. Only the connector's creator can call this endpoint. Requires the ShareConnectorToWorkspace workspace permission.

- Operation id: `connector_unshare_v1`
- Tag: beta/connectors

### Parameters

- `connector_id` (string (uuid), required, in path)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Activate a connector for the given consumer (organization, workspace, user). {#operation-connector_activate_for_consumer_v1}

`POST /v1/connectors/{connector_id}/{consumer_scope}/activate`

Enable a connector for the consumer.

- Operation id: `connector_activate_for_consumer_v1`
- Tag: beta/connectors

### Parameters

- `connector_id` (string (uuid), required, in path)
- `consumer_scope` (enum: 'user', 'workspace', 'organization', required, in path)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Deactivate a connector for the current consumer (at organization, workspace or user level). {#operation-connector_deactivate_for_consumer_v1}

`POST /v1/connectors/{connector_id}/{consumer_scope}/deactivate`

Disable a connector for the calling consumer only.

- Operation id: `connector_deactivate_for_consumer_v1`
- Tag: beta/connectors

### Parameters

- `connector_id` (string (uuid), required, in path)
- `consumer_scope` (enum: 'user', 'workspace', 'organization', required, in path)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Call Connector Tool {#operation-connector_call_tool_v1}

`POST /v1/connectors/{connector_id_or_name}/tools/{tool_name}/call`

Call a tool on an MCP connector.

- Operation id: `connector_call_tool_v1`
- Tag: beta/connectors

### Parameters

- `tool_name` (string, required, in path)
- `connector_id_or_name` (object, required, in path)
- `credentials_name` (string or null, optional, in query)

### Request body

`application/json` (required), schema `ConnectorCallToolRequest`

- `arguments` (object, optional)

### Responses

- `200` — Successful Response (application/json, schema ConnectorToolCallResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List tools for a connector. {#operation-connector_list_tools_v1}

`GET /v1/connectors/{connector_id_or_name}/tools`

List all tools available for an MCP connector.

- Operation id: `connector_list_tools_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (object, required, in path)
- `page` (integer, optional, in query)
- `page_size` (integer, optional, in query)
- `refresh` (boolean, optional, in query)
- `pretty` (boolean, optional, in query) — Return a simplified payload with only name, description, annotations, and a compact inputSchema.
- `credentials_name` (string or null, optional, in query)

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get authentication methods for a connector. {#operation-connector_get_authentication_methods_v1}

`GET /v1/connectors/{connector_id_or_name}/authentication_methods`

Get the authentication schema for a connector. Returns the list of supported authentication methods and their required headers.

- Operation id: `connector_get_authentication_methods_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (object, required, in path)

### Responses

- `200` — Successful Response (application/json)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List organization credentials for a connector. {#operation-connector_list_organization_credentials_v1}

`GET /v1/connectors/{connector_id_or_name}/organization/credentials`

List all credentials configured at the organization level for a given connector.

- Operation id: `connector_list_organization_credentials_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (object, required, in path)
- `auth_type` (enum: 'oauth2', 'bearer', 'none', 'github_app', 'slack_app', optional, in query)
- `fetch_default` (boolean, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema CredentialsResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create or update organization credentials for a connector. {#operation-connector_create_or_update_organization_credentials_v1}

`POST /v1/connectors/{connector_id_or_name}/organization/credentials`

Create or update credentials at the organization level for a given connector.

- Operation id: `connector_create_or_update_organization_credentials_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (object, required, in path)

### Request body

`application/json` (required), schema `CredentialsCreateOrUpdate`

- `name` (string, required) — Name of the credentials. Use this name to access or modify your credentials.
- `title` (string or null, optional) — Human-readable title for the credentials.
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
  - `github_installation_id` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List workspace credentials for a connector. {#operation-connector_list_workspace_credentials_v1}

`GET /v1/connectors/{connector_id_or_name}/workspace/credentials`

List all credentials configured at the workspace level for a given connector.

- Operation id: `connector_list_workspace_credentials_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (object, required, in path)
- `auth_type` (enum: 'oauth2', 'bearer', 'none', 'github_app', 'slack_app', optional, in query)
- `fetch_default` (boolean, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema CredentialsResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create or update workspace credentials for a connector. {#operation-connector_create_or_update_workspace_credentials_v1}

`POST /v1/connectors/{connector_id_or_name}/workspace/credentials`

Create or update credentials at the workspace level for a given connector.

- Operation id: `connector_create_or_update_workspace_credentials_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (object, required, in path)

### Request body

`application/json` (required), schema `CredentialsCreateOrUpdate`

- `name` (string, required) — Name of the credentials. Use this name to access or modify your credentials.
- `title` (string or null, optional) — Human-readable title for the credentials.
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
  - `github_installation_id` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## List user credentials for a connector. {#operation-connector_list_user_credentials_v1}

`GET /v1/connectors/{connector_id_or_name}/user/credentials`

List all credentials configured at the user level for a given connector.

- Operation id: `connector_list_user_credentials_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (object, required, in path)
- `auth_type` (enum: 'oauth2', 'bearer', 'none', 'github_app', 'slack_app', optional, in query)
- `fetch_default` (boolean, optional, in query)

### Responses

- `200` — Successful Response (application/json, schema CredentialsResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Create or update user credentials for a connector. {#operation-connector_create_or_update_user_credentials_v1}

`POST /v1/connectors/{connector_id_or_name}/user/credentials`

Create or update credentials at the user level for a given connector.

- Operation id: `connector_create_or_update_user_credentials_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (object, required, in path)

### Request body

`application/json` (required), schema `CredentialsCreateOrUpdate`

- `name` (string, required) — Name of the credentials. Use this name to access or modify your credentials.
- `title` (string or null, optional) — Human-readable title for the credentials.
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
  - `github_installation_id` (string or null, optional)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Delete all user credentials for a connector. {#operation-connector_delete_all_user_credentials_v1}

`DELETE /v1/connectors/{connector_id_or_name}/user/credentials`

Delete all credentials configured at the user level for a given connector.

- Operation id: `connector_delete_all_user_credentials_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (object, required, in path)

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
- `connector_id_or_name` (object, required, in path)

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
- `connector_id_or_name` (object, required, in path)

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
- `connector_id_or_name` (object, required, in path)

### Responses

- `200` — Successful Response (application/json, schema MessageResponse)
- `422` — Validation Error (application/json, schema HTTPValidationError)

## Get a connector. {#operation-connector_get_v1}

`GET /v1/connectors/{connector_id_or_name}`

Get a connector by its ID or name.

- Operation id: `connector_get_v1`
- Tag: beta/connectors

### Parameters

- `connector_id_or_name` (object, required, in path)
- `fetch_user_data` (boolean, optional, in query) — Fetch the user-level data associated with the connector (e.g. connection credentials).
- `fetch_customer_data` (boolean, optional, in query) — Fetch the customer data associated with the connector (e.g. customer secrets / config).

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

`application/json` (required), schema `UpdateConnectorRequest`

- `title` (string or null, optional) — Optional human-readable title for the connector.
- `name` (string or null, optional) — The name of the connector.
- `description` (string or null, optional) — The description of the connector.
- `icon_url` (string or null, optional) — The optional url of the icon you want to associate to the connector.
- `system_prompt` (string or null, optional) — Optional system prompt for the connector.
- `protocol` (string, optional)
- `server` (string (uri) or null, optional) — New server url for your mcp connector.
- `auth_methods` (array of AuthenticationMethodCreateOrUpdateRequest or null, optional) — list of authentication methods to add to the connector or to update
  - `method_type` (object, required) — The type of authentication method (e.g. oauth2, bearer, none).
  - `auth_direction` (enum: 'inbound', 'outbound', optional) — Whether the authentication method is for outbound or inbound requests.
  - `headers` (array of ConnectorAuthenticationHeader or null, optional) — Set of headers to connect to the connector
  - `global_headers` (object, optional) — Connector-wide headers keyed by header name, applied to every credential. Secret values are encrypted at rest and never returned in clear.
  - `oauth2_metadata_secrets` (object or null, optional) — New OAuth2 client credentials (client_id and client_secret).
  - `oauth2_server_metadata` (object or null, optional) — New OAuth2 authorization server metadata.

### Responses

- `200` — Successful Response (application/json, schema Connector)
- `422` — Validation Error (application/json, schema HTTPValidationError)
