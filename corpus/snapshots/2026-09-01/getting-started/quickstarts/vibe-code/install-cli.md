---
url: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli
title: Install the Vibe CLI and send your first prompt
breadcrumbs: [Getting started, Quickstarts, Vibe Code]
kind: doc
locale: en
source_path: src/content/en/docs/getting-started/quickstarts/vibe-code/install-cli/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Install the Vibe CLI and send your first prompt

Install the [Vibe CLI](https://docs.mistral.ai/vibe/code/overview), register your API key, and send your first prompt directly from the terminal.

- **One-line install**: get the CLI running in seconds on macOS or Linux.
- **Setup wizard**: register your API key on first launch.
- **Send a prompt**: have Vibe read your project and respond in the terminal.

By the end you'll have the Vibe CLI installed, configured, and responding to prompts in your terminal.

**Time to complete:** ~5 minutes

## Prerequisites {#prerequisites}

- macOS, Linux, or Windows.
- Python 3.12 or later (for manual install).
- *(Optional)* a Mistral account if you want to use Mistral-hosted models. The CLI also works fully [offline with local models](https://docs.mistral.ai/vibe/code/cli/offline-models) or against any OpenAI-compatible API key you provide. See [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles) for the full provider matrix.

> **Tip**
>
> On a different interface? See the [VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate) or [Vibe Code Web](https://docs.mistral.ai/vibe/code/vibe-code-web/get-started) guides.

## Step 1: Install the CLI {#step-1}

**One-liner (macOS/Linux)**

Run this in your terminal:

```bash
curl -LsSf https://mistral.ai/vibe/install.sh | bash
```

The installer checks `uv` (Astral's Python tool installer), installs or upgrades `mistral-vibe`, and makes the `vibe` and `vibe-acp` commands available, provided your `PATH` is configured.

**Manual install (macOS/Linux/Windows)**

If you prefer manual setup, or you're on Windows:

1. Confirm Python 3.12+ is installed: `python3 --version`.
2. Install with your preferred package manager:

```bash
# With uv (recommended)
uv tool install mistral-vibe

# With pip
pip install mistral-vibe
```

For Windows, install `uv` first via PowerShell, then run `uv tool install mistral-vibe`. See [Install and setup](https://docs.mistral.ai/vibe/code/cli/install-setup) for the full per-platform instructions.

## Step 2: Launch and configure {#step-2}

1. Open a terminal in any project directory.
2. Run:

```bash
vibe
```

![Vibe CLI running in a terminal](https://docs.mistral.ai/assets/quickstarts/vibe/home.png)

On first launch, the CLI runs a **setup wizard** to register your API key. By default it opens a browser to sign you in with your Mistral account; credentials are stored locally so you don't need to enter them again.

For non-Mistral providers or automation, paste an API key instead. Generate one from [Code › Vibe CLI](https://chat.mistral.ai/code/extensions). The same key works in Free mode, with a paid plan, or with pay-as-you-go enabled.

![Sign in on first launch](https://docs.mistral.ai/assets/quickstarts/vibe/api-key.png)

> **Tip**
>
> You can re-run the wizard anytime with `vibe --setup`.

> **Note**
>
> If you run `vibe` for the first time in a non-empty project containing a `.vibe/` directory, the CLI asks whether you trust the folder before loading any local configuration. See [Trusted folders](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders).

## Step 3: Send your first prompt {#step-3}

Type a request directly in the prompt. For example:

> List the files in this directory and explain what each one does.

The CLI reads your project context and responds with relevant information. It can also generate code, edit files, and run shell commands when you approve.

![Sending a query to the Vibe CLI](https://docs.mistral.ai/assets/quickstarts/vibe/query.png)

To run a shell command directly from the CLI, prefix it with `!`. For example: `!ls` or `!git status`.

## Verify {#verify}

You've completed the setup if:

1. `vibe --version` returns a version number.
2. You're signed in (or your API key is registered).
3. The CLI responds to prompts with context-aware answers.

## What's next {#whats-next}

- [Scaffold a project with Vibe Code](https://docs.mistral.ai/getting-started/quickstarts/vibe-code/scaffold-a-project)

- [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles) — Switch providers, manage keys per profile.

- [Choose CLI, VS Code, or web sessions](https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions)

- [CLI install and setup reference](https://docs.mistral.ai/vibe/code/cli/install-setup)
