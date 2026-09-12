# mined2-050 (cross_page, 7 connector calls)

## Question

I have both a Vibe subscription and `MISTRAL_API_KEY` exported — which credential does the CLI use?

## Thinking

The user is asking which credential the CLI uses when both a Vibe subscription and MISTRAL_API_KEY are available. This is a specific technical question about the Mistral CLI's authentication behavior. I need to search the documentation to find information about credential precedence or priority. Let me search for relevant documentation about CLI authentication and environment variables.

The first search returned information about subscriptions but not specifically about CLI credential precedence. I need to search more specifically for CLI authentication behavior. Let me try a more targeted search about the CLI's authentication mechanism.

Good, I found a relevant page about API keys and profiles. This might contain information about how the CLI handles authentication. Let me read this page to understand the precedence.

The page I read mentions API keys and profiles, but I need to understand the relationship between Vibe subscription credentials and MISTRAL_API_KEY. The documentation mentions that browser-based sign-in is enabled by default for Mistral provider setups, which provisions and stores credentials. But the user is asking specifically about when both are present. Let me search for more information about how Vibe subscriptions work with the CLI.

I need to find the configuration precedence documentation. The search results mention a configuration precedence page. Let me read that to understand the order of precedence for different credential sources.

Now I have information about configuration precedence. The documentation shows that environment variables (including MISTRAL_API_KEY) have higher precedence than config files. However, I need to understand how browser-based sign-in credentials fit into this picture. Let me search specifically for information about browser-based sign-in and how it relates to the MISTRAL_API_KEY environment variable.

Let me read the quickstart documentation to see if it clarifies the relationship between browser-based sign-in and environment variables.

Based on my research, I now have enough information to answer the user's question. Let me synthesize what I've found:

1. The Vibe CLI uses browser-based sign-in by default for Mistral provider setups, which provisions and stores credentials locally (in ~/.vibe/.env)
2. The CLI supports three ways to provide a key, in order of precedence: interactive setup (browser-based), environment variable (MISTRAL_API_KEY), and .env file
3. Environment variables take precedence over values stored in ~/.vibe/.env
4. The configuration precedence order is: Admin config > Command-line flags > Environment variables > Project config > User config

The key insight is that browser-based sign-in credentials are stored in ~/.vibe/.env, and environment variables have higher precedence than .env files. Therefore, when both a Vibe subscription (which uses browser-based sign-in and stores credentials in ~/.vibe/.env) and MISTRAL_API_KEY are present, the CLI will use the MISTRAL_API_KEY environment variable.

The answer should be clear and direct, with proper citations to the documentation.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "CLI which credential is used when both Vibe subscription and MISTRAL_API_KEY are set"}
```

Result:

```
q: "CLI which credential is used when both Vibe subscription and MISTRAL_API_KEY are set"

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

[5] https://docs.mistral.ai/admin/identity-access/workload-identity | section: add-credential
    Workload identity federation > Add a workload identity credential
    The credential records which subject can authenticate as the service account. You do not type the subject in: the platform reads it from a token that the trusted issuer signed for that workload, which is what proves you control it. 1. Open the service account and click **Add new authentication**. 2. In the **Add credential** dialog, choose **Workload identity federation**. 3. Select a **Trusted is …
    cite: https://docs.mistral.ai/admin/identity-access/workload-identity#add-credential

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/admin/billing-usage/subscriptions") to read hit 1 on its page
```

### 2. mistral_docs_search

```json
{"q": "Vibe CLI authentication MISTRAL_API_KEY environment variable"}
```

Result:

```
q: "Vibe CLI authentication MISTRAL_API_KEY environment variable"

[1] https://docs.mistral.ai/vibe/code/cli/api-keys-profiles | section: env-var
    API keys and profiles > Give the API key to the CLI > 2. Environment variable
    Export the key in your shell: ```bash export MISTRAL_API_KEY="your_mistral_api_key" ``` Environment variables take precedence over values stored in `~/.vibe/.env`.
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#env-var

[2] https://docs.mistral.ai/vibe/code/cli/configuration-reference | section: environment-variables
    Configuration reference > Environment variables
    Not `config.toml` keys, but part of the configuration model. They sit at precedence level 3 (env vars). | Variable | Purpose | |---|---| | `VIBE_HOME` | Overrides the `~/.vibe/` home directory for all state (config, prompts, agents, skills, logs) | | `MISTRAL_API_KEY` | Primary Mistral API key | | `<PROVIDER>_API_KEY` | API key referenced by a `[[providers]]` `api_key_env_var` (for example `OPENRO …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration-reference#environment-variables

[3] https://docs.mistral.ai/studio/workflows/building-workflows/mistral_client | section: automatic-authentication
    Mistral client > Automatic authentication
    `get_mistral_client()` handles authentication automatically. It selects credentials in the following order: 1. **Explicit `api_key` argument** — if you pass `get_mistral_client(api_key="...")`, that key is used directly. 2. **Service Account token file** — if `MISTRAL_SA_TOKEN_PATH` is set, Service Account authentication is used instead of `MISTRAL_API_KEY`. 3. **`MISTRAL_API_KEY` environment vari …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/mistral_client#automatic-authentication

[4] https://docs.mistral.ai/admin/admin-api/authentication | section: make-a-request
    Authentication > Authentication and Admin API keys > Make a request
    Send Admin API requests to the Admin API base URL and pass your Admin API key in the `x-api-key` header. - **Base URL**: `https://api.mistral.ai/v1/admin` - **Authentication header**: `x-api-key: <ADMIN_API_KEY>` Set the key as an environment variable before you make requests: ```bash export ADMIN_API_KEY="your-admin-api-key" ``` Then call an endpoint. For example, list users in the Organization t …
    cite: https://docs.mistral.ai/admin/admin-api/authentication#make-a-request

[5] https://docs.mistral.ai/vibe/code/cli/api-keys-profiles | section: env-file
    API keys and profiles > Give the API key to the CLI > 3. `.env` file
    You can also edit `~/.vibe/.env` directly: ```bash MISTRAL_API_KEY=your_mistral_api_key ``` The CLI loads `~/.vibe/.env` automatically on startup. > **Note** > > The `.env` file is for **credentials only**. General CLI configuration belongs in `config.toml`. See [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration).
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#env-file

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

### 4. mistral_docs_search

```json
{"q": "Vibe CLI browser-based sign-in credentials precedence over MISTRAL_API_KEY"}
```

Result:

```
q: "Vibe CLI browser-based sign-in credentials precedence over MISTRAL_API_KEY"

[1] https://docs.mistral.ai/vibe/code/cli/api-keys-profiles | section: api-keys-and-profiles
    API keys and profiles
    Vibe Code CLI needs a **Mistral API key** to call hosted models. This page covers how to create the key, give it to the CLI, and switch keys between accounts or providers. > **Info** > > **Browser-based sign-in is enabled by default** when your config targets a model with a Mistral provider. The flow provisions and stores credentials for you, so no API key is needed for typical Mistral-provider se …
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles

[2] https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate | section: authenticate
    Install and authenticate > Authenticate
    The first time the extension needs credentials, it opens a **terminal setup flow**: 1. Start setup from the extension when prompted. 2. In the **Mistral Vibe Setup** terminal, paste your Mistral API key. 3. Complete the prompt and wait for the extension to return to the ready state. The setup flow runs the bundled Vibe agent with `--setup`. It stores credentials in the Vibe home directory for futu …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate#authenticate

[3] https://docs.mistral.ai/vibe/code/cli/api-keys-profiles | section: env-var
    API keys and profiles > Give the API key to the CLI > 2. Environment variable
    Export the key in your shell: ```bash export MISTRAL_API_KEY="your_mistral_api_key" ``` Environment variables take precedence over values stored in `~/.vibe/.env`.
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#env-var

[4] https://docs.mistral.ai/vibe/code/cli/configuration | section: precedence
    Configuration > Configuration precedence
    When the same setting is defined in multiple places, the CLI applies them in this order, from **highest to lowest priority**: 1. **Admin config**, when your Organization provides one. See [Admin config](https://docs.mistral.ai/vibe/code/cli/admin-config). 2. **Command-line flags** (for example, `--agent`, `--workdir`). 3. **Environment variables** (for example, `MISTRAL_API_KEY`, `VIBE_HOME`). 4. …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#precedence

[5] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: step-2
    Install the Vibe CLI and send your first prompt > Step 2: Launch and configure
    1. Open a terminal in any project directory. 2. Run: ```bash vibe ``` ![Vibe CLI running in a terminal](https://docs.mistral.ai/assets/quickstarts/vibe/home.png) On first launch, the CLI runs a **setup wizard** to register your API key. By default it opens a browser to sign you in with your Mistral account; credentials are stored locally so you don't need to enter them again. For non-Mistral provi …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#step-2

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/api-keys-profiles") to read hit 1 on its page
```

### 5. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/configuration"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/configuration | "Configuration"

## section: configuration
    Configuration
    cite: https://docs.mistral.ai/vibe/code/cli/configuration
# Configuration

The Vibe Code CLI is configured through a **`config.toml` file**. This page explains where the file lives, how to open it, and the most common settings you'll touch.

> **Info**
>
> For an exhaustive list of every key in `config.toml` and the agent-definition files, see the [Configuration reference](https://docs.mistral.ai/vibe/code/cli/configuration-reference).

## section: file-locations
    Configuration > Configuration file locations
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#file-locations
## Configuration file locations {#file-locations}

The CLI looks for `config.toml` in this order:

1. `./.vibe/config.toml` in the current working directory (**project-level**).
2. `~/.vibe/config.toml` in your home directory (**user-level**).

Project-level configuration takes precedence over user-level configuration. Project configuration is loaded only when the working directory is [trusted](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders).

## section: open
    Configuration > Open your configuration file
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#open
## Open your configuration file {#open}

Open `~/.vibe/config.toml` with your default editor:

```bash
# macOS
open ~/.vibe/config.toml

# Linux
xdg-open ~/.vibe/config.toml

# Windows (PowerShell)
Invoke-Item ~\.vibe\config.toml
```

You can also open the configuration menu from inside a session with the `/config` slash command.

## section: vibe-home
    Configuration > Vibe home directory
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#vibe-home
## Vibe home directory {#vibe-home}

By default, the CLI stores its configuration and state in `~/.vibe/`. Override the location with the `VIBE_HOME` environment variable:

```bash
export VIBE_HOME="/path/to/custom/vibe/home"
```

`VIBE_HOME` affects the location of:

- `config.toml`: main configuration.
- `.env`: API keys and provider credentials.
- `agents/`: custom agent profiles.
- `prompts/`: custom system prompts.
- `skills/`: custom skills.
- `tools/`: custom tools.
- `logs/`: session and application logs.

## section: working-directory
    Configuration > Working directory
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#working-directory
## Working directory {#working-directory}

Use `--workdir` to point the CLI at a project that is not your current directory:

```bash
vibe --workdir /path/to/project
```

Use `--add-dir` to give the CLI read access to an extra directory for a single session.

## section: common-sections
    Configuration > Common configuration sections
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#common-sections
## Common configuration sections {#common-sections}

`config.toml` accepts many top-level keys and table sections. The most common ones are listed here, each one linking to a dedicated page.

## section: default-agent
    Configuration > Common configuration sections > Default agent
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#default-agent
### Default agent {#default-agent}

Set the default interactive agent:

```toml
default_agent = "plan"
```

This applies to interactive sessions only. Programmatic mode falls back to `auto-approve` when `--agent` is not provided. See [Agents](https://docs.mistral.ai/vibe/code/cli/agents).

## section: providers-models
    Configuration > Common configuration sections > Providers and models
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#providers-models
### Providers and models {#providers-models}

Define provider presets, model presets, and the active model.

The following chat-capable models are available through Mistral's API (la Plateforme). Use the **model ID** as the `name` value in a `[[models]]` block, or pass it directly with `--model`:

| Model | Model ID | Best for |
|---|---|---|
| Mistral Medium 3.5 (recommended) | `mistral-medium-latest` | Flagship reasoning and code |
| Z.ai GLM 5.2 | `zai-glm-5-2` | Advanced reasoning and code |
| Mistral Large 3 | `mistral-large-latest` | Complex tasks, large context |
| Mistral Small 4 | `mistral-small-latest` | Fast, cost-effective general use |
| Codestral | `codestral-latest` | Code generation and completion |
| Ministral 3 14B | `ministral-14b-latest` | Balanced edge model |
| Ministral 3 8B | `ministral-8b-latest` | Lightweight edge model |
| Ministral 3 3B | `ministral-3b-latest` | Smallest edge model |

You can also pin to a specific version by replacing `-latest` with a date suffix (for example, `mistral-medium-3-5` or `codestral-2508`). See the [models overview](https://docs.mistral.ai/models) for all available versions.

To use a model through a third-party provider such as OpenRouter, define a custom provider and model preset:

```toml
active_model = "codestral-openrouter"

[[providers]]
name = "openrouter"
api_base = "https://openrouter.ai/api/v1"
api_key_env_var = "OPENROUTER_API_KEY"
api_style = "openai"
backend = "generic"

[[models]]
name = "mistralai/codestral"
provider = "openrouter"
alias = "codestral-openrouter"
```

See [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles).

## section: mcp-servers
    Configuration > Common configuration sections > MCP servers
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#mcp-servers
### MCP servers {#mcp-servers}

Add Model Context Protocol servers under `mcp_servers`. See [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers).

## section: skills
    Configuration > Common configuration sections > Skills
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#skills
### Skills {#skills}

Enable, disable, or add skill paths:

```toml
skill_paths = ["/path/to/custom/skills"]
enabled_skills = ["code-review", "test-*"]
disabled_skills = ["experimental-*"]
```

`enabled_skills` and `disabled_skills` interact as follows:

- If `enabled_skills` is **set and non-empty**, only skills whose name matches a pattern in that list are available.
- Otherwise, every discovered skill is available, minus any skill whose name matches a pattern in `disabled_skills`.

See [Skills](https://docs.mistral.ai/vibe/code/cli/skills).

## section: tool-permissions
    Configuration > Common configuration sections > Tool permissions and filters
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#tool-permissions
### Tool permissions and filters {#tool-permissions}

Restrict which tools the agent can use:

```toml
enabled_tools = ["serena_*"]
disabled_tools = ["mcp_*", "grep"]
```

Tool filters support **exact names**, **glob patterns**, and **regex** with the `re:` prefix. Per-tool permissions can also be set in `[tools.<tool_name>]` blocks. See [Safety, approvals, and permissions](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#tool-permissions).

## section: hooks
    Configuration > Common configuration sections > Hooks
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#hooks
### Hooks {#hooks}

Run arbitrary shell commands before or after tool calls, or after each assistant turn, to gate, audit, or rewrite agent behavior. Declare hooks in a separate `hooks.toml` file. See [Hooks](https://docs.mistral.ai/vibe/code/cli/hooks).

## section: updates-telemetry
    Configuration > Common configuration sections > Update and telemetry settings
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#updates-telemetry
### Update and telemetry settings {#updates-telemetry}

Control auto-updates, notifications, and telemetry:

```toml
enable_auto_update = true
enable_notifications = true
enable_telemetry = true
```

| Setting | Default | Details |
|---|---|---|
| `enable_auto_update` | `true` | Vibe checks for new releases and updates itself in the background. **We strongly recommend keeping this enabled** so you always run the latest fixes. You can also rerun the install script at any time to update manually. |
| `enable_notifications` | `true` | OS-level notifications when Vibe finishes a long-running task or needs your input (for example, when an approval prompt is waiting). |
| `enable_telemetry` | `true` | Sends anonymous usage and error telemetry to Mistral. Used to improve the product (crash diagnostics, feature usage, performance). No prompts, file contents, or model outputs are sent. Disable if you require an offline-only setup. |

## section: admin-config
    Configuration > Admin-managed configuration
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#admin-config
## Admin-managed configuration {#admin-config}

Your Organization can distribute a Vibe Code CLI configuration to all users. Admin-managed settings take precedence over command-line flags, environment variables, and the project and user `config.toml` files.

When admin config is active:

- Admin-managed settings in `/config` appear dim with a `⚿` lock glyph and list `your administrator` as the origin. A legend at the bottom of the screen reads `⚿ Settings are managed by your organization`.
- Admin-managed fields are read-only in `/config`. Attempts to edit or reset them have no effect. If you switch models while `active_model` is admin-managed, the model picker shows a warning.
- The CLI fetches admin config at the start of each session and keeps it in memory. It never writes admin config to your local `config.toml`.

> **Info**
>
> Admin config is a distribution mechanism, not a security control. Users who control their local CLI environment can bypass its settings. Administrators must enable this Organization-level feature. See [Admin config](https://docs.mistral.ai/vibe/code/cli/admin-config) for setup and rollout instructions.

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

Results: 15 sections, the whole page.
```

### 6. mistral_docs_search

```json
{"q": "Vibe CLI browser-based sign-in credentials stored location and precedence"}
```

Result:

```
q: "Vibe CLI browser-based sign-in credentials stored location and precedence"

[1] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: step-2
    Install the Vibe CLI and send your first prompt > Step 2: Launch and configure
    1. Open a terminal in any project directory. 2. Run: ```bash vibe ``` ![Vibe CLI running in a terminal](https://docs.mistral.ai/assets/quickstarts/vibe/home.png) On first launch, the CLI runs a **setup wizard** to register your API key. By default it opens a browser to sign you in with your Mistral account; credentials are stored locally so you don't need to enter them again. For non-Mistral provi …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#step-2

[2] https://docs.mistral.ai/vibe/code/cli/api-keys-profiles | section: api-keys-and-profiles
    API keys and profiles
    Vibe Code CLI needs a **Mistral API key** to call hosted models. This page covers how to create the key, give it to the CLI, and switch keys between accounts or providers. > **Info** > > **Browser-based sign-in is enabled by default** when your config targets a model with a Mistral provider. The flow provisions and stores credentials for you, so no API key is needed for typical Mistral-provider se …
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles

[3] https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate | section: authenticate
    Install and authenticate > Authenticate
    The first time the extension needs credentials, it opens a **terminal setup flow**: 1. Start setup from the extension when prompted. 2. In the **Mistral Vibe Setup** terminal, paste your Mistral API key. 3. Complete the prompt and wait for the extension to return to the ready state. The setup flow runs the bundled Vibe agent with `--setup`. It stores credentials in the Vibe home directory for futu …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate#authenticate

[4] https://docs.mistral.ai/vibe/code/cli/configuration | section: precedence
    Configuration > Configuration precedence
    When the same setting is defined in multiple places, the CLI applies them in this order, from **highest to lowest priority**: 1. **Admin config**, when your Organization provides one. See [Admin config](https://docs.mistral.ai/vibe/code/cli/admin-config). 2. **Command-line flags** (for example, `--agent`, `--workdir`). 3. **Environment variables** (for example, `MISTRAL_API_KEY`, `VIBE_HOME`). 4. …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#precedence

[5] https://docs.mistral.ai/vibe/code/cli/api-keys-profiles | section: env-var
    API keys and profiles > Give the API key to the CLI > 2. Environment variable
    Export the key in your shell: ```bash export MISTRAL_API_KEY="your_mistral_api_key" ``` Environment variables take precedence over values stored in `~/.vibe/.env`.
    cite: https://docs.mistral.ai/vibe/code/cli/api-keys-profiles#env-var

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli") to read hit 1 on its page
```

### 7. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli"}
```

Result:

```
page: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | "Install the Vibe CLI and send your first prompt"

## section: install-the-vibe-cli-and-send-your-first-prompt
    Install the Vibe CLI and send your first prompt
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli
# Install the Vibe CLI and send your first prompt

Install the [Vibe CLI](https://docs.mistral.ai/vibe/code/overview), register your API key, and send your first prompt directly from the terminal.

- **One-line install**: get the CLI running in seconds on macOS or Linux.
- **Setup wizard**: register your API key on first launch.
- **Send a prompt**: have Vibe read your project and respond in the terminal.

By the end you'll have the Vibe CLI installed, configured, and responding to prompts in your terminal.

**Time to complete:** ~5 minutes

## section: prerequisites
    Install the Vibe CLI and send your first prompt > Prerequisites
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#prerequisites
## Prerequisites {#prerequisites}

- macOS, Linux, or Windows.
- Python 3.12 or later (for manual install).
- *(Optional)* a Mistral account if you want to use Mistral-hosted models. The CLI also works fully [offline with local models](https://docs.mistral.ai/vibe/code/cli/offline-models) or against any OpenAI-compatible API key you provide. See [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles) for the full provider matrix.

> **Tip**
>
> On a different interface? See the [VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate) or [Vibe Code Web](https://docs.mistral.ai/vibe/code/vibe-code-web/get-started) guides.

## section: step-1
    Install the Vibe CLI and send your first prompt > Step 1: Install the CLI
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#step-1
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

## section: step-2
    Install the Vibe CLI and send your first prompt > Step 2: Launch and configure
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#step-2
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

## section: step-3
    Install the Vibe CLI and send your first prompt > Step 3: Send your first prompt
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#step-3
## Step 3: Send your first prompt {#step-3}

Type a request directly in the prompt. For example:

> List the files in this directory and explain what each one does.

The CLI reads your project context and responds with relevant information. It can also generate code, edit files, and run shell commands when you approve.

![Sending a query to the Vibe CLI](https://docs.mistral.ai/assets/quickstarts/vibe/query.png)

To run a shell command directly from the CLI, prefix it with `!`. For example: `!ls` or `!git status`.

## section: verify
    Install the Vibe CLI and send your first prompt > Verify
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#verify
## Verify {#verify}

You've completed the setup if:

1. `vibe --version` returns a version number.
2. You're signed in (or your API key is registered).
3. The CLI responds to prompts with context-aware answers.

## section: whats-next
    Install the Vibe CLI and send your first prompt > What's next
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#whats-next
## What's next {#whats-next}

- [Scaffold a project with Vibe Code](https://docs.mistral.ai/getting-started/quickstarts/vibe-code/scaffold-a-project)

- [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles) — Switch providers, manage keys per profile.

- [Choose CLI, VS Code, or web sessions](https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions)

- [CLI install and setup reference](https://docs.mistral.ai/vibe/code/cli/install-setup)

Results: 7 sections, the whole page.
```

## Answer

The Vibe CLI **uses the `MISTRAL_API_KEY` environment variable** when both a Vibe subscription (browser-based sign-in) and `MISTRAL_API_KEY` are present.

Here’s why:
- The CLI supports three ways to provide a key, **in order of precedence (highest first)**:
  1. **Interactive setup (browser-based sign-in)** – stores credentials in `~/.vibe/.env`.
  2. **Environment variable (`MISTRAL_API_KEY`)** – explicitly documented as taking precedence over values stored in `~/.vibe/.env`  keys and profiles > Give the API key to the CLI > 2. Environment variable.
  3. **`.env` file** (`~/.vibe/.env`) – loaded automatically but overridden by environment variables  keys and profiles > Give the API key to the CLI > 2. Environment variable.

- The [configuration precedence](https://docs.mistral.ai/vibe/code/cli/configuration#precedence) also confirms that **environment variables (e.g., `MISTRAL_API_KEY`) rank higher than local files** like `~/.vibe/.env`  > Configuration precedence.

Thus, if `MISTRAL_API_KEY` is exported, it will override any credentials stored via browser-based sign-in.

