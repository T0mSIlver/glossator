---
url: https://docs.mistral.ai/studio-api/agents/introduction
title: Agents Introduction
breadcrumbs: [Studio, Agents]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/agents/introduction/page.mdx
source_commit: 5b47202ab46644bb5e7c7ca35d64b121b24c2b11
---

# What are AI agents?

AI agents are autonomous systems powered by large language models (LLMs) that, given high-level instructions, can plan, use tools, carry out processing steps, and take actions to achieve specific goals. These agents use advanced natural language processing to understand and execute complex tasks, and can collaborate with each other to achieve more sophisticated outcomes.

![agents_graph](https://docs.mistral.ai/img/agent_overview.png)

Our Agents and Conversations API allows developers to build such agents, leveraging multiple features such as:
- Multiple mutlimodal models available, **text and vision models**.
- **Persistent state** across conversations.
- Ability to have conversations with **base models**, **a single agent**, and **multiple agents**.
- Built-in connector tools for **code execution**, **web search**, **image generation** and **document library** out of the box.
- **Handoff capability** to use different agents as part of a workflow, allowing agents to call other agents.
- Features supported via our chat completions endpoint are also supported, such as:
  - **Structured Outputs**
  - **Document Understanding**
  - **Tool Usage**
  - **Citations**

### More informations {#more-informations}

- [Agents & Conversations](https://docs.mistral.ai/studio-api/agents/agents-api): Basic explanations and code snippets around our Agents and Conversations API.
- [Tools](https://docs.mistral.ai/studio-api/agents/agent-tools): Make tools accessible to any Agent.
  - [Websearch](https://docs.mistral.ai/studio-api/agents/agent-tools/websearch): In-depth explanation of our web search built-in connector tool.
  - [Code Interpreter](https://docs.mistral.ai/studio-api/agents/agent-tools/code_interpreter): In-depth explanation of our code interpreter for code execution built-in connector tool.
  - [Image Generation](https://docs.mistral.ai/studio-api/agents/agent-tools/image_generation): In-depth explanation of our image generation built-in connector tool.
  - [Document Library](https://docs.mistral.ai/studio-api/knowledge-rag/libraries#connecting-libraries-to-agents): A RAG built-in tool enabling Agents to search through your [Libraries](https://docs.mistral.ai/studio-api/knowledge-rag/libraries).
  - [Function Calling](https://docs.mistral.ai/studio-api/agents/agent-tools/function-calling): Use function calling to create custom tools.
  - [Connectors](https://docs.mistral.ai/studio-api/knowledge-rag/connectors): Register MCP servers as managed Connectors and use them as tools in conversations and Agents.
- [Handoffs](https://docs.mistral.ai/studio-api/agents/handoffs): Relay tasks and use other agents as tools in agentic workflows.

## Cookbooks {#cookbooks}

For more information and guides on how to use our Agents, we have the following cookbooks:
- [Github Agent](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/github_agent)
- [Linear Tickets](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/prd_linear_ticket)
- [Financial Analyst](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/financial_analyst)
- [Travel Assistant](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/travel_assistant)
- [Food Diet Companion](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/food_diet_companion)

## FAQ {#faq}

### Which models are supported? {#which-models-are-supported}

Currently, only `mistral-medium-latest` and `mistral-large-latest` are supported, but we will soon enable it for more models.
