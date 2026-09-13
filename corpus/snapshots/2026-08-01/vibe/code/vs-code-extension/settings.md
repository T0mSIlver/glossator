---
url: https://docs.mistral.ai/vibe/code/vs-code-extension/settings
title: Extension settings
breadcrumbs: [Vibe, Code, VS Code extension]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/vs-code-extension/settings/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Extension settings

A dedicated settings panel for the VS Code extension is in progress. Until it ships, **all Vibe behavior comes from the bundled Vibe agent and the same Vibe configuration model used by the CLI** (config files, environment variables, project overrides).

## Telemetry {#telemetry}

The extension reuses VS Code's global telemetry setting and Vibe's CLI telemetry toggle:

- **VS Code telemetry**: controlled by `telemetry.telemetryLevel` in VS Code settings. The extension only sends telemetry when VS Code telemetry is enabled.
- **Vibe telemetry**: controlled by `enable_telemetry` in `~/.vibe/config.toml`. See [Update and telemetry settings](https://docs.mistral.ai/vibe/code/cli/configuration#updates-telemetry).

To opt out of extension telemetry, disable either of those toggles.

## Shared Vibe configuration {#shared-vibe-configuration}

The extension runs the Vibe ACP agent. **Agent-level behavior** (models, providers, tools, agents, skills, and MCP servers) follows the shared Vibe configuration model. Use the CLI configuration docs for the shared format:

- **[Configuration](https://docs.mistral.ai/vibe/code/cli/configuration)**: full `config.toml` reference.
- **[API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles)**: manage credentials and switch providers.
- **[MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers)**: connect external tools through the Model Context Protocol.
- **[Agents](https://docs.mistral.ai/vibe/code/cli/agents)**: built-in and custom agents.
- **[Skills](https://docs.mistral.ai/vibe/code/cli/skills)**: reusable, scoped behaviors.
