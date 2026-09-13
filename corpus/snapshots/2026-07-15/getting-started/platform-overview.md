---
url: https://docs.mistral.ai/getting-started/platform-overview
title: Platform overview
breadcrumbs: [Getting started]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/platform-overview/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Platform overview

Mistral AI has three products. Pick the one that matches what you want to do.

- **Vibe**: the unified agent for productivity and coding. Chat with it on the web or mobile, or run it in your terminal and editor.
- **Studio**: the developer console and Mistral API. Generate keys, prototype in the Playground, build durable workflows, and call text, audio, and OCR models from a single SDK.
- **Admin**: the control plane for organization setup, billing, SSO, workspaces, and access policies.

> **Tip**
>
> For a side-by-side feature and plan comparison across products, see the [pricing page](https://mistral.ai/pricing).

Vibe is Mistral's unified agent. It runs in three modes, each shaped for a different kind of task:

- **Work**: productivity mode in the Vibe web and mobile apps. Describe an outcome, Work picks the tools, runs the steps, and shows live todos. Use it for research, document analysis, data exploration, and scheduled tasks.
- **Code**: developer mode as a CLI, a VS Code extension, or remote Vibe Code Web sessions. Vibe Code reads your files, edits code, runs commands, and opens pull requests under your supervision.
- **Chat**: turn-based mode for quick conversations and legacy features migrated from Le Chat (Agents, Think mode, Deep Research, Code Interpreter, Memories).

[Open Vibe Work](https://chat.mistral.ai)

- [Get started with Vibe Work](https://docs.mistral.ai/vibe/work/get-started)

- [Get started with Vibe Code](https://docs.mistral.ai/vibe/code/overview)

- [Choose Chat, Work, or Code](https://docs.mistral.ai/vibe/choose-chat-work-code)

Studio is the developer console. Generate API keys, test prompts in the Playground, build and deploy agents, run evaluations, and monitor usage. Everything you need to ship AI applications on the Mistral API.

[Open Studio](https://console.mistral.ai)

- [Studio documentation](https://docs.mistral.ai/studio-api/overview)

- [Studio quickstarts](https://docs.mistral.ai/#quickstarts)

- [Developer quickstarts](https://docs.mistral.ai/#quickstarts)

Admin is the control plane for IT, security, and finance teams. Manage your organization's account, members, roles, Workspaces, billing, SSO, and security policies.

[Open Admin](https://admin.mistral.ai)

- [Admin documentation](https://docs.mistral.ai/admin/set-up-organization/create-organization)

- [Admin quickstarts](https://docs.mistral.ai/#quickstarts)

## Common questions {#common-questions}

### What's the difference between Vibe and Studio? {#whats-the-difference-between-vibe-and-studio}

Vibe is the end-user product. You use it to get things done, in the chat UI, in your editor, or in your terminal. Studio is the developer console. You use it to generate API keys, test prompts, run evaluations, and ship applications built on the Mistral API. Most organizations use both: knowledge workers in Vibe, developers in Studio.

### What's the difference between Vibe Work and Vibe Code? {#whats-the-difference-between-vibe-work-and-vibe-code}

Vibe Work runs in the Vibe web and mobile apps with a chat interface. Use it for productivity tasks: research, document analysis, scheduled tasks, Connectors, Skills, Projects.

Vibe Code runs as a CLI, a VS Code extension, or as a remote web session. Use it for tasks that depend on a codebase: reading files, editing code, running commands, opening pull requests.

Both are modes of the same agent. See [Choose Chat, Work, or Code](https://docs.mistral.ai/vibe/choose-chat-work-code) for a side-by-side comparison.

### I was using Le Chat. What changes for me? {#i-was-using-le-chat-what-changes-for-me}

Le Chat is now Vibe. Your account, plan, history, and settings carry over. The Chat tab in Vibe keeps the turn-based experience you're used to, and the legacy features (Agents, Think mode, Deep Research, Code Interpreter, Memories) are still available there. New work happens in **Work** mode, which adds tools, Connectors, Skills, and live todos. See the [Vibe overview](https://docs.mistral.ai/vibe/overview) for the migration details.

### Who should have the Billing role? {#who-should-have-the-billing-role}

Only the person responsible for financial operations, typically a finance team member or office manager. The Billing role grants access to subscriptions, invoices, and payment methods without exposing organization settings or user management. Most team members should be Admins or Members.

### Are Chat agents and Vibe Work Skills the same thing? {#are-chat-agents-and-vibe-work-skills-the-same-thing}

[Chat Agents](https://docs.mistral.ai/vibe/chat-legacy/agents) live in Vibe Chat as a legacy feature carried over from Le Chat. In Vibe Work, the equivalent concept is [Skills](https://docs.mistral.ai/vibe/work/skills): reusable methods you package once and apply across tasks. New work should use Skills. Agents are kept available for users who built workflows on them before the rebrand.
