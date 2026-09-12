# mined2-075 (single_page, 3 connector calls)

## Question

What is the difference between a Connector and an MCP server in the Vibe CLI, and who sets each one up?

## Thinking

The user is asking a specific question about the difference between a Connector and an MCP server in the Vibe CLI, and who is responsible for setting each up. This requires precise information from Mistral's documentation. I need to search for these terms in the context of Vibe CLI to understand their definitions, differences, and setup responsibilities. I'll start with a targeted search query to find relevant documentation.

The first search returned results but they seem incomplete. I need to refine my search to be more specific. Let me try a more direct query that focuses on the definitions and setup of both Connectors and MCP servers specifically within the Vibe CLI context.

The search results are still not giving me the complete picture. I found a reference to a "Connectors" page in the Vibe CLI documentation. This is likely the primary source for the information I need. Let me read this page directly to get the detailed comparison between Connectors and MCP servers.

I have the comparison table from the documentation. Now I need to provide a clear, structured answer that addresses both parts of the user's question: the functional differences and the setup responsibilities. I should organize this into a summary table and then elaborate on each aspect. I also need to make sure I properly cite the source as required. The answer should be concise but comprehensive, covering all key differences: configuration, authentication, discoverability, and best use cases.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "difference between Connector and MCP server in Vibe CLI and who sets each one up", "max_hits": 5}
```

Result:

```
q: "difference between Connector and MCP server in Vibe CLI and who sets each one up"

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

[4] https://docs.mistral.ai/resources/mcp | section: tools
    MCP > What the server exposes
    **Skills**, the reusable instruction sets you manage in [Skills](https://console.mistral.ai/build/skills). An agent browses the workspace catalog, reads a Skill and the files shipped with it, creates a new Skill version, changes who it is shared with, or deletes it. A Skill written from your editor appears in Studio, and a Skill written in Studio is available to the agent. Skills is the first capa …
    cite: https://docs.mistral.ai/resources/mcp#tools

[5] https://docs.mistral.ai/vibe/work/connectors/mcp-connectors | section: mcp-connectors
    MCP Connectors
    Beyond our [featured Connectors](https://docs.mistral.ai/vibe/work/connectors), you can connect Work to third-party and custom services built on the **Model Context Protocol (MCP)**. > **Info** > > MCP is an open standard that lets language models call tools and read data from external services through a common interface. Any service that exposes an MCP server — whether built by a third party or b …
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/safety-approvals-permissions") to read hit 1 on its page
```

### 2. mistral_docs_search

```json
{"q": "Vibe CLI Connector vs MCP server definition and setup", "max_hits": 5}
```

Result:

```
q: "Vibe CLI Connector vs MCP server definition and setup"

[1] https://docs.mistral.ai/vibe/code/safety-approvals-permissions | section: mcp-and-connector-tools
    Safety, approvals, and permissions > Per-tool permissions > MCP and connector tools
    MCP tools are addressed as `{server_name}_{tool_name}`. For example, to always allow a `get` tool exposed by an MCP server named `fetch_server`: ```toml [tools.fetch_server_get] permission = "always" ``` See [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers) for the full configuration model and [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) for the precedence be …
    cite: https://docs.mistral.ai/vibe/code/safety-approvals-permissions#mcp-and-connector-tools

[2] https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions | section: what-each-surface-gives-you
    Choose CLI, VS Code, or web sessions > What each surface gives you
    | | CLI | VS Code extension | Vibe Code Web | |---|---|---|---| | Local install | Required | Required | None | | Repository access | Local clone | Local clone | Directly via GitHub | | Filesystem and shell access | Local working tree | Local working tree, through ACP | Remote sandbox | | Custom agents, skills, MCP servers, and connectors | Yes | Yes | Yes | | Non-interactive mode | Yes (`vibe --pr …
    cite: https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions#what-each-surface-gives-you

[3] https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions | section: choose-cli-vs-code-or-web-sessions
    Choose CLI, VS Code, or web sessions
    **One agent, three surfaces.** Vibe Code runs as the CLI, the VS Code extension, and Vibe Code Web. They share the same engine, configuration, and customization layer (agents, skills, MCP servers), so you can pick whichever fits the task at hand. > **Info** > > Vibe also implements the [Agent Client Protocol (ACP)](https://agentclientprotocol.com/) and is published in the [ACP registry](https://gi …
    cite: https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions

[4] https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions | section: get-started
    Choose CLI, VS Code, or web sessions > Get started
    [Get started with Vibe Code Web](https://docs.mistral.ai/vibe/code/vibe-code-web/get-started) > **Tip** > > **CLI and VS Code extension share the same configuration and sessions** (agents, skills, MCP servers, profiles, and conversation history). You can start a session in the CLI and resume it in the extension, or the other way around, without losing context. > > To hand off work to Vibe Code Web …
    cite: https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions#get-started:~:text=started%20with%20Vibe

[5] https://docs.mistral.ai/vibe/code/cli/connectors | section: vs-mcp
    Connectors > Connectors vs. MCP servers
    Both expose tools to Vibe, but they're operated differently. Pick whichever fits the service you want to connect: | | Connectors | MCP servers | |---|---|---| | **Configured by** | Mistral, as integrated services | You, in `config.toml` | | **Auth model** | Account or service login | Headers, environment variables, or API keys | | **Discoverability** | Curated, listed in the CLI | Anything that sp …
    cite: https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/safety-approvals-permissions") to read hit 1 on its page
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/connectors", "section": "vs-mcp"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/connectors | "Connectors" | section: vs-mcp

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

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/connectors", section="manage") for the section after it
```

## Answer

Here’s the difference between **Connectors** and **MCP servers** in the Vibe CLI, and who sets each up:

| **Aspect**          | **Connectors**                          | **MCP servers**                          |
|---------------------|----------------------------------------|----------------------------------------|
| **Configured by**    | Mistral (pre-integrated services)       | You (via `config.toml`)                 |
| **Auth model**      | Account or service login               | Headers, environment variables, or API keys |
| **Discoverability** | Curated, listed in the CLI              | Any service that speaks MCP             |
| **Best for**        | Common services with managed integrations | Custom tools, private servers, or experimental tools |

**Summary**:
- **Connectors** are pre-built, Mistral-managed integrations for common services (e.g., GitHub, Slack). Mistral sets them up, and you enable them via your account or service login.
- **MCP servers** are custom, user-configured integrations for any service that supports the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). You define them in your `config.toml` and handle authentication (e.g., API keys).

Source: [Connectors vs. MCP servers](https://docs.mistral.ai/vibe/code/cli/connectors#vs-mcp)

