# mined2-063 (unanswerable, 9 connector calls)

## Question

Is there a maximum execution time for code run by the Code Interpreter tool?

## Thinking

The user asks about a maximum execution time for code run by the Code Interpreter tool. I need to search the Mistral documentation for this information. I'll use the mistral_docs_search tool with a query that matches the user's question.

The initial search returned some results but didn't directly answer the question. I need to read the full documentation page for the Code Interpreter tool to find details about execution time limits. I'll call mistral_docs_read_page on the relevant page.

The first read didn't reveal the limit. I should also check the Vibe documentation, as the Code Interpreter tool might be mentioned there. I'll search for the same query but under the Vibe code-interpreter path.

The search under Vibe returned some results. I need to read the full Vibe code-interpreter page to see if it contains the maximum execution time.

The Vibe page also didn't mention a maximum execution time. I need to search for any documentation that mentions limits or timeouts for the Code Interpreter tool. I'll search for "Code Interpreter timeout" to see if there's a specific timeout mentioned.

The timeout search didn't yield a clear answer. I'll try a broader search for "Code Interpreter limits" to see if there are any documented limits, including execution time.

The limits search also didn't provide a clear answer. I'll search for "maximum execution time" to see if there's a general policy on execution time limits for tools.

The search for "maximum execution time" returned results related to workflows, which might have a different limit. I need to check if there's a known limitations page that lists all limits, including Code Interpreter. I'll search for "Code Interpreter" under the known-limitations path.

The search under known-limitations didn't find anything. I'll search the entire known-limitations page to see if there's any mention of Code Interpreter limits.

After searching through the Mistral documentation for Code Interpreter, I found mentions of rate limits but no explicit maximum execution time. The documentation does not specify a maximum execution time for the Code Interpreter tool. Therefore, I must conclude that the information is not available in the current documentation. I will inform the user that the documentation does not specify a maximum execution time, but mentions rate limits based on the plan.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "maximum execution time for Code Interpreter tool"}
```

Result:

```
q: "maximum execution time for Code Interpreter tool"

[1] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: explanation-of-the-output
    Code Interpreter > How it Works > Explanation of the Output
    Below we will explain the different outputs of the response of the previous snippet example: - **`message.output`**: This entry corresponds to the initial response from the assistant, indicating that it can help generate the first 20 Fibonacci numbers. - **`tool.execution`**: This entry corresponds to the execution of the code interpreter tool. It includes metadata about the execution, such as: - …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#explanation-of-the-output

[2] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: code-interpreter
    Code Interpreter
    Code Interpreter adds the capability to safely execute code in an isolated container, this built-in [tool](https://docs.mistral.ai/studio/agents/agent-tools#built-in-tools) allows Agents to run code at any point on demand, practical to draw graphs, data analysis, mathematical operations, code validation, and much more. ![code_interpreter_graph](https://docs.mistral.ai/img/code_interpreter_connecto …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter

[3] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: create-a-code-interpreter-agent
    Code Interpreter > Create a Code Interpreter Agent
    **Output** ```json { "model": "mistral-medium-latest", "name": "Coding Agent", "description": "Agent used to execute code using the interpreter tool.", "id": "ag_06830595b7ea7e70800087c4ec8a74e7", "version": 0, "created_at": "2025-05-23T11:17:47.497956Z", "updated_at": "2025-05-23T11:17:47.497959Z", "instructions": "Use the code interpreter tool when you have to run code.", "tools": [ { "type": "c …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#create-a-code-interpreter-agent:~:text=As%20for%20other

[4] https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | section: activation
    Code Interpreter > Activation
    Code Interpreter must be enabled before Vibe can use it. 1. Select the **Chat** tab in the sidebar. 2. Click the `+` icon or type `/` in the chat window. 3. Select `Tools` then enable `Code Interpreter`. The tool stays active for the duration of the conversation and subsequent chats. > **Note** > > Code Interpreter usage is **subject to rate limits** based on your plan. For details, visit our [pri …
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#activation

[5] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: conversation-with-code-interpreter
    Code Interpreter > How it Works > Conversations with Code Interpreter
    ```json { "conversation_id": "conv_06835b9dc0c7749180001958779d13c5", "outputs": [ { "content": "Sure, I can help with that. Here's a simple Python function to generate the first 20 Fibonacci numbers.", "object": "entry", "type": "message.output", "created_at": "2025-05-27T13:10:52.208822Z", "completed_at": "2025-05-27T13:10:52.470589Z", "id": "msg_06835b9dc35772be800073298138bacc", "agent_id": "a …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#conversation-with-code-interpreter

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter"}
```

Result:

```
page: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | "Code Interpreter"

## section: code-interpreter
    Code Interpreter
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter
# Code Interpreter

Code Interpreter adds the capability to safely execute code in an isolated container, this built-in [tool](https://docs.mistral.ai/studio/agents/agent-tools#built-in-tools) allows Agents to run code at any point on demand, practical to draw graphs, data analysis, mathematical operations, code validation, and much more.

![code_interpreter_graph](https://docs.mistral.ai/img/code_interpreter_connector.png)

> **Warning**
>
> `code_interpreter` works with the [Conversations API](https://docs.mistral.ai/studio/connectors/conversations) (`/v1/conversations`) and the Agents API. It isn't **supported** in the Chat Completions API (`/v1/chat/completions`). To use it with an Agent, create the Agent with `code_interpreter`, then start the conversation with `/v1/conversations`.

To use the code interpreter, create an Agent with the code interpreter tool. Then start a conversation with the Agent, and it runs code on demand to answer your questions.

## section: create-a-code-interpreter-agent
    Code Interpreter > Create a Code Interpreter Agent
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#create-a-code-interpreter-agent
## Create a Code Interpreter Agent {#create-a-code-interpreter-agent}

You can create an agent with access to our code interpreter by providing it as one of the tools.
Note that you can still add more tools to the agent, the model is free to run code or not on demand.

**Python**

```py
code_agent = client.beta.agents.create(
    model="mistral-medium-latest",
    name="Coding Agent",
    description="Agent used to execute code using the interpreter tool.",
    instructions="Use the code interpreter tool when you have to run code.",
    tools=[{"type": "code_interpreter"}],
    completion_args={
        "temperature": 0.3,
        "top_p": 0.95,
    }
)
```

(samples in TypeScript and cURL omitted: pass lang="typescript" or lang="curl")

**Output**

**Output**

```json
{
  "model": "mistral-medium-latest",
  "name": "Coding Agent",
  "description": "Agent used to execute code using the interpreter tool.",
  "id": "ag_06830595b7ea7e70800087c4ec8a74e7",
  "version": 0,
  "created_at": "2025-05-23T11:17:47.497956Z",
  "updated_at": "2025-05-23T11:17:47.497959Z",
  "instructions": "Use the code interpreter tool when you have to run code.",
  "tools": [
    {
      "type": "code_interpreter"
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

## section: how-it-works
    Code Interpreter > How it Works
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#how-it-works
## How it Works {#how-it-works}

Now that we have our coding agent ready, we can at any point make use of it to run code.

## section: conversation-with-code-interpreter
    Code Interpreter > How it Works > Conversations with Code Interpreter
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#conversation-with-code-interpreter
### Conversations with Code Interpreter {#conversation-with-code-interpreter}

To start a conversation with our code interpreter agent, we can use the following code:

**Python**

```py
response = client.beta.conversations.start(
    agent_id=code_agent.id,
    inputs="Run a fibonacci function for the first 20 values."
)
```

(samples in TypeScript and cURL omitted: pass lang="typescript" or lang="curl")

**Output**

```json
{
  "conversation_id": "conv_06835b9dc0c7749180001958779d13c5",
  "outputs": [
    {
      "content": "Sure, I can help with that. Here's a simple Python function to generate the first 20 Fibonacci numbers.",
      "object": "entry",
      "type": "message.output",
      "created_at": "2025-05-27T13:10:52.208822Z",
      "completed_at": "2025-05-27T13:10:52.470589Z",
      "id": "msg_06835b9dc35772be800073298138bacc",
      "agent_id": "ag_06835b9dbded7f39800034281a63e4f0",
      "model": "mistral-medium-latest",
      "role": "assistant"
    },
    {
      "name": "code_interpreter",
      "object": "entry",
      "type": "tool.execution",
      "created_at": "2025-05-27T13:10:52.561656Z",
      "completed_at": "2025-05-27T13:10:54.431304Z",
      "id": "tool_exec_06835b9dc8fc763880004b7aa94286d8",
      "info": {
        "code": "def fibonacci(n):\n    fib_sequence = [0, 1]\n    for i in range(2, n):\n        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])\n    return fib_sequence[:n]\n\nfibonacci_20 = fibonacci(20)\nfibonacci_20",
        "code_output": "[0,\n 1,\n 1,\n 2,\n 3,\n 5,\n 8,\n 13,\n 21,\n 34,\n 55,\n 89,\n 144,\n 233,\n 377,\n 610,\n 987,\n 1597,\n 2584,\n 4181]\n"
      }
    },
    {
      "content": "The first 20 values of the Fibonacci sequence are:\n\n[0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181]",
      "object": "entry",
      "type": "message.output",
      "created_at": "2025-05-27T13:10:54.517935Z",
```
(output cut after 1,500 characters; 18 more lines)

## section: explanation-of-the-output
    Code Interpreter > How it Works > Explanation of the Output
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#explanation-of-the-output
### Explanation of the Output {#explanation-of-the-output}

Below we will explain the different outputs of the response of the previous snippet example:

- **`message.output`**: This entry corresponds to the initial response from the assistant, indicating that it can help generate the first 20 Fibonacci numbers.

- **`tool.execution`**: This entry corresponds to the execution of the code interpreter tool. It includes metadata about the execution, such as:
  - `name`: The name of the tool, which in this case is `code_interpreter`.
  - `object`: The type of object, which is `entry`.
  - `type`: The type of entry, which is `tool.execution`.
  - `created_at` and `completed_at`: Timestamps indicating when the tool execution started and finished.
  - `id`: A unique identifier for the tool execution.
  - `info`: This section contains additional information specific to the tool execution. For the `code_interpreter` tool, the `info` section includes:
    - `code`: The actual code that was executed. In this example, it contains a Python function `fibonacci(n)` that generates the first `n` numbers in the Fibonacci sequence and a call to this function to get the first 20 Fibonacci numbers.
    - `code_output`: The output of the executed code, which is the list of the first 20 Fibonacci numbers.

- **`message.output`**: This entry corresponds to the final response from the assistant, providing the first 20 values of the Fibonacci sequence.

Results: 5 sections, the whole page.
```

### 3. mistral_docs_search

```json
{"q": "maximum execution time for Code Interpreter tool", "under": "https://docs.mistral.ai/vibe/chat-legacy/code-interpreter"}
```

Result:

```
q: "maximum execution time for Code Interpreter tool" | under: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter

[1] https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | section: activation
    Code Interpreter > Activation
    Code Interpreter must be enabled before Vibe can use it. 1. Select the **Chat** tab in the sidebar. 2. Click the `+` icon or type `/` in the chat window. 3. Select `Tools` then enable `Code Interpreter`. The tool stays active for the duration of the conversation and subsequent chats. > **Note** > > Code Interpreter usage is **subject to rate limits** based on your plan. For details, visit our [pri …
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#activation

[2] https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | section: code-interpreter
    Code Interpreter
    > **Warning** > > Code Interpreter is a legacy Chat feature. It remains available in the **Chat** tab, with no public deprecation date. > > Vibe Work has a built-in **TypeScript code environment** that covers most data-processing and graphing use cases, including cleaning data, generating charts, and transforming files. Pick Work when TypeScript fits the task. Pick Chat with Code Interpreter when …
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter

[3] https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | section: running-code
    Code Interpreter > Running code
    Describe what you want **in plain language** and Vibe writes and executes the Python code for you. ```text Load this CSV and show the top 5 rows, then plot sales by month. ``` The code runs in the sandbox and returns tables, figures, or files inline. You can follow up to refine results, adjust filters, or ask for explanations of what the code does. > **Info** > > Code Interpreter cannot fetch file …
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#running-code

[4] https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | section: use-cases
    Code Interpreter > Common use cases
    Code Interpreter combines the versatility of Vibe with the precision of Python. It's perfect for: - **Data analysis**: explore CSV, XLSX, or JSON files. Summarize, filter, flag outliers, or clean missing values. - **Charts and visuals**: generate line charts, bar charts, pie charts, or any Matplotlib visualization from your data. - **Calculations**: work through formulas, financial models, or unit …
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#use-cases

[5] https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | section: tips-for-better-results
    Code Interpreter > Tips for better results
    - **Be specific.** For charts or tables, specify column names, filters, and the desired output format. - **Ask for explanations.** Try *"Explain the steps and show the code"* to understand what's happening. - **Iterate.** Follow up with requests to fine-tune the output (e.g., *"Now add a rolling average and label the axes."*) - **Prototype with smaller files.** If you hit a limit, upload a sample …
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#tips-for-better-results

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/chat-legacy/code-interpreter") to read hit 1 on its page
```

### 4. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/chat-legacy/code-interpreter"}
```

Result:

```
page: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | "Code Interpreter"

## section: code-interpreter
    Code Interpreter
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter
# Code Interpreter

> **Warning**
>
> Code Interpreter is a legacy Chat feature. It remains available in the **Chat** tab, with no public deprecation date.
>
> Vibe Work has a built-in **TypeScript code environment** that covers most data-processing and graphing use cases, including cleaning data, generating charts, and transforming files. Pick Work when TypeScript fits the task. Pick Chat with Code Interpreter when you specifically need Python or a Python-only library.

Code Interpreter lets you **run Python directly inside Vibe**.

Not a developer? No problem. Describe what you want in plain language, and Vibe generates and executes the code for you.

> **Info**
>
> Code runs in a **secure, isolated environment** with no internet access. It cannot reach your system or external services. Common data-analysis packages are preinstalled (pandas, numpy, matplotlib). Uploaded files are available for the current conversation only.

## section: use-cases
    Code Interpreter > Common use cases
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#use-cases
## Common use cases {#use-cases}

Code Interpreter combines the versatility of Vibe with the precision of Python. It's perfect for:

- **Data analysis**: explore CSV, XLSX, or JSON files. Summarize, filter, flag outliers, or clean missing values.
- **Charts and visuals**: generate line charts, bar charts, pie charts, or any Matplotlib visualization from your data.
- **Calculations**: work through formulas, financial models, or unit conversions with verified accuracy.
- **File transformations**: convert formats, merge datasets, or export processed results as downloadable files.

## section: activation
    Code Interpreter > Activation
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#activation
## Activation {#activation}

Code Interpreter must be enabled before Vibe can use it.

1. Select the **Chat** tab in the sidebar.
2. Click the `+` icon or type `/` in the chat window.
3. Select `Tools` then enable `Code Interpreter`.

The tool stays active for the duration of the conversation and subsequent chats.

> **Note**
>
> Code Interpreter usage is **subject to rate limits** based on your plan. For details, visit our [pricing page](https://mistral.ai/pricing).

## section: running-code
    Code Interpreter > Running code
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#running-code
## Running code {#running-code}

Describe what you want **in plain language** and Vibe writes and executes the Python code for you.

```text
Load this CSV and show the top 5 rows, then plot sales by month.
```

The code runs in the sandbox and returns tables, figures, or files inline. You can follow up to refine results, adjust filters, or ask for explanations of what the code does.

> **Info**
>
> Code Interpreter cannot fetch files directly from URLs. If your data is online, download it locally and upload the file. Alternatively, enable [Web search](https://docs.mistral.ai/vibe/work/web-search-open-url) and ask Vibe to fetch the data before running code.

## section: working-with-files
    Code Interpreter > Working with files
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#working-with-files
## Working with files {#working-with-files}

Upload files using the `+` button in the chat toolbar. Supported formats include:

- **Documents**: PDF, Word (`.docx`, `.doc`), PowerPoint (`.pptx`, `.ppt`), ODT, EPUB, RTF
- **Spreadsheets**: Excel (`.xlsx`, `.xls`), CSV, ODS, Numbers
- **Images**: PNG, JPEG, WebP, GIF
- **Text and markup**: TXT, Markdown, RST, LaTeX
- **Data formats**: JSON, JSONL, XML, YAML
- **Code files**: Python, JavaScript/TypeScript, Java, Go, Rust, C/C++, Ruby, PHP, SQL, and many more
- **Email**: EML, MSG

Typical prompts:

- *"Summarize this spreadsheet and flag outliers."*
- *"Clean this CSV, fix missing values, and export a new file."*
- *"Extract all emails from this PDF and give me a CSV."*

> **Note**
>
> For details and advanced workflows, see the [Files and Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas) article.

## section: tips-for-better-results
    Code Interpreter > Tips for better results
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#tips-for-better-results
## Tips for better results {#tips-for-better-results}

- **Be specific.** For charts or tables, specify column names, filters, and the desired output format.
- **Ask for explanations.** Try *"Explain the steps and show the code"* to understand what's happening.
- **Iterate.** Follow up with requests to fine-tune the output (e.g., *"Now add a rolling average and label the axes."*)
- **Prototype with smaller files.** If you hit a limit, upload a sample to test your approach, then scale up.
- **Avoid sharing secrets.** Never share API keys or credentials in the chat or in code.

## section: related-features
    Code Interpreter > Related features
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#related-features
## Related features {#related-features}

- **[Files and Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas)**: edit and refine code, data, and text, and import documents, spreadsheets, and images into your conversation.

Results: 7 sections, the whole page.
```

### 5. mistral_docs_search

```json
{"q": "Code Interpreter timeout"}
```

Result:

```
q: "Code Interpreter timeout"

[1] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: code-interpreter
    Code Interpreter
    Code Interpreter adds the capability to safely execute code in an isolated container, this built-in [tool](https://docs.mistral.ai/studio/agents/agent-tools#built-in-tools) allows Agents to run code at any point on demand, practical to draw graphs, data analysis, mathematical operations, code validation, and much more. ![code_interpreter_graph](https://docs.mistral.ai/img/code_interpreter_connecto …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter

[2] https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | section: code-interpreter
    Code Interpreter
    > **Warning** > > Code Interpreter is a legacy Chat feature. It remains available in the **Chat** tab, with no public deprecation date. > > Vibe Work has a built-in **TypeScript code environment** that covers most data-processing and graphing use cases, including cleaning data, generating charts, and transforming files. Pick Work when TypeScript fits the task. Pick Chat with Code Interpreter when …
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter

[3] https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | section: activation
    Code Interpreter > Activation
    Code Interpreter must be enabled before Vibe can use it. 1. Select the **Chat** tab in the sidebar. 2. Click the `+` icon or type `/` in the chat window. 3. Select `Tools` then enable `Code Interpreter`. The tool stays active for the duration of the conversation and subsequent chats. > **Note** > > Code Interpreter usage is **subject to rate limits** based on your plan. For details, visit our [pri …
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#activation

[4] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: create-a-code-interpreter-agent
    Code Interpreter > Create a Code Interpreter Agent
    You can create an agent with access to our code interpreter by providing it as one of the tools. Note that you can still add more tools to the agent, the model is free to run code or not on demand. **Python** ```py code_agent = client.beta.agents.create( model="mistral-medium-latest", name="Coding Agent", description="Agent used to execute code using the interpreter tool.", instructions="Use the c …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#create-a-code-interpreter-agent

[5] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: conversation-with-code-interpreter
    Code Interpreter > How it Works > Conversations with Code Interpreter
    To start a conversation with our code interpreter agent, we can use the following code: **Python** ```py response = client.beta.conversations.start( agent_id=code_agent.id, inputs="Run a fibonacci function for the first 20 values." ) ``` **TypeScript** ```typescript let conversation = await client.beta.conversations.start({ agentId: codeAgent.id, inputs:"Run a fibonacci function for the first 20 v …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#conversation-with-code-interpreter

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter") to read hit 1 on its page
```

### 6. mistral_docs_search

```json
{"q": "Code Interpreter limits"}
```

Result:

```
q: "Code Interpreter limits"

[1] https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | section: activation
    Code Interpreter > Activation
    Code Interpreter must be enabled before Vibe can use it. 1. Select the **Chat** tab in the sidebar. 2. Click the `+` icon or type `/` in the chat window. 3. Select `Tools` then enable `Code Interpreter`. The tool stays active for the duration of the conversation and subsequent chats. > **Note** > > Code Interpreter usage is **subject to rate limits** based on your plan. For details, visit our [pri …
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#activation

[2] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: code-interpreter
    Code Interpreter
    Code Interpreter adds the capability to safely execute code in an isolated container, this built-in [tool](https://docs.mistral.ai/studio/agents/agent-tools#built-in-tools) allows Agents to run code at any point on demand, practical to draw graphs, data analysis, mathematical operations, code validation, and much more. ![code_interpreter_graph](https://docs.mistral.ai/img/code_interpreter_connecto …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter

[3] https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | section: code-interpreter
    Code Interpreter
    > **Warning** > > Code Interpreter is a legacy Chat feature. It remains available in the **Chat** tab, with no public deprecation date. > > Vibe Work has a built-in **TypeScript code environment** that covers most data-processing and graphing use cases, including cleaning data, generating charts, and transforming files. Pick Work when TypeScript fits the task. Pick Chat with Code Interpreter when …
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter

[4] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: create-a-code-interpreter-agent
    Code Interpreter > Create a Code Interpreter Agent
    You can create an agent with access to our code interpreter by providing it as one of the tools. Note that you can still add more tools to the agent, the model is free to run code or not on demand. **Python** ```py code_agent = client.beta.agents.create( model="mistral-medium-latest", name="Coding Agent", description="Agent used to execute code using the interpreter tool.", instructions="Use the c …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#create-a-code-interpreter-agent

[5] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: conversation-with-code-interpreter
    Code Interpreter > How it Works > Conversations with Code Interpreter
    To start a conversation with our code interpreter agent, we can use the following code: **Python** ```py response = client.beta.conversations.start( agent_id=code_agent.id, inputs="Run a fibonacci function for the first 20 values." ) ``` **TypeScript** ```typescript let conversation = await client.beta.conversations.start({ agentId: codeAgent.id, inputs:"Run a fibonacci function for the first 20 v …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#conversation-with-code-interpreter

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/chat-legacy/code-interpreter") to read hit 1 on its page
```

### 7. mistral_docs_search

```json
{"q": "maximum execution time"}
```

Result:

```
q: "maximum execution time"

[1] https://docs.mistral.ai/api/endpoint/workflows/executions | section: operation-get_workflow_execution_logs/parameters
    Workflows Executions API > Get Workflow Execution Logs > Parameters
    - `execution_id` (string, required, in path) - `run_id` (string (uuid) or null, optional, in query) — Filter logs by workflow run ID - `activity_id` (string or null, optional, in query) — Filter logs by activity ID - `after` (string (date-time) or null, optional, in query) — Only return logs at or after this timestamp - `before` (string (date-time) or null, optional, in query) — Only return logs b …
    cite: https://docs.mistral.ai/api/endpoint/workflows/executions#operation-get_workflow_execution_logs

[2] https://docs.mistral.ai/studio/workflows/getting-started/your_first_workflow | section: step-3-trigger-execution-of-your-workflow
    Your first workflow > Step 3: Trigger execution of your workflow
    **Output** ```json { "workflow_name": "hello-world", "execution_id": "my-execution-id", "root_execution_id": "my-execution-id", "status": "RUNNING", "start_time": "<timestamp>", "end_time": null, "result": null, "parent_execution_id": null, "total_duration_ms": null } ``` When you're done testing your workflow, press `Ctrl+C` to stop the worker.
    cite: https://docs.mistral.ai/studio/workflows/getting-started/your_first_workflow#step-3-trigger-execution-of-your-workflow:~:text=When%20you%27re%20done

[3] https://docs.mistral.ai/studio/workflows/building-workflows/workflows | section: execution-timeout
    Workflows > Execution timeout
    For the role and default of `execution_timeout`, see [Core Concepts > Execution timeout](https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/workflows#execution-timeout). To override the 1-hour default, pass a `timedelta` to the decorator: ```python from datetime import timedelta from mistralai.workflows import workflow @workflow.define(name="long_running_workflow", execution_ti …
    cite: https://docs.mistral.ai/studio/workflows/building-workflows/workflows#execution-timeout

[4] https://docs.mistral.ai/resources/known-limitations | section: batch-processing
    Known limitations > Batch processing
    - Maximum batch file size: **512 MB**. - Maximum requests per batch: **100,000**. - Batch jobs are processed asynchronously; completion time depends on queue depth and request complexity. - Batch results are available for download for **24 hours** after completion.
    cite: https://docs.mistral.ai/resources/known-limitations#batch-processing

[5] https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/workflows | section: execution-timeout
    Workflows > Execution timeout
    Every workflow has an `execution_timeout`, the hard cap on its total lifetime including all retries and [continue-as-new](https://docs.mistral.ai/studio/workflows/building-workflows/continue_as_new) iterations. The default is 1 hour. Workflows that need to run longer must opt in: **Python** ```python from datetime import timedelta @workflows.workflow.define(name="long_running_workflow", execution_ …
    cite: https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/workflows#execution-timeout

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/api/endpoint/workflows/executions") to read hit 1 on its page
```

### 8. mistral_docs_search

```json
{"q": "Code Interpreter", "under": "https://docs.mistral.ai/resources/known-limitations"}
```

Result:

```
q: "Code Interpreter" | under: https://docs.mistral.ai/resources/known-limitations

Results: no section under https://docs.mistral.ai/resources/known-limitations matched; 1 pages exist there.
next: mistral_docs_search(under="https://docs.mistral.ai/resources/known-limitations") lists them; a page not listed does not exist at this commit.
```

### 9. mistral_docs_search

```json
{"q": "Code Interpreter", "under": "https://docs.mistral.ai"}
```

Result:

```
q: "Code Interpreter" | under: https://docs.mistral.ai

[1] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: code-interpreter
    Code Interpreter
    Code Interpreter adds the capability to safely execute code in an isolated container, this built-in [tool](https://docs.mistral.ai/studio/agents/agent-tools#built-in-tools) allows Agents to run code at any point on demand, practical to draw graphs, data analysis, mathematical operations, code validation, and much more. ![code_interpreter_graph](https://docs.mistral.ai/img/code_interpreter_connecto …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter

[2] https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | section: code-interpreter
    Code Interpreter
    > **Warning** > > Code Interpreter is a legacy Chat feature. It remains available in the **Chat** tab, with no public deprecation date. > > Vibe Work has a built-in **TypeScript code environment** that covers most data-processing and graphing use cases, including cleaning data, generating charts, and transforming files. Pick Work when TypeScript fits the task. Pick Chat with Code Interpreter when …
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter

[3] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: create-a-code-interpreter-agent
    Code Interpreter > Create a Code Interpreter Agent
    You can create an agent with access to our code interpreter by providing it as one of the tools. Note that you can still add more tools to the agent, the model is free to run code or not on demand. **Python** ```py code_agent = client.beta.agents.create( model="mistral-medium-latest", name="Coding Agent", description="Agent used to execute code using the interpreter tool.", instructions="Use the c …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#create-a-code-interpreter-agent

[4] https://docs.mistral.ai/vibe/chat-legacy/code-interpreter | section: activation
    Code Interpreter > Activation
    Code Interpreter must be enabled before Vibe can use it. 1. Select the **Chat** tab in the sidebar. 2. Click the `+` icon or type `/` in the chat window. 3. Select `Tools` then enable `Code Interpreter`. The tool stays active for the duration of the conversation and subsequent chats. > **Note** > > Code Interpreter usage is **subject to rate limits** based on your plan. For details, visit our [pri …
    cite: https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#activation

[5] https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter | section: conversation-with-code-interpreter
    Code Interpreter > How it Works > Conversations with Code Interpreter
    To start a conversation with our code interpreter agent, we can use the following code: **Python** ```py response = client.beta.conversations.start( agent_id=code_agent.id, inputs="Run a fibonacci function for the first 20 values." ) ``` **TypeScript** ```typescript let conversation = await client.beta.conversations.start({ agentId: codeAgent.id, inputs:"Run a fibonacci function for the first 20 v …
    cite: https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter#conversation-with-code-interpreter

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/studio/agents/agent-tools/code_interpreter") to read hit 1 on its page
```

## Answer

The Mistral documentation does **not** specify a **maximum execution time** for the Code Interpreter tool. It only mentions that Code Interpreter usage is **subject to rate limits** based on your plan, as noted in the [Activation section for Vibe's legacy Code Interpreter](https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#activation)
cite: [https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#activation](https://docs.mistral.ai/vibe/chat-legacy/code-interpreter#activation).

If you need precise limits, you may need to refer to your plan's details or contact Mistral support.

