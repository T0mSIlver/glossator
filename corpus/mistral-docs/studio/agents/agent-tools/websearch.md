---
url: https://docs.mistral.ai/studio/agents/agent-tools/websearch
title: Websearch
breadcrumbs: [Studio, Agents, Agents Tools Overview]
kind: doc
locale: en
source_path: src/content/en/docs/studio/agents/agent-tools/websearch/page.mdx
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
---

# Websearch

Websearch is the capability to **browse the web in search of information**, this tool does not only fix the limitations of models of not being up to date due to their training data, but also allows them to actually retrieve recent information or access specific websites.

A handy tool for any agent that needs to be up to date with the world.

Our built-in [tool](https://docs.mistral.ai/studio/agents/agent-tools#built-in-tools) for websearch allows any of our models to access the web at any point to search websites and sources for relevant information to answer the given query.

There are two versions:
- `web_search`: A simple web search tool that enables access to a search engine.
- `web_search_premium`: A more complex web search tool that enables access to both a search engine and to news articles via integrated news provider verification.

> **Warning**
>
> `web_search` and `web_search_premium` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`) because Chat Completions responses don't include the search result references that these tools return.

## Create a Websearch Agent {#create-a-websearch-agent}

You can create an agent with access to websearch by providing it as one of the tools.
Note that you can still add more tools to the agent, the model is free to search the web or not on demand.

**Python**

```py
websearch_agent = client.beta.agents.create(
    model="mistral-medium-latest",
    description="Agent able to search information over the web, such as news, weather, sport results...",
    name="Websearch Agent",
    instructions="You have the ability to perform web searches with `web_search` to find up-to-date information.",
    tools=[{"type": "web_search"}],
    completion_args={
        "temperature": 0.3,
        "top_p": 0.95,
    }
)
```

**TypeScript**

```typescript
const websearchAgent = await client.beta.agents.create({
  model: "mistral-medium-latest",
  name: "WebSearch Agent",
  instructions: "Use your websearch abilities when answering requests you don't know.",
  description: "Agent able to fetch new information on the web.",
  tools: [{ type: "web_search" }],
});
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/agents" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "model": "mistral-medium-latest",
     "name": "Websearch Agent",
     "description": "Agent able to search information over the web, such as news, weather, sport results...",
     "instructions": "You have the ability to perform web searches with `web_search` to find up-to-date information.",
     "tools": [
       {
         "type": "web_search"
       }
     ],
     "completion_args": {
       "temperature": 0.3,
       "top_p": 0.95
     }
  }'
```

**Output**

```json
{
  "model": "mistral-medium-latest",
  "name": "Websearch Agent",
  "description": "Agent able to search information over the web, such as news, weather, sport results...",
  "id": "ag_06835b734cc47dec8000b5f8f860b672",
  "version": 0,
  "created_at": "2025-05-27T12:59:32.803403Z",
  "updated_at": "2025-05-27T12:59:32.803405Z",
  "instructions": "You have the ability to perform web searches with `web_search` to find up-to-date information.",
  "tools": [
    {
      "type": "web_search"
    }
  ],
  "completion_args": {
    "stop": null,
    "presence_penalty": null,
    "frequency_penalty": null,
    "temperature": 0.3,
    "top_p": 0.95,
    "max_tokens": null,
    "random_seed": null,
    "prediction": null,
    "response_format": null,
    "tool_choice": "auto"
  },
  "handoffs": null,
  "object": "agent"
}
```

As for other agents, when creating one you will receive an agent id corresponding to the created agent that you can use to start a conversation.

## How it Works {#how-it-works}

Now that we have our websearch agent ready, we can at any point make use of it to ask it questions about recent events.

### Conversations with Websearch {#conversation-with-websearch}

To start a conversation with our websearch agent, we can use the following code:

**Python**

```py
response = client.beta.conversations.start(
    agent_id=websearch_agent.id,
    inputs="Who won the last European Football cup?"
)
```

**TypeScript**

```typescript
let conversation = await client.beta.conversations.start({
      agentId: agent.id,
      inputs:"Who is Albert Einstein?",
      //store:false
});
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/conversations" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "inputs": "Who won the last European Football cup?",
     "stream": false,
     "agent_id": "<agent_id>"
  }'
```

**Output**

```json
{
  "conversation_id": "conv_06835b734f2776bb80008fa7a309bf5a",
  "outputs": [
    {
      "type": "tool.execution",
      "name": "web_search",
      "object": "entry",
      "created_at": "2025-05-27T12:59:33.171501Z",
      "completed_at": "2025-05-27T12:59:34.828228Z",
      "id": "tool_exec_06835b7352be74d38000b3523a0cce2e"
    },
    {
      "type": "message.output",
      "content": [
        {
          "type": "text",
          "text": "The last winner of the European Football Cup was Spain, who won the UEFA Euro 2024 by defeating England 2-1 in the final"
        },
        {
          "type": "tool_reference",
          "tool": "web_search",
          "title": "UEFA Euro Winners List from 1960 to today - MARCA in English",
          "url": "https://www.marca.com/en/football/uefa-euro/winners.html",
          "source": "brave"
        },
        {
          "type": "tool_reference",
          "tool": "web_search",
          "title": "UEFA Euro winners: Know the champions - full list",
          "url": "https://www.olympics.com/en/news/uefa-european-championships-euro-winners-list-champions",
          "source": "brave"
        },
        {
          "type": "tool_reference",
          "tool": "web_search",
          "title": "Full list of UEFA European Championship winners",
          "url": "https://www.givemesport.com/football-european-championship-winners/",
          "source": "brave"
        },
        {
          "type": "text",
          "text": "."
        }
      ],
      "object": "entry",
      "created_at": "2025-05-27T12:59:35.457474Z",
      "completed_at": "2025-05-27T12:59:36.156233Z",
      "id": "msg_06835b7377517a3680009b05207112ce",
      "agent_id": "ag_06835b734cc47dec8000b5f8f860b672",
      "model": "mistral-medium-latest",
      "role": "assistant"
    }
  ],
  "usage": {
    "prompt_tokens": 188,
    "completion_tokens": 55,
    "total_tokens": 7355,
    "connector_tokens": 7112,
    "connectors": {
      "web_search": 1
    }
  },
  "object": "conversation.response"
}
```

### Explanation of the Output {#explanation-of-the-output}

Below we will explain the different outputs of the response of the previous snippet example:

- **`tool.execution`**: This entry corresponds to the execution of the web search tool. It includes metadata about the execution, such as:
  - `name`: The name of the tool, which in this case is `web_search`.
  - `object`: The type of object, which is `entry`.
  - `type`: The type of entry, which is `tool.execution`.
  - `created_at` and `completed_at`: Timestamps indicating when the tool execution started and finished.
  - `id`: A unique identifier for the tool execution.

- **`message.output`**: This entry corresponds to the generated answer from our agent. It includes metadata about the message, such as:
  - `content`: The actual content of the message, which in this case is a list of chunks. These chunks include the model response text, interleaved with reference chunks. Reference chunks are used for citations during Retrieval-Augmented Generation (RAG) tool calls. In this case, they provide the source of the information in the answer. The `content` section includes:
    - `type`: The type of chunk, which can be `text` or `tool_reference`.
    - `text`: The actual text content of the message.
    - `tool`: The name of the tool used for the reference, which in this case is `web_search`.
    - `title`: The title of the reference source.
    - `url`: The URL of the reference source.
    - `source`: The source of the reference.
  - `object`: The type of object, which is `entry`.
  - `type`: The type of entry, which is `message.output`.
  - `created_at` and `completed_at`: Timestamps indicating when the message was created and completed.
  - `id`: A unique identifier for the message.
  - `agent_id`: A unique identifier for the agent that generated the message.
  - `model`: The model used to generate the message, which in this case is `mistral-medium-latest`.
  - `role`: The role of the message, which is `assistant`.

### More {#more}

Another tool that uses references is the Document Library tool. For details, see the [Libraries guide](https://docs.mistral.ai/studio/search/libraries#connecting-libraries-to-agents).
For more on citations, see the [citations guide](https://docs.mistral.ai/studio/conversations/citations).
