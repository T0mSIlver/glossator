---
url: https://docs.mistral.ai/studio-api/agents/agent-tools/function-calling
title: Function Calling
breadcrumbs: [Studio, Agents, Agents Tools Overview]
kind: doc
locale: en
source_path: src/content/en/docs/studio-api/agents/agent-tools/function-calling/page.mdx
source_commit: 6e06c6cfc14e66e45ddf1f06445146314cff5393
---

# Function Calling

The core of an agent relies on its tool usage capabilities, enabling it to use and call tools and workflows depending on the task it must accomplish.

Built into our API, we provide [built-in tools](https://docs.mistral.ai/studio-api/agents/agent-tools#built-in-tools) such as `websearch`, `code_interpreter`, `image_generation` and `document_library`. However, you can also use standard function tool calling by defining a JSON schema for your function.

You can also register MCP servers as [Connectors](https://docs.mistral.ai/studio-api/connectors) to use external tools in conversations and Agents.

For more information regarding function calling, we recommend to visit our [function calling docs](https://docs.mistral.ai/studio-api/conversations/function-calling).

## Creating an Agent {#creating-an-agent-with-function-calling}

To use function calling, we can either create an Agent or use the Conversations API directly without.
Below we will show you how to create an Agent with function calling and use it.

### Define the Function {#define-the-function}

We need to define our function that we want our model to call when needed, in this case, the function is a dummy for demonstration purposes.

**Python**

```py
from typing import Dict

def get_european_central_bank_interest_rate(date: str) -> Dict[str, str]:
    """
    Retrieve the real interest rate of the European Central Bank for a given date.

    Parameters:
    - date (str): The date for which to retrieve the interest rate in the format YYYY-MM-DD.

    Returns:
    - dict: A dictionary containing the date and the corresponding interest rate.
    """
    # This is a mock implementation. In a real scenario, you would fetch this data from an API or database.
    # For demonstration, let's assume the interest rate is fixed at 2.5% for any date.
    interest_rate = "2.5%"

    return {
        "date": date,
        "interest_rate": interest_rate
    }
```

**TypeScript**

```typescript
async function getEuropeanentralBankInterestRate(date: str){
    /*
    Retrieve the real interest rate of the European Central Bank for a given date.

    Parameters:
    - date (str): The date for which to retrieve the interest rate in the format YYYY-MM-DD.

    Returns:
    - dict: A dictionary containing the date and the corresponding interest rate.
    */
    // This is a mock implementation. In a real scenario, you would fetch this data from an API or database.
    // For demonstration, let's assume the interest rate is fixed at 2.5% for any date.
    let interestRate = "2.5%";

    return {
        date: date,
        interestRate: interestRate
    }
}
```

Once defined, we provide a Shema corresponding to the same function.

**Python**

```py
ecb_interest_rate_agent = client.beta.agents.create(
    model="mistral-medium-latest",
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
```

**TypeScript**

```typescript
let ecbInterestRateAgent = await client.beta.agents.create({
    model:"mistral-medium-latest",
    description:"Can find the current interest rate of the European central bank",
    name:"ecb-interest-rate-agent",
    tools:[
        {
            type: "function",
            function: {
                name: "getEuropeanCentralBankInterestRate",
                description: "Retrieve the real interest rate of European central bank.",
                parameters: {
                    type: "object",
                    properties: {
                        date: {
                            type: "string",
                        },
                    },
                    required: [
                        "date",
                    ]
                },
            },
        },
    ],
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
     "name": "ecb-interest-rate-agent",
     "description": "Can find the current interest rate of the European central bank",
     "instructions": "You can provide interest rate and information regarding the European central bank.",
     "tools": [
         {
             "function": {
                 "name": "get_european_central_bank_interest_rate",
                 "parameters": {
                     "type": "object",
                     "properties": {
                         "date": {
                             "type": "string"
                         }
                     },
                     "required": ["date"]
                 },
                 "description": "Retrieve the real interest rate of European central bank."
             },
             "type": "function"
         }
     ]
 }'

```

**Output**

```json
{
  "model": "mistral-medium-latest",
  "name": "ecb-interest-rate-agent",
  "description": "Can find the current interest rate of the European central bank",
  "id": "ag_06835a34f2c476518000c372a505c2c4",
  "version": 0,
  "created_at": "2025-05-27T11:34:39.175924Z",
  "updated_at": "2025-05-27T11:34:39.175926Z",
  "instructions": "You can provide interest rate and information regarding the European central bank.",
  "tools": [
    {
      "function": {
        "name": "get_european_central_bank_interest_rate",
        "parameters": {
          "type": "object",
          "properties": {
            "date": {
              "type": "string"
            }
          },
          "required": [
            "date"
          ]
        },
        "description": "Retrieve the real interest rate of European central bank.",
        "strict": false
      },
      "type": "function"
    }
  ],
  "completion_args": {
    "stop": null,
    "presence_penalty": null,
    "frequency_penalty": null,
    "temperature": 0.3,
    "top_p": null,
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

The output of the agent creation is the agent object, which contains the agent ID, which we will use to start a conversation.

## Using an Agent {#using-an-agent-with-function-calling}

Then, to use it, we start a conversation or continue a previously existing one.

**Python**

```py
response = client.beta.conversations.start(
    agent_id=ecb_interest_rate_agent.id,
    inputs=[{"role": "user", "content": "Whats the current 2025 real interest rate?"}]
)
```

**TypeScript**

```typescript
let response = await client.beta.conversations.start({
    agentId: (await ecbInterestRateAgent).id,
    inputs:[{role: "user", content: "Whats the current 2025 real interest rate?"}]
});
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/conversations" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "inputs": [
         {
             "role": "user",
             "content": "Whats the current 2025 real interest rate?",
             "object": "entry",
             "type": "message.input"
         }
     ],
     "stream": false,
     "agent_id": "<agent_id>"
 }'
```

**Output**

```json
{
  "conversation_id": "conv_06835a34f58773bd8000f46c0d11e42c",
  "outputs": [
    {
      "tool_call_id": "6TI17yZkV",
      "name": "get_european_central_bank_interest_rate",
      "arguments": "{\"date\": \"2024-06-06\"}",
      "object": "entry",
      "type": "function.call",
      "created_at": "2025-05-27T11:34:39.610632Z",
      "completed_at": null,
      "id": "fc_06835a34f9c47fc88000e0370a295774"
    }
  ],
  "usage": {
    "prompt_tokens": 91,
    "completion_tokens": 29,
    "total_tokens": 120,
    "connector_tokens": null,
    "connectors": null
  },
  "object": "conversation.response"
}

```

### Return the Function Result {#return-result}

The model will output either an answer, or a function call, we need to detect and return the result of the expected function.

**Python**

**V1**

```py
from mistralai import FunctionResultEntry
import json

if response.outputs[-1].type == "function.call" and response.outputs[-1].name == "get_european_central_bank_interest_rate":

    # Running our function
    function_result = json.dumps(get_european_central_bank_interest_rate(**json.loads(response.outputs[-1].arguments)))

    # Providing the result to our Agent
    user_function_calling_entry = FunctionResultEntry(
        tool_call_id=response.outputs[-1].tool_call_id,
        result=function_result,
    )

    # Retrieving the final response
    response = client.beta.conversations.append(
        conversation_id=response.conversation_id,
        inputs=[user_function_calling_entry]
    )
    print(response.outputs[-1])
else:

    # In case the model did not call our function
    print(response.outputs[-1])
```

**V2**

```py
from mistralai.client import FunctionResultEntry
import json

if response.outputs[-1].type == "function.call" and response.outputs[-1].name == "get_european_central_bank_interest_rate":

    # Running our function
    function_result = json.dumps(get_european_central_bank_interest_rate(**json.loads(response.outputs[-1].arguments)))

    # Providing the result to our Agent
    user_function_calling_entry = FunctionResultEntry(
        tool_call_id=response.outputs[-1].tool_call_id,
        result=function_result,
    )

    # Retrieving the final response
    response = client.beta.conversations.append(
        conversation_id=response.conversation_id,
        inputs=[user_function_calling_entry]
    )
    print(response.outputs[-1])
else:

    # In case the model did not call our function
    print(response.outputs[-1])
```

**TypeScript**

```typescript
import type { FunctionResultEntry, MessageOutputEntry } from "@mistralai/mistralai/models/components/index.js";

let output = response.outputs[response.outputs.length - 1];

if (output.type === "function.call" && output.name === "getEuropeanCentralBankInterestRate") {
    const args = output.arguments as unknown as string;
    const parsedArgs = JSON.parse(args);
    const date = parsedArgs.date;

    const functionResult = JSON.stringify(await getEuropeanCentralBankInterestRate(date));

    const toolCallId = output.toolCallId;

    const userFunctionCallingEntry: FunctionResultEntry = {
        toolCallId: toolCallId,
        result: functionResult,
    };

    response = await client.beta.conversations.append({
        conversationId: response.conversationId,
        conversationAppendRequest:{
            inputs: [userFunctionCallingEntry]
        }
    });

    const finalEntry = response.outputs[response.outputs.length - 1];
    const finalMessageOutputEntry = finalEntry as MessageOutputEntry;
    console.log(finalMessageOutputEntry);
} else {
    console.log(output);
}
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/conversations/<conv_id>" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
     "inputs": [
         {
             "tool_call_id": "6TI17yZkV",
             "result": "{\"date\": \"2024-06-06\", \"interest_rate\": \"2.5%\"}",
             "object": "entry",
             "type": "function.result"
         }
     ],
     "stream": false,
     "store": true,
     "handoff_execution": "server"
 }'
```

**Output**

```json
{
  "content": "The current interest rate as of June 6, 2024, is 2.5%. This information is relevant for understanding the economic conditions in 2025.",
  "object": "entry",
  "type": "message.output",
  "created_at": "2025-05-27T11:34:40.142767Z",
  "completed_at": "2025-05-27T11:34:40.801117Z",
  "id": "msg_06835a35024879bc80005b1bf9ab0f12",
  "agent_id": "ag_06835a34f2c476518000c372a505c2c4",
  "model": "mistral-medium-latest",
  "role": "assistant"
}
```
