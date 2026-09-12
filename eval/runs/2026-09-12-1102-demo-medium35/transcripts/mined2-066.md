# mined2-066 (unanswerable, 9 connector calls)

## Question

Which models can be chained in agent handoffs — is there a published list, or is any chat model allowed?

## Thinking

The user is asking about which models can be chained in agent handoffs, specifically whether there's a published list or if any chat model is allowed. This is a specific question about Mistral AI's agent handoff capabilities and model compatibility.

I need to search the Mistral documentation for information about:
1. Agent handoffs
2. Model chaining
3. Which models are supported
4. Any published lists of compatible models

Let me start by searching for "agent handoff" or related terms in the documentation.

The search results show information about handoffs in Mistral Studio, but they don't explicitly mention which models can be chained. Let me read the main handoffs documentation page to see if there are any restrictions mentioned.

The documentation page shows that agents can be created with different models (like `mistral-large-latest` and `mistral-medium-latest` in the examples), and there's no explicit restriction mentioned about which models can be chained. However, I need to search more specifically for any published list or restrictions.

Let me search for information about model compatibility or restrictions for handoffs.

The search results still don't explicitly mention model restrictions. Let me check the durable agents page which mentions multi-agent handoffs.

This page also doesn't mention specific model restrictions. Let me search more specifically for model lists or compatibility information in the context of agents.

Let me check the models API endpoint to see if there's information about which models are available and if there are any restrictions mentioned.

The models API endpoint exists but doesn't show the actual list. Let me search for more specific information about model compatibility with agents and handoffs.

Excellent! I found a relevant result. The search shows that in the Agents Introduction FAQ, there's a section "Which models are supported?" that states:

"Currently, only `mistral-medium-latest` and `mistral-large-latest` are supported, but we will soon enable it for more models."

This directly answers the user's question. Let me read this page to confirm and get the full context.

Perfect! I found the answer. The documentation explicitly states in the Agents Introduction FAQ that currently only `mistral-medium-latest` and `mistral-large-latest` are supported for agents, and they will soon enable it for more models.

This means:
1. There IS a published list (in the FAQ)
2. NOT any chat model is allowed - only specific ones
3. The current list is: mistral-medium-latest and mistral-large-latest

Now I need to check if this information is specific to agents in general or specifically to handoffs. Let me search for any handoff-specific model restrictions.

The search results confirm that the model support information is in the Agents Introduction FAQ. The handoffs documentation doesn't seem to have separate model restrictions - it inherits from the general agent model support.

Based on the documentation I've found:

1. There IS a published list of supported models for agents (which includes handoffs)
2. Currently only `mistral-medium-latest` and `mistral-large-latest` are supported
3. More models will be enabled soon

The handoffs documentation shows examples using `mistral-large-latest` and `mistral-medium-latest`, which aligns with the FAQ statement.

Therefore, the answer is: No, not any chat model is allowed. There is a published list, and currently only `mistral-medium-latest` and `mistral-large-latest` are supported for agents (including handoffs).

Let me verify if there are any other model-related restrictions or if this is the complete answer.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "agent handoffs chained models list", "max_hits": 5}
```

Result:

```
q: "agent handoffs chained models list"

[1] https://docs.mistral.ai/studio/agents/handoffs | section: create-an-agentic-workflow
    Handoffs > Create an Agentic Workflow
    When creating a workflow powered by Handoffs, we first need to create all the Agents that our workflow will use. There is no limit to how many chained Handoffs a workflow can have. You are free to create multiple Agents using diverse tools, models and handoffs, and orchestrate your own workflow using these Agents.
    cite: https://docs.mistral.ai/studio/agents/handoffs#create-an-agentic-workflow

[2] https://docs.mistral.ai/studio/agents/handoffs | section: define-handoffs-responsibilities
    Handoffs > Create an Agentic Workflow > Define Handoffs Responsabilities
    ![handoffs_graph](https://docs.mistral.ai/img/responsibilities_handoffs.png) Once all our Agents created, we update our previous defined Agents with a list of `handoffs` available. **Python** ```py # Allow the finance_agent to handoff the conversation to the ecb_interest_rate_agent or web_search_agent finance_agent = client.beta.agents.update( agent_id=finance_agent.id, handoffs=[ecb_interest_rate …
    cite: https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities

[3] https://docs.mistral.ai/studio/agents/handoffs | section: handoffs
    Handoffs
    When creating and using Agents, often with access to specific tools, there are moments where it is desired to call other Agents mid-action. To elaborate and engineer workflows for diverse tasks that you may want automated, this ability to give Agents tasks or hand over a conversation to other agents is called **Handoffs**. ![handoffs_graph](https://docs.mistral.ai/img/handoffs.png)
    cite: https://docs.mistral.ai/studio/agents/handoffs

[4] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: multi-agent-handoffs
    Durable agents > Multi-agent handoffs
    Agents can delegate tasks to specialized agents using handoffs. The coordinator agent's `instructions` and the specialized agents' `description` fields guide handoff decisions; the model decides when to hand off based on the user query and the available specialists' descriptions. The system automatically manages the handoff conversation. **Python** ```python import mistralai.workflows as workflows …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs

[5] https://docs.mistral.ai/studio/agents/handoffs | section: how-it-works/output-events
    Handoffs > How it Works > Output Events
    ```bash curl --location "https://api.mistral.ai/v1/conversations" \ --header 'Content-Type: application/json' \ --header 'Accept: application/json' \ --header "Authorization: Bearer $MISTRAL_API_KEY" \ --data '{ "inputs": [ { "type": "function.result", "tool_call_id": "<tool_call_id>", "result": "2.5%" } ], "stream": false, "agent_id": "<agent_id>" }' ```
    cite: https://docs.mistral.ai/studio/agents/handoffs#how-it-works

Results: 5 hits
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

### 3. mistral_docs_search

```json
{"q": "agent handoff model compatibility list restrictions", "max_hits": 5}
```

Result:

```
q: "agent handoff model compatibility list restrictions"

[1] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: multi-agent-handoffs
    Durable agents > Multi-agent handoffs
    Agents can delegate tasks to specialized agents using handoffs. The coordinator agent's `instructions` and the specialized agents' `description` fields guide handoff decisions; the model decides when to hand off based on the user query and the available specialists' descriptions. The system automatically manages the handoff conversation. **Python** ```python import mistralai.workflows as workflows …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs

[2] https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription | section: compatibility-table
    Offline > Offline Transcription > OpenAI SDK compatibility > Compatibility table
    | Feature | OpenAI SDK compatible | | :-------------------------------------------------- | :------------------------ | | Basic transcription (`file`) | Yes | | Language specification (`language`) | Yes | | Timestamp granularities (`timestamp_granularities`) | Yes | | Streaming (`stream`) | Yes | | Diarization (`diarize`) | Yes with `extra_body` | | Context biasing (`context_bias`) | Yes with `ext …
    cite: https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription#compatibility-table
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription", section="compatibility-table") reads this section

[3] https://docs.mistral.ai/studio/agents/handoffs | section: define-handoffs-responsibilities
    Handoffs > Create an Agentic Workflow > Define Handoffs Responsabilities
    ![handoffs_graph](https://docs.mistral.ai/img/responsibilities_handoffs.png) Once all our Agents created, we update our previous defined Agents with a list of `handoffs` available. **Python** ```py # Allow the finance_agent to handoff the conversation to the ecb_interest_rate_agent or web_search_agent finance_agent = client.beta.agents.update( agent_id=finance_agent.id, handoffs=[ecb_interest_rate …
    cite: https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities

[4] https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription | section: openai-sdk-compatibility
    Offline > Offline Transcription > OpenAI SDK compatibility
    The Mistral transcription endpoint follows the same request structure as the OpenAI audio transcriptions API. You can use the OpenAI SDK by pointing it at the Mistral base URL and swapping the model name. > **Warning** > > We don't recommend using the OpenAI SDK for long-term use. This compatibility layer targets quick testing and prototyping. For production usage, we recommend using the [Mistral …
    cite: https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription#openai-sdk-compatibility
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription", section="openai-sdk-compatibility") reads this section

[5] https://docs.mistral.ai/studio/agents/handoffs | section: how-it-works/output-events
    Handoffs > How it Works > Output Events
    ```shell Conversation started: conv_067f7fce0aba70728000b32dcb0ac7e5 ## Event type: agent.handoff agent_id='ag_067f7fce04517b60800013b213ff2acb' agent_name='websearch-agent' object='conversation.entry' type='agent.handoff' created_at=datetime.datetime(2025, 4, 10, 17, 16, 18, 952817, tzinfo=TzInfo(UTC)) id='handoff_067f7fce2f3f7423800094104f3e3589' ## Event type: tool.execution name='web_search' o …
    cite: https://docs.mistral.ai/studio/agents/handoffs#how-it-works

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents") to read hit 1 on its page
```

### 4. mistral_docs_read_page

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

### 5. mistral_docs_search

```json
{"q": "chat models list agents studio", "max_hits": 5}
```

Result:

```
q: "chat models list agents studio"

[1] https://docs.mistral.ai/vibe/chat-legacy/agents | section: agents-and-api
    Agents > Agents and the API
    Agents created in Chat are designed for the chat interface and can't be used programmatically. If you need API access, create Agents through [Agents](https://console.mistral.ai/build/agents) or the [REST API](https://docs.mistral.ai/api/#tag/beta.agents). Studio Agents can be deployed to Chat and appear in a dedicated section of your Agent list.
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#agents-and-api

[2] https://docs.mistral.ai/studio | section: studio-capabilities
    Studio > Studio capabilities
    Studio gives you programmatic access to Mistral models for text generation, agents, data processing, and more. - [Core API](https://docs.mistral.ai/studio/conversations/chat-completion) — Interact with Mistral models through a unified API for text generation, vision, and structured data extraction. - [Agent Tools](https://docs.mistral.ai/studio/agents/introduction) — Combine language models with b …
    cite: https://docs.mistral.ai/studio#studio-capabilities

[3] https://docs.mistral.ai/api/endpoint/models | section: operation-list_models_v1_models_get
    Models API > List Models
    `GET /v1/models` List all models available to the user. - Operation id: `list_models_v1_models_get` - Tag: models
    cite: https://docs.mistral.ai/api/endpoint/models#operation-list_models_v1_models_get

[4] https://docs.mistral.ai/studio | section: studio
    Studio
    [Studio](https://console.mistral.ai) is Mistral's developer platform for AI applications. Use the API to build conversational AI, autonomous agents, document intelligence, and RAG applications. Use the console to manage reusable building blocks, manage keys, test models, and monitor usage.
    cite: https://docs.mistral.ai/studio

[5] https://docs.mistral.ai/api/endpoint/models | section: operation-list_models_v1_models_get/parameters
    Models API > List Models > Parameters
    - `provider` (string or null, optional, in query) - `model` (string or null, optional, in query)
    cite: https://docs.mistral.ai/api/endpoint/models#operation-list_models_v1_models_get

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/chat-legacy/agents") to read hit 1 on its page
```

### 6. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/api/endpoint/models", "section": "operation-list_models_v1_models_get"}
```

Result:

```
page: https://docs.mistral.ai/api/endpoint/models | "Models API" | section: operation-list_models_v1_models_get

## section: operation-list_models_v1_models_get
    Models API > List Models
    cite: https://docs.mistral.ai/api/endpoint/models#operation-list_models_v1_models_get
## List Models {#operation-list_models_v1_models_get}

`GET /v1/models`

List all models available to the user.

- Operation id: `list_models_v1_models_get`
- Tag: models

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/models", section="operation-list_models_v1_models_get/parameters") for the section after it
```

### 7. mistral_docs_search

```json
{"q": "agent model parameter chat models supported", "max_hits": 5}
```

Result:

```
q: "agent model parameter chat models supported"

[1] https://docs.mistral.ai/resources/languages | section: supported-languages
    Supported languages
    Mistral's language models are trained on multilingual data and support a wide range of languages. The lists below reflect languages with **strong expected performance**. Because of how models are trained, they can also perform well in additional languages not listed here.
    cite: https://docs.mistral.ai/resources/languages

[2] https://docs.mistral.ai/studio/agents/introduction | section: which-models-are-supported
    Agents Introduction > What are AI agents? > FAQ > Which models are supported?
    Currently, only `mistral-medium-latest` and `mistral-large-latest` are supported, but we will soon enable it for more models.
    cite: https://docs.mistral.ai/studio/agents/introduction#which-models-are-supported

[3] https://docs.mistral.ai/resources/languages | section: language-models
    Supported languages > Language models
    | Region | Languages | |--------|-----------| | **European** | French, German, Spanish, Portuguese, Italian, Dutch, Polish, Czech, Danish, Finnish, Greek, Norwegian, Romanian, Swedish, Croatian, Serbian, Ukrainian, Catalan, Breton | | **Middle Eastern** | Arabic, Farsi, Hebrew, Turkish, Urdu | | **South Asian** | Hindi, Bengali, Gujarati, Kannada, Marathi, Nepali, Punjabi, Tamil, Telugu | | **Sout …
    cite: https://docs.mistral.ai/resources/languages#language-models

[4] https://docs.mistral.ai/admin/monitor-comply/zero-data-retention | section: supported-endpoints
    Zero data retention > Supported API endpoints
    ZDR applies to the following stateless API endpoints: | Endpoint | Coverage | |----------|----------| | `/v1/chat/completions` | Chat completions | | `/v1/fim/completions` | Fill-in-the-middle completions | | `/v1/embeddings` | Embeddings | | `/v1/moderations` | Text moderation | | `/v1/chat/moderations` | Chat moderation | | `/v1/classifications` | Text classification | | `/v1/chat/classification …
    cite: https://docs.mistral.ai/admin/monitor-comply/zero-data-retention#supported-endpoints

[5] https://docs.mistral.ai/studio/agents/agent-tools | section: general-usage
    Agents Tools Overview > Tools > Built-in tools > General usage
    Built-in tool support depends on the API you use. > **Warning** > > `web_search`, `web_search_premium`, and `code_interpreter` work with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. They aren't **supported** in the Chat Completions API (`/v1/chat/completions`). Built-in tools such as `image_generation` are also supported …
    cite: https://docs.mistral.ai/studio/agents/agent-tools#general-usage

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/resources/languages") to read hit 1 on its page
```

### 8. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/agents/introduction", "section": "which-models-are-supported"}
```

Result:

```
page: https://docs.mistral.ai/studio/agents/introduction | "Agents Introduction" | section: which-models-are-supported

## section: which-models-are-supported
    Agents Introduction > What are AI agents? > FAQ > Which models are supported?
    cite: https://docs.mistral.ai/studio/agents/introduction#which-models-are-supported
### Which models are supported? {#which-models-are-supported}

Currently, only `mistral-medium-latest` and `mistral-large-latest` are supported, but we will soon enable it for more models.

Results: the whole section.
```

### 9. mistral_docs_search

```json
{"q": "handoff model restrictions supported models", "max_hits": 5}
```

Result:

```
q: "handoff model restrictions supported models"

[1] https://docs.mistral.ai/resources/languages | section: supported-languages
    Supported languages
    Mistral's language models are trained on multilingual data and support a wide range of languages. The lists below reflect languages with **strong expected performance**. Because of how models are trained, they can also perform well in additional languages not listed here.
    cite: https://docs.mistral.ai/resources/languages

[2] https://docs.mistral.ai/studio/agents/introduction | section: which-models-are-supported
    Agents Introduction > What are AI agents? > FAQ > Which models are supported?
    Currently, only `mistral-medium-latest` and `mistral-large-latest` are supported, but we will soon enable it for more models.
    cite: https://docs.mistral.ai/studio/agents/introduction#which-models-are-supported

[3] https://docs.mistral.ai/resources/languages | section: language-models
    Supported languages > Language models
    | Region | Languages | |--------|-----------| | **European** | French, German, Spanish, Portuguese, Italian, Dutch, Polish, Czech, Danish, Finnish, Greek, Norwegian, Romanian, Swedish, Croatian, Serbian, Ukrainian, Catalan, Breton | | **Middle Eastern** | Arabic, Farsi, Hebrew, Turkish, Urdu | | **South Asian** | Hindi, Bengali, Gujarati, Kannada, Marathi, Nepali, Punjabi, Tamil, Telugu | | **Sout …
    cite: https://docs.mistral.ai/resources/languages#language-models

[4] https://docs.mistral.ai/admin/monitor-comply/zero-data-retention | section: supported-endpoints
    Zero data retention > Supported API endpoints
    ZDR applies to the following stateless API endpoints: | Endpoint | Coverage | |----------|----------| | `/v1/chat/completions` | Chat completions | | `/v1/fim/completions` | Fill-in-the-middle completions | | `/v1/embeddings` | Embeddings | | `/v1/moderations` | Text moderation | | `/v1/chat/moderations` | Chat moderation | | `/v1/classifications` | Text classification | | `/v1/chat/classification …
    cite: https://docs.mistral.ai/admin/monitor-comply/zero-data-retention#supported-endpoints

[5] https://docs.mistral.ai/inference/regional-inference | section: regional-inference-limitations
    Regional inference > What is supported by regional inference? > Limitations
    Regional endpoints have feature limitations. If a workload depends on an unsupported feature, the regional processing guarantees for that workload do not apply. - Not all [tool calls](https://docs.mistral.ai/studio/agents/agent-tools) are currently supported. [Function calling](https://docs.mistral.ai/studio/agents/agent-tools/function-calling) is the only supported regional tool. - Stateful featu …
    cite: https://docs.mistral.ai/inference/regional-inference#regional-inference-limitations

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/resources/languages") to read hit 1 on its page
```

## Answer

To answer your question: **there is a published list, and not every chat model is allowed for agent handoffs**.

The [Agents Introduction FAQ explicitly states](https://docs.mistral.ai/studio/agents/introduction#which-models-are-supported):
> Currently, only `mistral-medium-latest` and `mistral-large-latest` are supported, but we will soon enable it for more models.

This means that, as of now, only these two models can be used for agents and their handoffs. The handoffs documentation itself does not impose additional model restrictions, so the same list applies to chained handoffs. The examples in the handoffs guide also use these models (`mistral-large-latest` and `mistral-medium-latest`) for agent workflows.

