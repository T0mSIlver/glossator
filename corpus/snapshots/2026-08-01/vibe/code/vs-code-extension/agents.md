---
url: https://docs.mistral.ai/vibe/code/vs-code-extension/agents
title: Agents
breadcrumbs: [Vibe, Code, VS Code extension]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/vs-code-extension/agents/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Agents

Agents are **configuration overrides** applied on top of the global config. They bundle a system prompt, a compaction prompt, an active model, an available tool set, and approval rules. The VS Code extension uses the same agent system as the CLI, with one additional `Chat` mode for tool-free conversation.

## Built-in agents {#built-in-agents}

| Agent | Behavior |
|---|---|
| `Default` | General-purpose agent. Asks for approval before running tools. |
| `Plan` | Read-only agent for exploration and planning. Auto-approves safe read tools. |
| `Accept Edits` | Auto-approves file edits in the working directory. Still asks for approval for other actions (for example, shell commands). |
| `Auto Approve` | Auto-approves all tool execution. Use **only in a trusted, sandboxed environment**: this agent can run arbitrary commands such as `rm -rf` against any path Vibe can reach. |
| `Chat` | Conversation-only mode with no tool execution. |

## Select an agent {#select}

Click the agent selector at the bottom of the Mistral Vibe panel to pick an agent from the dropdown. The list includes all built-in and custom agents available in your configuration.

You can also cycle through agents on the fly with `Shift+Tab`, the same shortcut as the CLI.

The selector defaults to `Default` and the selection persists for the session.

## Custom agents {#custom-agents}

The VS Code extension reads the same agent definitions as the CLI from `~/.vibe/agents/` (user-level) and `./.vibe/agents/` (project-level). Custom agents declared there appear in the selector alongside the built-ins.

See the [CLI Agents reference](https://docs.mistral.ai/vibe/code/cli/agents) for the full configuration schema, examples, and the difference between `agent_type = "agent"` and `agent_type = "subagent"`.
