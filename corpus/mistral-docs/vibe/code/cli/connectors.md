---
url: https://docs.mistral.ai/vibe/code/cli/connectors
title: Connectors
breadcrumbs: [Vibe, Code, CLI]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/cli/connectors/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Connectors

Connectors give the Vibe Code CLI access to **supported first-party and third-party services** from inside a coding session. Unlike [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers), which you wire up yourself, Connectors are **Mistral-managed integrations**.

> **Info**
>
> For the full list of supported connectors and what each one can do, see [Connectors in Vibe Work](https://docs.mistral.ai/vibe/work/connectors). Vibe Code and Vibe Work share the same integrations.

## Connectors vs. MCP servers {#vs-mcp}

Both expose tools to Vibe, but they're operated differently. Pick whichever fits the service you want to connect:

| | Connectors | MCP servers |
|---|---|---|
| **Configured by** | Mistral, as integrated services | You, in `config.toml` |
| **Auth model** | Account or service login | Headers, environment variables, or API keys |
| **Discoverability** | Curated, listed in the CLI | Anything that speaks MCP |
| **Best for** | Common services with managed integrations | Custom tools, private servers, experimental tools |

## Manage connectors {#manage}

Connectors are detected and configured automatically. You can list, enable, disable, and inspect them from inside a CLI session.

List all connectors and MCP servers:

```text
/connectors
```

(`/connectors` is an alias for `/mcp`.)

From the list, with a connector highlighted:

| Key | Action |
|---|---|
| `E` | Enable the connector |
| `D` | Disable the connector |

Pass a name to inspect the tools exposed by a specific connector:

```text
/connectors fetch_server
```

## Stay in control {#stay-in-control}

- **Review what each connector can access** before authenticating.
- **Prefer read-only or scoped access** when the task doesn't need write permissions.
- **Revoke unused connectors** from the relevant service when you no longer need them.
