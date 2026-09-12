# mined2-075 (single_page, 5 connector calls)

## Question

What is the difference between a Connector and an MCP server in the Vibe CLI, and who sets each one up?

## Thinking

The user is asking about the difference between a Connector and an MCP server in the Vibe CLI, and who sets each one up. This is a specific technical question about Mistral's Vibe CLI architecture. I need to search the Mistral documentation to find accurate information about these components.

Let me break this down:
1. I need to understand what a Connector is in Vibe CLI context
2. I need to understand what an MCP server is in Vibe CLI context
3. I need to find who sets up each one
4. I need to find the differences between them

I should start by searching for information about Vibe CLI connectors and MCP servers in the Mistral documentation.

The search returned some relevant hits. Let me examine the key ones:

1. Hit 3 from `vibe/code/cli/mcp-servers` seems very relevant - it mentions MCP servers extend Vibe CLI with external tools through Model Context Protocol, configured in `config.toml` under `mcp_servers`, and are **user-configured**. It also mentions that for Mistral-managed integrations, see Connectors instead.

2. Hit 4 and 5 are about Work connectors and MCP connectors, which might be relevant but the user specifically asked about Vibe CLI.

3. Hit 6 shows an example of adding an MCP server to Vibe Code CLI with `vibe mcp add` command.

I need to read the MCP servers page to get more details, and also search for information about Connectors in the Vibe CLI context.

Good, I have information about MCP servers. Now I need to find information about Connectors in the Vibe CLI context. The page mentioned that for Mistral-managed integrations, I should see Connectors. Let me search for that.

The search didn't directly show the Connectors page. Let me search more specifically for the connectors page that was referenced in the MCP servers page.

Perfect! Now I have a direct hit for the Connectors page. Let me read it to get the details.

Excellent! Now I have all the information I need. Let me summarize what I've found:

From the MCP servers page:
- MCP servers extend the Vibe Code CLI with external tools through the Model Context Protocol
- They are **user-configured** in `config.toml` under `mcp_servers`
- Their tools become available to Vibe like any built-in tool
- They are for user-configured custom tools, private servers, experimental tools

From the Connectors page:
- Connectors give the Vibe Code CLI access to supported first-party and third-party services
- Unlike MCP servers, which you wire up yourself, **Connectors are Mistral-managed integrations**
- Connectors are **Mistral-managed integrations**
- The comparison table shows:
  - **Configured by**: Mistral, as integrated services (Connectors) vs You, in `config.toml` (MCP servers)
  - **Auth model**: Account or service login (Connectors) vs Headers, environment variables, or API keys (MCP servers)
  - **Discoverability**: Curated, listed in the CLI (Connectors) vs Anything that speaks MCP (MCP servers)
  - **Best for**: Common services with managed integrations (Connectors) vs Custom tools, private servers, experimental tools (MCP servers)

So the answer is:
- **Connector**: Mistral-managed integrations for supported services, configured automatically by Mistral, use account/service login
- **MCP server**: User-configured custom integrations, set up by the user in config.toml, use headers/env vars/API keys

Let me structure this clearly for the user.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Vibe CLI Connector MCP server difference setup", "max_hits": 10}
```

Result:

```
q: "Vibe CLI Connector MCP server difference setup"

[1] https://docs.mistral.ai/vibe/code/safety-approvals-permissions | section: mcp-and-connector-tools
    Safety, approvals, and permissions > Per-tool permissions > MCP and connector tools
    MCP tools are addressed as `{server_name}_{tool_name}`. For example, to always allow a `get` tool exposed by an MCP server named `fetch_server`: ```toml [tools.fetch_server_get] permission = "always" ``` See [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for the full configuration model and [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) for the precedence be …
    cite: https://docs.mistral.ai/vibe/code/safety-approvals-permissions#mcp-and-connector-tools

[2] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: browse
    MCP servers > Browse MCP servers from the CLI
    From a CLI session: ```text /mcp ``` Pass a server name to list its tools: ```text /mcp fetch_server ``` > **Note** > > `/connectors` is an alias for `/mcp`.
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#browse

[3] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: mcp-servers
    MCP servers
    MCP servers extend the Vibe Code CLI with **external tools** through the [Model Context Protocol](https://modelcontextprotocol.io). You configure them in `config.toml` under `mcp_servers`, then their tools become available to Vibe like any built-in tool. MCP servers are **user-configured**. For Mistral-managed integrations, see [Connectors](https://docs.mistral.ai/vibe/code/cli/connectors) instead …
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers

[4] https://docs.mistral.ai/vibe/work/connectors/mcp-connectors | section: custom-connectors
    MCP Connectors > Configuring a custom Connector
    Custom Connectors let you connect Work to any MCP-compatible server. This is useful for internal tools, private APIs, or services that aren't in the directory. 1. Open the `Connectors` page. 2. Click `+ Add Connector` and switch to the `Custom MCP Connector` tab. 3. Fill in the required fields: - **Connector name**: a unique identifier (no spaces or special characters). - **Server URL**: the full …
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#custom-connectors

[5] https://docs.mistral.ai/vibe/work/connectors/mcp-connectors | section: mcp-connectors
    MCP Connectors
    Beyond our [featured Connectors](https://docs.mistral.ai/vibe/work/connectors), you can connect Work to third-party and custom services built on the **Model Context Protocol (MCP)**. > **Info** > > MCP is an open standard that lets language models call tools and read data from external services through a common interface. Any service that exposes an MCP server — whether built by a third party or b …
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors

[6] https://docs.mistral.ai/resources/mcp | section: connect
    MCP > Connect a client
    **Vibe Code CLI** ```bash vibe mcp add mistralai \ --url https://api.mistral.ai/mcp \ --transport streamable-http \ --api-key-env MISTRAL_API_KEY ``` This writes the entry to `~/.vibe/config.toml`: ```toml [[mcp_servers]] name = "mistralai" transport = "streamable-http" url = "https://api.mistral.ai/mcp" [mcp_servers.auth] type = "static" api_key_env = "MISTRAL_API_KEY" ``` The configuration store …
    cite: https://docs.mistral.ai/resources/mcp#connect

[7] https://docs.mistral.ai/vibe/code/cli/install-setup | section: install-and-setup
    Install and setup
    Install the Vibe CLI, run `vibe` in your project, and complete the setup prompt.
    cite: https://docs.mistral.ai/vibe/code/cli/install-setup

[8] https://docs.mistral.ai/studio/search/agentic-search | section: run-mcp-server
    Agentic Search > Use Agentic Search as MCP tools > Run the MCP server
    The MCP server starts automatically when Vibe launches in the project directory. To run it standalone, use the tab that matches your transport mode. **Stdio** ```bash uv run python -m entrypoints.mcp_server ``` Use stdio mode for local agents such as Vibe. **HTTP** ```bash uv run python -m entrypoints.mcp_server --http --host 127.0.0.1 --port 8000 ``` Use HTTP mode for remote or shared deployments …
    cite: https://docs.mistral.ai/studio/search/agentic-search#run-mcp-server

[9] https://docs.mistral.ai/resources/mcp | section: next-steps
    MCP > Next steps
    - [Create a Skill in Studio](https://docs.mistral.ai/getting-started/quickstarts/studio/create-skill) to give the agent something to work with. - [MCP servers in the Vibe Code CLI](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for per-tool permissions and filtering. - [API keys](https://docs.mistral.ai/admin/identity-access/api-keys) to create and rotate the key you connect with.
    cite: https://docs.mistral.ai/resources/mcp#next-steps

[10] https://docs.mistral.ai/resources/mcp | section: mcp
    MCP
    The Mistral MCP server connects an AI agent to your Studio workspace over the [Model Context Protocol](https://modelcontextprotocol.io). It exposes your workspace as MCP tools and authenticates each request with your Mistral API key. Use it from wherever your agent runs: a coding CLI, an IDE, a desktop assistant, or your own application. | | | |---|---| | **Endpoint** | `https://api.mistral.ai/mcp …
    cite: https://docs.mistral.ai/resources/mcp

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/safety-approvals-permissions") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/mcp-servers"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/mcp-servers | "MCP servers"

## section: mcp-servers
    MCP servers
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers
# MCP servers

MCP servers extend the Vibe Code CLI with **external tools** through the [Model Context Protocol](https://modelcontextprotocol.io). You configure them in `config.toml` under `mcp_servers`, then their tools become available to Vibe like any built-in tool.

MCP servers are **user-configured**. For Mistral-managed integrations, see [Connectors](https://docs.mistral.ai/vibe/code/cli/connectors) instead.

> **Info**
>
> **Known limitation:** the CLI does not yet support MCP servers that require OAuth authentication. Use the `stdio` or `http` transport with an API key or other static credential.

## section: transports
    MCP servers > Supported transports
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#transports
## Supported transports {#transports}

| Transport | Use it when |
|---|---|
| `http` | The server is reachable over standard HTTP. |
| `streamable-http` | The server is reachable over HTTP and supports streaming responses. |
| `stdio` | The server is a local process you start from a command. |

## section: add
    MCP servers > Add an MCP server
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#add
## Add an MCP server {#add}

Append a `[[mcp_servers]]` table to `config.toml`. Required fields depend on the transport.

**HTTP**

```toml
[[mcp_servers]]
name = "my_http_server"
transport = "http"
url = "http://localhost:8000"
headers = { "Authorization" = "Bearer my_token" }
api_key_env = "MY_API_KEY_ENV_VAR"
api_key_header = "Authorization"
api_key_format = "Bearer {token}"
```

**Streamable HTTP**

```toml
[[mcp_servers]]
name = "my_streamable_server"
transport = "streamable-http"
url = "http://localhost:8001"
headers = { "X-API-Key" = "my_api_key" }
```

**Local process (stdio)**

```toml
[[mcp_servers]]
name = "fetch_server"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
env = { "DEBUG" = "1", "LOG_LEVEL" = "info" }
```

## section: fields
    MCP servers > Common fields
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#fields
## Common fields {#fields}

| Field | Purpose |
|---|---|
| `name` | Short alias for the server. Used as a prefix in tool names. |
| `transport` | One of `http`, `streamable-http`, or `stdio`. |
| `url` | Base URL for HTTP transports. |
| `command` / `args` | Command and arguments for the stdio transport. |
| `headers` | Extra HTTP headers for HTTP transports. |
| `api_key_env` | Environment variable that holds the API key. |
| `env` | Environment variables passed to the server process (stdio). |
| `startup_timeout_sec` | How long to wait for the server to start. |
| `tool_timeout_sec` | How long to wait for a tool call to complete. |

## section: permissions
    MCP servers > Tool naming and permissions
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#permissions
## Tool naming and permissions {#permissions}

MCP tools are exposed under the pattern `{server_name}_{tool_name}`. Configure permissions per tool just like built-in tools:

```toml
[tools.fetch_server_get]
permission = "always"

[tools.my_http_server_query]
permission = "ask"
```

You can also restrict which MCP tools are active using `enabled_tools` and `disabled_tools`:

```toml
# Only enable serena's tools
enabled_tools = ["serena_*"]

# Disable all MCP tools and grep
disabled_tools = ["mcp_*", "grep"]
```

Filters support **exact names**, **glob patterns**, and **regex** with the `re:` prefix.

## section: browse
    MCP servers > Browse MCP servers from the CLI
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#browse
## Browse MCP servers from the CLI {#browse}

From a CLI session:

```text
/mcp
```

Pass a server name to list its tools:

```text
/mcp fetch_server
```

> **Note**
>
> `/connectors` is an alias for `/mcp`.

Results: 6 sections, the whole page.
```

### 3. mistral_docs_search

```json
{"q": "Vibe CLI Connectors configuration setup", "max_hits": 10}
```

Result:

```
q: "Vibe CLI Connectors configuration setup"

[1] https://docs.mistral.ai/vibe/code/cli/install-setup | section: reset-config
    Install and setup > Reset your configuration
    If the CLI fails to start or behaves unexpectedly after editing the config, move the file aside and restart Vibe. A fresh `~/.vibe/config.toml` is generated on the next launch: ```bash mv ~/.vibe/config.toml ~/.vibe/config.toml.bkp vibe ```
    cite: https://docs.mistral.ai/vibe/code/cli/install-setup#reset-config

[2] https://docs.mistral.ai/vibe/code/cli/install-setup | section: install-and-setup
    Install and setup
    Install the Vibe CLI, run `vibe` in your project, and complete the setup prompt.
    cite: https://docs.mistral.ai/vibe/code/cli/install-setup

[3] https://docs.mistral.ai/vibe/code/cli/configuration | section: configuration
    Configuration
    The Vibe Code CLI is configured through a **`config.toml` file**. This page explains where the file lives, how to open it, and the most common settings you'll touch. > **Info** > > For an exhaustive list of every key in `config.toml` and the agent-definition files, see the [Configuration reference](https://docs.mistral.ai/vibe/code/cli/configuration-reference).
    cite: https://docs.mistral.ai/vibe/code/cli/configuration

[4] https://docs.mistral.ai/vibe/code/cli/configuration | section: admin-config
    Configuration > Admin-managed configuration
    Your Organization can distribute a Vibe Code CLI configuration to all users. Admin-managed settings take precedence over command-line flags, environment variables, and the project and user `config.toml` files. When admin config is active: - Admin-managed settings in `/config` appear dim with a `⚿` lock glyph and list `your administrator` as the origin. A legend at the bottom of the screen reads `⚿ …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#admin-config

[5] https://docs.mistral.ai/vibe/code/cli/configuration | section: vibe-home
    Configuration > Vibe home directory
    By default, the CLI stores its configuration and state in `~/.vibe/`. Override the location with the `VIBE_HOME` environment variable: ```bash export VIBE_HOME="/path/to/custom/vibe/home" ``` `VIBE_HOME` affects the location of: - `config.toml`: main configuration. - `.env`: API keys and provider credentials. - `agents/`: custom agent profiles. - `prompts/`: custom system prompts. - `skills/`: cus …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#vibe-home

[6] https://docs.mistral.ai/vibe/code/cli/install-setup | section: start
    Install and setup > Start Vibe in your project
    Open a terminal in your project root and run: ```bash vibe ``` On first launch, Vibe: - Creates a default configuration file at `~/.vibe/config.toml` if it does not already exist. - Walks you through a **setup wizard** to register your API key.
    cite: https://docs.mistral.ai/vibe/code/cli/install-setup#start

[7] https://docs.mistral.ai/vibe/code/cli/configuration | section: precedence
    Configuration > Configuration precedence
    When the same setting is defined in multiple places, the CLI applies them in this order, from **highest to lowest priority**: 1. **Admin config**, when your Organization provides one. See [Admin config](https://docs.mistral.ai/vibe/code/cli/admin-config). 2. **Command-line flags** (for example, `--agent`, `--workdir`). 3. **Environment variables** (for example, `MISTRAL_API_KEY`, `VIBE_HOME`). 4. …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#precedence

[8] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: step-2
    Install the Vibe CLI and send your first prompt > Step 2: Launch and configure
    1. Open a terminal in any project directory. 2. Run: ```bash vibe ``` ![Vibe CLI running in a terminal](https://docs.mistral.ai/assets/quickstarts/vibe/home.png) On first launch, the CLI runs a **setup wizard** to register your API key. By default it opens a browser to sign you in with your Mistral account; credentials are stored locally so you don't need to enter them again. For non-Mistral provi …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#step-2

[9] https://docs.mistral.ai/vibe/code/use-vibe-in-other-ides | section: authenticate
    Use Vibe in other IDEs > Authenticate Vibe
    The first time Vibe needs credentials, it runs the bundled agent setup flow. Provide your Mistral API key when prompted. Vibe stores credentials in the Vibe home directory (`~/.vibe/`) and reuses them across sessions. If you already authenticated the [Vibe CLI](https://docs.mistral.ai/vibe/code/cli/install-setup) or the [VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/instal …
    cite: https://docs.mistral.ai/vibe/code/use-vibe-in-other-ides#authenticate

[10] https://docs.mistral.ai/vibe/code/cli/configuration | section: file-locations
    Configuration > Configuration file locations
    The CLI looks for `config.toml` in this order: 1. `./.vibe/config.toml` in the current working directory (**project-level**). 2. `~/.vibe/config.toml` in your home directory (**user-level**). Project-level configuration takes precedence over user-level configuration. Project configuration is loaded only when the working directory is [trusted](https://docs.mistral.ai/vibe/code/safety-approvals-perm …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#file-locations

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/install-setup") to read hit 1 on its page
```

### 4. mistral_docs_search

```json
{"q": "Vibe CLI connectors", "max_hits": 10}
```

Result:

```
q: "Vibe CLI connectors"

[1] https://docs.mistral.ai/vibe/code/cli/connectors | section: connectors
    Connectors
    Connectors give the Vibe Code CLI access to **supported first-party and third-party services** from inside a coding session. Unlike [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers), which you wire up yourself, Connectors are **Mistral-managed integrations**. > **Info** > > For the full list of supported connectors and what each one can do, see [Connectors in Vibe Work](https://docs …
    cite: https://docs.mistral.ai/vibe/code/cli/connectors

[2] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: whats-next
    Install the Vibe CLI and send your first prompt > What's next
    - [Scaffold a project with Vibe Code](https://docs.mistral.ai/getting-started/quickstarts/vibe-code/scaffold-a-project) - [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles) — Switch providers, manage keys per profile. - [Choose CLI, VS Code, or web sessions](https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions) - [CLI install and setup reference](https://d …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#whats-next

[3] https://docs.mistral.ai/vibe/code/cli/connectors | section: vs-mcp
    Connectors > Connectors vs. MCP servers
    Both expose tools to Vibe, but they're operated differently. Pick whichever fits the service you want to connect: | | Connectors | MCP servers | |---|---|---| | **Configured by** | Mistral, as integrated services | You, in `config.toml` | | **Auth model** | Account or service login | Headers, environment variables, or API keys | | **Discoverability** | Curated, listed in the CLI | Anything that sp …
    cite: https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp

[4] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: install-the-vibe-cli-and-send-your-first-prompt
    Install the Vibe CLI and send your first prompt
    Install the [Vibe CLI](https://docs.mistral.ai/vibe/code/overview), register your API key, and send your first prompt directly from the terminal. - **One-line install**: get the CLI running in seconds on macOS or Linux. - **Setup wizard**: register your API key on first launch. - **Send a prompt**: have Vibe read your project and respond in the terminal. By the end you'll have the Vibe CLI install …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli

[5] https://docs.mistral.ai/admin/workspaces/workspaces-in-vibe | section: connectors
    Workspaces in Vibe > Admin settings for Vibe > Connectors
    Admins can manage the Connectors and Connector tools available in Vibe and Studio for each Workspace. See [Connectors](https://docs.mistral.ai/admin/identity-access/connectors).
    cite: https://docs.mistral.ai/admin/workspaces/workspaces-in-vibe#connectors

[6] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: step-2
    Install the Vibe CLI and send your first prompt > Step 2: Launch and configure
    1. Open a terminal in any project directory. 2. Run: ```bash vibe ``` ![Vibe CLI running in a terminal](https://docs.mistral.ai/assets/quickstarts/vibe/home.png) On first launch, the CLI runs a **setup wizard** to register your API key. By default it opens a browser to sign you in with your Mistral account; credentials are stored locally so you don't need to enter them again. For non-Mistral provi …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#step-2

[7] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: step-1
    Install the Vibe CLI and send your first prompt > Step 1: Install the CLI
    **One-liner (macOS/Linux)** Run this in your terminal: ```bash curl -LsSf https://mistral.ai/vibe/install.sh | bash ``` The installer checks `uv` (Astral's Python tool installer), installs or upgrades `mistral-vibe`, and makes the `vibe` and `vibe-acp` commands available, provided your `PATH` is configured. **Manual install (macOS/Linux/Windows)** If you prefer manual setup, or you're on Windows: …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#step-1

[8] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: prerequisites
    Install the Vibe CLI and send your first prompt > Prerequisites
    - macOS, Linux, or Windows. - Python 3.12 or later (for manual install). - *(Optional)* a Mistral account if you want to use Mistral-hosted models. The CLI also works fully [offline with local models](https://docs.mistral.ai/vibe/code/cli/offline-models) or against any OpenAI-compatible API key you provide. See [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles) for th …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#prerequisites

[9] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: verify
    Install the Vibe CLI and send your first prompt > Verify
    You've completed the setup if: 1. `vibe --version` returns a version number. 2. You're signed in (or your API key is registered). 3. The CLI responds to prompts with context-aware answers.
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#verify

[10] https://docs.mistral.ai/vibe/code/overview | section: set-up-vibe-code
    Vibe Code > Set up Vibe Code
    Pick the interface that fits your workflow: - [Install the CLI](https://docs.mistral.ai/vibe/code/cli/install-setup) — Run Vibe Code from your terminal. - [Install the VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate) — Use Vibe Code directly in VS Code. - [Start a web session](https://docs.mistral.ai/vibe/code/vibe-code-web/get-started) — Run a cloud ses …
    cite: https://docs.mistral.ai/vibe/code/overview#set-up-vibe-code

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/connectors") to read hit 1 on its page
```

### 5. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/connectors"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/connectors | "Connectors"

## section: connectors
    Connectors
    cite: https://docs.mistral.ai/vibe/code/cli/connectors
# Connectors

Connectors give the Vibe Code CLI access to **supported first-party and third-party services** from inside a coding session. Unlike [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers), which you wire up yourself, Connectors are **Mistral-managed integrations**.

> **Info**
>
> For the full list of supported connectors and what each one can do, see [Connectors in Vibe Work](https://docs.mistral.ai/vibe/work/connectors). Vibe Code and Vibe Work share the same integrations.

## section: vs-mcp
    Connectors > Connectors vs. MCP servers
    cite: https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp
## Connectors vs. MCP servers {#vs-mcp}

Both expose tools to Vibe, but they're operated differently. Pick whichever fits the service you want to connect:

| | Connectors | MCP servers |
|---|---|---|
| **Configured by** | Mistral, as integrated services | You, in `config.toml` |
| **Auth model** | Account or service login | Headers, environment variables, or API keys |
| **Discoverability** | Curated, listed in the CLI | Anything that speaks MCP |
| **Best for** | Common services with managed integrations | Custom tools, private servers, experimental tools |

## section: manage
    Connectors > Manage connectors
    cite: https://docs.mistral.ai/vibe/code/cli/connectors#manage
## Manage connectors {#manage}

Connectors are detected and configured automatically. You can list, enable, disable, and inspect them from inside a CLI session.

List all connectors and MCP servers:

```text
/connectors
```

(`/connectors` is an alias for `/mcp`.)

From the list, with a connector highlighted:

| Key | Action |
|---|---|
| `E` | Enable the connector |
| `D` | Disable the connector |

Pass a name to inspect the tools exposed by a specific connector:

```text
/connectors fetch_server
```

## section: stay-in-control
    Connectors > Stay in control
    cite: https://docs.mistral.ai/vibe/code/cli/connectors#stay-in-control
## Stay in control {#stay-in-control}

- **Review what each connector can access** before authenticating.
- **Prefer read-only or scoped access** when the task doesn't need write permissions.
- **Revoke unused connectors** from the relevant service when you no longer need them.

Results: 4 sections, the whole page.
```

## Answer

In the **Vibe Code CLI**, **Connectors** and **MCP servers** both expose tools to the agent, but they differ in who manages them and how they're set up:

---

### **Connectors**
- **What they are**: Mistral-managed integrations for supported first-party and third-party services (e.g., GitHub, Slack, or Mistral's own tools).
- **Who sets them up**: **Mistral** provides and maintains these integrations. They are curated, pre-configured, and listed directly in the CLI.
- **Authentication**: Typically uses **account or service login** (e.g., OAuth or Mistral account credentials).
- **Discoverability**: Automatically detected and available in the CLI. Users can enable/disable them from the session (e.g., via `/connectors`).
- **Best for**: Common services with managed, tested integrations.
  *[Connectors](https://docs.mistral.ai/vibe/code/cli/connectors)*

---

### **MCP Servers**
- **What they are**: Custom integrations built on the **Model Context Protocol (MCP)**, allowing you to connect any external tool or server that speaks MCP (e.g., a private API, local script, or third-party MCP server).
- **Who sets them up**: **You**, the user. Configured manually in `~/.vibe/config.toml` under the `[[mcp_servers]]` section, where you define the transport (`http`, `stdio`, etc.), URL, commands, and credentials.
- **Authentication**: Uses **headers, environment variables, or API keys** (static credentials). *Note*: The CLI does not yet support OAuth for MCP servers.
- **Discoverability**: Any service that implements MCP can be connected. Tools are exposed under the pattern `{server_name}_{tool_name}`.
- **Best for**: Custom tools, private servers, or experimental integrations.
  *[MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers)*

---

### **Key Difference Summary**
| Aspect               | Connectors                          | MCP Servers                          |
|----------------------|-------------------------------------|--------------------------------------|
| **Managed by**       | Mistral (pre-built)                 | You (user-configured)                |
| **Setup**            | Automatic (listed in CLI)           | Manual (`config.toml`)               |
| **Auth**             | Account/service login               | API keys, headers, or env vars        |
| **Use case**         | Supported services                  | Custom/private tools or servers      |

---
For a side-by-side comparison, see the official table: *[Connectors vs. MCP servers](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)*.

