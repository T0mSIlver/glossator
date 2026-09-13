---
url: https://docs.mistral.ai/studio-api/connectors
title: Connectors
breadcrumbs: [Studio]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/connectors/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Connectors

> **Info**
>
> Connectors are a **Public Preview** feature. The API interface can change.

Connectors are registered [MCP servers](https://modelcontextprotocol.io/) that you can use as **tools in conversations and Agents**, from any SDK or directly via the API, **without managing MCP transport locally**.

Once registered, a Connector **exposes its tools to the model** on demand: the model discovers them automatically and calls the right one **based on the user's request**.

API keys can be scoped for Connector access. When you create an API key, choose whether it can call only Workspace-shared Connectors or both your private Connectors and Workspace-shared Connectors. See [API keys](https://docs.mistral.ai/admin/security-access/api-keys#connector-access-scope) for the access options.

> **What is MCP?**
>
> The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open standard for connecting AI models to external tools and data sources through a unified interface. Any **MCP-compatible server** can be registered as a Connector.

## Next steps {#next-steps}

- **[Create and manage Connectors](https://docs.mistral.ai/studio-api/connectors/management)**: register a Connector with the MCP server URL and visibility scope.
- **[Debug Connectors](https://docs.mistral.ai/studio-api/connectors/debugger)**: validate a Connector server from Studio before using it in production flows.
- **[Use Connectors in conversations](https://docs.mistral.ai/studio-api/connectors/conversations)**: pass a Connector in the `tools` array and let the model pick the right tool.
- **[Call tools directly](https://docs.mistral.ai/studio-api/connectors/tool_calling)**: invoke a specific tool when you already know which one and what arguments to use.
- **[Human-in-the-loop confirmation](https://docs.mistral.ai/studio-api/connectors/confirmation)**: intercept tool calls for user approval before execution.
