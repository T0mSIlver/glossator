---
url: https://docs.mistral.ai/capabilities/function-calling
title: Function calling
breadcrumbs:
  - Capabilities
  - Function calling
kind: doc
locale: en
source_path: src/content/en/docs/capabilities/function-calling/page.mdx
source_commit: 2e094f7
---

# Function calling

Function calling lets a model ask your application to run code on its behalf. You
describe the functions you are willing to run; the model decides when to call one,
with which arguments; your application runs it and returns the result; the model
uses that result to write its answer.

Nothing is executed by Mistral. A tool call is a structured request, and running
it is entirely under your control, which is what makes the feature safe to expose
to untrusted end users as long as the functions themselves are safe to call.

## When to use it {#when-to-use-it}

Reach for function calling when the answer depends on data or an action the model
cannot have: the current state of a database, a price, a booking, a calculation
that must be exact. Do not use it to enforce output structure -- structured
outputs cover that case with less machinery and no round trip.

A rough rule: if the model would have to guess, and a system you own knows the
answer, that is a function.

## Defining tools {#defining-tools}

A tool is a JSON Schema description of one function: its name, what it does, and
the arguments it takes. The description is prompt text, not documentation; the
model reads it to decide whether the function applies, so it should say when to
call the function, not only what the function does.

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_payment_status",
            "description": "Look up the status of a payment by transaction id. "
                           "Use when the user asks whether a payment went through.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction id, e.g. T1001",
                    }
                },
                "required": ["transaction_id"],
            },
        },
    }
]
```

Keep the schema tight. Every optional parameter is a decision the model has to
make correctly, and an enum with four values is answered right far more often than
a free-form string.

### Parameter descriptions {#parameter-descriptions}

Each parameter's `description` is also prompt text. Include the format you expect
and one example. A parameter documented as "a date" is filled with whatever the
model considers a date; one documented as "an ISO 8601 date, e.g. 2026-04-28" is
filled with an ISO 8601 date.

### Tool choice {#tool-choice}

The `tool_choice` field controls how freely the model may call tools:

- `auto` (default): the model decides whether to call a tool.
- `any`: the model must call one of the supplied tools.
- `none`: the model may not call a tool, and answers directly.
- A named tool: the model must call that specific tool.

Use `any` for a step in a pipeline where a tool call is the only valid outcome,
and `none` to force a plain answer on a turn where you have already gathered
everything the model needs.

## The call loop {#the-call-loop}

A conversation with tools runs as a loop. Each pass appends to the message list,
and the loop ends on the first assistant message that carries no tool calls.

```python
messages = [{"role": "user", "content": "What is the status of transaction T1001?"}]

while True:
    response = client.chat.complete(
        model="mistral-medium-latest",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    message = response.choices[0].message
    messages.append(message)
    if not message.tool_calls:
        break
    for call in message.tool_calls:
        result = dispatch(call.function.name, json.loads(call.function.arguments))
        messages.append(
            {
                "role": "tool",
                "name": call.function.name,
                "content": json.dumps(result),
                "tool_call_id": call.id,
            }
        )
```

Two details matter for correctness. The assistant message that requested the calls
must be appended verbatim, including its `tool_calls`; and every tool message must
carry the `tool_call_id` it answers. A missing id is the most common cause of a
model repeating a call it has already made.

### Parallel tool calls {#parallel-tool-calls}

One assistant message may carry several tool calls. Run them concurrently when
they are independent, and append one tool message per call, in any order. The
model matches them by id, not by position.

### Error handling {#error-handling}

When a function fails, return the failure as the tool result rather than raising
past the loop. A model that is told "transaction T1001 was not found" asks the
user for a different id; a model that receives nothing repeats the call.

Keep the error text short and factual. Stack traces waste context and give the
model text it may quote back to the user.

## Limits {#limits}

The number of tools you can supply is bounded by the context window rather than by
a fixed count: every tool definition is prompt text on every request. Past roughly
thirty tools, retrieval over your tool catalogue beats sending all of them.

Tool call arguments are generated text, so validate them before use. Treat a tool
call the way you would treat a form submitted by an anonymous user. In particular,
never interpolate an argument into a shell command, a SQL statement or a file path
without the same escaping you would apply to any other untrusted input. The model
is not adversarial, but the user talking to it may be, and a description that says
"the file to read" is an invitation the model will accept.

Argument types are advisory. A schema that declares an integer usually receives an
integer, but a model under pressure from a confusing prompt will occasionally send
the string `"42"`, and a client that assumes otherwise raises inside the tool loop
where the traceback is least useful. Parse and coerce at the boundary.

Names are load-bearing in a way that is easy to underestimate. Two tools called
`search` and `search_docs` are chosen between almost at random; the same two
called `search_web` and `search_internal_handbook` are chosen correctly. If a
model is calling the wrong tool, rename before you reach for prompt engineering.

The same applies to a tool that is never called at all. Before concluding the
model cannot use it, check that its description says when to use it rather than
only what it does: `get_weather` described as "returns weather data" is called far
less often than the same function described as "use whenever the user asks about
weather, temperature, rain or what to wear".

Latency compounds across the loop. Each pass is a full model call plus your
function's own runtime, so a three-step conversation costs three round trips
before the user sees anything. Streaming does not help here -- the first two
passes produce tool calls, not text -- so where the sequence is predictable it is
usually better to run the first step yourself and hand the model the result.

Cost compounds the same way. Every pass resends the whole message list, including
the tool definitions and every prior result, so a long tool conversation is
quadratic in tokens. Trimming old tool results once they have been summarised is
the single most effective saving available in an agent loop.

Finally, a tool call is not a guarantee. `tool_choice: "any"` forces the model to
call something, not to call the right thing with the right arguments, and no
setting removes the need to validate. Design each function so that being called
with wrong arguments is harmless, and the loop stays safe under every failure mode
the model can produce.
