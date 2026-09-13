# mined2-075 (single_page, 4 connector calls)

## Question

What is the difference between a Connector and an MCP server in the Vibe CLI, and who sets each one up?

## Thinking

The user is asking about the difference between a Connector and an MCP server in the Vibe CLI, and who sets each one up. This is a specific technical question about Mistral AI's Vibe CLI architecture. I need to search the documentation for accurate information about these components and their roles.

Let me start by searching for information about Connectors and MCP servers in the Vibe CLI documentation.

I got some search results. Let me look at the most relevant ones. The first result mentions "MCP and connector tools" which seems directly relevant. I should read the MCP servers page and the connectors page to understand the distinction. Let me start with the MCP servers page.

Good, I got information about MCP servers. Now I need to find information about Connectors in the Vibe CLI to understand the difference. Let me search for the connectors page.

Perfect! Now I have information from both pages. Let me also check the Vibe Work connectors page to see if there's additional context about who sets up connectors.

Now I have comprehensive information from both the MCP servers page and the Connectors page. Let me synthesize the key differences:

From the MCP servers page:
- MCP servers extend Vibe Code CLI with external tools via Model Context Protocol
- They are **user-configured** in `config.toml` under `mcp_servers`
- Tools become available like built-in tools
- User sets them up

From the Connectors page:
- Connectors give Vibe Code CLI access to supported first-party and third-party services
- Unlike MCP servers, Connectors are **Mistral-managed integrations**
- They are configured automatically/detected
- Mistral sets them up

The Connectors vs. MCP servers section provides a clear table:
- Configured by: Mistral (Connectors) vs You (MCP servers)
- Auth model: Account or service login vs Headers, env vars, or API keys
- Discoverability: Curated, listed in CLI vs Anything that speaks MCP
- Best for: Common services with managed integrations vs Custom tools, private servers, experimental tools

So the answer is:
- **Connector**: Mistral-managed integration for common services, set up by Mistral, configured via OAuth/account login
- **MCP server**: User-configured custom integration, set up by the user in config.toml, uses API keys/headers

Let me format this clearly with the differences and who sets up each.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "difference between Connector and MCP server in Vibe CLI", "max_hits": 10}
```

Result:

```
q: "difference between Connector and MCP server in Vibe CLI"

[1] https://docs.mistral.ai/vibe/code/safety-approvals-permissions | section: mcp-and-connector-tools
    Safety, approvals, and permissions > Per-tool permissions > MCP and connector tools
    MCP tools are addressed as `{server_name}_{tool_name}`. For example, to always allow a `get` tool exposed by an MCP server named `fetch_server`: ```toml [tools.fetch_server_get] permission = "always" ``` See [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for the full configuration model and [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) for the precedence be …
    cite: https://docs.mistral.ai/vibe/code/safety-approvals-permissions#mcp-and-connector-tools

[2] https://docs.mistral.ai/getting-started/platform-overview | section: whats-the-difference-between-vibe-work-and-vibe-code
    Platform overview > Common questions > What's the difference between Vibe Work and Vibe Code?
    Vibe Work runs in the Vibe web and mobile apps with a chat interface. Use it for productivity tasks: research, document analysis, scheduled tasks, Connectors, Skills, Projects. Vibe Code runs as a CLI, a VS Code extension, or as a remote web session. Use it for tasks that depend on a codebase: reading files, editing code, running commands, opening pull requests. Both are modes of the same agent. S …
    cite: https://docs.mistral.ai/getting-started/platform-overview#whats-the-difference-between-vibe-work-and-vibe-code

[3] https://docs.mistral.ai/getting-started/platform-overview | section: whats-the-difference-between-vibe-and-studio
    Platform overview > Common questions > What's the difference between Vibe and Studio?
    Vibe is the end-user product. You use it to get things done, in the chat UI, in your editor, or in your terminal. Studio is the developer console. You use it to generate API keys, test prompts, run evaluations, and ship applications built on the Mistral API. Most organizations use both: knowledge workers in Vibe, developers in Studio.
    cite: https://docs.mistral.ai/getting-started/platform-overview#whats-the-difference-between-vibe-and-studio

[4] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: browse
    MCP servers > Browse MCP servers from the CLI
    From a CLI session: ```text /mcp ``` Pass a server name to list its tools: ```text /mcp fetch_server ``` > **Note** > > `/connectors` is an alias for `/mcp`.
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers#browse

[5] https://docs.mistral.ai/vibe/code/cli/mcp-servers | section: mcp-servers
    MCP servers
    MCP servers extend the Vibe Code CLI with **external tools** through the [Model Context Protocol](https://modelcontextprotocol.io). You configure them in `config.toml` under `mcp_servers`, then their tools become available to Vibe like any built-in tool. MCP servers are **user-configured**. For Mistral-managed integrations, see [Connectors](https://docs.mistral.ai/vibe/code/cli/connectors) instead …
    cite: https://docs.mistral.ai/vibe/code/cli/mcp-servers

[6] https://docs.mistral.ai/vibe/work/connectors/mcp-connectors | section: custom-connectors
    MCP Connectors > Configuring a custom Connector
    Custom Connectors let you connect Work to any MCP-compatible server. This is useful for internal tools, private APIs, or services that aren't in the directory. 1. Open the `Connectors` page. 2. Click `+ Add Connector` and switch to the `Custom MCP Connector` tab. 3. Fill in the required fields: - **Connector name**: a unique identifier (no spaces or special characters). - **Server URL**: the full …
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#custom-connectors

[7] https://docs.mistral.ai/vibe/work/connectors/mcp-connectors | section: mcp-connectors
    MCP Connectors
    Beyond our [featured Connectors](https://docs.mistral.ai/vibe/work/connectors), you can connect Work to third-party and custom services built on the **Model Context Protocol (MCP)**. > **Info** > > MCP is an open standard that lets language models call tools and read data from external services through a common interface. Any service that exposes an MCP server — whether built by a third party or b …
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors

[8] https://docs.mistral.ai/resources/mcp | section: next-steps
    MCP > Next steps
    - [Create a Skill in Studio](https://docs.mistral.ai/getting-started/quickstarts/studio/create-skill) to give the agent something to work with. - [MCP servers in the Vibe Code CLI](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for per-tool permissions and filtering. - [API keys](https://docs.mistral.ai/admin/identity-access/api-keys) to create and rotate the key you connect with.
    cite: https://docs.mistral.ai/resources/mcp#next-steps

[9] https://docs.mistral.ai/resources/mcp | section: connect
    MCP > Connect a client
    **Vibe Code CLI** ```bash vibe mcp add mistralai \ --url https://api.mistral.ai/mcp \ --transport streamable-http \ --api-key-env MISTRAL_API_KEY ``` This writes the entry to `~/.vibe/config.toml`: ```toml [[mcp_servers]] name = "mistralai" transport = "streamable-http" url = "https://api.mistral.ai/mcp" [mcp_servers.auth] type = "static" api_key_env = "MISTRAL_API_KEY" ``` The configuration store …
    cite: https://docs.mistral.ai/resources/mcp#connect

[10] https://docs.mistral.ai/studio/search/agentic-search | section: run-mcp-server
    Agentic Search > Use Agentic Search as MCP tools > Run the MCP server
    The MCP server starts automatically when Vibe launches in the project directory. To run it standalone, use the tab that matches your transport mode. **Stdio** ```bash uv run python -m entrypoints.mcp_server ``` Use stdio mode for local agents such as Vibe. **HTTP** ```bash uv run python -m entrypoints.mcp_server --http --host 127.0.0.1 --port 8000 ``` Use HTTP mode for remote or shared deployments …
    cite: https://docs.mistral.ai/studio/search/agentic-search#run-mcp-server

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

### 3. mistral_docs_read_page

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

### 4. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/work/connectors"}
```

Result:

```
page: https://docs.mistral.ai/vibe/work/connectors | "Connect tools with Connectors"

## section: connect-tools-with-connectors
    Connect tools with Connectors
    cite: https://docs.mistral.ai/vibe/work/connectors
# Connect tools with Connectors

Connectors are **secure bridges** between Work and your external tools and data sources. They let Work retrieve, analyze, and act on data from services like Gmail, Google Drive, GitHub, or Notion as part of a task.

Instead of switching between apps, you ask Work: *"Check my Gmail for unread messages about the quarterly report and summarize them"* or *"Find the latest design document in Google Drive and create a brief I can share with my team."* Work decides which Connector to call, asks for authentication if missing, and requests approval before sensitive actions.

## section: available-connectors
    Connect tools with Connectors > Available Connectors
    cite: https://docs.mistral.ai/vibe/work/connectors#available-connectors
## Available Connectors {#available-connectors}

**Featured**

Featured Connectors use a direct OAuth flow. Click `Connect` on the card and authenticate. Administrators can disable specific Connectors for the whole organization on a case-by-case basis.

| Connector | What it does |
|-----------|-------------|
| Atlassian | Connect to Confluence and Jira to search, summarize, and perform project actions. |
| Box | Search, analyze, and get insights from your Box files. |
| GitHub App | Search repositories, review issues, and manage pull requests in GitHub. |
| Gmail | Include your email in your chats. |
| Google Calendar | Include your calendar in your chats. |
| Linear | Search, summarize, and manage your issues and projects in Linear. |
| Notion | Search, summarize, and author content in Notion. |
| Outlook | Read and send emails with Outlook. |
| Outlook Calendar | Manage your Outlook Calendar — search events, schedule and delete meetings, and accept or decline invitations. |
| SharePoint Search API | Search and open SharePoint content via Microsoft Graph API. |
| Slack | Search messages, read channels, send messages, and manage canvases in Slack. |
| Stripe | Access and manage payments, customers, and transactions in Stripe. |

**MCP**

Connect Work to **any service** built on the [Model Context Protocol](https://modelcontextprotocol.io) (MCP). Pick a pre-configured Connector from our directory, or point Work at your own MCP-compatible server. Requires an administrator.

For directory browsing, custom configuration, and security best practices, see our [MCP Connectors guide](https://docs.mistral.ai/vibe/work/connectors/mcp-connectors).

## section: connecting
    Connect tools with Connectors > Connecting a service
    cite: https://docs.mistral.ai/vibe/work/connectors#connecting
## Connecting a service {#connecting}

To connect a featured Connector:

1. Open the `Connectors` page from the sidebar.
2. Find the Connector card and click `Connect`.
3. Complete the authentication flow (typically OAuth 2.0). Your password is never shared with us.

A green `Connected` indicator confirms the connection. You can disconnect at any time from the same page.

## section: using-connectors
    Connect tools with Connectors > Using Connectors in tasks
    cite: https://docs.mistral.ai/vibe/work/connectors#using-connectors
## Using Connectors in tasks {#using-connectors}

Once connected, Work can use the Connector automatically when relevant. You can also enable a specific Connector for a task:

1. Click the `+` icon or type `/` in the chat window.
2. Select `Tools` then enable the Connector you want to use.

Then describe the task naturally. Work figures out which Connector to call based on your request.

Typical prompts:

- *"What meetings do I have tomorrow?"*
- *"Find the latest Q3 revenue deck in Google Drive and prepare a one-page summary."*
- *"Create a calendar event for Friday at 2pm with the product team."*
- *"Check my unread emails from the legal team and draft replies for me to review."*

## section: approving-actions
    Connect tools with Connectors > Using Connectors in tasks > Approving actions
    cite: https://docs.mistral.ai/vibe/work/connectors#approving-actions
### Approving actions {#approving-actions}

When a Connector performs an action on your behalf (sending an email, creating an event, modifying a file), Work asks for your **approval before executing** it. See [Safety and approvals](https://docs.mistral.ai/vibe/work/safety-and-approvals#approvals) for the full approval flow and the three options (`Continue`, `Always allow`, `Decline`).

You can also pre-authorize specific functions per Connector — see [Per-function Connector permissions](https://docs.mistral.ai/vibe/work/safety-and-approvals#connector-functions).

## section: data-privacy
    Connect tools with Connectors > Data and privacy
    cite: https://docs.mistral.ai/vibe/work/connectors#data-privacy
## Data and privacy {#data-privacy}

Featured Connectors fetch data in real time for your current request. We don't store it on our servers, and disconnecting revokes access immediately.

**Training**: data accessed through Connectors is **never used to train or fine-tune our models**, regardless of your plan. Conversations that reference Connector data are treated as regular user-provided content and follow your plan's [data policies](https://mistral.ai/terms#privacy-policy).

For more details, see our [trust center](https://trust.mistral.ai/).

Results: 6 sections, the whole page.
```

## Answer

Here’s the difference between a **Connector** and an **MCP server** in the Vibe CLI, and who sets each up:

---

### **Connector**
- **What it is**: A **Mistral-managed integration** for supported first- and third-party services (e.g., GitHub, Gmail, Notion).
  [Connectors give the Vibe Code CLI access to supported first-party and third-party services from inside a coding session. Unlike MCP servers, which you wire up yourself, Connectors are Mistral-managed integrations.](https://docs.mistral.ai/vibe/code/cli/connectors#connectors)
- **Who sets it up**: **Mistral** provides and maintains the integration. You only need to authenticate (e.g., via OAuth) or enable/disable it in the CLI.
  [Configured by: Mistral, as integrated services](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)
- **Auth model**: Account or service login (e.g., OAuth 2.0).
  [Auth model: Account or service login](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)
- **Best for**: Common services with managed, curated integrations.
  [Best for: Common services with managed integrations](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)

---

### **MCP Server**
- **What it is**: A **user-configured** external tool or service that extends the Vibe CLI via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io). You define it in `config.toml` under `mcp_servers`.
  [MCP servers extend the Vibe Code CLI with external tools through the Model Context Protocol. You configure them in `config.toml` under `mcp_servers`, then their tools become available to Vibe like any built-in tool. MCP servers are user-configured.](https://docs.mistral.ai/vibe/code/cli/mcp-servers#mcp-servers)
- **Who sets it up**: **You** (the user) configure and manage the server, including its transport (HTTP, stdio, etc.), URL, and credentials.
  [Configured by: You, in `config.toml`](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)
- **Auth model**: Headers, environment variables, or API keys.
  [Auth model: Headers, environment variables, or API keys](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)
- **Best for**: Custom tools, private servers, or experimental integrations.
  [Best for: Custom tools, private servers, experimental tools](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)

---
---
### **Summary Table**
| Aspect               | **Connector**                          | **MCP Server**                          |
|----------------------|----------------------------------------|-----------------------------------------|
| **Setup by**         | Mistral (pre-integrated)               | You (user-configured in `config.toml`)   |
| **Auth**             | OAuth/account login                    | API keys, headers, or env vars          |
| **Discoverability**  | Curated, listed in the CLI             | Any service that speaks MCP             |
| **Use case**         | Common services (e.g., GitHub, Gmail) | Custom/private tools or servers         |

---
For more details, see:
- [Connectors in Vibe Code CLI](https://docs.mistral.ai/vibe/code/cli/connectors)
- [MCP Servers in Vibe Code CLI](https://docs.mistral.ai/vibe/code/cli/mcp-servers)

