# mined-024 (single_page, 2 connector calls)

## Question

Which models take `reasoning_effort`, and what does each value do?

## Thinking

The user is asking about which models support the `reasoning_effort` parameter and what each value does. This is a specific technical question about Mistral's API and model capabilities. I need to search the official documentation to find accurate information about this parameter.

I should search for:
1. Which models support `reasoning_effort`
2. The possible values for `reasoning_effort`
3. What each value does

Let me start with a search query that covers these aspects.

I got some search results. The first result mentions that `mistral-small-latest` and `mistral-medium-3-5` support `reasoning_effort`. Let me read the full page to get complete information about the parameter and its values.

Good, I have the documentation page. From the search results and the page content, I can see that:

1. **Models that support `reasoning_effort`**:
   - `mistral-small-latest`
   - `mistral-medium-3-5`

2. **Values and their effects**:
   - `reasoning_effort = "high"`: The response includes a full thinking chunk before the final answer, at the cost of increased token usage.
   - `reasoning_effort = "none"`: The model thinks minimally and the thinking chunk is omitted from the response.

The documentation also mentions that `reasoning_effort` is available on the Agents and Conversations endpoints via the API, inside the `completion_args` field.

Let me verify if there are any other models or more details by checking if there's more information on the page or related pages. The search results also mentioned deprecated native reasoning models, but those are not relevant to the current question.

The information seems complete. I should structure the answer clearly:
- List the models
- Explain each value
- Include the citations from the documentation

The user wants a clear, concise answer with the specific information.

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

(V1 identical)

(samples in TypeScript and cURL omitted: pass lang="typescript" or lang="curl")


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
```
(output cut after 1,500 characters; 7 more lines)

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

(sample in TypeScript omitted: pass lang="typescript")

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

(sample in TypeScript omitted: pass lang="typescript")



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

The following models accept the `reasoning_effort` parameter:

- **`mistral-small-latest`**
- **`mistral-medium-3-5`**

[Model support](https://docs.mistral.ai/studio/conversations/reasoning#before-you-start)

---

### Values for `reasoning_effort`

| Value | Behavior |
|-------|----------|
| **`"high"`** | The response includes a full **thinking chunk** (reasoning trace) before the final answer, which increases token usage. The `message.content` is a list of chunks: `ThinkChunk` (type: `"thinking"`) and `TextChunk` (type: `"text"`). |
| **`"none"`** | The model performs minimal internal reasoning, and the response is a plain string with no thinking trace. |

[Reasoning effort values](https://docs.mistral.ai/studio/conversations/reasoning#before-you-start)
[Handling thinking chunks](https://docs.mistral.ai/studio/conversations/reasoning#handling-thinking-chunks)

