# mined2-066 (unanswerable, 6 connector calls)

## Question

Which models can be chained in agent handoffs — is there a published list, or is any chat model allowed?

## Thinking

The user is asking about which Mistral models can be chained in agent handoffs, and whether there's a published list or if any chat model is allowed. This is a specific question about Mistral's agent handoff functionality and model compatibility.

I need to search the Mistral documentation for information about agent handoffs and model chaining. Let me start by searching for "agent handoff" and related terms.

The search results show some information about handoffs, but I need to look more specifically at the handoffs documentation. Let me read the handoffs page to understand the constraints.

The handoffs documentation doesn't explicitly state model restrictions. Let me search more specifically for model compatibility information in agent handoffs.

Let me read the durable agents page to see if there are any model restrictions mentioned there.

The durable agents documentation also doesn't explicitly mention model restrictions for handoffs. Let me search for information about which models support the Agents API, as that might be the limiting factor.

Perfect! I found a direct answer. The search result shows that there's a FAQ section in the Agents Introduction that explicitly states which models are supported. Let me read that page to get the full context.

The user asks: "Which models can be chained in agent handoffs — is there a published list, or is any chat model allowed?"

From the documentation I found:

1. In the Agents Introduction FAQ, there's a specific section that states: "Currently, only `mistral-medium-latest` and `mistral-large-latest` are supported, but we will soon enable it for more models." This is explicitly about which models are supported for agents.

2. The handoffs documentation shows examples using `mistral-medium-latest` and `mistral-large-latest` in the code samples.

3. There's no explicit statement that "any chat model" is allowed - in fact, the FAQ explicitly restricts it to specific models.

4. The documentation doesn't provide a comprehensive list beyond these two models, but it does state that more models will be enabled in the future.

So the answer is: There IS a published list (in the FAQ), and currently only `mistral-medium-latest` and `mistral-large-latest` are supported. It's not the case that any chat model is allowed.

I should provide a clear, direct answer with the citation to the documentation.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "agent handoff chaining models list allowed"}
```

Result:

```
q: "agent handoff chaining models list allowed"

[1] https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers | section: chaining-rerankers
    Rerankers > Chaining rerankers
    Multiple rerankers can be applied in sequence for progressive refinement: ```python from mistralai.search.toolkit.retrieval.rerankers import RRFRanker, LLMReRanker query_engine = QueryEngine( retriever=[dense_retriever, hybrid_retriever], rerankers=[ RRFRanker(rrf_k=60, top_k=50), # Step 1: Fuse results → top 50 MetadataReRanker(), # Step 2: Boost verified content LLMReRanker(llm_provider=llm, top …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers#chaining-rerankers

[2] https://docs.mistral.ai/studio/agents/handoffs | section: define-handoffs-responsibilities
    Handoffs > Create an Agentic Workflow > Define Handoffs Responsabilities
    ![handoffs_graph](https://docs.mistral.ai/img/responsibilities_handoffs.png) Once all our Agents created, we update our previous defined Agents with a list of `handoffs` available. **Python** ```py # Allow the finance_agent to handoff the conversation to the ecb_interest_rate_agent or web_search_agent finance_agent = client.beta.agents.update( agent_id=finance_agent.id, handoffs=[ecb_interest_rate …
    cite: https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities

[3] https://docs.mistral.ai/api/endpoint/models | section: operation-list_models_v1_models_get
    Models API > List Models
    `GET /v1/models` List all models available to the user. - Operation id: `list_models_v1_models_get` - Tag: models
    cite: https://docs.mistral.ai/api/endpoint/models#operation-list_models_v1_models_get

[4] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: multi-agent-handoffs
    Durable agents > Multi-agent handoffs
    Agents can delegate tasks to specialized agents using handoffs. The coordinator agent's `instructions` and the specialized agents' `description` fields guide handoff decisions; the model decides when to hand off based on the user query and the available specialists' descriptions. The system automatically manages the handoff conversation. **Python** ```python import mistralai.workflows as workflows …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs

[5] https://docs.mistral.ai/api/endpoint/models | section: operation-list_models_v1_models_get/responses
    Models API > List Models > Responses
    - `200` — Successful Response (application/json, schema ModelList) - `422` — Validation Error (application/json, schema HTTPValidationError)
    cite: https://docs.mistral.ai/api/endpoint/models#operation-list_models_v1_models_get

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/search/search-toolkit/retrieval/rerankers") to read hit 1 on its page
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

### 3. mistral_docs_search

```json
{"q": "agent handoff model compatibility chat models allowed list"}
```

Result:

```
q: "agent handoff model compatibility chat models allowed list"

[1] https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | section: multi-agent-handoffs
    Durable agents > Multi-agent handoffs
    Agents can delegate tasks to specialized agents using handoffs. The coordinator agent's `instructions` and the specialized agents' `description` fields guide handoff decisions; the model decides when to hand off based on the user query and the available specialists' descriptions. The system automatically manages the handoff conversation. **Python** ```python import mistralai.workflows as workflows …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#multi-agent-handoffs

[2] https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription | section: compatibility-table
    Offline > Offline Transcription > OpenAI SDK compatibility > Compatibility table
    | Feature | OpenAI SDK compatible | | :-------------------------------------------------- | :------------------------ | | Basic transcription (`file`) | Yes | | Language specification (`language`) | Yes | | Timestamp granularities (`timestamp_granularities`) | Yes | | Streaming (`stream`) | Yes | | Diarization (`diarize`) | Yes with `extra_body` | | Context biasing (`context_bias`) | Yes with `ext …
    cite: https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription#compatibility-table
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription", section="compatibility-table") reads this section

[3] https://docs.mistral.ai/api/endpoint/models | section: operation-list_models_v1_models_get
    Models API > List Models
    `GET /v1/models` List all models available to the user. - Operation id: `list_models_v1_models_get` - Tag: models
    cite: https://docs.mistral.ai/api/endpoint/models#operation-list_models_v1_models_get

[4] https://docs.mistral.ai/studio/agents/handoffs | section: define-handoffs-responsibilities
    Handoffs > Create an Agentic Workflow > Define Handoffs Responsabilities
    ![handoffs_graph](https://docs.mistral.ai/img/responsibilities_handoffs.png) Once all our Agents created, we update our previous defined Agents with a list of `handoffs` available. **Python** ```py # Allow the finance_agent to handoff the conversation to the ecb_interest_rate_agent or web_search_agent finance_agent = client.beta.agents.update( agent_id=finance_agent.id, handoffs=[ecb_interest_rate …
    cite: https://docs.mistral.ai/studio/agents/handoffs#define-handoffs-responsibilities

[5] https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription | section: openai-sdk-compatibility
    Offline > Offline Transcription > OpenAI SDK compatibility
    The Mistral transcription endpoint follows the same request structure as the OpenAI audio transcriptions API. You can use the OpenAI SDK by pointing it at the Mistral base URL and swapping the model name. > **Warning** > > We don't recommend using the OpenAI SDK for long-term use. This compatibility layer targets quick testing and prototyping. For production usage, we recommend using the [Mistral …
    cite: https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription#openai-sdk-compatibility
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription", section="openai-sdk-compatibility") reads this section

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents") to read hit 1 on its page
```

### 4. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents"}
```

Result:

```
page: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents | "Durable agents"

## section: durable-agents
    Durable agents
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents
# Durable agents

A durable agent is an LLM agent whose loop (model calls, tool use, and handoffs) runs **inside a workflow**, so its state survives crashes and restarts. The Mistral plugin (`mistralai-workflows[mistralai]`) provides the primitives for building them: `Agent`, `Runner`, `RemoteSession`, and `LocalSession` (experimental).

What you get on top of a regular agent loop:

- **Durability**: agent state is preserved across worker crashes and restarts
- **Tool integration**: workflow activities can be passed directly as agent tools
- **Multi-agent handoffs**: agents can delegate tasks to specialized agents
- **MCP support**: connect to external tools with the Model Context Protocol (stdio or SSE)
- **Telemetry and observability**: the plugin uses [`get_mistral_client()`](https://docs.mistral.ai/studio/workflows/building-workflows/mistral_client) under the hood, so all LLM calls include telemetry and workflow tracing metadata by default

## section: installation
    Durable agents > Installation
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#installation
## Installation {#installation}

To use Durable Agents, install the Mistral plugin:

```bash
uv add 'mistralai-workflows[mistralai]'
```

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

## section: runner
    Durable agents > Core components > Runner
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#runner
### Runner {#runner}

The `Runner` executes an agent with user inputs and manages the conversation loop. It calls the model, processes tool calls, and repeats until the agent produces a final response or reaches `max_turns`. If `max_turns` is reached, the runner returns whatever outputs have been collected so far.

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai

outputs = await workflows_mistralai.Runner.run(
    agent=agent,
    inputs="What is the interest rate for 2024?",
    session=session,
    max_turns=10,  # Maximum model call iterations before stopping
)
```

The returned `outputs` is a list of output items produced by the agent during the run (text responses, tool results, handoff results).

## section: sessions
    Durable agents > Core components > Sessions
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#sessions
### Sessions {#sessions}

Sessions manage agent state and API communication. Two session types are available:

| Session         | Use case                   | Backend               |
| --------------- | -------------------------- | --------------------- |
| `RemoteSession` | Production (recommended)   | Mistral Agents SDK    |
| `LocalSession`  | Experimental / On-premises | Direct completion API |

`RemoteSession` lazily creates an agent server-side (or reuses an existing one if `agent.id` is set) and delegates completions to it. `LocalSession` runs the agent loop in your worker process using the chat completions API directly.

## section: basic-example
    Durable agents > Basic example
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#basic-example
## Basic example {#basic-example}

Here's a simple agent workflow that uses an activity as a tool:

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai
from mistralai.client.models import TextChunk


@workflows.activity()
async def get_interest_rate(year: int) -> dict:
    """Get the interest rate for a given year.

    Args:
        year: The year to get the interest rate for
    """
    # Your implementation here
    return {"interest_rate": 1.62}


@workflows.workflow.define(name="finance_agent_workflow")
class FinanceAgentWorkflow:
    @workflows.workflow.entrypoint
    async def entrypoint(self, question: str) -> dict:
        session = workflows_mistralai.RemoteSession()

        agent = workflows_mistralai.Agent(
            model="mistral-medium-latest",
            name="finance-agent",
            description="Agent for financial queries",
            instructions="Use tools to answer financial questions.",
            tools=[get_interest_rate],
        )

        outputs = await workflows_mistralai.Runner.run(
            agent=agent,
            inputs=question,
            session=session,
        )

        answer = "\n".join([
            output.text for output in outputs
            if isinstance(output, TextChunk)
        ])

        return {"answer": answer}
```

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

## section: mcp-integration
    Durable agents > MCP integration
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#mcp-integration
## MCP integration {#mcp-integration}

Connect to external tool servers using the Model Context Protocol. Two transport types are supported:

## section: stdio-mcp-server
    Durable agents > MCP integration > Stdio MCP server
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#stdio-mcp-server
### Stdio MCP server {#stdio-mcp-server}

For local command-line MCP servers:

**Python**

```python
import mistralai.workflows.plugins.mistralai as workflows_mistralai
from mistralai.workflows.plugins.mistralai import MCPStdioConfig

mcp_config = MCPStdioConfig(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-everything"],
    name="server-everything",
)

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="mcp-agent",
    description="Agent with access to MCP tools",
    mcp_clients=[mcp_config],
)
```

**Forwarding credentials to a stdio server**

Some stdio MCP servers need credentials, such as a bot token, to authenticate. Use `env_mapping` to pass them from the worker's environment into the subprocess. Each mapping entry pairs the subprocess variable name with the worker variable name:

**Python**

```python
from mistralai.workflows.plugins.mistralai import MCPStdioConfig

mcp_config = MCPStdioConfig(
    command="npx",
    args=["-y", "@notionhq/notion-mcp-server"],
    name="notion",
    env_mapping={"NOTION_TOKEN": "NOTION_TOKEN_BOT_A"},
)
```

Use a mapping instead of raw values because activity inputs are persisted to the workflow's [event history](https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events). Loading secrets from the worker's environment and passing them directly would expose them there.

With `env_mapping`, only the variable names are serialized. The activity reads the secret values from the worker's environment, and the values never leave the worker. A mapping also lets you run several instances of the same server with different credentials on one worker. If a declared worker variable is missing from the environment, the activity fails fast.

## section: sse-mcp-server
    Durable agents > MCP integration > SSE MCP server
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#sse-mcp-server
### SSE MCP server {#sse-mcp-server}

For remote MCP servers over Server-Sent Events:

**Python**

```python
from mistralai.workflows.plugins.mistralai import MCPSSEConfig

mcp_config = MCPSSEConfig(
    url="https://your-mcp-server.com/sse",
    timeout=60,
    name="remote-tools",
    headers={"Authorization": "Bearer your-token"},  # Optional
)

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="sse-mcp-agent",
    description="Agent with access to remote MCP tools",
    mcp_clients=[mcp_config],
)
```

## section: streamable-http-mcp-server
    Durable agents > MCP integration > Streamable HTTP MCP Server
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#streamable-http-mcp-server
### Streamable HTTP MCP Server {#streamable-http-mcp-server}

For remote MCP servers that speak the Streamable HTTP transport (`--transport http`), such as a self-hosted server behind an HTTP endpoint:

> **Note**
>
> Requires `mistralai>=2.8.0` (the release that ships the Streamable HTTP client). If you use `MCPStreamableHTTPConfig`, pin `mistralai>=2.8.0` in your project's dependencies.

**Python**

```python
from mistralai.workflows.plugins.mistralai import MCPStreamableHTTPConfig

mcp_config = MCPStreamableHTTPConfig(
    url="https://your-mcp-server.com/mcp",
    name="remote-tools",
)

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="streamable-http-mcp-agent",
    description="Agent with access to a Streamable HTTP MCP server",
    mcp_clients=[mcp_config],
)
```

**Forwarding credentials to a Streamable HTTP server**

A Streamable HTTP server usually needs credentials on every request: a bearer token gating the endpoint and/or a per-request integration token. Set them from the worker's environment so no secret is serialized into the workflow's [event history](https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/events).

Use `auth_token_env` for the endpoint bearer (the SDK reads the raw token from that worker variable and adds the `Bearer` scheme). Use `header_mapping` for any other per-request secret header, mapping an HTTP header name to a worker variable name:

**Python**

```python
from mistralai.workflows.plugins.mistralai import MCPStreamableHTTPConfig

mcp_config = MCPStreamableHTTPConfig(
    url="https://your-mcp-server.com/mcp",
    name="notion",
    auth_token_env="MCP_ENDPOINT_TOKEN",                    # -> Authorization: Bearer <value>
    header_mapping={"Notion-Token": "NOTION_TOKEN_BOT_A"},  # header <- whole env value
)
```

Only the variable names are serialized into activity params and event history; the secret values are read from the worker's environment inside the activity and never leave it. Put only non-secret values in the static `headers` field. If a declared worker variable is missing from the environment, the activity fails fast.

**Redirects**

By default the client does not follow HTTP redirects (`follow_redirects=False`). On a redirect, `httpx` only strips the `Authorization` header on cross-origin hops, so the per-request secret headers above (e.g. `Notion-Token`) would be resent to the redirect target. Set `follow_redirects=True` only if your MCP server relies on redirects (for example `/mcp` -> `/mcp/`) and you trust every host it can redirect to.

## section: built-in-tools
    Durable agents > Built-in tools
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#built-in-tools
## Built-in tools {#built-in-tools}

Use Mistral's built-in tools alongside activities:

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai
from mistralai.client.models import WebSearchTool

agent = workflows_mistralai.Agent(
    model="mistral-medium-latest",
    name="web-search-agent",
    description="Agent with web search capability",
    instructions="Use web search to answer user questions",
    tools=[WebSearchTool()],
)
```

Available built-in tools:

| Tool | Description |
|------|-------------|
| `WebSearchTool()` | Search the web and return results to the model |
| `CodeInterpreterTool()` | Execute Python code in a sandboxed environment |
| `ImageGenerationTool()` | Generate images from text descriptions |
| `DocumentLibraryTool()` | Analyze and extract information from uploaded documents |

These tools are executed server-side by the Mistral platform; they do not run in your worker process. Pass them in the `tools` list alongside any activity-based tools.

> **Warning**
>
> **Built-in tools require RemoteSession**: `LocalSession` silently drops built-in tools (logs a warning and proceeds without them). Use `RemoteSession` for any agent that relies on `WebSearchTool`, `CodeInterpreterTool`, `ImageGenerationTool`, or `DocumentLibraryTool`.

## section: remote-session
    Durable agents > Session types > RemoteSession (recommended)
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#remote-session
### RemoteSession (recommended) {#remote-session}

Uses the Mistral Agents SDK for production workloads:

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai

session = workflows_mistralai.RemoteSession()

outputs = await workflows_mistralai.Runner.run(
    agent=agent,
    inputs="Your question here",
    session=session,
)
```

Features:

- Full Agents SDK integration
- Automatic agent creation and updates
- Managed conversation state
- Production-ready

## section: agent-lifecycle
    Durable agents > Session types > Agent lifecycle
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#agent-lifecycle
### Agent lifecycle {#agent-lifecycle}

When a `RemoteSession` initializes a conversation, it iterates over every agent in the handoff graph and either creates or updates it via the Agents API:

- **`Agent(id=None)`**: a new remote agent is created with `beta.agents.create()`. The returned ID is stored back on the `Agent` object, so subsequent runs with the **same instance** reuse it.
- **`Agent(id="existing-id")`**: the existing remote agent is updated with `beta.agents.update()`. No new agent is created.

To reuse a pre-existing agent across workflow executions, set `agent.id` before calling `Runner.run()`:

**Python**

```python
agent = workflows_mistralai.Agent(
    id="ag_abc123",  # Reuse an existing remote agent
    model="mistral-medium-latest",
    name="finance-agent",
    instructions="Use tools to answer financial questions.",
    tools=[get_interest_rate],
)
```

> **Warning**
>
> Agents created by `RemoteSession` are **not cleaned up automatically** after a run completes. If you create agents dynamically (without setting `id`), a new remote agent will be created on every workflow execution.

## section: local-session
    Durable agents > Session types > LocalSession (experimental)
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#local-session
### LocalSession (experimental) {#local-session}

Runs agents locally using the completion endpoint:

**Python**

```python
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai

session = workflows_mistralai.LocalSession()

outputs = await workflows_mistralai.Runner.run(
    agent=agent,
    inputs="Your question here",
    session=session,
)
```

Use cases:

- On-premises or private cloud deployments where the Agents API is not available
- Development and testing
- Full context control

> **Warning**
>
> `LocalSession` is experimental and might be removed in a later version. Use `RemoteSession` for production workloads.

## section: complete-workflow-example
    Durable agents > Complete workflow example
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#complete-workflow-example
## Complete workflow example {#complete-workflow-example}

A full example combining activities, handoffs, and workflow orchestration:

**Python**

```python
import asyncio
import mistralai.workflows as workflows
import mistralai.workflows.plugins.mistralai as workflows_mistralai
from mistralai.client.models import TextChunk


@workflows.activity()
async def calculate_risk_score(deal_type: str, amount: float) -> dict:
    """Calculate financial risk score for a deal.

    Args:
        deal_type: The type of deal being analyzed
        amount: The monetary amount of the deal
    """
    risk_score = min(100.0, amount / 10000.0)
    risk_factors = []
    if amount > 100000:
        risk_factors.append("High value transaction")
    return {"risk_score": risk_score, "risk_factors": risk_factors}


@workflows.workflow.define(name="deal_analysis_workflow")
class DealAnalysisWorkflow:
    @workflows.workflow.entrypoint
    async def entrypoint(self, deal_request: str) -> dict:
        """Analyze a deal request.

        Args:
            deal_request: The deal request to analyze
        """
        session = workflows_mistralai.RemoteSession()

        # Risk assessment agent
        risk_agent = workflows_mistralai.Agent(
            model="mistral-medium-latest",
            name="risk-agent",
            description="Analyzes financial risk of deals",
            instructions="Use the risk calculation tool to assess deal risk.",
            tools=[calculate_risk_score],
        )

        # Main coordinator agent
        coordinator = workflows_mistralai.Agent(
            model="mistral-medium-latest",
            name="deal-coordinator",
            description="Coordinates deal analysis",
            instructions="Analyze the deal request and hand off to specialists.",
            handoffs=[risk_agent],
        )

        outputs = await workflows_mistralai.Runner.run(
            agent=coordinator,
            inputs=deal_request,
            session=session,
        )

        analysis = "\n".join([
            output.text for output in outputs
            if isinstance(output, TextChunk)
        ])

        return {"analysis": analysis}


if __name__ == "__main__":
    asyncio.run(workflows.run_worker([DealAnalysisWorkflow]))
```

## section: observability
    Durable agents > Observability
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#observability
## Observability {#observability}

Agent activity emits the same workflow and activity events as any other workflow. Subscribe to them live via [Streaming](https://docs.mistral.ai/studio/workflows/building-workflows/streaming) and [Consuming Streaming Events](https://docs.mistral.ai/studio/workflows/building-workflows/consuming_events), or replay the full event history after the fact.

## section: best-practices
    Durable agents > Best practices
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/durable_agents#best-practices
## Best practices {#best-practices}

1. **Use `RemoteSession` for production** so the agent runs against the Agents API rather than the raw completion endpoint.
2. **Set `agent.id`** on agents you want to reuse across runs. Otherwise, `RemoteSession` creates a new remote agent on every execution and never cleans them up.
3. **Wrap tool side-effects in activities** so they get retry isolation and appear in the execution history.

Results: 18 sections, the whole page.
```

### 5. mistral_docs_search

```json
{"q": "Agents API supported models chat models list"}
```

Result:

```
q: "Agents API supported models chat models list"

[1] https://docs.mistral.ai/studio/agents/introduction | section: which-models-are-supported
    Agents Introduction > What are AI agents? > FAQ > Which models are supported?
    Currently, only `mistral-medium-latest` and `mistral-large-latest` are supported, but we will soon enable it for more models.
    cite: https://docs.mistral.ai/studio/agents/introduction#which-models-are-supported

[2] https://docs.mistral.ai/api/endpoint/models | section: operation-list_models_v1_models_get
    Models API > List Models
    `GET /v1/models` List all models available to the user. - Operation id: `list_models_v1_models_get` - Tag: models
    cite: https://docs.mistral.ai/api/endpoint/models#operation-list_models_v1_models_get

[3] https://docs.mistral.ai/api/endpoint/models | section: operation-list_models_v1_models_get/parameters
    Models API > List Models > Parameters
    - `provider` (string or null, optional, in query) - `model` (string or null, optional, in query)
    cite: https://docs.mistral.ai/api/endpoint/models#operation-list_models_v1_models_get

[4] https://docs.mistral.ai/api/endpoint/models | section: operation-list_models_v1_models_get/responses
    Models API > List Models > Responses
    - `200` — Successful Response (application/json, schema ModelList) - `422` — Validation Error (application/json, schema HTTPValidationError)
    cite: https://docs.mistral.ai/api/endpoint/models#operation-list_models_v1_models_get

[5] https://docs.mistral.ai/resources/languages | section: supported-languages
    Supported languages
    Mistral's language models are trained on multilingual data and support a wide range of languages. The lists below reflect languages with **strong expected performance**. Because of how models are trained, they can also perform well in additional languages not listed here.
    cite: https://docs.mistral.ai/resources/languages

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/introduction") to read hit 1 on its page
```

### 6. mistral_docs_read_page

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

## Answer

Yes, there is a published list. Currently, **only `mistral-medium-latest` and `mistral-large-latest` are supported** for use with agent handoffs in the Agents API. Mistral states they will enable more models in the future.

[Which models are supported?](https://docs.mistral.ai/studio/agents/introduction#which-models-are-supported)

