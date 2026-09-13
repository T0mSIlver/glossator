---
url: https://docs.mistral.ai/vibe/choose-chat-work-code
title: Choose Chat, Work, or Code
breadcrumbs: [Vibe]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/choose-chat-work-code/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Choose Chat, Work, or Code

A closer look at each Vibe mode: when to use it, what it does, and where to start.

## Work {#work}

**Pick Work when you want the agent to do the legwork, not just answer a question.** Available in the Vibe web and mobile apps with a chat interface, Work is the right mode when your task needs multiple steps, several sources, or actions in connected tools, and when you want to review the result before using it.

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

## Chat (migrating from Le Chat) {#chat}

**Pick Chat when you want a quick turn-based conversation, or when you rely on a legacy feature.** Available in the Vibe web and mobile apps as the Chat tab, Chat keeps the turn-based experience and the features that shipped in Le Chat, so existing workflows keep working.

Each of these features is being reimagined in Work. Stay in Chat if you depend on the current behavior; switch to Work when the new shape fits the task better.

**Chat features and their Work equivalents:**
| Chat feature | Work equivalent |
|---|---|
| [Agents](https://docs.mistral.ai/vibe/chat-legacy/agents): specialized assistants with their own tools and instructions. | [Skills](https://docs.mistral.ai/vibe/work/skills), with a different configuration model. |
| [Think mode](https://docs.mistral.ai/vibe/chat-legacy/think-mode): extended reasoning for problems that need deeper analysis. | Reasoning level chosen automatically by the model. |
| [Deep Research](https://docs.mistral.ai/vibe/chat-legacy/deep-research): multi-source research with structured, cited reports. | Available as a [Skill](https://docs.mistral.ai/vibe/work/skills). |
| [Code Interpreter](https://docs.mistral.ai/vibe/chat-legacy/code-interpreter): Python in a sandbox for charts and data analysis. | Built-in TypeScript code environment for most data-processing and graphing use cases. |
| [Memories](https://docs.mistral.ai/vibe/chat-legacy/memories): long-term facts and preferences the assistant remembers across chats. | Soon new memory system that scales to user knowledge and projects. |

> **Note**
>
> If your team or organization built workflows around Le Chat Agents, those continue to work in Chat. Migration paths to Skills, Sub-Agents, or custom agents are planned for a later phase.
