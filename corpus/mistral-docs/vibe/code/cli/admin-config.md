---
url: https://docs.mistral.ai/vibe/code/cli/admin-config
title: Admin config
breadcrumbs: [Vibe, Code, CLI]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/cli/admin-config/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Admin config

Admin config, also called **managed config**, lets Organization and Workspace administrators distribute Vibe Code CLI settings to all users. You define it once in the Admin Panel, and the CLI applies it to users in the Organization or Workspace. Use it to distribute models, providers, MCP servers, and tool policies without requiring users to edit `config.toml`.

> **Info**
>
> Admin config is a **distribution mechanism, not a security control**. It applies settings by default and shows them in `/config`, but users who control their local CLI environment can bypass them. Don't use admin config to restrict access to tools or models.

Unlike `config.toml`, admin config doesn't live on the user's machine. The CLI fetches it over HTTP at startup, keeps it **in memory only**, and never writes it to disk.

Admin config is available at two scopes:

- **Organization level**: configure it in [Admin Panel > Vibe > Preferences](https://admin.mistral.ai/vibe/preferences). It applies to all users in the Organization.
- **Workspace level**: open [Admin Panel > Administration > Workspaces](https://admin.mistral.ai/organization/workspaces), select a Workspace, and open `Settings`. This configuration can override or block specific Organization-level settings.

The server merges the Organization and Workspace configurations. The client receives one resolved configuration.

## Minimum client versions {#requirements}

Support for admin config starts with these client versions:

| Client | Minimum version |
|---|---|
| **Vibe Code CLI** | `2.24.2` |
| **VS Code extension** | `1.16` |

Earlier clients don't request admin config or apply its settings. Upgrade every client before you distribute an admin config.

## How it works {#how-it-works}

1. In [Admin Panel > Vibe > Preferences](https://admin.mistral.ai/vibe/preferences), enter a TOML configuration under `Vibe Code Clients managed config`.
2. At startup and after `/reload`, the CLI calls the managed-config endpoint with the user's Mistral API key.
3. If admin config is enabled, its values take precedence over every other configuration source.

## Permissions {#permissions}

Managing admin config requires the `manage_code_config` role-based access control (RBAC) permission at the Organization scope. Organization administrators can delegate admin config management without granting full administrator access.

## Enable the feature {#enable}

Admin config is **disabled by default**, and Mistral must enable it for your Organization. Contact your account team to request activation.

> **Warning**
>
> We recommend validating your configuration in a test Organization before distributing it to all users.

## Activation by deployment type {#deployment}

The activation process depends on the deployment type:

| Deployment | How to activate |
|---|---|
| **Serverless** | Contact your account team to enable the feature flag. |
| **Dedicated (private cloud)** | Contact your account team. Mistral enables the feature flag when available or sets its value in the deployment configuration. |
| **Self-hosted** | Contact your account team to request activation through the Helm chart. This option is available on request. |

> **Info**
>
> **Dedicated and self-hosted deployments** require `/whoami` to return the correct Vibe and API domains. See [Troubleshooting](https://docs.mistral.ai/vibe/code/cli/admin-config#troubleshooting) for validation steps.

## Precedence {#precedence}

Admin config is the **highest-priority** layer. It takes precedence over command-line flags, environment variables, and both project and user `config.toml`:

```text
admin config  >  CLI flags  >  env vars  >  project config.toml  >  user config.toml
```

This precedence means the admin-provided values take effect for users by default, without them needing to update their own `config.toml`.

## What admins can set {#what-can-be-set}

Admin config accepts most of the same keys as [`config.toml`](https://docs.mistral.ai/vibe/code/cli/configuration), for example:

- Active model, models, and providers.
- MCP server.
- Connectors, and enabled/disabled tools, agents, and skills.
- Telemetry, auto-update, and notification toggles.

```toml
active_model = "mistral-large-latest"
enable_auto_update = false
disabled_tools = ["shell"]

[[providers]]
name = "mistral"
api_base = "https://api.mistral.ai"
api_key_env_var = "MISTRAL_API_KEY"
```

## Enforce enterprise defaults {#enterprise-defaults}

A common use is giving everyone in the organization ready-to-use models out of the box. Instead of each user manually setting up providers and models, admins ship the right model and provider once, pointed at your enterprise endpoint with the correct backend, base URL, and headers. Users get a working setup on first launch, with nothing to configure.

```toml
active_model = "mistral-large-enterprise"

[[providers]]
name = "acme-enterprise"
backend = "mistral"
api_base = "https://mistral.acme.internal/v1"
api_key_env_var = "ACME_MISTRAL_API_KEY"
api_style = "openai"
region = "eu-west-1"

[providers.extra_headers]
"x-acme-tenant" = "engineering"

[[models]]
name = "mistral-large-2411"
provider = "acme-enterprise"
alias = "mistral-large-enterprise"
```

Here the model `mistral-large-2411` is served through the `acme-enterprise` provide, exposed to users under the alias `mistral-large-enterprise`, which is set as the active model. The credential is still supplied locally via the `ACME_MISTRAL_API_KEY` environment variable.

## Secrets {#secrets}

Admin config never contains literal secrets. Credential fields must reference an environment variable (for example, `api_key_env_var = "MISTRAL_API_KEY"`), never the key itself. Literal API keys, tokens, or passwords are rejected on the server.

## What users see {#user-experience}

When admin config is active, users in the Vibe Code CLI notice the following:

- Admin-managed settings in `/config` appear dim with a `⚿` lock glyph and list `your administrator` as the origin. A legend at the bottom of the screen reads `⚿ Settings are managed by your organization`.
- Admin-managed fields are read-only in `/config`. Attempts to edit or reset them have no effect.
- The model picker is an exception. If a user switches models while `active_model` is admin-managed, a warning explains that the administrator controls the setting.
- Users see admin-managed markers only when they open `/config`. There is no startup banner or global indicator.
- The CLI fetches admin config in the background at the start of each session. It keeps the configuration in memory and never writes it to the local `config.toml`.
- If a network or server error prevents the fetch, the session continues without admin config. The CLI logs the failure at debug level and doesn't show a warning.

## Stop applying admin config {#disable}

Disabling the feature flag only hides the admin UI. Clients continue to fetch and apply the saved configuration.

To stop applying admin config, **submit an empty configuration** before you disable the feature flag. This prevents a stale configuration from being applied to user sessions.

## Troubleshoot dedicated and self-hosted deployments {#troubleshooting}

If users in dedicated or self-hosted deployments don't receive admin config, check the endpoints and domain values.

### Check endpoint access {#check-endpoints}

The client needs to reach two authenticated endpoints:

- `<console_base_url>/api/vibe/whoami` returns the tenant's Vibe and API domains in `vibe_base` and `api_base`.
- `<vibe_base_url>/api/v1/code/managed-config` returns the admin config response. The client derives `vibe_base_url` from the `vibe_base` value returned by `/whoami`.

Set the URLs for the user's deployment, make sure `MISTRAL_API_KEY` is available in the environment, and run both requests from the user's environment:

```bash
CONSOLE_BASE_URL="https://console.mistral.ai"
VIBE_BASE_URL="https://chat.mistral.ai"

curl --silent --show-error --fail-with-body \
  --header "Authorization: Bearer ${MISTRAL_API_KEY}" \
  "${CONSOLE_BASE_URL}/api/vibe/whoami"

curl --silent --show-error --fail-with-body \
  --header "Authorization: Bearer ${MISTRAL_API_KEY}" \
  "${VIBE_BASE_URL}/api/v1/code/managed-config"
```

For dedicated and self-hosted deployments, replace both URL values with the deployment's console and Vibe origins.

- If either request fails to connect, check the deployment's DNS, TLS, and network configuration. Contact your account team or Mistral support if the endpoint remains unavailable.
- If either request returns `401` or `403`, verify the user's API key and access.
- If both requests return a successful HTTP status, continue with the domain checks.

### Check the `/whoami` domains {#check-domains}

The `/whoami` response must contain the expected `vibe_base` and `api_base` origins. The client stores a valid `vibe_base` value as `vibe_base_url` in the user's `config.toml` and uses it to build the managed-config URL.

If `/whoami` returns an incorrect domain, contact Mistral support to correct the server configuration. If the response is correct but the client doesn't fetch admin config, investigate the Vibe Code client.

### Apply fixes for your deployment type {#deployment-fixes}

| Deployment | How fixes are delivered |
|---|---|
| **Serverless** | Mistral includes the fix in a platform release. |
| **Dedicated** | Request a redeployment of the dedicated instance. |
| **Self-hosted** | Update to a self-hosted release. For critical issues, contact Mistral support to discuss a hotfix. |
