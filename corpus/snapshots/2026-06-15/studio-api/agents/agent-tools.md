---
url: https://docs.mistral.ai/studio-api/agents/agent-tools
title: Agents Tools Overview
breadcrumbs: [Studio, Agents]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/agents/agent-tools/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# Tools

Agents can use tools to interact with the external world, these can be APIs, databases, or other services, increasing the capabilities of your agent and extending its functionality beyond its own knowledge base and fixed environment.

![tools_graph](https://docs.mistral.ai/img/tools_graph.png)

## Tool types {#tool-types}

We provide a variety of different **types** of tools agents can use.

|Type|Description|
|---|---|
|[Web Search](https://docs.mistral.ai/studio-api/agents/agent-tools/websearch)| Built-in. Search the web for up-to-date information not in the agent's knowledge.|
|[Code Interpreter](https://docs.mistral.ai/studio-api/agents/agent-tools/code_interpreter)| Built-in. Run code and generate plots, useful for data analysis, visualization, or sandboxed execution.|
|[Image Generation](https://docs.mistral.ai/studio-api/agents/agent-tools/image_generation)| Built-in. Generate images based on a prompt or description.|
|[Document Library](https://docs.mistral.ai/studio-api/knowledge-rag/libraries#connecting-libraries-to-agents)| Built-in. Search through documents uploaded to your [Libraries](https://docs.mistral.ai/studio-api/knowledge-rag/libraries), enabling RAG to answer questions based on specific information.|
|[Function Calling](https://docs.mistral.ai/studio-api/agents/agent-tools/function-calling)| Custom local tools: functions defined in your environment that can be called by the agent. Execution happens locally.|
|[Connectors](https://docs.mistral.ai/studio-api/knowledge-rag/connectors)| Register MCP servers as managed Connectors. Tools are discovered automatically and executed server-side.|

## Built-in tools {#built-in-tools}

![built_in_graph](https://docs.mistral.ai/img/built_in_graph.png)

Built-in tools are ready out of the box. They can be called at any point, and all execution happens in our internal environment. They're also available for users to use directly via Conversations without creating an Agent first.

### General usage {#general-usage}

These built-in tools are only available when using the Agents and/or Conversations APIs.

To use them, specify the tool in the `tools` parameter when creating an Agent or calling the Conversations API.

> **Tip**
>
> You can use multiple tools at the same time!

**Python**

**agent creation**

```py
agent = client.beta.agents.create(
    model="<model>",
    name="<name_of_the_agent>",
    description="<description>",
    instructions="<instructions_or_system_prompt>",
    tools=[<list_of_tools>]
)
```

**direct conversation**

```py
response = client.beta.conversations.start(
    model="<model>",
    inputs=[<messages_or_question>],
    tools=[<list_of_tools>],
    # store=False
)
```

**TypeScript**

**agent creation**

```typescript
agent = client.beta.agents.create({
    model:"<model>",
    name:"<name_of_the_agent>",
    description:"<description>",
    instructions:"<instructions_or_system_prompt>",
    tools:[<list_of_tools>]
});
```

**direct conversation**

```typescript
response = client.beta.conversations.start({
    model:"<model>",
    inputs:[<messages_or_question>],
    tools:[<list_of_tools>],
    // store:False
});
```

**cURL**

**agent creation**

```bash
curl --location "https://api.mistral.ai/v1/agents" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "model": "<model>",
     "name": "<name_of_the_agent>",
     "description": "<description>",
     "instructions": "<instructions_or_system_prompt>",
     "tools": [<list_of_tools>]
  }'
```

**direct conversation**

```bash
curl --location "https://api.mistral.ai/v1/conversations" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "model": "<model>",
     "inputs": [<messages_or_question>],
     "tools": [<list_of_tools>]
  }'
```
