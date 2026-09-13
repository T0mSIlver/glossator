---
url: https://docs.mistral.ai/vibe/code/use-vibe-in-other-ides
title: Use Vibe in other IDEs
breadcrumbs: [Vibe, Code]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/use-vibe-in-other-ides/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Use Vibe in other IDEs

Vibe implements the **[Agent Client Protocol (ACP)](https://agentclientprotocol.com/)** and is published in the [ACP registry](https://github.com/agentclientprotocol/registry/tree/main/mistral-vibe). This means you can run Vibe in ACP-compatible clients outside the CLI, the VS Code extension, and Vibe Code Web.

This page explains how to add Vibe to an ACP-compatible client, including JetBrains IDEs such as IntelliJ IDEA, PyCharm, WebStorm, and GoLand. For the full client list, see the [ACP clients directory](https://agentclientprotocol.com/get-started/clients).

In these clients, Vibe runs as an agent in the client's native chat. It uses the same engine, configuration, and customization layer as the supported surfaces, including agents, skills, and MCP servers.

> **Warning**
>
> **Don't use the [Mistral Code Enterprise](https://plugins.jetbrains.com/plugin/27493-mistral-code-enterprise) JetBrains plugin.** It's deprecated, and there isn't a standalone Mistral extension for JetBrains. The supported path is to run Vibe through ACP. For the primary surfaces, see [Choose CLI, VS Code, or web sessions](https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions).

## Before you start {#requirements}

| Requirement | Details |
|---|---|
| **ACP-compatible client** | An IDE or client that supports ACP agents, such as a JetBrains IDE with the AI Assistant plugin. |
| **Mistral account** | Required to create or manage API keys. |
| **Plan or API key** | A [Mistral plan](https://mistral.ai/pricing) or an API key you manage yourself. Usage and rate limits depend on your plan, included monthly usage, and pay-as-you-go settings. |

## Add Vibe as an ACP agent {#general-setup}

The exact steps depend on your client, but the flow is the same across ACP-compatible IDEs:

1. **Add Vibe as an ACP agent** from your client's agent registry or settings.
2. **Select Mistral Vibe** as the active agent in the client's chat.
3. **Authenticate** with your Mistral API key when prompted.

After it connects, the client's chat runs against the Vibe agent and can use your open project and editor context.

## Set up JetBrains AI Assistant {#jetbrains}

JetBrains AI Assistant is an ACP-compatible client that hosts the ACP agent registry.

Before you add Vibe, make sure you have:

- **JetBrains IDE 2025.3.2 or later**. The ACP agent registry is available from this version.
- **AI Assistant plugin**. It hosts the ACP integration. If it isn't installed, open the `AI Chat` icon in the right tool window bar and click `Install Plugin`, or install `AI Assistant` from `Settings > Plugins`.

After the AI Assistant plugin is installed, add Vibe:

1. Open `Settings` (`Cmd+,` on macOS, `Ctrl+Alt+S` on Windows or Linux).
2. Go to `Tools > AI Assistant > Agents`.
3. In `Search agents`, search for `Mistral Vibe`.
4. On the `Mistral Vibe` entry, click `Install`. The IDE downloads the agent and any required runtime.
5. Open the `AI Chat` tool window.
6. Choose `Mistral Vibe` in the agent selector at the bottom of the chat input.

## Authenticate Vibe {#authenticate}

The first time Vibe needs credentials, it runs the bundled agent setup flow. Provide your Mistral API key when prompted. Vibe stores credentials in the Vibe home directory (`~/.vibe/`) and reuses them across sessions.

If you already authenticated the [Vibe CLI](https://docs.mistral.ai/vibe/code/cli/install-setup) or the [VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate) on the same machine, Vibe reuses the same configuration and credentials.

## Check that Vibe is ready {#verify}

Your setup is ready when:

- `Mistral Vibe` is available as the agent in your client's chat.
- You can send a prompt and receive a response.
- Vibe can use the active project and editor context.

Try a small first prompt:

```text
Explain the currently open file.
```

## Use shared configuration {#shared-config}

Vibe in an ACP client shares the same configuration and customization layer as the CLI and the VS Code extension: agents, skills, MCP servers, and profiles defined in `~/.vibe/` and per-project `.vibe/` directories. For details, see [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration).
