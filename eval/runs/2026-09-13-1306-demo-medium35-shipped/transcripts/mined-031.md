# mined-031 (single_page, 8 connector calls)

## Question

How do handoffs between agents work, and can an agent that has its own tools hand off to another agent?

## Thinking

The user is asking about agent handoffs in Mistral's system. They want to know:
1. How handoffs between agents work
2. Whether an agent with its own tools can hand off to another agent

I need to search the Mistral documentation for information about agent handoffs, multi-agent systems, and tool usage. Let me start by searching for relevant documentation.

The search returned results about durable agents and multi-agent handoffs. Let me read the main page about durable agents to understand the handoff mechanism.

Good, I found information about multi-agent handoffs. Now let me search for more specific information about whether agents with tools can hand off to other agents. Let me also check the handoffs page.

Now let me search for more information about how agents with tools can hand off to other agents. Let me look for details about the handoff mechanism and whether tools are preserved or relevant.

Let me read the Agent class definition to understand how tools and handoffs work together.

Now let me search for more details about how the handoff decision is made and whether an agent's tools are considered.

Let me read the handoffs page more comprehensively to understand the full mechanism.

Now I have comprehensive information about handoffs. Let me also check if there are any limitations or specific behaviors when agents with tools hand off. Let me search for any constraints or special considerations.

I have gathered comprehensive information about handoffs from the Mistral documentation. Let me now synthesize this into a clear answer for the user.

From the documentation, I can see:

1. **How handoffs work**: 
   - Agents can delegate tasks to specialized agents using handoffs
   - The coordinator agent's `instructions` and the specialized agents' `description` fields guide handoff decisions
   - The model decides when to hand off based on the user query and the available specialists' descriptions
   - The system automatically manages the handoff conversation
   - There are two execution modes: `server` (default, runs on Mistral's cloud) and `client` (returns response to user for manual handling)

2. **Can an agent with its own tools hand off to another agent?**
   - Yes, absolutely. The examples in the documentation show agents with tools (like `web_search`, `code_interpreter`, or custom functions) can both receive handoffs and initiate handoffs to other agents
   - The handoff mechanism is independent of whether an agent has tools or not
   - An agent can have both tools and handoffs defined simultaneously

3. **Key details from examples**:
   - The `finance_agent` can hand off to `ecb_interest_rate_agent` or `web_search_agent`
   - The `ecb_interest_rate_agent` has its own tool (`get_european_central_bank_interest_rate`) and can hand off to `graph_agent` or `calculator_agent`
   - The `web_search_agent` has the `web_search` built-in tool and can also hand off to other agents
   - This demonstrates that agents with tools can absolutely hand off to other agents

4. **Configuration**:
   - When creating an agent, you can specify both `tools` and `handoffs` parameters
   - The `Agent` class in the workflows SDK accepts both `tools=[...]` and `handoffs=[...]`

5. **No limitations found**: There's no documentation suggesting that having tools prevents an agent from handing off or receiving handoffs.

Let me structure this answer clearly with proper citations.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "handoff between agents", "max_hits": 10}
```

Result:

```
q: "handoff between agents"

[1] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: multi-agent-handoffs
    Durable agents > Multi-agent handoffs
    Agents can delegate tasks to specialized agents using handoffs. The coordinator agent's `instructions` and the specialized agents' `description` fields guide handoff decisions; the model decides when to hand off based on the user query and the available specialists' descriptions. The system automatically manages the handoff conversation. **Python** ```python import mistralai.workflows as workflows …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs

[2] https://docs.mistral.ai/studio/agents/handoffs | section: define-handoffs-responsibilities
    Handoffs > Create an Agentic Workflow > Define Handoffs Responsabilities
    ![handoffs_graph](https://docs.mistral.ai/img/responsibilities_handoffs.png) Once all our Agents created, we update our previous defined Agents with a list of `handoffs` available. **Python** ```py # Allow the finance_agent to handoff the conversation to the ecb_interest_rate_agent or web_search_agent finance_agent = client.beta.agents.update( agent_id=finance_agent.id, handoffs=[ecb_interest_rate …
    cite: https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities

[3] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: agent-lifecycle
    Durable agents > Session types > Agent lifecycle
    When a `RemoteSession` initializes a conversation, it iterates over every agent in the handoff graph and either creates or updates it via the Agents API: - **`Agent(id=None)`**: a new remote agent is created with `beta.agents.create()`. The returned ID is stored back on the `Agent` object, so subsequent runs with the **same instance** reuse it. - **`Agent(id="existing-id")`**: the existing remote …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent-lifecycle

[4] https://docs.mistral.ai/vibe/code/vs-code-extension/agents | section: custom-agents
    Agents > Custom agents
    The VS Code extension reads the same agent definitions as the CLI from `~/.vibe/agents/` (user-level) and `./.vibe/agents/` (project-level). Custom agents declared there appear in the selector alongside the built-ins. See the [CLI Agents reference](https://docs.mistral.ai/vibe/code/cli/agents) for the full configuration schema, examples, and the difference between `agent_type = "agent"` and `agent …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/agents#custom-agents

[5] https://docs.mistral.ai/studio/agents/agents-api | section: retrieve-all-messages-from-a-specific-conversation
    Agents & Conversations > Conversations > Retrieve all messages from a specific conversation
    **cURL** ```bash curl --location "https://api.mistral.ai/v1/conversations" \ --header 'Content-Type: application/json' \ --header 'Accept: text/event-stream' \ --header "Authorization: Bearer $MISTRAL_API_KEY" \ --data '{ "inputs": "Who is Albert Einstein?", "stream": true, "agent_id": "ag_06811008e6e07cb48000fd3f133e1771" }' ``` When streaming, you will have specific indexes for specific content …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=When%20streaming%2C%20you
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="retrieve-all-messages-from-a-specific-conversation") reads this section

[6] https://docs.mistral.ai/studio/agents/introduction | section: what-are-ai-agents
    Agents Introduction > What are AI agents?
    AI agents are autonomous systems powered by large language models (LLMs) that, given high-level instructions, can plan, use tools, carry out processing steps, and take actions to achieve specific goals. These agents use advanced natural language processing to understand and execute complex tasks, and can collaborate with each other to achieve more sophisticated outcomes. ![agents_graph](https://do …
    cite: https://docs.mistral.ai/studio/agents/introduction

[7] https://docs.mistral.ai/studio/agents/agents-api | section: conversations-2
    Agents & Conversations > Conversations
    In the other hand, Conversations are a history of interactions with an assistant. They are more flexible and expressive than the Chat Completion API, allowing for more control over describing events. > **Conversation access** > > The public Conversations API can read and modify only the conversations owned by the creator of the API key used in the request. Once your agent is created, you can **sta …
    cite: https://docs.mistral.ai/studio/agents/agents-api#:~:text=hand%2C%20Conversations%20are
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="conversations-2") reads this section

[8] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: runner
    Durable agents > Core components > Runner
    The `Runner` executes an agent with user inputs and manages the conversation loop. It calls the model, processes tool calls, and repeats until the agent produces a final response or reaches `max_turns`. If `max_turns` is reached, the runner returns whatever outputs have been collected so far. **Python** ```python import mistralai.workflows as workflows import mistralai.workflows.plugins.mistralai …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#runner

[9] https://docs.mistral.ai/studio/agents/agents-api | section: objects
    Agents & Conversations > Objects
    We introduce three new main objects that our API makes use of: - **Agents**: A set of pre-selected values to augment model abilities, such as tools, instructions, and completion parameters. - **Conversation**: A history of interactions, past events and entries with an assistant, such as messages and tool executions, Conversations can be started by an Agent or a Model. - **Entry**: An action that c …
    cite: https://docs.mistral.ai/studio/agents/agents-api#objects
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="objects") reads this section

[10] https://docs.mistral.ai/studio/agents/agents-api | section: conversations_management
    Agents & Conversations > Conversations > How to manage conversations
    **Continue** Once created, to continue the conversation you will simply provide the next user input, the history of events being stored by default. **Python** ```py response = client.beta.conversations.append( conversation_id=response.conversation_id, inputs="Translate to French.", completion_args={ "temperature": 0.3, "top_p": 0.95, } ) ``` **TypeScript** ```typescript conversation = await client …
    cite: https://docs.mistral.ai/studio/agents/agents-api#conversations_management:~:text=Continue%20Once%20created%2C
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="conversations_management") reads this section

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents", "section": "multi-agent-handoffs"}
```

Result:

```
page: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | "Durable agents" | section: multi-agent-handoffs

## section: multi-agent-handoffs
    Durable agents > Multi-agent handoffs
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs
## Multi-agent handoffs {#multi-agent-handoffs}

Agents can delegate tasks to specialized agents using handoffs. The coordinator agent's `instructions` and the specialized agents' `description` fields guide handoff decisions; the model decides when to hand off based on the user query and the available specialists' descriptions. The system automatically manages the handoff conversation.

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai

# Create a specialized agent for interest rate queries
interest_rate_agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="ecb-interest-rate-agent",
    description="Agent for European Central Bank interest rate research",
    instructions="Use tools to get the interest rate for a given year.",
    tools=[get_interest_rate],
)

# Main agent that can hand off to the specialist
finance_agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="finance-agent",
    description="Agent for financial queries",
    handoffs=[interest_rate_agent],  # Can delegate to interest_rate_agent
)

outputs = await workflows_mistralai.Runner.run(
    agent=finance_agent,
    inputs="What was the ECB interest rate in 2023?",
    session=workflows_mistralai.RemoteSession(),
)
```

When the finance agent receives a query about ECB interest rates, it can automatically hand off to the specialized `interest_rate_agent`.

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents", section="mcp-integration") for the section after it
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/agents/handoffs", "section": "define-handoffs-responsibilities"}
```

Result:

```
page: https://docs.mistral.ai/studio/agents/handoffs | "Handoffs" | section: define-handoffs-responsibilities

## section: define-handoffs-responsibilities
    Handoffs > Create an Agentic Workflow > Define Handoffs Responsabilities
    cite: https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities
### Define Handoffs Responsabilities {#define-handoffs-responsibilities}

![handoffs_graph](https://docs.mistral.ai/img/responsibilities_handoffs.png)

Once all our Agents created, we update our previous defined Agents with a list of `handoffs` available.

**Python**

```py
# Allow the finance_agent to handoff the conversation to the ecb_interest_rate_agent or web_search_agent
finance_agent = client.beta.agents.update(
    agent_id=finance_agent.id,
    handoffs=[ecb_interest_rate_agent.id, web_search_agent.id]
)

# Allow the ecb_interest_rate_agent to handoff the conversation to the graph_agent or calculator_agent
ecb_interest_rate_agent = client.beta.agents.update(
    agent_id=ecb_interest_rate_agent.id,
    handoffs=[graph_agent.id, calculator_agent.id]
)

# Allow the web_search_agent to handoff the conversation to the graph_agent or calculator_agent
web_search_agent = client.beta.agents.update(
    agent_id=web_search_agent.id,
    handoffs=[graph_agent.id, calculator_agent.id]
)
```

(samples in TypeScript and cURL omitted: pass lang="typescript" or lang="curl")



Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/handoffs", section="how-it-works") for the section after it
```

### 4. mistral_docs_search

```json
{"q": "agent with tools handoff to another agent", "max_hits": 10}
```

Result:

```
q: "agent with tools handoff to another agent"

[1] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: build-an-agent-with-tools
    Build an agent with tools
    Give a Mistral model access to external functions it can call mid-conversation. - Define a tool schema that describes your function - Send a message that triggers a tool call - Execute the function locally and feed the result back to the model The pattern works for any data source: APIs, databases, or internal services. **Time to complete:** ~10 minutes
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent

[2] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: multi-agent-handoffs
    Durable agents > Multi-agent handoffs
    Agents can delegate tasks to specialized agents using handoffs. The coordinator agent's `instructions` and the specialized agents' `description` fields guide handoff decisions; the model decides when to hand off based on the user query and the available specialists' descriptions. The system automatically manages the handoff conversation. **Python** ```python import mistralai.workflows as workflows …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs

[3] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: agent-lifecycle
    Durable agents > Session types > Agent lifecycle
    When a `RemoteSession` initializes a conversation, it iterates over every agent in the handoff graph and either creates or updates it via the Agents API: - **`Agent(id=None)`**: a new remote agent is created with `beta.agents.create()`. The returned ID is stored back on the `Agent` object, so subsequent runs with the **same instance** reuse it. - **`Agent(id="existing-id")`**: the existing remote …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent-lifecycle

[4] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: whats-next
    Build an agent with tools > What's next
    - [RAG with document search](https://docs.mistral.ai/getting-started/quickstarts/developer/rag-document-search) - [All developer quickstarts](https://docs.mistral.ai/#quickstarts)
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#whats-next

[5] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: verify
    Build an agent with tools > Verify
    A successful run prints a natural-language response that includes the tool's return value. The model: - Detected the request needed external data - Generated a structured `tool_calls` request - Incorporated your function's result into a conversational answer Set `tool_choice: "any"` to force the model to always call a tool, or use `tool_choice: "auto"` (default) to let the model decide.
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#verify

[6] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: agent
    Durable agents > Core components > Agent
    The `Agent` class defines an LLM agent with its model, instructions, tools, and handoffs: **Python** ```python import mistralai.workflows as workflows import mistralai.workflows.plugins.mistralai as workflows_mistralai agent = workflows_mistralai.Agent( model="mistral-medium-latest", name="my-agent", description="Agent that performs specific tasks", instructions="Use tools to complete the user's r …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent

[7] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: step-2
    Build an agent with tools > Step 2: Send a request with the tool
    Ask the model a question that requires the tool. The model returns a `tool_calls` response instead of a text answer. **Python** ```python messages = [ {"role": "user", "content": "What's the weather in Paris today?"} ] response = client.chat.complete( model="mistral-medium-latest", messages=messages, tools=tools, ) tool_call = response.choices[0].message.tool_calls[0] print(f"Model wants to call: …
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#step-2

[8] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: step-1
    Build an agent with tools > Step 1: Define a tool
    Define the function the model can call. This example creates a `get_weather` tool that accepts a city name. **Python** ```python import json import os from mistralai.client import Mistral client = Mistral(api_key=os.environ["MISTRAL_API_KEY"]) # Define the tool schema tools = [ { "type": "function", "function": { "name": "get_weather", "description": "Get the current weather for a given city.", "p …
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#step-1

[9] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: prerequisites
    Build an agent with tools > Prerequisites
    - A Mistral API key (see [Get your API key](https://docs.mistral.ai/getting-started/quickstarts/developer/first-api-request#step-1) if you don't have one yet) - Python 3.9+ or Node.js 18+ installed - The Mistral SDK installed (see [Install the SDK](https://docs.mistral.ai/getting-started/quickstarts/developer/first-api-request#step-2) if you haven't yet)
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#prerequisites

[10] https://docs.mistral.ai/studio/agents/handoffs | section: define-handoffs-responsibilities
    Handoffs > Create an Agentic Workflow > Define Handoffs Responsabilities
    ![handoffs_graph](https://docs.mistral.ai/img/responsibilities_handoffs.png) Once all our Agents created, we update our previous defined Agents with a list of `handoffs` available. **Python** ```py # Allow the finance_agent to handoff the conversation to the ecb_interest_rate_agent or web_search_agent finance_agent = client.beta.agents.update( agent_id=finance_agent.id, handoffs=[ecb_interest_rate …
    cite: https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent") to read hit 1 on its page
```

### 5. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents", "section": "agent"}
```

Result:

```
page: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | "Durable agents" | section: agent

## section: agent
    Durable agents > Core components > Agent
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent
### Agent {#agent}

The `Agent` class defines an LLM agent with its model, instructions, tools, and handoffs:

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="my-agent",
    description="Agent that performs specific tasks",
    instructions="Use tools to complete the user's request.",
    tools=[my_activity],  # Workflows activities as tools
    handoffs=[other_agent],  # Agents to delegate to
)
```

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents", section="runner") for the section after it
```

### 6. mistral_docs_search

```json
{"q": "handoff decision model instructions description tools", "max_hits": 10}
```

Result:

```
q: "handoff decision model instructions description tools"

[1] https://docs.mistral.ai/studio/agents/agent-tools | section: general-usage
    Agents Tools Overview > Tools > Built-in tools > General usage
    Built-in tool support depends on the API you use. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`). Built-in tools such as `image_generation` are also supported …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#general-usage

[2] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: multi-agent-handoffs
    Durable agents > Multi-agent handoffs
    Agents can delegate tasks to specialized agents using handoffs. The coordinator agent's `instructions` and the specialized agents' `description` fields guide handoff decisions; the model decides when to hand off based on the user query and the available specialists' descriptions. The system automatically manages the handoff conversation. **Python** ```python import mistralai.workflows as workflows …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs

[3] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: built-in-tools
    Durable agents > Built-in tools
    Use Mistral's built-in tools alongside activities: **Python** ```python import mistralai.workflows as workflows import mistralai.workflows.plugins.mistralai as workflows_mistralai from mistralai.client.models import WebSearchTool agent = workflows_mistralai.Agent( model="mistral-medium-latest", name="web-search-agent", description="Agent with web search capability", instructions="Use web search to …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#built-in-tools

[4] https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows | section: complete-example
    Conversational Workflows > Complete example
    ```python import mistralai.workflows as workflows import mistralai.workflows.plugins.mistralai as workflows_mistralai @workflows.workflow.define( name="full-expense-workflow", workflow_display_name="Full Expense Processing", workflow_description="Complete expense workflow with AI analysis and approval", ) class FullExpenseWorkflow(workflows.InteractiveWorkflow): @workflows.workflow.entrypoint asyn …
    cite: https://docs.mistral.ai/studio/workflows/interacting-with-workflows/conversational_workflows#complete-example

[5] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: agent
    Durable agents > Core components > Agent
    The `Agent` class defines an LLM agent with its model, instructions, tools, and handoffs: **Python** ```python import mistralai.workflows as workflows import mistralai.workflows.plugins.mistralai as workflows_mistralai agent = workflows_mistralai.Agent( model="mistral-medium-latest", name="my-agent", description="Agent that performs specific tasks", instructions="Use tools to complete the user's r …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent

[6] https://docs.mistral.ai/studio/agents/agent-tools | section: tool-types
    Agents Tools Overview > Tools > Tool types
    We provide a variety of different **types** of tools agents can use. |Type|Description| |---|---| |[Web Search](https://docs.mistral.ai/studio/agents/agent-tools/websearch)| Built-in. Search the web for up-to-date information not in the agent's knowledge.| |[Code Interpreter](https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter)| Built-in. Run code and generate plots, useful for data …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#tool-types

[7] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: step-1
    Build an agent with tools > Step 1: Define a tool
    Define the function the model can call. This example creates a `get_weather` tool that accepts a city name. **Python** ```python import json import os from mistralai.client import Mistral client = Mistral(api_key=os.environ["MISTRAL_API_KEY"]) # Define the tool schema tools = [ { "type": "function", "function": { "name": "get_weather", "description": "Get the current weather for a given city.", "p …
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent#step-1

[8] https://docs.mistral.ai/studio/agents/handoffs | section: create-multiple-agents
    Handoffs > Create an Agentic Workflow > Create Multiple Agents
    ```py from mistralai import CompletionArgs, ResponseFormat, JSONSchema from pydantic import BaseModel class CalcResult(BaseModel): reasoning: str result: str # Create your agents finance_agent = client.beta.agents.create( model="mistral-large-latest", description="Agent used to answer financial related requests", name="finance-agent", ) web_search_agent = client.beta.agents.create( model="mistral- …
    cite: https://docs.mistral.ai/studio/agents/handoffs#create-multiple-agents

[9] https://docs.mistral.ai/studio/agents/agents-api | section: agent-creation-and-management
    Agents & Conversations > Agent Creation and Management
    Agents are a set of pre-selected values, such as tools, instructions, and completion parameters, that will define the behavior of the model. **Agent Creation** When creating an Agent, there are multiple parameters and values that need to be set in advance. These are: - `model`: The model your agent will use among our available models for chat completion. - `description`: The agent description, rel …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="agent-creation-and-management") reads this section

[10] https://docs.mistral.ai/studio/agents/agents-api | section: creating-an-agent
    Agents & Conversations > Agent Creation and Management > Creating an Agent
    **TypeScript** ```typescript let websearchAgent = await client.beta.agents.create({ model: "mistral-medium-latest", name: "WebSearch Agent", instructions: "Use your websearch abilities when answering requests you don't know.", description: "Agent able to fetch new information on the web.", tools: [{ type: "web_search" }], }); ``` **cURL** ```bash curl -X POST "https://api.mistral.ai/v1/agents" \ - …
    cite: https://docs.mistral.ai/studio/agents/agents-api
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agents-api", section="creating-an-agent") reads this section

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agent-tools") to read hit 1 on its page
```

### 7. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/agents/handoffs"}
```

Result:

```
page: https://docs.mistral.ai/studio/agents/handoffs | "Handoffs"

## section: handoffs
    Handoffs
    cite: https://docs.mistral.ai/studio/agents/handoffs
# Handoffs

When creating and using Agents, often with access to specific tools, there are moments where it is desired to call other Agents mid-action. To elaborate and engineer workflows for diverse tasks that you may want automated, this ability to give Agents tasks or hand over a conversation to other agents is called **Handoffs**.

![handoffs_graph](https://docs.mistral.ai/img/handoffs.png)

## section: create-an-agentic-workflow
    Handoffs > Create an Agentic Workflow
    cite: https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow
## Create an Agentic Workflow {#create-an-agentic-workflow}

When creating a workflow powered by Handoffs, we first need to create all the Agents that our workflow will use.
There is no limit to how many chained Handoffs a workflow can have. You are free to create multiple Agents using diverse tools, models and handoffs, and orchestrate your own workflow using these Agents.

## section: create-multiple-agents
    Handoffs > Create an Agentic Workflow > Create Multiple Agents
    cite: https://docs.mistral.ai/studio/agents/handoffs#create-multiple-agents
### Create Multiple Agents {#create-multiple-agents}

![handoffs_graph](https://docs.mistral.ai/img/multiple_agents_handoffs.png)

First things first, let's create diverse Agents with multiple tasks and capabilities.

**Python**

**V1**

```py
from mistralai import CompletionArgs, ResponseFormat, JSONSchema
from pydantic import BaseModel

class CalcResult(BaseModel):
    reasoning: str
    result: str

# Create your agents
finance_agent = client.beta.agents.create(
    model="mistral-large-latest",
    description="Agent used to answer financial related requests",
    name="finance-agent",
)
web_search_agent = client.beta.agents.create(
    model="mistral-large-latest",
    description="Agent that can search online for any information if needed",
    name="websearch-agent",
    tools=[{"type": "web_search"}],
)
ecb_interest_rate_agent = client.beta.agents.create(
    model="mistral-large-latest",
    description="Can find the current interest rate of the European central bank",
    name="ecb-interest-rate-agent",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_european_central_bank_interest_rate",
                "description": "Retrieve the real interest rate of European central bank.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "date",
                    ]
                },
            },
        },
    ],
)
graph_agent = client.beta.agents.create(
    model="mistral-large-latest",
    name="graph-drawing-agent",
    description="Agent used to create graphs using the code interpreter tool.",
    instructions="Use the code interpreter tool when you have to draw a graph.",
    tools=[{"type": "code_interpreter"}]
)
calculator_agent = client.beta.agents.create(
    model="mistral-large-latest",
    name="calculator-agent",
    description="Agent used to make detailed calculations",
    instructions="When doing calculations explain step by step what you are doing.",
    completion_args=CompletionArgs(
          response_format=ResponseFormat(
            type="json_schema",
            json_schema=JSONSchema(
                name="calc_result",
                schema=CalcResult.model_json_schema(),
            )
        )
    )
)
```

**V2**

```py
from mistralai.client import CompletionArgs, ResponseFormat, JSONSchema
from pydantic import BaseModel

class CalcResult(BaseModel):
    reasoning: str
    result: str

# Create your agents
finance_agent = client.beta.agents.create(
    model="mistral-large-latest",
    description="Agent used to answer financial related requests",
    name="finance-agent",
)
web_search_agent = client.beta.agents.create(
    model="mistral-large-latest",
    description="Agent that can search online for any information if needed",
    name="websearch-agent",
    tools=[{"type": "web_search"}],
)
ecb_interest_rate_agent = client.beta.agents.create(
    model="mistral-large-latest",
    description="Can find the current interest rate of the European central bank",
    name="ecb-interest-rate-agent",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_european_central_bank_interest_rate",
                "description": "Retrieve the real interest rate of European central bank.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "date",
                    ]
                },
            },
        },
    ],
)
graph_agent = client.beta.agents.create(
    model="mistral-large-latest",
    name="graph-drawing-agent",
    description="Agent used to create graphs using the code interpreter tool.",
    instructions="Use the code interpreter tool when you have to draw a graph.",
    tools=[{"type": "code_interpreter"}]
)
calculator_agent = client.beta.agents.create(
    model="mistral-large-latest",
    name="calculator-agent",
    description="Agent used to make detailed calculations",
    instructions="When doing calculations explain step by step what you are doing.",
    completion_args=CompletionArgs(
          response_format=ResponseFormat(
            type="json_schema",
            json_schema=JSONSchema(
                name="calc_result",
                schema=CalcResult.model_json_schema(),
            )
        )
    )
)
```

(samples in TypeScript and cURL omitted: pass lang="typescript" or lang="curl")









## section: define-handoffs-responsibilities
    Handoffs > Create an Agentic Workflow > Define Handoffs Responsabilities
    cite: https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities
### Define Handoffs Responsabilities {#define-handoffs-responsibilities}

![handoffs_graph](https://docs.mistral.ai/img/responsibilities_handoffs.png)

Once all our Agents created, we update our previous defined Agents with a list of `handoffs` available.

**Python**

```py
# Allow the finance_agent to handoff the conversation to the ecb_interest_rate_agent or web_search_agent
finance_agent = client.beta.agents.update(
    agent_id=finance_agent.id,
    handoffs=[ecb_interest_rate_agent.id, web_search_agent.id]
)

# Allow the ecb_interest_rate_agent to handoff the conversation to the graph_agent or calculator_agent
ecb_interest_rate_agent = client.beta.agents.update(
    agent_id=ecb_interest_rate_agent.id,
    handoffs=[graph_agent.id, calculator_agent.id]
)

# Allow the web_search_agent to handoff the conversation to the graph_agent or calculator_agent
web_search_agent = client.beta.agents.update(
    agent_id=web_search_agent.id,
    handoffs=[graph_agent.id, calculator_agent.id]
)
```

(samples in TypeScript and cURL omitted: pass lang="typescript" or lang="curl")



## section: how-it-works
    Handoffs > How it Works
    cite: https://docs.mistral.ai/studio/agents/handoffs#how-it-works
## How it Works {#how-it-works}

Our workflow and behavior are defined, now we can run it.

We created 5 agents, some of them have access to built-in tools, and others to local tools like `get_european_central_bank_interest_rate`.

It is now possible to have a chain of actions by sending a request to the `finance_agent`.

We also provide the parameter `handoff_execution`, which currently has two modes: `server` or `client`.

- `server`: Runs the handoff as expected internally on our cloud servers; this is the default setting.
- `client`: When a handoff is triggered, a response is provided directly to the user, enabling them to handle the handoff with control.

Let’s trigger two different behaviors as examples:

**Example A**

**"Fetch the current US bank interest rate and calculate the compounded effect if investing for the next 10y"**

The first example asks for the US central bank interest rate, so we expect to involve the `websearch-agent` and then to calculate the compounded interest over 10 years. This should use the `calculator-agent` to do this.

![handoffs_graph_examplea](https://docs.mistral.ai/img/examplea_handoffs.png)

**Python**

```py
response = client.beta.conversations.start(
    agent_id=finance_agent.id,
    inputs="Fetch the current US bank interest rate and calculate the compounded effect if investing for the next 10y"
)
```

(samples in TypeScript and cURL omitted: pass lang="typescript" or lang="curl")

## section: how-it-works/output-events
    Handoffs > How it Works > Output Events
    cite: https://docs.mistral.ai/studio/agents/handoffs#how-it-works
### Output Events

Below, you can see the output events of the conversation in order of appearance for the example above.

```shell
Conversation started: conv_067f7fce0aba70728000b32dcb0ac7e5

## Event type: agent.handoff

agent_id='ag_067f7fce04517b60800013b213ff2acb' agent_name='websearch-agent' object='conversation.entry' type='agent.handoff' created_at=datetime.datetime(2025, 4, 10, 17, 16, 18, 952817, tzinfo=TzInfo(UTC)) id='handoff_067f7fce2f3f7423800094104f3e3589'


## Event type: tool.execution

name='web_search' object='conversation.entry' type='tool.execution' created_at=datetime.datetime(2025, 4, 10, 17, 16, 23, 12996, tzinfo=TzInfo(UTC)) id='tool_exec_067f7fce7035747e800085153507b345'


## Event type: message.output

content=[TextChunk(text='The current US bank interest rate is 4.50 percent', type='text'), ToolReferenceChunk(tool='web_search', title='United States Fed Funds Interest Rate', type='tool_reference', url='https://tradingeconomics.com/united-states/interest-rate'), TextChunk(text='.\n\nI will now handoff the conversation to the calculator agent to calculate the compounded effect if investing for the next 10 years.', type='text')] object='conversation.entry' type='message.output' created_at=datetime.datetime(2025, 4, 10, 17, 16, 23, 14612, tzinfo=TzInfo(UTC)) id='msg_067f7fce703b7e01800045b2309a0750' agent_id='ag_067f7fce04517b60800013b213ff2acb' model='mistral-medium-latest' role='assistant'


## Event type: agent.handoff

agent_id='ag_067f7fce017f71a580001bf69f2cc11e' agent_name='calculator-agent' object='conversation.entry' type='agent.handoff' created_at=datetime.datetime(2025, 4, 10, 17, 16, 23, 14726, tzinfo=TzInfo(UTC)) id='handoff_067f7fce703c753680006aedb42ba7b7'


## Event type: message.output

content=' {"result": "The future value of the investment after 10 years is $1,540.10.", "reasoning": "To calculate the compounded effect of investing at the current US bank interest rate of 4.50% for the next 10 years, we use the formula for compound interest: A = P(1 + r/n)^(nt), where A is the amount of money accumulated after n years, including interest. P is the principal amount (the initial amount of money). r is the annual interest rate (decimal). n is the number of times that interest is compounded per year. t is the time the money is invested for, in years. Assuming an initial investment (P) of $1,000, an annual interest rate (r) of 4.50% (or 0.045 as a decimal), compounded annually (n = 1), over 10 years (t = 10): A = 1000(1 + 0.045/1)^(1*10) = 1000(1 + 0.045)^10 = 1000(1.045)^10 ≈ 1540.10. Therefore, the future value of the investment after 10 years is approximately $1,540.10."}' object='conversation.entry' type='message.output' created_at=datetime.datetime(2025, 4, 10, 17, 16, 30, 145207, tzinfo=TzInfo(UTC)) id='msg_067f7fcee2527cf08000744d983639dc' agent_id='ag_067f7fce017f71a580001bf69f2cc11e' model='mistral-medium-latest' role='assistant'
```

**Example B**

**"Given the interest rate of the European Central Bank as of jan 2025, plot a graph of the compounded interest rate over the next 10 years"**

The second example asks for the European central bank interest rate and to plot a graph of the compounded interest. Now we require a local function call since the `ecb-interest-rate-agent` will surelly be required.

![handoffs_graph_exampleb](https://docs.mistral.ai/img/exampleb_handoffs.png)

**Python**

**V1**

```py
from mistralai import FunctionResultEntry

response = client.beta.conversations.start(
    agent_id=finance_agent.id,
    inputs="Given the interest rate of the European Central Bank as of jan 2025, plot a graph of the compounded interest rate over the next 10 years"
)
if response.outputs[-1].type == "function.call" and response.outputs[-1].name == "get_european_central_bank_interest_rate":

    # Add a dummy result for the function call
    user_entry = FunctionResultEntry(
        tool_call_id=response.outputs[-1].tool_call_id,
        result="2.5%",
    )
    response = client.beta.conversations.append(
        conversation_id=response.conversation_id,
        inputs=[user_entry]
    )

# A full code snippet to download all generated images and plots from the response could look like so:
from mistralai.models import ToolFileChunk

for i, chunk in enumerate(response.outputs[-1].content):
    # Check if chunk corresponds to a ToolFileChunk
    if isinstance(chunk, ToolFileChunk):

      # Download using the ToolFileChunk ID
      file_bytes = client.files.download(file_id=chunk.file_id).read()

      # Save the file locally
      with open(f"plot_generated_{i}.png", "wb") as file:
          file.write(file_bytes)
```

**V2**


```py
from mistralai.client import FunctionResultEntry

response = client.beta.conversations.start(
    agent_id=finance_agent.id,
    inputs="Given the interest rate of the European Central Bank as of jan 2025, plot a graph of the compounded interest rate over the next 10 years"
)
if response.outputs[-1].type == "function.call" and response.outputs[-1].name == "get_european_central_bank_interest_rate":

    # Add a dummy result for the function call
    user_entry = FunctionResultEntry(
        tool_call_id=response.outputs[-1].tool_call_id,
        result="2.5%",
    )
    response = client.beta.conversations.append(
        conversation_id=response.conversation_id,
        inputs=[user_entry]
    )

# A full code snippet to download all generated images and plots from the response could look like so:
from mistralai.client.models import ToolFileChunk

for i, chunk in enumerate(response.outputs[-1].content):
    # Check if chunk corresponds to a ToolFileChunk
    if isinstance(chunk, ToolFileChunk):

      # Download using the ToolFileChunk ID
      file_bytes = client.files.download(file_id=chunk.file_id).read()

      # Save the file locally
      with open(f"plot_generated_{i}.png", "wb") as file:
          file.write(file_bytes)
```

(samples in TypeScript and cURL omitted: pass lang="typescript" or lang="curl")





## section: how-it-works/output-events-2
    Handoffs > How it Works > Output Events
    cite: https://docs.mistral.ai/studio/agents/handoffs#how-it-works
### Output Events

Below, you can see the output events of the conversation in order of appearance for the example above.

```shell
Conversation started: conv_067f7e71523d7be3800005c4ac560a7b

## Event type: agent.handoff

agent_id='ag_067f7e714f6e751480002beb3bfe0779' agent_name='ecb-interest-rate-agent' object='conversation.entry' type='agent.handoff' created_at=datetime.datetime(2025, 4, 10, 15, 43, 18, 590169, tzinfo=TzInfo(UTC)) id='handoff_067f7e71697176098000aa403030a74e'


## Event type: function.call

tool_call_id='NqCFiwvSV' name='get_european_central_bank_interest_rate' arguments='{"date": "2025-01-01"}' object='conversation.entry' type='function.call' created_at=datetime.datetime(2025, 4, 10, 15, 43, 20, 173505, tzinfo=TzInfo(UTC)) id='fc_067f7e7182c67b9c80006f27131026a8'


## User added event function.result:

tool_call_id='NqCFiwvSV' result='2.5%' object='conversation.entry' type='function.result' created_at=None id=None

## Event type: agent.handoff:

agent_id='ag_067f7e7147e077a280005b4ae524d317' agent_name='graph-drawing-agent' object='conversation.entry' type='agent.handoff' created_at=datetime.datetime(2025, 4, 10, 15, 43, 26, 261436, tzinfo=TzInfo(UTC)) id='handoff_067f7e71e42e7e2080009fc4fd68164a'


## Event type: message.output:

content="To plot the graph of the compounded interest rate over the next 10 years, we can use the formula for compound interest:\n\n\\[ A = P \\left(1 + \\frac{r}{n}\\right)^{nt} \\]\n\nwhere:\n- \\( A \\) is the amount of money accumulated after n years, including interest.\n- \\( P \\) is the principal amount (the initial amount of money).\n- \\( r \\) is the annual interest rate (decimal).\n- \\( n \\) is the number of times that interest is compounded per year.\n- \\( t \\) is the time the money is invested for, in years.\n\nGiven:\n- The annual interest rate \\( r = 2.5\\% = 0.025 \\).\n- Assuming the interest is compounded annually (\\( n = 1 \\)).\n- We will calculate the compounded amount for each year over the next 10 years.\n\nLet's assume the principal amount \\( P = 1000 \\) (you can choose any amount as it will not affect the rate plot).\n\nWe will calculate the compounded amount for each year and plot it." object='conversation.entry' type='message.output' created_at=datetime.datetime(2025, 4, 10, 15, 43, 39, 385339, tzinfo=TzInfo(UTC)) id='msg_067f7e72b62a768f800022b2504adfc9' agent_id='ag_067f7e7147e077a280005b4ae524d317' model='mistral-medium-latest' role='assistant'


## Event type: tool.execution:

name='code_interpreter' object='conversation.entry' type='tool.execution' created_at=datetime.datetime(2025, 4, 10, 15, 43, 39, 385463, tzinfo=TzInfo(UTC)) id='tool_exec_067f7e72b62a7e3a800072733a6a57f2'


## Event type: message.output:

content=[ToolFileChunk(tool='code_interpreter', file_id='40420c94-5f99-477f-8891-943f0defbe3b', type='tool_file', file_name='plot_0.png', file_type='png'), TextChunk(text='![Image](__emitted_0.png)\n\nThe graph shows the compounded interest over 10 years with an annual interest rate of 2.5%. The principal amount is set to $1000, and the interest is compounded once per year. The y-axis represents the amount of money, and the x-axis represents the number of years.', type='text')] object='conversation.entry' type='message.output' created_at=datetime.datetime(2025, 4, 10, 15, 43, 39, 898738, tzinfo=TzInfo(UTC)) id='msg_067f7e72be6173f48000e85e9976305a' agent_id='ag_067f7e7147e077a280005b4ae524d317' model='mistral-medium-latest' role='assistant'
```

Results: 7 sections, the whole page.
```

### 8. mistral_docs_search

```json
{"q": "agent handoff tools limitations constraints", "max_hits": 10}
```

Result:

```
q: "agent handoff tools limitations constraints"

[1] https://docs.mistral.ai/inference/regional-inference | section: regional-inference-limitations
    Regional inference > What is supported by regional inference? > Limitations
    Regional endpoints have feature limitations. If a workload depends on an unsupported feature, the regional processing guarantees for that workload do not apply. - Not all [tool calls](https://docs.mistral.ai/studio/agents/agent-tools) are currently supported. [Function calling](https://docs.mistral.ai/studio/agents/agent-tools/function-calling) is the only supported regional tool. - Stateful featu …
    cite: https://docs.mistral.ai/inference/regional-inference#regional-inference-limitations

[2] https://docs.mistral.ai/resources/known-limitations | section: function-calling
    Known limitations > Function calling
    - Maximum number of tools per request: **128**. - Tool descriptions are included in the token count. Long descriptions reduce available context for messages. - Parallel function calls are supported but may return calls in any order. - `tool_choice: "any"` forces a tool call but does not guarantee which tool is selected.
    cite: https://docs.mistral.ai/resources/known-limitations#function-calling

[3] https://docs.mistral.ai/resources/known-limitations | section: known-limitations
    Known limitations
    This page documents current limitations of the Mistral platform. We actively work to address these. Check the [changelogs](https://docs.mistral.ai/resources/changelogs) for updates.
    cite: https://docs.mistral.ai/resources/known-limitations

[4] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: multi-agent-handoffs
    Durable agents > Multi-agent handoffs
    Agents can delegate tasks to specialized agents using handoffs. The coordinator agent's `instructions` and the specialized agents' `description` fields guide handoff decisions; the model decides when to hand off based on the user query and the available specialists' descriptions. The system automatically manages the handoff conversation. **Python** ```python import mistralai.workflows as workflows …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs

[5] https://docs.mistral.ai/vibe/work/connectors/mcp-connectors | section: limitations
    MCP Connectors > Current limitations
    Custom MCP Connectors don't yet support all MCP capabilities: - [Dynamic tool discovery](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) - [Resources](https://modelcontextprotocol.io/specification/2025-06-18/server/resources) - [Automatic prompt templates](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts#prompts) We plan to add support for these in fut …
    cite: https://docs.mistral.ai/vibe/work/connectors/mcp-connectors#limitations

[6] https://docs.mistral.ai/studio/workflows/building-workflows/on_behalf_of | section: constraints
    On-behalf-of workflows > Constraints
    > **Warning** > > `on_behalf_of=True` **cannot** be combined with `schedules`. Scheduled executions have no triggering user, so the identity context would be undefined. This is enforced at both decorator time and registration time. - The caller must have a full user identity. Executions triggered by API keys without `user_id` / `organization_id` headers are rejected. - The identity JWT is short-li …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/on_behalf_of#constraints

[7] https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent | section: build-an-agent-with-tools
    Build an agent with tools
    Give a Mistral model access to external functions it can call mid-conversation. - Define a tool schema that describes your function - Send a message that triggers a tool call - Execute the function locally and feed the result back to the model The pattern works for any data source: APIs, databases, or internal services. **Time to complete:** ~10 minutes
    cite: https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent

[8] https://docs.mistral.ai/studio/agents/agent-tools | section: general-usage
    Agents Tools Overview > Tools > Built-in tools > General usage
    Built-in tool support depends on the API you use. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`). Built-in tools such as `image_generation` are also supported …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#general-usage

[9] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: agent-lifecycle
    Durable agents > Session types > Agent lifecycle
    When a `RemoteSession` initializes a conversation, it iterates over every agent in the handoff graph and either creates or updates it via the Agents API: - **`Agent(id=None)`**: a new remote agent is created with `beta.agents.create()`. The returned ID is stored back on the `Agent` object, so subsequent runs with the **same instance** reuse it. - **`Agent(id="existing-id")`**: the existing remote …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent-lifecycle

[10] https://docs.mistral.ai/resources/known-limitations | section: file-uploads
    Known limitations > File uploads
    - Maximum file size: **512 MB** - Supported formats for OCR: PDF, PNG, JPG, JPEG, TIFF, BMP, GIF, WEBP - Uploaded files are retained for 30 days unless deleted earlier.
    cite: https://docs.mistral.ai/resources/known-limitations#file-uploads

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/inference/regional-inference") to read hit 1 on its page
```

## Answer

Yes, **an agent with its own tools can absolutely hand off to another agent**. Handoffs are a core feature of Mistral's multi-agent system, and having tools does not prevent an agent from delegating work to other agents.

---

## How Handoffs Work

- **Decision mechanism**: The model decides when to hand off based on the **user query**, the **coordinator agent's `instructions`**, and the **specialized agents' `description`** fields. The system automatically manages the handoff conversation flow.
  [Durable agents > Multi-agent handoffs](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs)

- **Execution modes**: Handoffs can run in two modes:
  - **`server`** (default): The handoff is executed internally on Mistral's cloud servers.
  - **`client`**: The handoff is returned to the user, allowing them to handle it manually.
  [Handoffs > How it Works](https://docs.mistral.ai/studio/agents/handoffs#how-it-works)

- **Conversation management**: The system tracks handoff events, tool executions, and messages as part of the conversation history, enabling seamless transitions between agents.
  [Handoffs > How it Works > Output Events](https://docs.mistral.ai/studio/agents/handoffs#how-it-works)

---

## Agents with Tools Can Hand Off

An agent can simultaneously have **tools** and **handoffs** configured. For example:

- The `finance_agent` (with no tools) can hand off to the `web_search_agent` (which has the `web_search` built-in tool) or the `ecb_interest_rate_agent` (which has a custom function tool).
- The `web_search_agent` or `ecb_interest_rate_agent` can, in turn, hand off to the `calculator_agent` or `graph_agent` (which has the `code_interpreter` tool).
  [Handoffs > Create an Agentic Workflow](https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow)

In the `Agent` class, you explicitly define both:
```python
agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="my-agent",
    tools=[my_tool],          # Agent has its own tools
    handoffs=[other_agent],   # Agent can hand off to others
)
```
[Durable agents > Core components > Agent](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent)

---

## Practical Example

In the documentation's workflow examples:
1. A user asks the `finance_agent` to *"Fetch the current US bank interest rate and calculate the compounded effect if investing for the next 10y"*.
2. The `finance_agent` hands off to the `web_search_agent` (which uses its `web_search` tool to find the rate).
3. The `web_search_agent` then hands off to the `calculator_agent` to perform the compound interest calculation.
   [Handoffs > How it Works > Example A](https://docs.mistral.ai/studio/agents/handoffs#how-it-works)

This demonstrates that **agents with tools can both receive and initiate handoffs** as part of a multi-agent workflow.

