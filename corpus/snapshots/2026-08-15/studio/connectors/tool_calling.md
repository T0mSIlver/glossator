---
url: https://docs.mistral.ai/studio/connectors/tool_calling
title: Direct tool calling with Connectors
breadcrumbs: [Studio, Connectors]
kind: doc
locale: en
source_path: src/content/en/docs/studio/connectors/tool_calling/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Direct tool calling

The `call_tool` method lets you call a specific MCP tool on a Connector directly, **without starting a conversation or involving the model**.

This is useful when you:

- Already know which tool to call and what arguments to pass
- Want the raw tool output for downstream processing
- Are building pipelines that chain tool calls programmatically
- Want to debug or verify Connector tools before using them in conversations

For scenarios where the model picks which tools to call, use [Connectors in conversations](https://docs.mistral.ai/studio/connectors/conversations) instead.

> **Note**
>
> If a Connector requires authentication, you must complete the [auth flow](https://docs.mistral.ai/studio/connectors/management#get-auth-url) before calling its tools.

## Call a tool directly {#call-tool}

To call a tool, pass the Connector name (or UUID), the tool name, and the arguments the tool expects.

**Python**

```python
import asyncio
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")


async def main() -> None:
    result = await client.beta.connectors.call_tool_async(
        connector_id_or_name="my_deepwiki",
        tool_name="read_wiki_structure",
        arguments={"repoName": "sqlite/sqlite"},
    )

    # result.content is a list of content blocks (TextContent, ImageContent, etc.)
    for item in result.content:
        if hasattr(item, "text"):
            print(item.text)


asyncio.run(main())
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const client = new Mistral({ apiKey: "your-api-key" });

async function main(): Promise<void> {
  const result = await client.beta.connectors.callTool({
    connectorIdOrName: "my_deepwiki",
    toolName: "read_wiki_structure",
    connectorCallToolRequest: {
      arguments: { repoName: "sqlite/sqlite" },
    },
  });

  // result.content is an array of content blocks (text, image, etc.)
  for (const item of result.content ?? []) {
    if ("text" in item) {
      console.log(item.text);
    }
  }
}

main();
```

**cURL**

The `tool_name` is part of the URL path, not the request body. The body only contains `arguments`.

```bash
curl -X POST "https://api.mistral.ai/v1/connectors/my_deepwiki/tools/read_wiki_structure/call" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {"repoName": "sqlite/sqlite"}
  }'
```

The response `content` array contains typed content blocks (text, image, audio, or resource) returned by the MCP server.

> **Info**
>
> Tool names must match exactly: use [list tools](https://docs.mistral.ai/studio/connectors/management#list-tools) to check what a Connector exposes.

## Chain multiple tool calls {#chaining}

You can call multiple tools in sequence to build a pipeline **without involving the model at each step**.

**Python**

```python
import asyncio
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")


async def main() -> None:
    # First call: get the repository structure
    structure = await client.beta.connectors.call_tool_async(
        connector_id_or_name="my_deepwiki",
        tool_name="read_wiki_structure",
        arguments={"repoName": "sqlite/sqlite"},
    )
    for item in structure.content:
        if hasattr(item, "text"):
            print("Structure:", item.text[:300])

    # Second call: ask a question about the repo
    answer = await client.beta.connectors.call_tool_async(
        connector_id_or_name="my_deepwiki",
        tool_name="ask_question",
        arguments={
            "repoName": "sqlite/sqlite",
            "question": "What is the purpose of the VDBE?",
        },
    )
    for item in answer.content:
        if hasattr(item, "text"):
            print("Answer:", item.text[:300])


asyncio.run(main())
```

**TypeScript**

```typescript
import { Mistral } from "@mistralai/mistralai";

const client = new Mistral({ apiKey: "your-api-key" });

async function main(): Promise<void> {
  // First call: get the repository structure
  const structure = await client.beta.connectors.callTool({
    connectorIdOrName: "my_deepwiki",
    toolName: "read_wiki_structure",
    connectorCallToolRequest: {
      arguments: { repoName: "sqlite/sqlite" },
    },
  });
  for (const item of structure.content ?? []) {
    if ("text" in item) {
      console.log("Structure:", item.text.substring(0, 300));
    }
  }

  // Second call: ask a question about the repo
  const answer = await client.beta.connectors.callTool({
    connectorIdOrName: "my_deepwiki",
    toolName: "ask_question",
    connectorCallToolRequest: {
      arguments: {
        repoName: "sqlite/sqlite",
        question: "What is the purpose of the VDBE?",
      },
    },
  });
  for (const item of answer.content ?? []) {
    if ("text" in item) {
      console.log("Answer:", item.text.substring(0, 300));
    }
  }
}

main();
```

**cURL**

```bash
# First call
curl -X POST "https://api.mistral.ai/v1/connectors/my_deepwiki/tools/read_wiki_structure/call" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"repoName": "sqlite/sqlite"}}'

# Second call
curl -X POST "https://api.mistral.ai/v1/connectors/my_deepwiki/tools/ask_question/call" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"repoName": "sqlite/sqlite", "question": "What is the purpose of the VDBE?"}}'
```
