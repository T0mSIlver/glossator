# mined2-050 (cross_page, 5 connector calls)

## Question

I have both a Vibe subscription and `MISTRAL_API_KEY` exported — which credential does the CLI use?

## Thinking

The user wants to know which credential the CLI uses when both a Vibe subscription and MISTRAL_API_KEY are present. I need to search the Mistral documentation for information about CLI authentication and credential precedence.

The first search didn't give me the specific information about credential precedence. Let me try a more targeted search focusing on CLI authentication and how it handles the MISTRAL_API_KEY environment variable.

I found some relevant hits about API keys and profiles. Let me read the full documentation page to understand the authentication flow better.

Now I need to check the configuration precedence documentation to understand how the CLI prioritizes different credential sources.

Let me also check the configuration reference to see if there are any details about how Vibe subscription credentials are handled.

Based on the documentation I've reviewed, I can now answer the user's question. The CLI uses environment variables (including MISTRAL_API_KEY) as the primary credential source, with precedence over other methods like the .env file. The Vibe subscription is used for browser-based sign-in, but when MISTRAL_API_KEY is explicitly exported, it takes precedence. I should provide a clear, direct answer with proper citations.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "CLI which credential is used when both Vibe subscription and MISTRAL_API_KEY are present", "max_hits": 5}
```

Result:

```
q: "CLI which credential is used when both Vibe subscription and MISTRAL_API_KEY are present"

[1] https://docs.mistral.ai/admin/billing-usage/subscriptions | section: mistral-code
    Subscriptions > Subscription > Mistral Code and Vibe Code
    Some Organizations still show Mistral Code seats. Mistral Code seats are legacy Enterprise seats for the coding assistant. Vibe Code covers the CLI, editor extensions, and coding workflows. If you need to change the number of Mistral Code Enterprise seats, contact Mistral.
    cite: https://docs.mistral.ai/admin/billing-usage/subscriptions#mistral-code

[2] https://docs.mistral.ai/admin/billing-usage/subscriptions | section: subscription
    Subscriptions > Subscription
    Use Subscription to review the Mistral plan, seats, included monthly usage, and pay-as-you-go settings active on your Organization. Mistral plans are global: the same plan applies across Vibe, Studio, and API usage. For the latest plan details, usage budgets, and model pricing, see [Mistral pricing](https://mistral.ai/pricing/).
    cite: https://docs.mistral.ai/admin/billing-usage/subscriptions

[3] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: step-2
    Install the Vibe CLI and send your first prompt > Step 2: Launch and configure
    1. Open a terminal in any project directory. 2. Run: ```bash vibe ``` ![Vibe CLI running in a terminal](https://docs.mistral.ai/assets/quickstarts/vibe/home.png) On first launch, the CLI runs a **setup wizard** to register your API key. By default it opens a browser to sign you in with your Mistral account; credentials are stored locally so you don't need to enter them again. For non-Mistral provi …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#step-2

[4] https://docs.mistral.ai/admin/billing-usage/subscriptions | section: pay-as-you-go
    Subscriptions > Subscription > Pay-as-you-go
    Pay-as-you-go lets you extend usage beyond the included monthly usage. It is not a separate API or Vibe plan. To enable pay-as-you-go, open [Admin Panel > Subscription](https://admin.mistral.ai/subscription). For exact model pricing, included usage, and feature availability, see [Mistral pricing](https://mistral.ai/pricing/).
    cite: https://docs.mistral.ai/admin/billing-usage/subscriptions#pay-as-you-go

[5] https://docs.mistral.ai/admin/billing-usage/subscriptions | section: open-subscriptions
    Subscriptions > Subscription > Open Subscription
    Open [Admin Panel > Subscription](https://admin.mistral.ai/subscription). In Subscription, you can review: - your Mistral plan and seats; - included monthly usage; - current estimated usage; - pay-as-you-go settings; - Mistral Code seats, when they apply.
    cite: https://docs.mistral.ai/admin/billing-usage/subscriptions#open-subscriptions

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/admin/billing-usage/subscriptions") to read hit 1 on its page
```

### 2. mistral_docs_search

```json
{"q": "Vibe CLI authentication MISTRAL_API_KEY environment variable precedence", "max_hits": 5}
```

Result:

```
q: "Vibe CLI authentication MISTRAL_API_KEY environment variable precedence"

[1] https://docs.mistral.ai/vibe/code/cli/api-keys-profiles | section: env-var
    API keys and profiles > Give the API key to the CLI > 2. Environment variable
    Export the key in your shell: ```bash export MISTRAL_API_KEY="your_mistral_api_key" ``` Environment variables take precedence over values stored in `~/.vibe/.env`.
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#env-var

[2] https://docs.mistral.ai/vibe/code/cli/configuration-reference | section: environment-variables
    Configuration reference > Environment variables
    Not `config.toml` keys, but part of the configuration model. They sit at precedence level 3 (env vars). | Variable | Purpose | |---|---| | `VIBE_HOME` | Overrides the `~/.vibe/` home directory for all state (config, prompts, agents, skills, logs) | | `MISTRAL_API_KEY` | Primary Mistral API key | | `<PROVIDER>_API_KEY` | API key referenced by a `[[providers]]` `api_key_env_var` (for example `OPENRO …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration-reference#environment-variables

[3] https://docs.mistral.ai/vibe/code/cli/configuration | section: precedence
    Configuration > Configuration precedence
    When the same setting is defined in multiple places, the CLI applies them in this order, from **highest to lowest priority**: 1. **Admin config**, when your Organization provides one. See [Admin config](https://docs.mistral.ai/vibe/code/cli/admin-config). 2. **Command-line flags** (for example, `--agent`, `--workdir`). 3. **Environment variables** (for example, `MISTRAL_API_KEY`, `VIBE_HOME`). 4. …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#precedence

[4] https://docs.mistral.ai/studio/workflows/building-workflows/workflows/determinism | section: precedence
    Determinism > Workflow Determinism > Precedence
    The decorator-level setting takes priority over the environment variable: | `@workflow.define(enforce_determinism=...)` | `DEFAULT_ENFORCE_DETERMINISM` | Result | |---|---|---| | `True` | any | sandboxed | | `False` | any | **not** sandboxed | | not set (default) | `1` / `True` (default) | sandboxed | | not set (default) | `0` / `False` | **not** sandboxed |
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/workflows/determinism#precedence

[5] https://docs.mistral.ai/studio/workflows/building-workflows/mistral_client | section: automatic-authentication
    Mistral client > Automatic authentication
    `get_mistral_client()` handles authentication automatically. It selects credentials in the following order: 1. **Explicit `api_key` argument** — if you pass `get_mistral_client(api_key="...")`, that key is used directly. 2. **Service Account token file** — if `MISTRAL_SA_TOKEN_PATH` is set, Service Account authentication is used instead of `MISTRAL_API_KEY`. 3. **`MISTRAL_API_KEY` environment vari …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/mistral_client#automatic-authentication

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/api-keys-profiles") to read hit 1 on its page
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/api-keys-profiles"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles | "API keys and profiles"

## section: api-keys-and-profiles
    API keys and profiles
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles
# API keys and profiles

Vibe Code CLI needs a **Mistral API key** to call hosted models. This page covers how to create the key, give it to the CLI, and switch keys between accounts or providers.

> **Info**
>
> **Browser-based sign-in is enabled by default** when your config targets a model with a Mistral provider. The flow provisions and stores credentials for you, so no API key is needed for typical Mistral-provider setups. This page remains useful for non-Mistral providers, automation, troubleshooting, or when you want to use a custom API key.

## section: where-to-create
    API keys and profiles > Where to create your API key
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#where-to-create
## Where to create your API key {#where-to-create}

Create your key from [Code › Vibe CLI](https://chat.mistral.ai/code/extensions). The same key works in Free mode, with a paid plan, or with pay-as-you-go enabled.

> **Tip**
>
> **Keep keys safe:**
>
> - **Use the least-privileged key** needed for the task.
> - **Rotate keys regularly** and revoke unused ones from the console.
> - **Never paste API keys** into prompts, logs, screenshots, or support tickets.

## section: give-key
    API keys and profiles > Give the API key to the CLI
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#give-key
## Give the API key to the CLI {#give-key}

The CLI supports **three ways** to provide your key, listed in order of precedence (highest first).

## section: interactive-setup
    API keys and profiles > Give the API key to the CLI > 1. Interactive setup (recommended)
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#interactive-setup
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

## section: env-var
    API keys and profiles > Give the API key to the CLI > 2. Environment variable
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#env-var
### 2. Environment variable {#env-var}

Export the key in your shell:

```bash
export MISTRAL_API_KEY="your_mistral_api_key"
```

Environment variables take precedence over values stored in `~/.vibe/.env`.

## section: env-file
    API keys and profiles > Give the API key to the CLI > 3. `.env` file
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#env-file
### 3. `.env` file {#env-file}

You can also edit `~/.vibe/.env` directly:

```bash
MISTRAL_API_KEY=your_mistral_api_key
```

The CLI loads `~/.vibe/.env` automatically on startup.

> **Note**
>
> The `.env` file is for **credentials only**. General CLI configuration belongs in `config.toml`. See [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration).

## section: switch-providers
    API keys and profiles > Switch between accounts or providers
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#switch-providers
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

## section: plan-billing
    API keys and profiles > Plan and billing notes
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#plan-billing
## Plan and billing notes {#plan-billing}

Mistral plans include monthly usage that is shared across Studio, the API, and Vibe Code. Vibe Code uses this included monthly usage before any pay-as-you-go charges apply.

After included monthly usage is exhausted, what happens next depends on your Organization settings:

- **Pay-as-you-go off**: Vibe Code can stop until the next billing period.
- **Pay-as-you-go on**: Vibe Code keeps working, and additional usage is billed pay-as-you-go.

Pay-as-you-go is off by default. Some Pro plans purchased through partners (Google, Apple, Free Mobile, Orange) cannot enable pay-as-you-go. On those plans, Vibe Code stops once included monthly usage is exhausted.

Results: 8 sections, the whole page.
```

### 4. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/configuration", "section": "precedence"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/configuration | "Configuration" | section: precedence

## section: precedence
    Configuration > Configuration precedence
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#precedence
## Configuration precedence {#precedence}

When the same setting is defined in multiple places, the CLI applies them in this order, from **highest to lowest priority**:

1. **Admin config**, when your Organization provides one. See [Admin config](https://docs.mistral.ai/vibe/code/cli/admin-config).
2. **Command-line flags** (for example, `--agent`, `--workdir`).
3. **Environment variables** (for example, `MISTRAL_API_KEY`, `VIBE_HOME`).
4. **Project** `./.vibe/config.toml`.
5. **User** `~/.vibe/config.toml`.

Results: the whole section.
```

### 5. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/configuration-reference", "section": "environment-variables"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/configuration-reference | "Configuration reference" | section: environment-variables

## section: environment-variables
    Configuration reference > Environment variables
    cite: https://docs.mistral.ai/vibe/code/cli/configuration-reference#environment-variables
## Environment variables {#environment-variables}

Not `config.toml` keys, but part of the configuration model. They sit at precedence level 3 (env vars).

| Variable | Purpose |
|---|---|
| `VIBE_HOME` | Overrides the `~/.vibe/` home directory for all state (config, prompts, agents, skills, logs) |
| `MISTRAL_API_KEY` | Primary Mistral API key |
| `<PROVIDER>_API_KEY` | API key referenced by a `[[providers]]` `api_key_env_var` (for example `OPENROUTER_API_KEY`) |

See [Configuration precedence](https://docs.mistral.ai/vibe/code/cli/configuration#precedence) and [Admin config](https://docs.mistral.ai/vibe/code/cli/admin-config) for how these layers combine.

Results: the whole section.
```

## Answer

The Vibe CLI uses the **`MISTRAL_API_KEY` environment variable** when it is exported.

Environment variables (including `MISTRAL_API_KEY`) take precedence over the key stored in `~/.vibe/.env` (from interactive setup) and are the primary way the CLI authenticates for Mistral-provider models when no admin config or command-line flag overrides them.
[Environment variable precedence](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#env-var)
[Configuration precedence](https://docs.mistral.ai/vibe/code/cli/configuration#precedence)
[MISTRAL_API_KEY as primary API key](https://docs.mistral.ai/vibe/code/cli/configuration-reference#environment-variables)

