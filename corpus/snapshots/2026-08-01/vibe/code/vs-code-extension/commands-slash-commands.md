---
url: https://docs.mistral.ai/vibe/code/vs-code-extension/commands-slash-commands
title: Commands and slash commands
breadcrumbs: [Vibe, Code, VS Code extension]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/vs-code-extension/commands-slash-commands/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Commands and slash commands

Use **slash commands** and **keyboard shortcuts** to control Vibe Code from inside the editor. A couple of VS Code commands are also available from the Command Palette for setup and debugging.

## Slash commands {#slash-commands}

The extension exposes a subset of Vibe slash commands. Type `/` in the Vibe panel to see the available commands. [Skills](https://docs.mistral.ai/vibe/code/cli/skills) that opt in are surfaced in the same picker.

| Command | Input hint | Description |
|---|---|---|
| `/help` |  | Show available commands and keyboard shortcuts. |
| `/compact` | Optional summary instructions | Compact conversation history by summarizing it. |
| `/reload` |  | Reload configuration, agent instructions, and skills from disk. |
| `/log` |  | Show the path to the current session log directory. |
| `/proxy-setup` | `KEY value`, `KEY`, or empty for help | Configure proxy and SSL certificate settings. |
| `/leanstall` |  | Install the Lean 4 agent, `leanstral`. |
| `/unleanstall` |  | Uninstall the Lean 4 agent. |
| `/data-retention` |  | Show data retention information. |

For the full CLI command set, see [Commands and shortcuts](https://docs.mistral.ai/vibe/code/cli/commands-shortcuts).

## Keyboard shortcuts {#hotkeys}

Inside the Vibe panel, `Mod` means `Command` on macOS and `Ctrl` on Windows or Linux.

| Shortcut | Action |
|---|---|
| `Mod+Y` | Approve a tool action. |
| `Mod+Alt+Y` | Approve an alternate tool action. |
| `Mod+Shift+Y` | Approve and apply a broader permission choice. |
| `Mod+Alt+N` | Reject a tool action. |
| `Mod+N` | Start a new conversation. |
| `Escape` | Cancel or blur the current input state. |
| `Shift+Tab` | Cycle the active input mode. |

## CLI parity {#cli-parity}

The extension doesn't expose every CLI slash command, but it still lets you control most runtime settings through the UI:

- **`/model` and `/thinking`** are not available as slash commands. Change the active model or reasoning level from the extension's interface instead.
- **`/resume`** is not available as a slash command, but you can load previous sessions from the panel UI.
- **`/rename`** has a UI equivalent in the panel. Use it to rename the current session.
- Use the CLI for the remaining session and runtime controls: `/rewind`, `/loop`, `/mcp`, `/voice`.

## VS Code commands {#vscode-commands}

A small set of VS Code Command Palette entries is available for setup and debugging.

| Command | What it does |
|---|---|
| **Mistral Vibe: Open Mistral Vibe** | Focuses the Mistral Vibe panel. |
| **Mistral Vibe: Show Logs** | Opens the extension log output. |

> **Note**
>
> The extension doesn't declare default VS Code keybindings. Add custom shortcuts in `keybindings.json` if you want direct keyboard access to these commands.
