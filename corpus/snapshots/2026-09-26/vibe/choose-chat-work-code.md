---
url: https://docs.mistral.ai/vibe/choose-chat-work-code
title: Choose Work or Code
breadcrumbs: [Vibe]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/choose-chat-work-code/page.mdx
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
---

# Choose Work or Code

A closer look at each Vibe mode: when to use it, what it does, and where to start.

## Work {#work}

**Pick Work for conversations and multi-step work alike.** Available in the Vibe web and mobile apps with a chat interface, Work is the unified experience: use the **fast/think toggle** to switch between quick conversational responses and deeper, agentic workflows in the same conversation. It's the right mode when your task needs multiple steps, several sources, or actions in connected tools, and when you want to review the result before using it.

Typical tasks:

- *"Catch me up on what happened in the Q4 launch Project this week."*
- *"Summarize this 80-page contract and flag the renewal risks."*
- *"Draft replies to my unread emails from the legal team."*
- *"Research the top 5 competitors in our space and create a one-page brief."*
- *"Find the latest customer feedback in Notion, group it by theme, and prepare a slide deck."*

What Work gives you:

- **Agentic work across an unbounded number of [Connectors](https://docs.mistral.ai/vibe/work/connectors)** including Gmail, Outlook, Slack, Notion, Linear, GitHub, Atlassian, Google Drive, SharePoint, and Stripe.
- Real-time progress and tool-call visibility, with clarifying questions when your prompt is ambiguous.
- Approval prompts before sensitive actions (sending email, modifying data, deleting).
- [Skills](https://docs.mistral.ai/vibe/work/skills) and [Projects](https://docs.mistral.ai/vibe/work/projects) to make repeated work easier over time.
- [Schedule tasks](https://docs.mistral.ai/vibe/work/scheduled-tasks) to run a prompt automatically, once or on a daily, weekly, monthly, or yearly cadence.
- **Temporary Chat**: conversations excluded from your history, search, memory, and model training.

- [Get started with Vibe Work](https://docs.mistral.ai/vibe/work/get-started) — Run your first multi-step task in Work.

## Code {#code}

**Pick Code when the task depends on a codebase, terminal, IDE, or coding session.** Available as a CLI, a VS Code extension, or remote web sessions, Code is the developer mode where Vibe reads files, edits code, runs commands, and opens pull requests.

Typical tasks:

- *"Explain how authentication works in this repo."*
- *"Refactor `src/api/handlers/` to use the new error handler pattern."*
- *"Add unit tests for the `parseInvoice` function."*
- *"Run the test suite, fix what fails, and open a PR."*
- *"Continue the session I started in the CLI on the web."*

What Code gives you:

- **CLI**: terminal-native, scriptable, ideal for local repos and automation.
- **VS Code extension**: inline help, file editing, and chat right in your editor.
- **Remote sessions**: cloud sandbox you can launch from any surface (web, mobile, desktop, IDE, CLI) against a GitHub repo.

- [Vibe Code CLI](https://docs.mistral.ai/vibe/code/cli/install-setup) — Install Vibe in your terminal.

- [VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate) — Install Vibe in VS Code.

- [Vibe Code Web](https://docs.mistral.ai/vibe/code/vibe-code-web/get-started) — Start a remote coding session against a GitHub repo.

## Chat (legacy) {#chat}

The **Chat** tab was the turn-based mode for quick conversations and the features that predate the unification: Agents, Think mode, Code Interpreter, and Memories. Merging it into Work makes Vibe simpler to use: one surface for everything, with the **fast/think toggle** setting the depth instead of a tab choice. It's being removed progressively: self-serve Free, Pro, and Teams accounts migrate to the unified experience first, and Enterprise organizations may still see the Chat tab during a six-month migration window — administrators pick the migration date in the admin panel or trigger the merge immediately.

If you still have access, the legacy features keep working as before. If you don't, here's where each one lives now:

**Chat features and their unified equivalents:**
| Chat feature | Unified equivalent |
|---|---|
| [Agents](https://docs.mistral.ai/vibe/chat-legacy/agents): specialized assistants with their own tools and instructions. | Use [Skills](https://docs.mistral.ai/vibe/work/skills) instead; invoke them with `@`. |
| [Think mode](https://docs.mistral.ai/vibe/chat-legacy/think-mode): extended reasoning for problems that need deeper analysis. | The **fast/think toggle** in the unified experience. |
| [Deep Research](https://docs.mistral.ai/vibe/chat-legacy/deep-research): multi-source research with structured, cited reports. | The [Deep Research Skill](https://docs.mistral.ai/vibe/work/skills) in Work. |
| [Code Interpreter](https://docs.mistral.ai/vibe/chat-legacy/code-interpreter): a sandbox for charts and data analysis. | The native [Code Interpreter](https://docs.mistral.ai/vibe/work/code-interpreter) in Work — a sandbox with the same capabilities, available on paid plans. |
| [Memories](https://docs.mistral.ai/vibe/chat-legacy/memories): long-term facts and preferences the assistant remembers across chats. | [Knowledge Base](https://docs.mistral.ai/vibe/work/knowledge): persistent knowledge that scales to your context and projects. |
