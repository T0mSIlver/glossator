# mined-031 (single_page, 3 connector calls)

## Question

How do handoffs between agents work, and can an agent that has its own tools hand off to another agent?

## Thinking

The user is asking about handoffs between agents and whether an agent with its own tools can hand off to another agent. This is a specific technical question about Mistral's agent framework. I need to search the documentation for information about agent handoffs, tool usage, and inter-agent communication.

I'll start by searching for "agent handoff" in the Mistral documentation to find relevant sections.

The search returned several relevant hits about handoffs. The first hit is a page specifically about handoffs at https://docs.mistral.ai/studio/agents/handoffs. This looks like the main documentation page for this feature. I should read this page to get a comprehensive understanding of how handoffs work.

I also see hits about:
- Define handoffs responsibilities
- Create an agentic workflow
- How it works
- Multi-agent handoffs in durable agents

I'll start by reading the main handoffs page to get the foundational information.

The page content shows that handoffs are indeed a feature in Mistral's agent framework. It explains that agents can call other agents mid-action, and there's a diagram showing the workflow. However, I need more specific details about the mechanics and the answer to the user's second question about whether an agent with its own tools can hand off to another agent.

Let me also check the durable agents documentation, as that was mentioned in the search results and might provide additional context about multi-agent handoffs.

Now I have enough information from both documentation pages. Let me synthesize the answer:

From the handoffs page:
- Handoffs allow agents to call other agents mid-action
- Agents can have access to specific tools
- You can create workflows with multiple agents with diverse tools, models, and handoffs
- The finance_agent example shows it can have handoffs to other agents like ecb_interest_rate_agent and web_search_agent
- The ecb_interest_rate_agent has its own tools (get_european_central_bank_interest_rate)
- The web_search_agent has its own tools (web_search)
- So yes, an agent with its own tools CAN hand off to another agent

From the durable agents page:
- Agents can delegate tasks to specialized agents using handoffs
- The coordinator agent's instructions and specialized agents' description fields guide handoff decisions
- The model decides when to hand off based on user query and available specialists' descriptions
- The system automatically manages the handoff conversation

Key points to address:
1. How handoffs work: Agents can delegate to other agents, the model decides when to hand off based on descriptions, system manages the conversation
2. Can an agent with tools hand off: Yes, the documentation explicitly shows examples where agents with tools (like web_search_agent with web_search tool) can have handoffs configured to other agents

I should structure the answer clearly with:
- Definition of handoffs
- How they work (mechanism)
- Answer to the specific question (yes, with examples)
- Cite the documentation appropriately

Let me craft the final answer.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "handoffs between agents", "max_hits": 10}
```

Result:

```
q: "handoffs between agents"

[1] https://docs.mistral.ai/studio/agents/handoffs | section: handoffs
    Handoffs
    When creating and using Agents, often with access to specific tools, there are moments where it is desired to call other Agents mid-action. To elaborate and engineer workflows for diverse tasks that you may want automated, this ability to give Agents tasks or hand over a conversation to other agents is called **Handoffs**. ![handoffs_graph](https://docs.mistral.ai/img/handoffs.png)
    cite: https://docs.mistral.ai/studio/agents/handoffs

[2] https://docs.mistral.ai/studio/agents/handoffs | section: define-handoffs-responsibilities
    Handoffs > Create an Agentic Workflow > Define Handoffs Responsabilities
    ![handoffs_graph](https://docs.mistral.ai/img/responsibilities_handoffs.png) Once all our Agents created, we update our previous defined Agents with a list of `handoffs` available. **Python** ```py # Allow the finance_agent to handoff the conversation to the ecb_interest_rate_agent or web_search_agent finance_agent = client.beta.agents.update( agent_id=finance_agent.id, handoffs=[ecb_interest_rate …
    cite: https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities

[3] https://docs.mistral.ai/studio/agents/handoffs | section: create-an-agentic-workflow
    Handoffs > Create an Agentic Workflow
    When creating a workflow powered by Handoffs, we first need to create all the Agents that our workflow will use. There is no limit to how many chained Handoffs a workflow can have. You are free to create multiple Agents using diverse tools, models and handoffs, and orchestrate your own workflow using these Agents.
    cite: https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow

[4] https://docs.mistral.ai/studio/agents/handoffs | section: create-multiple-agents
    Handoffs > Create an Agentic Workflow > Create Multiple Agents
    ![handoffs_graph](https://docs.mistral.ai/img/multiple_agents_handoffs.png) First things first, let's create diverse Agents with multiple tasks and capabilities. **Python** **V1**
    cite: https://docs.mistral.ai/studio/agents/handoffs#create-multiple-agents

[5] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: multi-agent-handoffs
    Durable agents > Multi-agent handoffs
    Agents can delegate tasks to specialized agents using handoffs. The coordinator agent's `instructions` and the specialized agents' `description` fields guide handoff decisions; the model decides when to hand off based on the user query and the available specialists' descriptions. The system automatically manages the handoff conversation. **Python** ```python import mistralai.workflows as workflows …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs

[6] https://docs.mistral.ai/studio/agents/handoffs | section: how-it-works
    Handoffs > How it Works
    Our workflow and behavior are defined, now we can run it. We created 5 agents, some of them have access to built-in tools, and others to local tools like `get_european_central_bank_interest_rate`. It is now possible to have a chain of actions by sending a request to the `finance_agent`. We also provide the parameter `handoff_execution`, which currently has two modes: `server` or `client`. - `serve …
    cite: https://docs.mistral.ai/studio/agents/handoffs#how-it-works

[7] https://docs.mistral.ai/studio/agents/handoffs | section: how-it-works/output-events
    Handoffs > How it Works > Output Events
    Below, you can see the output events of the conversation in order of appearance for the example above.
    cite: https://docs.mistral.ai/studio/agents/handoffs#how-it-works

[8] https://docs.mistral.ai/studio/agents/handoffs | section: how-it-works/output-events-2
    Handoffs > How it Works > Output Events
    Below, you can see the output events of the conversation in order of appearance for the example above.
    cite: https://docs.mistral.ai/studio/agents/handoffs#how-it-works

[9] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: agent
    Durable agents > Core components > Agent
    The `Agent` class defines an LLM agent with its model, instructions, tools, and handoffs: **Python** ```python import mistralai.workflows as workflows import mistralai.workflows.plugins.mistralai as workflows_mistralai agent = workflows_mistralai.Agent( model="mistral-medium-latest", name="my-agent", description="Agent that performs specific tasks", instructions="Use tools to complete the user's r …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent

[10] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: complete-workflow-example
    Durable agents > Complete workflow example
    A full example combining activities, handoffs, and workflow orchestration: **Python**
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#complete-workflow-example

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/handoffs") to read hit 1 on its page
```

### 2. mistral_docs_read_page

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

**TypeScript**

```typescript
// First, let's make the following import
import { z } from 'zod';
import { responseFormatFromZodObject } from '@mistralai/mistralai/extra/structChat.js';

//Then, we define and create our agents
const CalcResult = z.object({
  reasoning: z.string(),
  result: z.string(),
});

let financeAgent = await client.beta.agents.create({
  model: 'mistral-large-latest',
  description: 'Agent used to answer financial related requests',
  name: 'finance-agent',
});

let webSearchAgent = await client.beta.agents.create({
  model: 'mistral-large-latest',
  description: 'Agent that can search online for any information if needed',
  name: 'websearch-agent',
  tools: [{ type: 'web_search' }],
});

let ecbInterestRateAgent = await client.beta.agents.create({
  model: 'mistral-large-latest',
  description:
    'Can find the current interest rate of the European central bank',
  name: 'ecb-interest-rate-agent',
  tools: [
    {
      type: 'function',
      function: {
        name: 'getEuropeanCentralBankInterestRate',
        description:
          'Retrieve the real interest rate of European central bank.',
        parameters: {
          type: 'object',
          properties: {
            date: {
              type: 'string',
            },
          },
          required: ['date'],
        },
      },
    },
  ],
});

const graphAgent = await client.beta.agents.create({
  model: 'mistral-large-latest',
  name: 'graph-drawing-agent',
  description: 'Agent used to create graphs using the code interpreter tool.',
  instructions: 'Use the code interpreter tool when you have to draw a graph.',
  tools: [{ type: 'code_interpreter' }],
});

const calculatorAgent = await client.beta.agents.create({
  model: 'mistral-large-latest',
  name: 'calculator-agent',
  description: 'Agent used to make detailed calculations',
  instructions:
    'When doing calculations explain step by step what you are doing.',
  completionArgs: {
    responseFormat: responseFormatFromZodObject(CalcResult),
  },
});
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/agents" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "model": "mistral-large-latest",
     "name": "finance-agent",
     "description": "Agent used to answer financial related requests"
  }'
```

```bash
curl --location "https://api.mistral.ai/v1/agents" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "model": "mistral-large-latest",
     "name": "websearch-agent",
     "description": "Agent that can search online for any information if needed",
     "tools": [{"type": "web_search"}]
  }'
```

```bash
curl --location "https://api.mistral.ai/v1/agents" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "model": "mistral-large-latest",
     "name": "ecb-interest-rate-agent",
     "description": "Can find the current interest rate of the European central bank",
     "tools": [
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
  }'
```

```bash
curl --location "https://api.mistral.ai/v1/agents" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "model": "mistral-large-latest",
     "name": "graph-drawing-agent",
     "description": "Agent used to create graphs using the code interpreter tool.",
     "instructions": "Use the code interpreter tool when you have to draw a graph.",
     "tools": [{"type": "code_interpreter"}]
  }'
```

```bash
curl --location "https://api.mistral.ai/v1/agents" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "model": "mistral-large-latest",
     "name": "calculator-agent",
     "description": "Agent used to make detailed calculations",
     "instructions": "When doing calculations explain step by step what you are doing.",
     "completion_args": {
          "response_format": {
            "type": "json_schema",
            "json_schema": {
              "schema": {
                "properties": {
                  "reasoning": {
                    "title": "Reasoning",
                    "type": "string"
                  },
                  "result": {
                    "title": "Result",
                    "type": "string"
                  }
                },
                "required": ["reasoning", "result"],
                "title": "CalcResult",
                "type": "object",
                "additionalProperties": false
              },
              "name": "calc_result",
              "strict": true
            }
        }
    }
  }'
```

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

**TypeScript**

```typescript
// Allow the financeAgent to handoff the conversation to the ecbInterestRateAgent or webSearchAgent
financeAgent = await client.beta.agents.update({
  agentId: financeAgent.id,
  agentUpdateRequest: {
    handoffs: [ecbInterestRateAgent.id, webSearchAgent.id],
  },
});

// Allow the ecbInterestRateAgent to handoff the conversation to the grapAgent or calculatorAgent
ecbInterestRateAgent = await client.beta.agents.update({
  agentId: ecbInterestRateAgent.id,
  agentUpdateRequest: {
    handoffs: [graphAgent.id, calculatorAgent.id],
  },
});

// Allow the webSearchAgent to handoff the conversation to the graphAgent or calculatorAgent
webSearchAgent = await client.beta.agents.update({
  agentId: webSearchAgent.id,
  agentUpdateRequest: {
    handoffs: [graphAgent.id, calculatorAgent.id],
  },
});
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/agents/<finance_agent_id>" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "handoffs": ["<ecb_interest_rate_agent_id>", "<web_search_agent_id>"]
  }'
```

```bash
curl --location "https://api.mistral.ai/v1/agents/<ecb_interest_rate_agent_id>" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "handoffs": ["<graph_agent_id>", "<calculator_agent_id>"]
  }'
```

```bash
curl --location "https://api.mistral.ai/v1/agents/<web_search_agent_id>" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "handoffs": ["<graph_agent_id>", "<calculator_agent_id>"]
  }'
```

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

**TypeScript**

```typescript
let response = await client.beta.conversations.start({
  agentId: financeAgent.id,
  inputs:
    'Fetch the current US bank interest rate and calculate the compounded effect if investing for the next 10y',
});
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/conversations" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "inputs": "Fetch the current US bank interest rate and calculate the compounded effect if investing for the next 10y",
     "stream": false,
     "agent_id": "<agent_id>"
  }'
```

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

**TypeScript**

Results: 5 of 7 sections; the page continues.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/handoffs", section="how-it-works/output-events:5") continues; remaining sections: how-it-works/output-events, how-it-works/output-events-2
```

### 3. mistral_docs_read_page

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

## Answer

Yes, **handoffs between agents are fully supported**, and an agent with its own tools **can hand off to another agent**.

### How Handoffs Work
- **Handoffs** allow an agent to delegate a conversation or task to another agent mid-action, enabling multi-agent workflows for complex or specialized tasks.
  [Handoffs](https://docs.mistral.ai/studio/agents/handoffs)

- **Workflow Design**:
  You first create all the agents (each with their own tools, models, and responsibilities), then define which agents can hand off to which others by updating their `handoffs` list with the target agent IDs.
  [Create an Agentic Workflow](https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow)
  [Define Handoffs Responsibilities](https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities)

- **Execution**:
  The coordinator agent (e.g., `finance_agent`) uses its `instructions` and the specialized agents' `description` fields to decide when to hand off. The model dynamically routes the conversation based on the user query and the descriptions of available agents. The system automatically manages the handoff process, including passing context and responses.
  [Multi-agent handoffs](https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs)
  [How it Works](https://docs.mistral.ai/studio/agents/handoffs#how-it-works)

- **Handoff Modes**:
  The `handoff_execution` parameter supports two modes:
  - `server` (default): The handoff is executed internally on Mistral’s cloud.
  - `client`: The handoff is returned to the user, allowing them to handle it externally.
  [How it Works](https://docs.mistral.ai/studio/agents/handoffs#how-it-works)

### Can an Agent with Tools Hand Off?
**Yes.** The documentation explicitly shows examples where:
- An agent like `web_search_agent` (with the `web_search` tool) or `ecb_interest_rate_agent` (with a custom `get_european_central_bank_interest_rate` tool) is configured to hand off to other agents (e.g., `graph_agent` or `calculator_agent`).
  [Define Handoffs Responsibilities](https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities)

- The `finance_agent` (which may or may not have tools) can hand off to `web_search_agent` or `ecb_interest_rate_agent`, both of which have their own tools.
  [Example A and B](https://docs.mistral.ai/studio/agents/handoffs#how-it-works)

### Key Takeaway
Handoffs are designed to chain agents with **diverse tools and specializations**, so an agent’s ability to use tools does not prevent it from handing off to another agent—or being handed off to. The workflow is flexible and supports arbitrary depth of chained handoffs.
[Create an Agentic Workflow](https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow)

