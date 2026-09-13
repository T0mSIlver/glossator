---
url: https://docs.mistral.ai/studio-api/knowledge-rag/connectors
title: Connectors
breadcrumbs: [Studio, Knowledge & RAG]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/knowledge-rag/connectors/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Connectors

> **Info**
>
> Connectors are a **beta** feature. The API interface can change.

Connectors are registered [MCP servers](https://modelcontextprotocol.io/) that you can use as **tools in conversations and Agents**, from any SDK or directly via the API, **without managing MCP transport locally**.

Once registered, a Connector **exposes its tools to the model** on demand: the model discovers them automatically and calls the right one **based on the user's request**.

> **What is MCP?**
>
> The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open standard for connecting AI models to external tools and data sources through a unified interface. Any **MCP-compatible server** can be registered as a Connector.

## Next steps {#next-steps}

- **[Create and manage Connectors](https://docs.mistral.ai/studio-api/knowledge-rag/connectors/management)** — register a Connector with the MCP server URL and visibility scope.
- **[Use Connectors in conversations](https://docs.mistral.ai/studio-api/knowledge-rag/connectors/conversations)** — pass a Connector in the `tools` array and let the model pick the right tool.
- **[Call tools directly](https://docs.mistral.ai/studio-api/knowledge-rag/connectors/tool_calling)** — invoke a specific tool when you already know which one and what arguments to use.
- **[Human-in-the-loop confirmation](https://docs.mistral.ai/studio-api/knowledge-rag/connectors/confirmation)** — intercept tool calls for user approval before execution.
