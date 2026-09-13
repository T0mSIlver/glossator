---
url: https://docs.mistral.ai/vibe/code/overview
title: Vibe Code
breadcrumbs: [Vibe, Code]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/overview/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Vibe Code

Vibe Code is Vibe's **coding mode**. With read/write access to your filesystem, a shell, and a configurable set of tools, it can read files, run commands, write code, and open pull requests on your behalf, under your supervision.

Run Vibe Code against a local checkout via the [CLI](https://docs.mistral.ai/vibe/code/cli/install-setup) or the [VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate), or against a GitHub repository in a remote sandbox via [Vibe Code Web](https://docs.mistral.ai/vibe/code/vibe-code-web/get-started).

> **Info**
>
> You stay in the loop. Vibe Code surfaces its plan, requests approval before sensitive actions (shell commands, file writes, pull requests), and can be interrupted at any step. Behavior is configurable per agent and per environment, see [Safety, approvals, and permissions](https://docs.mistral.ai/vibe/code/safety-approvals-permissions).

## Why use Vibe Code {#why-use-vibe-code}

Common use cases:

- **Write code**: describe what you want to build, and Vibe Code applies changes that follow your project structure and conventions.
- **Explore and understand codebases**: ask Vibe Code to inspect files, explain architecture, and trace how systems fit together.
- **Review code**: find bugs, logic errors, missing edge cases, and risky changes before they ship.
- **Debug**: drop in an error, a failing test, or a stack trace, and let Vibe Code inspect the relevant context and propose a targeted fix.
- **Automate development tasks**: delegate repetitive work such as refactors, tests, migrations, setup tasks, and pull request preparation.

> **Tip**
>
> **Working outside the codebase?** Vibe Code is built primarily for source code work (files, repositories, commands, diffs, pull requests). For tasks that live across apps, documents, chats, meetings, or business tools, [Vibe Work](https://docs.mistral.ai/vibe/work/get-started) is usually a better fit.

## Set up Vibe Code {#set-up-vibe-code}

Pick the interface that fits your workflow:

- [Install the CLI](https://docs.mistral.ai/vibe/code/cli/install-setup) — Run Vibe Code from your terminal.

- [Install the VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate) — Use Vibe Code directly in VS Code.

- [Start a web session](https://docs.mistral.ai/vibe/code/vibe-code-web/get-started) — Run a cloud session on a GitHub repository.

> **Tip**
>
> Not sure where to start? Compare the [CLI, VS Code extension, and Vibe Code Web](https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions).
