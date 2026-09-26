---
url: https://docs.mistral.ai/getting-started/platform-overview
title: Platform overview
breadcrumbs: [Getting started]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/platform-overview/page.mdx
source_commit: bee3023d26c331c00fa6c24bc746ef4cf5e97031
---

# Platform overview

Mistral AI has three products. Pick the one that matches what you want to do.

- **Vibe**: the unified agent for productivity and coding. Chat with it on the web or mobile, or run it in your terminal and editor.
- **Studio**: the developer console and Mistral API. Generate keys, prototype in the Playground, build durable workflows, and call text, audio, and OCR models from a single SDK.
- **Admin**: the control plane for organization setup, billing, SSO, workspaces, and access policies.

> **Tip**
>
> For a side-by-side feature and plan comparison across products, see the [pricing page](https://mistral.ai/pricing).

Vibe is Mistral's unified agent. It runs in two modes, each shaped for a different kind of task:

- **Work**: the unified experience in the Vibe web and mobile apps. Ask a quick question or describe an outcome; Work picks the tools, runs the steps, and shows live todos. A **fast/think toggle** switches between quick conversational responses and deeper, agentic workflows. Use it for conversations, research, document analysis, data exploration, and scheduled tasks.
- **Code**: developer mode as a CLI, a VS Code extension, or remote Vibe Code Web sessions. Vibe Code reads your files, edits code, runs commands, and opens pull requests under your supervision.

The separate **Chat** tab is being removed progressively, starting with self-serve plans, so there's one surface and no more choosing between tabs; Enterprise organizations may still see it during a six-month migration window. See the [Vibe overview](https://docs.mistral.ai/vibe) for details.

[Open Vibe Work](https://chat.mistral.ai)

- [Get started with Vibe Work](https://docs.mistral.ai/vibe/work/get-started)

- [Get started with Vibe Code](https://docs.mistral.ai/vibe/code/overview)

- [Choose Work or Code](https://docs.mistral.ai/vibe/choose-chat-work-code)

Studio is the developer console. Generate API keys, test prompts in the Playground, build and deploy agents, run evaluations, and monitor usage. Everything you need to ship AI applications on the Mistral API.

[Open Studio](https://console.mistral.ai)

- [Studio documentation](https://docs.mistral.ai/studio)

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

Both are modes of the same agent. See [Choose Work or Code](https://docs.mistral.ai/vibe/choose-chat-work-code) for a side-by-side comparison.

### I was using Le Chat. What changes for me? {#i-was-using-le-chat-what-changes-for-me}

Le Chat is now Vibe. Your account, plan, history, and settings carry over, and [chat.mistral.ai](https://chat.mistral.ai) remains the entry point. The separate Chat tab is being removed progressively, starting with self-serve plans: quick conversations now happen in **Work**, the unified experience, with a **fast/think toggle** to switch between quick responses and deeper agentic workflows — one surface for everything, and no more guessing which tab a task belongs to. If you relied on Agents, use [Skills](https://docs.mistral.ai/vibe/work/skills) instead — invoke them with `@`. Enterprise organizations may still see the Chat tab during a six-month migration window. See the [Vibe overview](https://docs.mistral.ai/vibe) for details.

### Who should have the Billing role? {#who-should-have-the-billing-role}

Only the person responsible for financial operations, typically a finance team member or office manager. The Billing role grants access to subscriptions, invoices, and payment methods without exposing organization settings or user management. Most team members should be Admins or Members.

### Are Chat agents and Vibe Work Skills the same thing? {#are-chat-agents-and-vibe-work-skills-the-same-thing}

[Chat Agents](https://docs.mistral.ai/vibe/chat-legacy/agents) were the legacy equivalent of [Skills](https://docs.mistral.ai/vibe/work/skills): reusable methods you package once and apply across tasks. For anything you did with Agents, use Skills — invoke them with `@` in the unified experience. The legacy Chat tab remains available only to some Enterprise organizations during the six-month migration window.
