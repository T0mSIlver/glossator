---
url: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles
title: API keys and profiles
breadcrumbs: [Vibe, Code, CLI]
kind: doc
locale: en
source_path: src/content/en/docs/vibe/code/cli/api-keys-profiles/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# API keys and profiles

Vibe Code CLI needs a **Mistral API key** to call hosted models. This page covers how to create the key, give it to the CLI, and switch keys between accounts or providers.

> **Info**
>
> **Browser-based sign-in is enabled by default** when your config targets a model with a Mistral provider. The flow provisions and stores credentials for you, so no API key is needed for typical Mistral-provider setups. This page remains useful for non-Mistral providers, automation, troubleshooting, or when you want to use a custom API key.

## Where to create your API key {#where-to-create}

Where you create your API key depends on your plan:

- **Mistral plan users** (Free, Pro, or higher, including partner-distributed Pro plans through Google, Apple, Free Mobile, or Orange): create your key from [Code › Vibe CLI](https://chat.mistral.ai/code/extensions).
- **Pay-as-you-go API access (Free mode or Scale plan)**: create your key from [API keys](https://console.mistral.ai/home?profile_dialog=api-keys).

> **Tip**
>
> **Keep keys safe:**
>
> - **Use the least-privileged key** needed for the task.
> - **Rotate keys regularly** and revoke unused ones from the console.
> - **Never paste API keys** into prompts, logs, screenshots, or support tickets.

## Give the API key to the CLI {#give-key}

The CLI supports **three ways** to provide your key, listed in order of precedence (highest first).

### 1. Interactive setup (recommended) {#interactive-setup}

On first run, the CLI starts a setup flow if it cannot find a key:

```bash
vibe
```

You can also rerun the setup at any time:

```bash
vibe --setup
```

The setup flow saves your key to `~/.vibe/.env` for future sessions.

### 2. Environment variable {#env-var}

Export the key in your shell:

```bash
export MISTRAL_API_KEY="your_mistral_api_key"
```

Environment variables take precedence over values stored in `~/.vibe/.env`.

### 3. `.env` file {#env-file}

You can also edit `~/.vibe/.env` directly:

```bash
MISTRAL_API_KEY=your_mistral_api_key
```

The CLI loads `~/.vibe/.env` automatically on startup.

> **Note**
>
> The `.env` file is for **credentials only**. General CLI configuration belongs in `config.toml`. See [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration).

## Switch between accounts or providers {#switch-providers}

The CLI supports multiple providers and models through **presets** in `config.toml`. Use this to switch between, for example, a Mistral key for production work and a key from another OpenAI-compatible provider for experiments.

Define a provider preset and a model preset:

```toml
[[providers]]
name = "openrouter"
api_base = "https://openrouter.ai/api/v1"
api_key_env_var = "OPENROUTER_API_KEY"
api_style = "openai"
backend = "generic"

[[models]]
name = "mistralai/devstral-2512:free"
provider = "openrouter"
alias = "devstral-openrouter"
temperature = 0.2
input_price = 0.0
output_price = 0.0
```

Set the active model:

```toml
active_model = "devstral-openrouter"
```

Then export the matching API key:

```bash
export OPENROUTER_API_KEY="your_openrouter_api_key"
```

You can also change the active model at any time inside the CLI with `/config` or `/model`.

## Plan and billing notes {#plan-billing}

Vibe Pro plans include a **monthly Vibe budget**. Once exhausted, what happens next depends on a toggle in the Admin Panel under [Subscriptions › Vibe subscription](https://admin.mistral.ai/subscriptions):

- **Toggle off (default)**: Vibe is disabled until the next billing period.
- **Toggle on**: Vibe keeps working and additional usage is billed pay-as-you-go.

This toggle is **off by default** on all subscriptions and **cannot be enabled on Vibe Pro plans purchased through partners** (Google, Apple, Free Mobile, Orange). On those plans, Vibe is disabled once the included budget is reached.
