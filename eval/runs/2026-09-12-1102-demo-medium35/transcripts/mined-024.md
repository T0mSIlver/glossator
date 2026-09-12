# mined-024 (single_page, 2 connector calls)

## Question

Which models take `reasoning_effort`, and what does each value do?

## Thinking

The user is asking about which Mistral models support the `reasoning_effort` parameter and what each value does. This is a specific technical question about model parameters. I need to search the Mistral documentation to find accurate information about this parameter and its supported values across different models. I'll use the mistral_docs_search tool to look for documentation about reasoning_effort.

The search returned a result pointing to the Reasoning documentation page. I need to read the full page to get comprehensive information about which models support `reasoning_effort` and what each value does. The hit mentions it's in the "before-you-start/model" section, so I should read that page to extract the details.

Now I have the documentation content. Let me extract the key information:
- Models: The documentation states that `mistral-small-latest` and `mistral-medium-3-5` support the `reasoning_effort` parameter
- Values: The parameter has two values - "high" and "none"
- Behavior:
  - "high": includes full thinking chunk (reasoning trace) before the final answer, but uses more tokens
  - "none": minimal thinking, no thinking chunk in response

I should also note that the documentation mentions this parameter is available on Agents and Conversations endpoints via the API in the `completion_args` field.

I need to structure this answer clearly, with proper citations to the documentation. The user wants to know which models take it and what each value does, so I'll organize it into two sections: Models and Values. I should also mention the deprecated native reasoning models as context, but focus on the current supported models.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "models that take reasoning_effort parameter and its values"}
```

Result:

```
q: "models that take reasoning_effort parameter and its values"

[1] https://docs.mistral.ai/studio/conversations/reasoning | section: before-you-start/model
    Reasoning > Before you start > Model
    - `mistral-small-latest`: Supports adjustable reasoning via the `reasoning_effort` parameter. No extra configuration required — just add the parameter to any chat completion request. - `mistral-medium-3-5`: Supports adjustable reasoning via the `reasoning_effort` parameter. For agentic and code use cases, `reasoning_effort="high"` is recommended. The `reasoning_effort` parameter controls how reaso …
    cite: https://docs.mistral.ai/studio/conversations/reasoning#before-you-start

[2] https://docs.mistral.ai/resources/deprecated/native-reasoning | section: native-reasoning-deprecated
    Native reasoning (deprecated)
    > **Deprecated** > > Native reasoning models (`magistral-small-latest`, `magistral-medium-latest`) are deprecated. We recommend using [Reasoning](https://docs.mistral.ai/studio/conversations/reasoning) with `mistral-small-latest` or `mistral-medium-3-5` instead, which provides the same capabilities with greater flexibility via the `reasoning_effort` parameter. > **Tip** > > Before continuing, we r …
    cite: https://docs.mistral.ai/resources/deprecated/native-reasoning
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/resources/deprecated/native-reasoning", section="native-reasoning-deprecated") reads this section

[3] https://docs.mistral.ai/studio/conversations/reasoning | section: handling-thinking-chunks
    Reasoning > Handling thinking chunks
    When `reasoning_effort` is set to `"high"`, the response `message.content` is a **list of chunks** instead of a plain string. Two chunk types appear: - **`ThinkChunk`** (`type: "thinking"`): contains the model's reasoning trace. The `thinking` field is itself a list of `TextChunk` objects. - **`TextChunk`** (`type: "text"`): contains the final answer. When `reasoning_effort` is `"none"`, `message. …
    cite: https://docs.mistral.ai/studio/conversations/reasoning#handling-thinking-chunks

[4] https://docs.mistral.ai/studio/conversations/reasoning | section: multi-turn
    Reasoning > Handling thinking chunks > Multi-turn conversations
    When building multi-turn conversations with reasoning, **always replay the full assistant message (including `ThinkChunk`) back into the message history**. Dropping the reasoning trace across turns degrades model performance. **Python** ```python from mistralai.client import Mistral from mistralai.client.models import TextChunk, ThinkChunk, UserMessage client = Mistral(api_key="your-api-key", time …
    cite: https://docs.mistral.ai/studio/conversations/reasoning#multi-turn

[5] https://docs.mistral.ai/studio/conversations/reasoning | section: reasoning-with-chat-completions
    Reasoning > Usage > Reasoning with chat completions
    **TypeScript** ```typescript import { Mistral } from '@mistralai/mistralai'; import * as dotenv from 'dotenv'; dotenv.config(); const apiKey = process.env.MISTRAL_API_KEY; const client = new Mistral({ apiKey: apiKey }); async function main() { const chatResponse = await client.chat.complete({ model: 'mistral-small-latest', messages: [ { role: 'user', content: 'John is one of 4 children. The first …
    cite: https://docs.mistral.ai/studio/conversations/reasoning#reasoning-with-chat-completions

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/conversations/reasoning") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/conversations/reasoning"}
```

Result:

```
page: https://docs.mistral.ai/studio/conversations/reasoning | "Reasoning"

## section: reasoning
    Reasoning
    cite: https://docs.mistral.ai/studio/conversations/reasoning
# Reasoning

**Reasoning** is the next step of CoT (Chain of Thought), naturally used to describe the **logical steps generated by the model** before reaching a conclusion. Reasoning strengthens this characteristic by going through **training steps that encourage the model to generate chains of thought freely before producing the final answer**. This allows models to **explore the problem more profoundly and ultimately reach a better solution** to the best of their ability by using extra compute time to generate more tokens and improve the answer—also described as **Test Time Computation**.

![Reasoning LLM AI](https://docs.mistral.ai/img/_reasoning_graph.png)

They excel at complex use cases like math and coding tasks, but can be used in a wide range of scenarios to solve diverse problems. The output of reasoning models includes a reasoning chunk with the model's thinking traces, followed by the final answer.

> **Note**
>
> Looking for native reasoning models (`magistral-small-latest`, `magistral-medium-latest`)? These have been deprecated. See [Native reasoning (deprecated)](https://docs.mistral.ai/resources/deprecated/native-reasoning).

> **Tip**
>
> Before continuing, we recommend reading the [Chat Completions](https://docs.mistral.ai/studio/conversations/chat-completion) documentation to learn more about the chat completions API and how to use it before proceeding.

## section: before-you-start/model
    Reasoning > Before you start > Model
    cite: https://docs.mistral.ai/studio/conversations/reasoning#before-you-start
### Model

- `mistral-small-latest`: Supports adjustable reasoning via the `reasoning_effort` parameter. No extra configuration required — just add the parameter to any chat completion request.
- `mistral-medium-3-5`: Supports adjustable reasoning via the `reasoning_effort` parameter. For agentic and code use cases, `reasoning_effort="high"` is recommended.

The `reasoning_effort` parameter controls how reasoning is surfaced in the output:

- `reasoning_effort = "high"`: The response includes a full thinking chunk before the final answer, at the cost of increased token usage.
- `reasoning_effort = "none"`: The model thinks minimally and the thinking chunk is omitted from the response.

> **Note**
>
> `reasoning_effort` is also available on the [Agents](https://docs.mistral.ai/api/endpoint/beta/agents) and [Conversations](https://docs.mistral.ai/api/endpoint/beta/conversations) endpoints via the API, inside the `completion_args` field.

## section: reasoning-with-chat-completions
    Reasoning > Usage > Reasoning with chat completions
    cite: https://docs.mistral.ai/studio/conversations/reasoning#reasoning-with-chat-completions
### Reasoning with chat completions {#reasoning-with-chat-completions}

Here is an example via our [chat completions](https://docs.mistral.ai/api/#tag/chat) endpoint:

**Python**

**V1**

```python
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-small-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model = model,
    messages = [
        {
            "role": "user",
            "content": "John is one of 4 children. The first sister is 4 years old. Next year, the second sister will be twice as old as the first sister. The third sister is two years older than the second sister. The third sister is half the age of her older brother. How old is John?",
        },
    ],
    reasoning_effort="high"
)
```

**V2**

```python
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-small-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model = model,
    messages = [
        {
            "role": "user",
            "content": "John is one of 4 children. The first sister is 4 years old. Next year, the second sister will be twice as old as the first sister. The third sister is two years older than the second sister. The third sister is half the age of her older brother. How old is John?",
        },
    ],
    reasoning_effort="high"
)
```

**TypeScript**

**TypeScript**

```typescript
import { Mistral } from '@mistralai/mistralai';
import * as dotenv from 'dotenv';

dotenv.config();

const apiKey = process.env.MISTRAL_API_KEY;

const client = new Mistral({ apiKey: apiKey });

async function main() {
  const chatResponse = await client.chat.complete({
    model: 'mistral-small-latest',
    messages: [
      {
        role: 'user',
        content:
          'John is one of 4 children. The first sister is 4 years old. Next year, the second sister will be twice as old as the first sister. The third sister is two years older than the second sister. The third sister is half the age of her older brother. How old is John?',
      },
    ],
    reasoning_effort: "high"
  });
}

main();
```

**cURL**

```bash
curl --location "https://api.mistral.ai/v1/chat/completions" \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $MISTRAL_API_KEY" \
     --data '{
    "model": "mistral-small-latest",
    "messages": [
     {
        "role": "user",
        "content": "John is one of 4 children. The first sister is 4 years old. Next year, the second sister will be twice as old as the first sister. The third sister is two years older than the second sister. The third sister is half the age of her older brother. How old is John?"
      }
    ],
    "reasoning_effort": "high"
  }'
```

**Output**

```json
{
  "id":"0d93cd053f4c4b3ca627ccd07cf2f18c",
  "created":1773842038,
  "model":"mistral-small-latest",
  "usage":
    {
      "prompt_tokens":77,
      "total_tokens":1191,
      "completion_tokens":1114,
      "prompt_tokens_details":
        {
          "cached_tokens":0
          }
    },
  "object":"chat.completion",
  "choices":
    [
      {
        "index":0,
        "finish_reason":"stop",
        "message":
          {
            "role":"assistant",
            "tool_calls":null,
            "content":
            [
              {"type":"thinking",
              "thinking":
                [
                  {
                    "type":"text",
                    "text":"Okay, let's try to figure out John's age. So, John is one of 4 children. There are three sisters and one brother (John). Wait, the problem says \"the first sister,\" \"the second sister,\" \"the third sister,\" so that means there are three sisters and John is the brother. So total four children: three sisters and John.\n\nFirst, the first sister is 4 years old. Let's note that down. Let's call the sisters S1, S2, S3, and John is J.\n\nGiven:\n- S1 = 4 years old (current age)\n- Next year, the second sister (S2) will be twice as old as the first sister (S1). Wait, \"next year\" meaning one year from now. So next year, S1 will be 5, and S2 will be twice that, so 10? Wait, but let's check.\n\nWait, the problem says: \"Next year, the second sister will be twice as old as the first sister.\" So next year, S2's age = 2 * S1's age next year.\n\nS1 is currently 4, so next year S1 will be 5. Therefore, next year S2 will be 2*5=10. Therefore, S2's current age is 10 - 1 = 9 years old.\n\nWait, let's confirm that. If S2 is currently X years old, then next year S2 will be X+1. At that time, S1 will be 4+1=5. So X+1 = 2*5 => X+1=10 => X=9. So S2 is currently 9.\n\nNext, \"The third sister is two years older than the second sister.\" So S3 = S2 + 2. Since S2 is 9, S3 is 11.\n\nThen, \"The third sister is half the age of her older brother.\" The older brother is John, since John is a brother (assuming he's older than the sisters; but wait, could John be younger? Wait, the problem says \"her older brother,\" so the brother is older than the third sister. So John is older than S3.\n\nSo S3 = (1/2) * J => J = 2 * S3.\n\nSince S3 is 11, then J = 22.\n\nWait, let's check all steps again.\n\nCurrent ages:\n\nS1 = 4\n\nNext year, S1 will be 5. At that time, S2 will be twice S1's age next year, so 10. Therefore, S2's current age is 10 - 1 = 9.\n\nS3 = S2 + 2 = 9 + 2 = 11.\n\nS3 is half the age of her older brother (John), so John's age is 2 * 11 = 22.\n\nSo John is 22 years old.\n\nWait, but let's make sure there's no mistake here. Let's verify each statement with these ages.\n\nFirst sister is 4: correct.\n\nNext year, first sister will be 5. Second sister next year will be 9 + 1 = 10, which is twice 5: correct.\n\nThird sister is two years older than second sister: 9 + 2 = 11, correct.\n\nThird sister (11) is half the age of her older brother: so brother is 22, which is older than 11: correct.\n\nSo all conditions are satisfied. Therefore, John is 22."}]},{"type":"text","text":"Let's denote the ages of the sisters as follows:\n- \\( S_1 \\): age of the first sister\n- \\( S_2 \\): age of the second sister\n- \\( S_3 \\): age of the third sister\n- \\( J \\): age of John\n\nFrom the problem statement, we have the following information:\n1. The first sister is currently 4 years old: \\( S_1 = 4 \\).\n2. Next year, the second sister will be twice as old as the first sister: \\( S_2 + 1 = 2 \\times (S_1 + 1) \\).\n3. The third sister is two years older than the second sister: \\( S_3 = S_2 + 2 \\).\n4. The third sister is half the age of her older brother: \\( S_3 = \\frac{1}{2}J \\).\n\nFirst, we calculate the age of the second sister:\n\\[ S_2 + 1 = 2 \\times (4 + 1) \\]\n\\[ S_2 + 1 = 2 \\times 5 \\]\n\\[ S_2 + 1 = 10 \\]\n\\[ S_2 = 9 \\]\n\nNext, we calculate the age of the third sister:\n\\[ S_3 = S_2 + 2 \\]\n\\[ S_3 = 9 + 2 \\]\n\\[ S_3 = 11 \\]\n\nFinally, we calculate John's age:\n\\[ S_3 = \\frac{1}{2}J \\]\n\\[ 11 = \\frac{1}{2}J \\]\n\\[ J = 22 \\]\n\nTherefore, John is \\(\\boxed{22}\\) years old."
                    }
                  ]
            }
        }
    ]
}
```

## section: handling-thinking-chunks
    Reasoning > Handling thinking chunks
    cite: https://docs.mistral.ai/studio/conversations/reasoning#handling-thinking-chunks
## Handling thinking chunks {#handling-thinking-chunks}

When `reasoning_effort` is set to `"high"`, the response `message.content` is a **list of chunks** instead of a plain string. Two chunk types appear:

- **`ThinkChunk`** (`type: "thinking"`): contains the model's reasoning trace. The `thinking` field is itself a list of `TextChunk` objects.
- **`TextChunk`** (`type: "text"`): contains the final answer.

When `reasoning_effort` is `"none"`, `message.content` is a plain `str` with no thinking trace.

## section: parsing-response
    Reasoning > Handling thinking chunks > Parsing the response
    cite: https://docs.mistral.ai/studio/conversations/reasoning#parsing-response
### Parsing the response {#parsing-response}

**Python**

```python
from mistralai.client.models import TextChunk, ThinkChunk

# Assuming chat_response from the example above
content = chat_response.choices[0].message.content

# reasoning_effort="none" returns a plain string
if isinstance(content, str):
    print(content)
else:
    for chunk in content:
        if isinstance(chunk, ThinkChunk):
            print("--- thinking ---")
            for inner in chunk.thinking:
                if isinstance(inner, TextChunk):
                    print(inner.text)
            print("--- /thinking ---")
        elif isinstance(chunk, TextChunk):
            print(chunk.text)
```

**TypeScript**

```typescript
// Assuming chatResponse from the example above
const content = chatResponse.choices[0].message.content;

if (typeof content === 'string') {
  console.log(content);
} else {
  for (const chunk of content) {
    if (chunk.type === 'thinking') {
      console.log('--- thinking ---');
      for (const inner of chunk.thinking) {
        if (inner.type === 'text') {
          console.log(inner.text);
        }
      }
      console.log('--- /thinking ---');
    } else if (chunk.type === 'text') {
      console.log(chunk.text);
    }
  }
}
```

## section: streaming
    Reasoning > Handling thinking chunks > Streaming
    cite: https://docs.mistral.ai/studio/conversations/reasoning#streaming
### Streaming {#streaming}

When streaming, `delta.content` changes shape during the response:

1. **Thinking phase**: `delta.content` is a list containing a `ThinkChunk`
2. **Transition**: a single list containing both a closing `ThinkChunk` and the first `TextChunk`
3. **Answer phase**: `delta.content` is a plain string

**Python**

```python
import os
from mistralai.client import Mistral
from mistralai.client.models import TextChunk, ThinkChunk

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

in_thinking = False

for event in client.chat.stream(
    model="mistral-medium-3-5",
    messages=[{"role": "user", "content": "What is 17 * 23?"}],
    reasoning_effort="high",
):
    delta = event.data.choices[0].delta.content
    if not delta:
        continue

    # After thinking ends, delta is a plain string
    if isinstance(delta, str):
        if in_thinking:
            print("\n--- /thinking ---")
            in_thinking = False
        print(delta, end="", flush=True)
        continue

    # During thinking, delta is a list of chunks
    for chunk in delta:
        if isinstance(chunk, ThinkChunk):
            if not in_thinking:
                print("--- thinking ---")
                in_thinking = True
            for inner in chunk.thinking:
                if isinstance(inner, TextChunk):
                    print(inner.text, end="", flush=True)
        elif isinstance(chunk, TextChunk):
            if in_thinking:
                print("\n--- /thinking ---")
                in_thinking = False
            print(chunk.text, end="", flush=True)
```

**TypeScript**

**TypeScript**

```typescript
import { Mistral } from '@mistralai/mistralai';

const client = new Mistral({ apiKey: process.env.MISTRAL_API_KEY });

let inThinking = false;

const stream = client.chat.stream({
  model: 'mistral-medium-3-5',
  messages: [{ role: 'user', content: 'What is 17 * 23?' }],
  reasoningEffort: 'high',
});

for await (const event of stream) {
  const delta = event.data.choices[0].delta.content;
  if (!delta) continue;

  if (typeof delta === 'string') {
    if (inThinking) {
      process.stdout.write('\n--- /thinking ---\n');
      inThinking = false;
    }
    process.stdout.write(delta);
    continue;
  }

  for (const chunk of delta) {
    if (chunk.type === 'thinking') {
      if (!inThinking) {
        process.stdout.write('--- thinking ---\n');
        inThinking = true;
      }
      for (const inner of chunk.thinking) {
        if (inner.type === 'text') {
          process.stdout.write(inner.text);
        }
      }
    } else if (chunk.type === 'text') {
      if (inThinking) {
        process.stdout.write('\n--- /thinking ---\n');
        inThinking = false;
      }
      process.stdout.write(chunk.text);
    }
  }
}
```

## section: multi-turn
    Reasoning > Handling thinking chunks > Multi-turn conversations
    cite: https://docs.mistral.ai/studio/conversations/reasoning#multi-turn
### Multi-turn conversations {#multi-turn}

When building multi-turn conversations with reasoning, **always replay the full assistant message (including `ThinkChunk`) back into the message history**. Dropping the reasoning trace across turns degrades model performance.

**Python**

```python
from mistralai.client import Mistral
from mistralai.client.models import TextChunk, ThinkChunk, UserMessage

client = Mistral(api_key="your-api-key", timeout_ms=300_000)

messages = []

for user_text in ["What is 17 * 23?", "Now multiply that by 3."]:
    messages.append(UserMessage(content=user_text))

    response = client.chat.complete(
        model="mistral-medium-3-5",
        messages=messages,
        reasoning_effort="high",
    )

    assistant_message = response.choices[0].message

    # Print only the final answer (for display purposes)
    content = assistant_message.content
    if isinstance(content, str):
        print(content)
    else:
        answer = "".join(
            c.text for c in (content or []) if isinstance(c, TextChunk)
        )
        print(answer)

    # IMPORTANT: append the full assistant message to history.
    # This preserves ThinkChunk so the model can see its own
    # reasoning trace in subsequent turns.
    # Do NOT rebuild the message with only the answer text.
    messages.append(assistant_message)
```

**Output**

**Output**

```
--- Turn 1: "What is 17 * 23?" ---
Usage: prompt=25, completion=187

ThinkChunk:
  Let me think about this multiplication problem. I know that
  17 times 20 is 340, and 17 times 3 is 51. So, if I add those
  together, 340 + 51 = 391. So, 17 * 23 should be 391.

TextChunk:
  17 * 23 = 391.

--- Turn 2: "Now multiply that by 3." ---
Usage: prompt=221, completion=143

ThinkChunk:
  The user wants me to multiply the previous result, which was
  391, by 3.
  391 * 3:
  - 300 * 3 = 900
  - 90 * 3 = 270
  - 1 * 3 = 3
  900 + 270 + 3 = 1173

TextChunk:
  391 * 3 = 1173.
```

Notice how the prompt token count grows between turns:
- **Turn 1**: `prompt=25` — just the user message
- **Turn 2**: `prompt=221` — the original user message (25) + the full assistant reply from turn 1 including its ThinkChunk (187) + the new user message (9) = 221

The 187 completion tokens from turn 1 are replayed as prompt tokens in turn 2 because we appended the full `assistant_message` (ThinkChunk + TextChunk) to the history. This is what allows the model to correctly reference "the previous result" without ambiguity.

> **Warning**
>
> Do not strip `ThinkChunk` from assistant messages before replaying them. The model relies on the reasoning trace to maintain coherence across turns. Stripping them increases token efficiency but significantly degrades output quality.

Results: 7 sections, the whole page.
```

## Answer

Here are the models and the behavior of each `reasoning_effort` value, as documented:

### Models supporting `reasoning_effort`
- **`mistral-small-latest`**
- **`mistral-medium-3-5`**

Both models allow you to control reasoning via the `reasoning_effort` parameter in any chat completion request.
[Reasoning > Before you start > Model](https://docs.mistral.ai/studio/conversations/reasoning#before-you-start)

---

### Values for `reasoning_effort`
- **`"high"`**: The response includes a **full thinking chunk** (reasoning trace) before the final answer, at the cost of **increased token usage**.
  - `message.content` is a **list of chunks**: `ThinkChunk` (reasoning trace) + `TextChunk` (final answer).
  [Reasoning > Before you start > Model](https://docs.mistral.ai/studio/conversations/reasoning#before-you-start)
  [Handling thinking chunks](https://docs.mistral.ai/studio/conversations/reasoning#handling-thinking-chunks)

- **`"none"`**: The model **thinks minimally**, and the thinking chunk is **omitted** from the response.
  - `message.content` is a **plain string** (no reasoning trace).
  [Handling thinking chunks](https://docs.mistral.ai/studio/conversations/reasoning#handling-thinking-chunks)

---
> **Note**: For agentic and code use cases, `reasoning_effort="high"` is recommended for `mistral-medium-3-5`.
> [Reasoning > Before you start > Model](https://docs.mistral.ai/studio/conversations/reasoning#before-you-start)

