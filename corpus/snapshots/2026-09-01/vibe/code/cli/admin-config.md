---
url: https://docs.mistral.ai/vibe/code/cli/admin-config
title: Admin config
breadcrumbs: [Vibe, Code, CLI]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/cli/admin-config/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Admin config

Admin config (also called **managed config**) lets organization and workspace admins enforce Vibe Code CLI settings centrally. It is defined once on the Mistral side and applied automatically to every CLI in the org or workspace.

Unlike `config.toml`, it does not live on the user's machine. The CLI fetches it over HTTP at startup, keeps it **in memory only**, and never writes it to disk.

## How it works {#how-it-works}

1. An admin authors a TOML config under **Vibe Code Clients managed config** in the [settings manager](https://admin.mistral.ai/vibe/preferences).
2. On startup (and on `/reload`), the CLI calls the managed-config endpoint with your Mistral API key.
3. If the config is enabled, its values are applied on top of every other setting.

## Precedence {#precedence}

Admin config is the **highest-priority** layer. It overrides everything, including command-line flags, environment variables, and both project and user `config.toml`:

```
admin config  >  CLI flags  >  env vars  >  project config.toml  >  user config.toml
```

This precedence is the enforcement mechanism: any setting an admin sets cannot be changed locally.

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
