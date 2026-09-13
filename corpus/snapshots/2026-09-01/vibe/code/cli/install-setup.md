---
url: https://docs.mistral.ai/vibe/code/cli/install-setup
title: Install and setup
breadcrumbs: [Vibe, Code, CLI]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/cli/install-setup/page.mdx
source_commit: 0c66041e3f05a5820976e058e9e305b744e4f045
---

# Install and setup

Install the Vibe CLI, run `vibe` in your project, and complete the setup prompt.

## Install the CLI {#install}

**macOS / Linux**

Use the one-line installer:

```bash
curl -LsSf https://mistral.ai/vibe/install.sh | bash
```

The installer:

- Checks whether `uv` is installed and installs it if needed.
- Installs or upgrades `mistral-vibe` with `uv tool install` or `uv tool upgrade`.
- Makes the `vibe` and `vibe-acp` commands available, provided your `PATH` is configured.

If the installer reports that `vibe` is not on your `PATH`, add the displayed directory to your shell profile and restart your terminal.

**Manual install**

Use manual installation when you prefer to manage Python tools yourself.

With `uv`:

```bash
uv tool install mistral-vibe
```

Or with `pip`:

```bash
pip install mistral-vibe
```

**Windows**

Install `uv` first:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then install Vibe:

```powershell
uv tool install mistral-vibe
```

> **Tip**
>
> **On a different interface?** This page covers the **CLI** specifically. If you'd rather work inside your editor or against a remote repo, jump to [VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate) or [Vibe Code Web](https://docs.mistral.ai/vibe/code/vibe-code-web/get-started). See [Choose CLI, VS Code, or web sessions](https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions) for a side-by-side comparison.

## Start Vibe in your project {#start}

Open a terminal in your project root and run:

```bash
vibe
```

On first launch, Vibe:

- Creates a default configuration file at `~/.vibe/config.toml` if it does not already exist.
- Walks you through a **setup wizard** to register your API key.

## Choose your access path {#choose-access-path}

The setup wizard asks you to sign in or provide an [API key](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles):

- **Sign in with a Mistral account**: use your Mistral plan. Vibe Code is included, with usage and rate limits based on your plan and pay-as-you-go settings.
- **Use a custom API key**: generate a key from [Code > Vibe CLI](https://chat.mistral.ai/code/extensions) or use a key from another compatible provider.

Paste your API key when prompted. The wizard saves it for future sessions in the Vibe home directory. You can also set `MISTRAL_API_KEY` in your shell environment if you prefer not to use the interactive prompt.

> **Tip**
>
> You can rerun the setup wizard at any time using `vibe --setup`.

## Verify the setup {#verify}

Your setup is ready when:

- `vibe --version` returns a version.
- `vibe` opens the interactive terminal interface from your project root.
- Vibe accepts a prompt without asking for an API key again.

Try a small first prompt:

```text
Find TODO comments in this project.
```

## Reset your configuration {#reset-config}

If the CLI fails to start or behaves unexpectedly after editing the config, move the file aside and restart Vibe. A fresh `~/.vibe/config.toml` is generated on the next launch:

```bash
mv ~/.vibe/config.toml ~/.vibe/config.toml.bkp
vibe
```

## Prerequisites {#prerequisites}

Before you install the CLI, make sure you have:

- **Python 3.12 or later** for manual installation.
- *(Optional)* a **Mistral account** to use Mistral-hosted models. The CLI also works fully offline with [local models](https://docs.mistral.ai/vibe/code/cli/offline-models), or against any compatible API key you provide.

If you choose to use Mistral-hosted models, sign in with your Mistral account during setup. For non-Mistral providers or automation, create an API key from [Code > Vibe CLI](https://chat.mistral.ai/code/extensions). The same key works in Free mode, with a paid plan, or with pay-as-you-go enabled.
