# mined2-070 (api_reference, 11 connector calls)

## Question

Can I set instructions on a conversation when the agent already carries its own instructions?

## Thinking

The user is asking about setting instructions on a conversation when the agent already has its own instructions. This is a specific question about Mistral AI's agent system and how instruction precedence works. I need to search the documentation to find information about this scenario.

I should search for terms like:
- "agent instructions"
- "conversation instructions"
- "override agent instructions"
- "instruction precedence"
- "set instructions conversation"

Let me start with a search query that captures the essence of the question.

The search returned some results about custom instructions. Let me read the custom-instructions page to understand the interaction between different levels of instructions.

The custom-instructions page gives me information about how custom instructions interact with other features. It mentions that Skills take precedence over custom instructions, and Projects can provide context tied to a specific work area. However, I need more specific information about the conversation-level instructions and how they interact with agent-level instructions.

Let me search for more specific information about conversation instructions and agent instructions precedence.

The search results are still pointing to the same custom-instructions page. Let me try a different approach and look for information about agents and their instructions, as well as how conversation-level instructions work.

I'm getting the same results. Let me try to find information specifically about agents and how their instructions work in the context of Work. I should look for the agents documentation.

The search results keep pointing to the same pages. Let me try to find the Work agents documentation specifically. I should look for the Work product documentation.

I see a result about agents being a legacy Chat feature. Let me read that page to understand the relationship between Agents and Custom Instructions.

Perfect! I found the key information. In the "Related features" section of the Agents page, it clearly states:

"Custom instructions: set persistent behavior rules that apply to all conversations (Agents override these when active)."

This directly answers the user's question. When an Agent is active in a conversation, its instructions take precedence over the Custom Instructions. So yes, you can set instructions on a conversation when the agent already carries its own instructions, but the agent's instructions will override the custom instructions.

Let me also check if there's any information about conversation-level instructions specifically. The user asked about "conversation" instructions, but in the Mistral Work documentation, it seems like the hierarchy is:
1. Agent instructions (when active) - highest priority
2. Project instructions
3. Custom instructions (account-level)

But I need to verify if there's a separate concept of conversation-level instructions. Let me search for that.

Based on my research, I now have a clear picture:

1. **Custom Instructions** are account-level persistent preferences that apply to all tasks/conversations
2. **Agents** are specialized assistants with their own instructions
3. **Projects** can have their own instructions that apply to chats within them
4. **Skills** can also have instructions that take precedence

From the Agents documentation: "Custom instructions: set persistent behavior rules that apply to all conversations **(Agents override these when active)**."

This means:
- When an Agent is active in a conversation, its instructions take precedence over Custom Instructions
- You CAN set instructions on a conversation (via Custom Instructions), but if an Agent is active, the Agent's instructions will override them
- The answer to the user's question is: **Yes, but the agent's instructions will override the conversation's custom instructions**

However, I should also check if there's a way to set conversation-specific instructions that are separate from Custom Instructions. Let me search for task-level or conversation-level instructions.

I have enough information now. Let me also check the Projects page to understand the full hierarchy.

Now I have a complete picture. Let me also check the Skills documentation to understand the full hierarchy.

I have gathered enough information from the documentation. Let me now synthesize the answer:

From the documentation:

1. **Custom Instructions** are persistent preferences that apply across all tasks/conversations
2. **Agents** (legacy Chat feature) override Custom Instructions when active - this is explicitly stated in the Agents documentation: "Custom instructions: set persistent behavior rules that apply to all conversations **(Agents override these when active)**."
3. **Projects** can have their own instructions that apply to every chat inside them
4. **Skills** take precedence over Custom Instructions when active for a task

The user's question is: "Can I set instructions on a conversation when the agent already carries its own instructions?"

Based on the documentation:
- Yes, you can set Custom Instructions (which apply to conversations)
- However, when an Agent is active in a conversation, **the Agent's instructions take precedence** over the Custom Instructions
- So the conversation will use the Agent's instructions, not the Custom Instructions

The answer should be: Yes, but the agent's instructions will override any custom instructions you set on the conversation.

I should structure this clearly with the relevant citations.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "set instructions on a conversation when agent already carries its own instructions"}
```

Result:

```
q: "set instructions on a conversation when agent already carries its own instructions"

[1] https://docs.mistral.ai/vibe/work/custom-instructions | section: interaction-with-other-features
    Set custom instructions > Interactions with other features
    Custom instructions apply alongside other context sources, but their priority depends on the feature. - **[Skills](https://docs.mistral.ai/vibe/work/skills)**: when a Skill is active for a task, its instructions take precedence over your custom instructions. This lets you apply task-specific procedures without conflicting with your general preferences. - **[Projects](https://docs.mistral.ai/vibe/w …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#interaction-with-other-features

[2] https://docs.mistral.ai/vibe/work/custom-instructions | section: setup
    Set custom instructions > Setting up custom instructions
    1. In the left sidebar, click `Context` then `Instructions`. 2. The Custom instructions pop-up opens. 3. Choose a **Tone** and enter your instructions: describe your role, output format, or any context you want Work to assume. 4. Save your changes. Your instructions take effect in all new tasks from that point on. Existing tasks aren't affected. > **Info** > > Custom instructions are included in t …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#setup

[3] https://docs.mistral.ai/vibe/work/custom-instructions | section: what-to-avoid
    Set custom instructions > What to avoid
    Custom instructions work best when they're focused. - **Don't use them as a project brief.** They're meant for persistent preferences, not task descriptions. For task-specific context, use the prompt itself or [Projects](https://docs.mistral.ai/vibe/work/projects). - **Don't contradict your prompts.** If your custom instruction says "always respond in French" but you ask questions in English and e …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#what-to-avoid

[4] https://docs.mistral.ai/vibe/work/custom-instructions | section: examples
    Set custom instructions > Examples
    A good custom instruction is short, specific, and tells Work something it can't infer from your prompts alone. **Role and domain expertise** - *"I'm a compliance officer at a European bank. Reference EU regulations (MiFID II, GDPR) when relevant."* - *"I'm a software engineer working with Python and TypeScript. Tailor code examples accordingly."* - *"When I ask about data, assume I'm working with …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#examples

[5] https://docs.mistral.ai/vibe/work/projects | section: project-instructions
    Group tasks with Projects > Project instructions and context
    Each Project can carry its own tone, instructions, and shared context that apply to every chat inside it. Open a Project to access these settings: - **Tone**: pick a tone for this Project, or keep `Default (Global)` to inherit the tone from your account-level [Custom instructions](https://docs.mistral.ai/vibe/work/custom-instructions). - **Instructions**: click `Customize` to write Project-specifi …
    cite: https://docs.mistral.ai/vibe/work/projects#project-instructions

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/work/custom-instructions") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/work/custom-instructions"}
```

Result:

```
page: https://docs.mistral.ai/vibe/work/custom-instructions | "Set custom instructions"

## section: set-custom-instructions
    Set custom instructions
    cite: https://docs.mistral.ai/vibe/work/custom-instructions
# Set custom instructions

Custom instructions let you define **persistent preferences** that shape how Work responds across every task.

> **Note**
>
> Think of them as a brief profile you give the assistant: your role, your domain, your preferred output style. Instead of repeating *"I work in compliance"* or *"use metric units"* at the start of each task, you set it once and Work applies it automatically.

For teams, custom instructions help standardize how your organization interacts with Work, so everyone gets responses tailored to shared conventions, terminology, and formatting requirements.

## section: setup
    Set custom instructions > Setting up custom instructions
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#setup
## Setting up custom instructions {#setup}

1. In the left sidebar, click `Context` then `Instructions`.
2. The Custom instructions pop-up opens.
3. Choose a **Tone** and enter your instructions: describe your role, output format, or any context you want Work to assume.
4. Save your changes.

Your instructions take effect in all new tasks from that point on. Existing tasks aren't affected.

> **Info**
>
> Custom instructions are included in the context Work uses to plan and execute every task, alongside your prompt, attached files, Connectors, Libraries, and Skills.

## section: interaction-with-other-features
    Set custom instructions > Interactions with other features
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#interaction-with-other-features
## Interactions with other features {#interaction-with-other-features}

Custom instructions apply alongside other context sources, but their priority depends on the feature.

- **[Skills](https://docs.mistral.ai/vibe/work/skills)**: when a Skill is active for a task, its instructions take precedence over your custom instructions. This lets you apply task-specific procedures without conflicting with your general preferences.
- **[Projects](https://docs.mistral.ai/vibe/work/projects)**: Projects can provide context tied to a specific work area. Both apply together for tasks inside a Project.
- **Tools**: custom instructions shape how Work communicates with you, but they don't change how tools execute. For example, a Connector still queries the same data regardless of your formatting preferences.

## section: examples
    Set custom instructions > Examples
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#examples
## Examples {#examples}

A good custom instruction is short, specific, and tells Work something it can't infer from your prompts alone.

**Role and domain expertise**
- *"I'm a compliance officer at a European bank. Reference EU regulations (MiFID II, GDPR) when relevant."*
- *"I'm a software engineer working with Python and TypeScript. Tailor code examples accordingly."*
- *"When I ask about data, assume I'm working with PostgreSQL."*

**Output formatting**
- *"Structure all technical responses with Problem, Analysis, Solution, and Next Steps sections."*
- *"Always format financial figures with two decimal places and include the currency symbol."*
- *"Keep responses concise. Use bullet points instead of paragraphs."*

**Language and tone**
- *"Always respond in French unless I ask otherwise."*
- *"Respond in British English. Use formal tone for client-facing content, casual for internal notes."*

**Constraints**
- *"Don't include disclaimers or caveats unless I'm asking about medical, legal, or financial advice."*
- *"When generating code, always include error handling and type annotations."*

## section: what-to-avoid
    Set custom instructions > What to avoid
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#what-to-avoid
## What to avoid {#what-to-avoid}

Custom instructions work best when they're focused.

- **Don't use them as a project brief.** They're meant for persistent preferences, not task descriptions. For task-specific context, use the prompt itself or [Projects](https://docs.mistral.ai/vibe/work/projects).
- **Don't contradict your prompts.** If your custom instruction says "always respond in French" but you ask questions in English and expect English answers, you'll get inconsistent results.
- **Keep them concise.** A few well-written sentences work better than multiple paragraphs. The more focused your instructions, the more reliably Work follows them.
- **Don't include secrets or credentials.** Custom instructions are persistent and apply across all your tasks.

Results: 5 sections, the whole page.
```

### 3. mistral_docs_search

```json
{"q": "agent instructions conversation instructions precedence override"}
```

Result:

```
q: "agent instructions conversation instructions precedence override"

[1] https://docs.mistral.ai/vibe/work/custom-instructions | section: interaction-with-other-features
    Set custom instructions > Interactions with other features
    Custom instructions apply alongside other context sources, but their priority depends on the feature. - **[Skills](https://docs.mistral.ai/vibe/work/skills)**: when a Skill is active for a task, its instructions take precedence over your custom instructions. This lets you apply task-specific procedures without conflicting with your general preferences. - **[Projects](https://docs.mistral.ai/vibe/w …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#interaction-with-other-features

[2] https://docs.mistral.ai/vibe/work/custom-instructions | section: setup
    Set custom instructions > Setting up custom instructions
    1. In the left sidebar, click `Context` then `Instructions`. 2. The Custom instructions pop-up opens. 3. Choose a **Tone** and enter your instructions: describe your role, output format, or any context you want Work to assume. 4. Save your changes. Your instructions take effect in all new tasks from that point on. Existing tasks aren't affected. > **Info** > > Custom instructions are included in t …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#setup

[3] https://docs.mistral.ai/vibe/work/custom-instructions | section: set-custom-instructions
    Set custom instructions
    Custom instructions let you define **persistent preferences** that shape how Work responds across every task. > **Note** > > Think of them as a brief profile you give the assistant: your role, your domain, your preferred output style. Instead of repeating *"I work in compliance"* or *"use metric units"* at the start of each task, you set it once and Work applies it automatically. For teams, custom …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions

[4] https://docs.mistral.ai/vibe/work/custom-instructions | section: what-to-avoid
    Set custom instructions > What to avoid
    Custom instructions work best when they're focused. - **Don't use them as a project brief.** They're meant for persistent preferences, not task descriptions. For task-specific context, use the prompt itself or [Projects](https://docs.mistral.ai/vibe/work/projects). - **Don't contradict your prompts.** If your custom instruction says "always respond in French" but you ask questions in English and e …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#what-to-avoid

[5] https://docs.mistral.ai/vibe/chat-legacy/agents | section: writing-instructions
    Agents > Writing effective instructions
    Good instructions make the difference between a generic chatbot and a reliable team tool. Here are a few principles: - **Define the role clearly.** Start with who the Agent is and what it does: *"You are a code reviewer. Focus on Python best practices, security issues, and performance."* - **Specify the output format.** Tell the Agent whether you expect bullet points, JSON, prose, a table, or some …
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#writing-instructions

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/work/custom-instructions") to read hit 1 on its page
```

### 4. mistral_docs_search

```json
{"q": "agent instructions conversation level instructions Work"}
```

Result:

```
q: "agent instructions conversation level instructions Work"

[1] https://docs.mistral.ai/vibe/work/custom-instructions | section: setup
    Set custom instructions > Setting up custom instructions
    1. In the left sidebar, click `Context` then `Instructions`. 2. The Custom instructions pop-up opens. 3. Choose a **Tone** and enter your instructions: describe your role, output format, or any context you want Work to assume. 4. Save your changes. Your instructions take effect in all new tasks from that point on. Existing tasks aren't affected. > **Info** > > Custom instructions are included in t …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#setup

[2] https://docs.mistral.ai/vibe/work/custom-instructions | section: set-custom-instructions
    Set custom instructions
    Custom instructions let you define **persistent preferences** that shape how Work responds across every task. > **Note** > > Think of them as a brief profile you give the assistant: your role, your domain, your preferred output style. Instead of repeating *"I work in compliance"* or *"use metric units"* at the start of each task, you set it once and Work applies it automatically. For teams, custom …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions

[3] https://docs.mistral.ai/vibe/work/custom-instructions | section: interaction-with-other-features
    Set custom instructions > Interactions with other features
    Custom instructions apply alongside other context sources, but their priority depends on the feature. - **[Skills](https://docs.mistral.ai/vibe/work/skills)**: when a Skill is active for a task, its instructions take precedence over your custom instructions. This lets you apply task-specific procedures without conflicting with your general preferences. - **[Projects](https://docs.mistral.ai/vibe/w …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#interaction-with-other-features

[4] https://docs.mistral.ai/vibe/work/custom-instructions | section: what-to-avoid
    Set custom instructions > What to avoid
    Custom instructions work best when they're focused. - **Don't use them as a project brief.** They're meant for persistent preferences, not task descriptions. For task-specific context, use the prompt itself or [Projects](https://docs.mistral.ai/vibe/work/projects). - **Don't contradict your prompts.** If your custom instruction says "always respond in French" but you ask questions in English and e …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#what-to-avoid

[5] https://docs.mistral.ai/vibe/work/projects | section: project-instructions
    Group tasks with Projects > Project instructions and context
    Each Project can carry its own tone, instructions, and shared context that apply to every chat inside it. Open a Project to access these settings: - **Tone**: pick a tone for this Project, or keep `Default (Global)` to inherit the tone from your account-level [Custom instructions](https://docs.mistral.ai/vibe/work/custom-instructions). - **Instructions**: click `Customize` to write Project-specifi …
    cite: https://docs.mistral.ai/vibe/work/projects#project-instructions

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/work/custom-instructions") to read hit 1 on its page
```

### 5. mistral_docs_search

```json
{"q": "Work agent instructions conversation instructions"}
```

Result:

```
q: "Work agent instructions conversation instructions"

[1] https://docs.mistral.ai/vibe/work/custom-instructions | section: setup
    Set custom instructions > Setting up custom instructions
    1. In the left sidebar, click `Context` then `Instructions`. 2. The Custom instructions pop-up opens. 3. Choose a **Tone** and enter your instructions: describe your role, output format, or any context you want Work to assume. 4. Save your changes. Your instructions take effect in all new tasks from that point on. Existing tasks aren't affected. > **Info** > > Custom instructions are included in t …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#setup

[2] https://docs.mistral.ai/vibe/work/custom-instructions | section: set-custom-instructions
    Set custom instructions
    Custom instructions let you define **persistent preferences** that shape how Work responds across every task. > **Note** > > Think of them as a brief profile you give the assistant: your role, your domain, your preferred output style. Instead of repeating *"I work in compliance"* or *"use metric units"* at the start of each task, you set it once and Work applies it automatically. For teams, custom …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions

[3] https://docs.mistral.ai/vibe/work/custom-instructions | section: interaction-with-other-features
    Set custom instructions > Interactions with other features
    Custom instructions apply alongside other context sources, but their priority depends on the feature. - **[Skills](https://docs.mistral.ai/vibe/work/skills)**: when a Skill is active for a task, its instructions take precedence over your custom instructions. This lets you apply task-specific procedures without conflicting with your general preferences. - **[Projects](https://docs.mistral.ai/vibe/w …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#interaction-with-other-features

[4] https://docs.mistral.ai/vibe/work/custom-instructions | section: what-to-avoid
    Set custom instructions > What to avoid
    Custom instructions work best when they're focused. - **Don't use them as a project brief.** They're meant for persistent preferences, not task descriptions. For task-specific context, use the prompt itself or [Projects](https://docs.mistral.ai/vibe/work/projects). - **Don't contradict your prompts.** If your custom instruction says "always respond in French" but you ask questions in English and e …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#what-to-avoid

[5] https://docs.mistral.ai/vibe/chat-legacy/agents | section: writing-instructions
    Agents > Writing effective instructions
    Good instructions make the difference between a generic chatbot and a reliable team tool. Here are a few principles: - **Define the role clearly.** Start with who the Agent is and what it does: *"You are a code reviewer. Focus on Python best practices, security issues, and performance."* - **Specify the output format.** Tell the Agent whether you expect bullet points, JSON, prose, a table, or some …
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#writing-instructions

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/work/custom-instructions") to read hit 1 on its page
```

### 6. mistral_docs_search

```json
{"q": "Work agents instructions"}
```

Result:

```
q: "Work agents instructions"

[1] https://docs.mistral.ai/vibe/work/custom-instructions | section: setup
    Set custom instructions > Setting up custom instructions
    1. In the left sidebar, click `Context` then `Instructions`. 2. The Custom instructions pop-up opens. 3. Choose a **Tone** and enter your instructions: describe your role, output format, or any context you want Work to assume. 4. Save your changes. Your instructions take effect in all new tasks from that point on. Existing tasks aren't affected. > **Info** > > Custom instructions are included in t …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#setup

[2] https://docs.mistral.ai/vibe/work/custom-instructions | section: set-custom-instructions
    Set custom instructions
    Custom instructions let you define **persistent preferences** that shape how Work responds across every task. > **Note** > > Think of them as a brief profile you give the assistant: your role, your domain, your preferred output style. Instead of repeating *"I work in compliance"* or *"use metric units"* at the start of each task, you set it once and Work applies it automatically. For teams, custom …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions

[3] https://docs.mistral.ai/vibe/chat-legacy/agents | section: agents
    Agents
    > **Warning** > > Agents are a legacy Chat feature. They remain available in the **Chat** tab, with no public deprecation date. > > In Vibe Work, use **[Skills](https://docs.mistral.ai/vibe/work/skills)** for reusable methods that apply across tasks. For the Work entry point, see [Get started with Work](https://docs.mistral.ai/vibe/work/get-started). An Agent is a **specialized assistant** you con …
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents

[4] https://docs.mistral.ai/vibe/chat-legacy/agents | section: related-features
    Agents > Related features
    - **[Skills](https://docs.mistral.ai/vibe/work/skills)**: the Vibe Work successor for reusable, specialized behavior. - **[Custom instructions](https://docs.mistral.ai/vibe/work/custom-instructions)**: set persistent behavior rules that apply to all conversations (Agents override these when active). - **[Libraries](https://docs.mistral.ai/vibe/work/libraries)**: build knowledge bases from uploaded …
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#related-features

[5] https://docs.mistral.ai/vibe/work/custom-instructions | section: what-to-avoid
    Set custom instructions > What to avoid
    Custom instructions work best when they're focused. - **Don't use them as a project brief.** They're meant for persistent preferences, not task descriptions. For task-specific context, use the prompt itself or [Projects](https://docs.mistral.ai/vibe/work/projects). - **Don't contradict your prompts.** If your custom instruction says "always respond in French" but you ask questions in English and e …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#what-to-avoid

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/work/custom-instructions") to read hit 1 on its page
```

### 7. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/chat-legacy/agents"}
```

Result:

```
page: https://docs.mistral.ai/vibe/chat-legacy/agents | "Agents"

## section: agents
    Agents
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents
# Agents

> **Warning**
>
> Agents are a legacy Chat feature. They remain available in the **Chat** tab, with no public deprecation date.
>
> In Vibe Work, use **[Skills](https://docs.mistral.ai/vibe/work/skills)** for reusable methods that apply across tasks. For the Work entry point, see [Get started with Work](https://docs.mistral.ai/vibe/work/get-started).

An Agent is a **specialized assistant** you configure once and reuse across conversations. Give it instructions, tools, and knowledge sources, and it handles the rest.

> **Tip**
>
> When you catch yourself **repeating the same prompts**, attaching the same files, or enabling the same tools every time you start a conversation, that's a good sign you need an Agent.

## section: use-cases
    Agents > Common use cases
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#use-cases
## Common use cases {#use-cases}

Agents work best when you need the same instructions, tone, or knowledge applied consistently:

- **Brand voice editor**: paste any draft and get it rewritten in your company's tone, with the same formatting rules every time.
- **Legal clause checker**: upload a contract and ask the Agent to flag non-standard clauses based on your internal policy [Library](https://docs.mistral.ai/vibe/work/libraries).
- **Meeting prep assistant**: share a prospect's website or a briefing doc and get structured talking points, key figures, and open questions.
- **Technical FAQ**: attach your product documentation as a [Library](https://docs.mistral.ai/vibe/work/libraries) and share the Agent with your team so anyone can get accurate, sourced answers.
- **Translation with context**: an Agent that translates content while respecting your glossary and brand terminology, attached as a [Library](https://docs.mistral.ai/vibe/work/libraries).

## section: creating-an-agent
    Agents > Creating an Agent
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#creating-an-agent
## Creating an Agent {#creating-an-agent}

Creating an Agent is simple and accessible to all users:

1. Select the **Chat** tab in the sidebar.
2. Click `Agents` in the left sidebar.
3. Click `Create Agent` to start from scratch, or pick a **pre-built template** as a starting point.
4. Configure the Agent (see [next section](https://docs.mistral.ai/vibe/chat-legacy/agents#configuration)).
5. Test it in the **preview panel** on the right side of the screen.

Agents save automatically as you configure them. There's no save button.

> **Tip**
>
> Templates cover common patterns like summarizers, translators, and code assistants. Start with one and customize it rather than building from scratch.

## section: configuration
    Agents > Configuration
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#configuration
## Configuration {#configuration}

Agent configuration is split into **main settings** and more advanced options. You can always come back and edit these later.

**Main settings**

Every Agent starts with four fields.

- **Name**: use a clear, descriptive name your team can find at a glance. For example, `Customer Support Triage` or `Sales Brief Generator`.
- **Description** (optional): a short explanation of what the Agent does, visible in the Agent picker.
- **Avatar** (optional): choose from presets or generate a custom one.
- **Instructions**: detailed guidance for the Agent's behavior. This is where you define its role, scope, and output format. Type `/` in the field to reference tools and knowledge sources inline.

**Guardrails and tone**

These settings are optional but can **refine how the Agent communicates**.

- **Guardrails**: set boundaries the Agent should respect. For example, *"Always use metric units"* or *"Don't share pricing information outside the approved rate card."*
- **Tone and personality**: expand `Tone` to define the Agent's communication style. A customer-facing Agent might need a warm, professional tone, while an internal code review Agent can be more direct.

**Tools and knowledge**

Agents can be enhanced with **pre-configured tools** and your own **knowledge sources**.

**Tools**

- **[Web search](https://docs.mistral.ai/vibe/work/web-search-open-url)**: retrieve current information from the web.
- **[Code Interpreter](https://docs.mistral.ai/vibe/chat-legacy/code-interpreter)**: run Python for calculations, data analysis, and charts.
- **[Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas)**: generate and edit documents, code, spreadsheets, or presentations.
- **[Image generation](https://docs.mistral.ai/vibe/work/image-generation)**: create images from text descriptions.

**Knowledge**

- **[Libraries](https://docs.mistral.ai/vibe/work/libraries)**: attach one or more Libraries to give the Agent access to your uploaded documents.
- **[Connectors](https://docs.mistral.ai/vibe/work/connectors)**: attach Connectors to pull data from external services like Google Drive, GitHub, or Notion.

## section: starting-conversation
    Agents > Using Agents in Chat > Starting a conversation with an Agent
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#starting-conversation
### Starting a conversation with an Agent {#starting-conversation}

1. Select the **Chat** tab in the sidebar.
2. Click `+` then select `Agents` or type `/` in the message box.

3. Search for or select an Agent. Its name appears at the top of the chat box.
4. Send your message. The Agent responds according to its configuration.

## section: switching-agents
    Agents > Using Agents in Chat > Switching Agents
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#switching-agents
### Switching Agents {#switching-agents}

Click the dropdown arrow next to the Agent name, or repeat the process above, and select a different Agent.

> **Info**
>
> Only **one Agent can be active at a time** within a conversation.

## section: returning-default-model
    Agents > Using Agents in Chat > Returning to the default model
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#returning-default-model
### Returning to the default model {#returning-default-model}

Click the cross icon next to the Agent name to remove it. The conversation continues with the default Vibe model. You can also start a new chat, which always begins with the default model.

## section: writing-instructions
    Agents > Writing effective instructions
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#writing-instructions
## Writing effective instructions {#writing-instructions}

Good instructions make the difference between a generic chatbot and a reliable team tool. Here are a few principles:

- **Define the role clearly.** Start with who the Agent is and what it does: *"You are a code reviewer. Focus on Python best practices, security issues, and performance."*
- **Specify the output format.** Tell the Agent whether you expect bullet points, JSON, prose, a table, or something else. Include a short example if the format matters.
- **Set explicit boundaries.** State what the Agent should not do: *"Don't provide legal advice"* or *"Only reference documents from the attached Library."*
- **Reference tools inline.** Type `/` in the instructions field to mention specific tools or knowledge sources. This tells the Agent when and how to use them.
- **Iterate in small steps.** Change one thing, test in the preview panel, repeat. Getting instructions right is an iterative process.

> **Info**
>
> For a broader introduction to prompt writing techniques, see our [prompt engineering guide](https://docs.mistral.ai/inference/prompting).

## section: sharing
    Agents > Sharing and permissions
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#sharing
## Sharing and permissions {#sharing}

By default, a new Agent is **private** (only you can see and use it).

## section: sharing-specific-people
    Agents > Sharing and permissions > Sharing with specific people
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#sharing-specific-people
### Sharing with specific people {#sharing-specific-people}

1. Open the Agent's card on the `Agents` page.
2. Click the sharing status label (`Private`, `Organization`, or `x people`).
3. Search for users or groups and assign a permission level:
   - **Collaborator**: can use, edit, and delete the Agent.
   - **Viewer**: can use the Agent in their own conversations but can't edit or delete it.

Changes save automatically. Close the modal when you're done.

## section: sharing-organization
    Agents > Sharing and permissions > Sharing with your entire organization
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#sharing-organization
### Sharing with your entire organization {#sharing-organization}

In the same sharing modal, toggle `Entire organization` and choose whether everyone gets Collaborator or Viewer access.

> **Note**
>
> We don't send notifications when you share an Agent. Let your teammates know so they can start using it.

## section: duplicating-agent
    Agents > Managing Agents > Duplicating an Agent
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#duplicating-agent
### Duplicating an Agent {#duplicating-agent}

Open the three-dots menu (`⠇`) on the Agent card and select `Duplicate my Agent`. This creates a new, independent copy you own. Changes to one won't affect the other.

> **Tip**
>
> Duplicating is also the workaround for transferring an Agent to a colleague. Share it as a Collaborator, ask them to duplicate it, then delete the original if needed.

## section: deleting-agent
    Agents > Managing Agents > Deleting an Agent
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#deleting-agent
### Deleting an Agent {#deleting-agent}

1. Open the three-dots menu (`⠇`) on the Agent card.
2. Select `Delete` and confirm.

> **Caution**
>
> Deleting an Agent is permanent and can't be undone. If the Agent was shared, it becomes unavailable to everyone.

> **Note**
>
> Agents are available on all plans. If you change or cancel your subscription, your Agents and their sharing settings are preserved. Some tools or knowledge sources may become unavailable on lower-tier plans.

## section: agents-and-api
    Agents > Agents and the API
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#agents-and-api
## Agents and the API {#agents-and-api}

Agents created in Chat are designed for the chat interface and can't be used programmatically. If you need API access, create Agents through [Agents](https://console.mistral.ai/build/agents) or the [REST API](https://docs.mistral.ai/api/#tag/beta.agents).

Studio Agents can be deployed to Chat and appear in a dedicated section of your Agent list.

## section: related-features
    Agents > Related features
    cite: https://docs.mistral.ai/vibe/chat-legacy/agents#related-features
## Related features {#related-features}

- **[Skills](https://docs.mistral.ai/vibe/work/skills)**: the Vibe Work successor for reusable, specialized behavior.
- **[Custom instructions](https://docs.mistral.ai/vibe/work/custom-instructions)**: set persistent behavior rules that apply to all conversations (Agents override these when active).
- **[Libraries](https://docs.mistral.ai/vibe/work/libraries)**: build knowledge bases from uploaded documents to attach to your Agents.
- **[Connectors](https://docs.mistral.ai/vibe/work/connectors)**: connect external data sources like Google Drive, GitHub, or Notion.
- **[Files and Canvas](https://docs.mistral.ai/vibe/work/files-and-canvas)**: create and edit content collaboratively with AI.
- **[Code Interpreter](https://docs.mistral.ai/vibe/chat-legacy/code-interpreter)**: run Python for data analysis and visualization.
- **[Projects](https://docs.mistral.ai/vibe/work/projects)**: organize conversations into scoped work areas.

Results: 15 sections, the whole page.
```

### 8. mistral_docs_search

```json
{"q": "conversation instructions Work"}
```

Result:

```
q: "conversation instructions Work"

[1] https://docs.mistral.ai/vibe/work/custom-instructions | section: setup
    Set custom instructions > Setting up custom instructions
    1. In the left sidebar, click `Context` then `Instructions`. 2. The Custom instructions pop-up opens. 3. Choose a **Tone** and enter your instructions: describe your role, output format, or any context you want Work to assume. 4. Save your changes. Your instructions take effect in all new tasks from that point on. Existing tasks aren't affected. > **Info** > > Custom instructions are included in t …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#setup

[2] https://docs.mistral.ai/vibe/work/custom-instructions | section: set-custom-instructions
    Set custom instructions
    Custom instructions let you define **persistent preferences** that shape how Work responds across every task. > **Note** > > Think of them as a brief profile you give the assistant: your role, your domain, your preferred output style. Instead of repeating *"I work in compliance"* or *"use metric units"* at the start of each task, you set it once and Work applies it automatically. For teams, custom …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions

[3] https://docs.mistral.ai/vibe/work/custom-instructions | section: what-to-avoid
    Set custom instructions > What to avoid
    Custom instructions work best when they're focused. - **Don't use them as a project brief.** They're meant for persistent preferences, not task descriptions. For task-specific context, use the prompt itself or [Projects](https://docs.mistral.ai/vibe/work/projects). - **Don't contradict your prompts.** If your custom instruction says "always respond in French" but you ask questions in English and e …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#what-to-avoid

[4] https://docs.mistral.ai/vibe/work/custom-instructions | section: interaction-with-other-features
    Set custom instructions > Interactions with other features
    Custom instructions apply alongside other context sources, but their priority depends on the feature. - **[Skills](https://docs.mistral.ai/vibe/work/skills)**: when a Skill is active for a task, its instructions take precedence over your custom instructions. This lets you apply task-specific procedures without conflicting with your general preferences. - **[Projects](https://docs.mistral.ai/vibe/w …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#interaction-with-other-features

[5] https://docs.mistral.ai/vibe/work/get-started | section: repeated-work
    Get started with Work > Make repeated work easier
    After your first tasks, use Vibe settings and reusable context to reduce repeated instructions: | Use case | Feature | |---|---| | Stable preferences such as tone, format, language, or recurring constraints | [Custom instructions](https://docs.mistral.ai/vibe/work/custom-instructions) | | Related work around the same team, customer, initiative, or topic | [Projects](https://docs.mistral.ai/vibe/wo …
    cite: https://docs.mistral.ai/vibe/work/get-started#repeated-work

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/work/custom-instructions") to read hit 1 on its page
```

### 9. mistral_docs_search

```json
{"q": "task instructions Work conversation level"}
```

Result:

```
q: "task instructions Work conversation level"

[1] https://docs.mistral.ai/vibe/work/custom-instructions | section: set-custom-instructions
    Set custom instructions
    Custom instructions let you define **persistent preferences** that shape how Work responds across every task. > **Note** > > Think of them as a brief profile you give the assistant: your role, your domain, your preferred output style. Instead of repeating *"I work in compliance"* or *"use metric units"* at the start of each task, you set it once and Work applies it automatically. For teams, custom …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions

[2] https://docs.mistral.ai/vibe/work/custom-instructions | section: setup
    Set custom instructions > Setting up custom instructions
    1. In the left sidebar, click `Context` then `Instructions`. 2. The Custom instructions pop-up opens. 3. Choose a **Tone** and enter your instructions: describe your role, output format, or any context you want Work to assume. 4. Save your changes. Your instructions take effect in all new tasks from that point on. Existing tasks aren't affected. > **Info** > > Custom instructions are included in t …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#setup

[3] https://docs.mistral.ai/vibe/work/custom-instructions | section: interaction-with-other-features
    Set custom instructions > Interactions with other features
    Custom instructions apply alongside other context sources, but their priority depends on the feature. - **[Skills](https://docs.mistral.ai/vibe/work/skills)**: when a Skill is active for a task, its instructions take precedence over your custom instructions. This lets you apply task-specific procedures without conflicting with your general preferences. - **[Projects](https://docs.mistral.ai/vibe/w …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#interaction-with-other-features

[4] https://docs.mistral.ai/vibe/work/custom-instructions | section: what-to-avoid
    Set custom instructions > What to avoid
    Custom instructions work best when they're focused. - **Don't use them as a project brief.** They're meant for persistent preferences, not task descriptions. For task-specific context, use the prompt itself or [Projects](https://docs.mistral.ai/vibe/work/projects). - **Don't contradict your prompts.** If your custom instruction says "always respond in French" but you ask questions in English and e …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#what-to-avoid

[5] https://docs.mistral.ai/getting-started/quickstarts/vibe-work/first-task | section: verify
    Run your first Vibe Work task > Verify
    You completed your first Work task if: - The conversation appears in your sidebar history. - The todos panel shows steps with checkmarks. - The final answer cites sources you can click through to.
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-work/first-task#verify

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/work/custom-instructions") to read hit 1 on its page
```

### 10. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/work/projects"}
```

Result:

```
page: https://docs.mistral.ai/vibe/work/projects | "Group tasks with Projects"

## section: group-tasks-with-projects
    Group tasks with Projects
    cite: https://docs.mistral.ai/vibe/work/projects
# Group tasks with Projects

Projects let you **group chats** into distinct, manageable collections — and give each group its own tone, instructions, and shared files. Use them to keep context, preferences, and reference material scoped to one initiative: you switch from a client engagement to a launch plan without remixing prompts, re-uploading files, or losing track of past chats.

> **Info**
>
> Projects are available on all plans. Limits may apply to the number of Projects and chats per Project. See our [pricing page](https://mistral.ai/pricing) for details.

## section: creating-a-project
    Group tasks with Projects > Creating a Project
    cite: https://docs.mistral.ai/vibe/work/projects#creating-a-project
## Creating a Project {#creating-a-project}

1. Click the `New Project` button next to the `Projects` header in the left sidebar.
2. Choose a name and an icon for your Project.
3. Click `Create`.

Your new Project appears in the sidebar, ready to receive chats.

## section: project-instructions
    Group tasks with Projects > Project instructions and context
    cite: https://docs.mistral.ai/vibe/work/projects#project-instructions
## Project instructions and context {#project-instructions}

Each Project can carry its own tone, instructions, and shared context that apply to every chat inside it. Open a Project to access these settings:

- **Tone**: pick a tone for this Project, or keep `Default (Global)` to inherit the tone from your account-level [Custom instructions](https://docs.mistral.ai/vibe/work/custom-instructions).
- **Instructions**: click `Customize` to write Project-specific instructions — formatting rules, domain-specific guidance, or any persistent context that should apply to every chat in the Project.
- **Additional context**:
  - **Files**: click `Upload files` to attach documents, spreadsheets, PDFs, or images directly to the Project. Every chat can reference them without re-uploading.
  - **Other chats**: toggle `Include other projects' chats as context` to let Work draw on the other chats in this Project when planning new tasks.

## section: managing-chats
    Group tasks with Projects > Managing chats
    cite: https://docs.mistral.ai/vibe/work/projects#managing-chats
## Managing chats {#managing-chats}

The Project overview page shows all your chats in list or grid view. From there you can add, move, or remove chats.

## section: adding-a-chat
    Group tasks with Projects > Managing chats > Adding a chat
    cite: https://docs.mistral.ai/vibe/work/projects#adding-a-chat
### Adding a chat {#adding-a-chat}

**Drag and drop**

1. Locate the chat in the sidebar.
2. Drag it over the target Project name and release.

**Folder icon**

1. Open the chat.
2. Click the folder icon in the chat header.
3. Select a Project from the dropdown.

## section: moving-a-chat
    Group tasks with Projects > Managing chats > Moving a chat to another Project
    cite: https://docs.mistral.ai/vibe/work/projects#moving-a-chat
### Moving a chat to another Project {#moving-a-chat}

Open the chat, click the folder icon, and select a different Project. The chat moves there automatically.

## section: removing-a-chat
    Group tasks with Projects > Managing chats > Removing a chat
    cite: https://docs.mistral.ai/vibe/work/projects#removing-a-chat
### Removing a chat {#removing-a-chat}

**From the Project overview**

1. Open the Project.
2. Click the three-dots menu on the chat card.
3. Select `Remove from project`.

**From the chat itself**

1. Open the chat.
2. Click the folder icon.
3. Deselect the current Project.

Removing a chat from a Project doesn't delete it. The chat stays in your main chat history and can be reassigned at any time.

> **Note**
>
> A chat can only belong to one Project at a time.

## section: deleting-a-project
    Group tasks with Projects > Deleting a Project
    cite: https://docs.mistral.ai/vibe/work/projects#deleting-a-project
## Deleting a Project {#deleting-a-project}

1. Open the Project.
2. Click the three-dots menu in the top-right corner.
3. Select `Delete` and confirm.

> **Caution**
>
> Deleting a Project is permanent and can't be undone. The chats inside aren't deleted. They return to your main chat history and can be reassigned to another Project.

Results: 8 sections, the whole page.
```

### 11. mistral_docs_search

```json
{"q": "Skills instructions precedence Work"}
```

Result:

```
q: "Skills instructions precedence Work"

[1] https://docs.mistral.ai/vibe/work/custom-instructions | section: interaction-with-other-features
    Set custom instructions > Interactions with other features
    Custom instructions apply alongside other context sources, but their priority depends on the feature. - **[Skills](https://docs.mistral.ai/vibe/work/skills)**: when a Skill is active for a task, its instructions take precedence over your custom instructions. This lets you apply task-specific procedures without conflicting with your general preferences. - **[Projects](https://docs.mistral.ai/vibe/w …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#interaction-with-other-features

[2] https://docs.mistral.ai/vibe/work/skills | section: how-skills-work
    Reuse work with Skills > How Skills work
    Work loads Skills through **progressive disclosure** in three stages: 1. **Discovery**: at session start, Work loads only each Skill's name and description (~100 tokens each), just enough to know when it might be relevant. 2. **Activation**: when a task matches a Skill's description, Work reads the full `SKILL.md` instructions into context. 3. **Execution**: Work follows the instructions, optional …
    cite: https://docs.mistral.ai/vibe/work/skills#how-skills-work

[3] https://docs.mistral.ai/vibe/work/skills | section: reuse-work-with-skills
    Reuse work with Skills
    Skills are **reusable instructions and resources** that give Work specialized capabilities for specific tasks. Use them when a task has a known method, checklist, template, output format, or domain-specific procedure: package an approach once and Work applies it whenever the task matches, with the same tone, format, and procedure every time. > **Info** > > Skills follow the open [Agent Skills](htt …
    cite: https://docs.mistral.ai/vibe/work/skills

[4] https://docs.mistral.ai/vibe/work/skills | section: create-from-ui
    Reuse work with Skills > Creating a Skill > Create from the editor
    1. Open `Context` > `Skills` in the sidebar. 2. Click `New Skill`. 3. Fill in the form: - **Title**: a short, descriptive name (for example, `Brand voice copywriting`). - **Description**: when Work should use this Skill. This text is what Work reads at discovery to decide whether to activate the Skill, so make it specific. - **SKILL.md**: the full instructions Work follows when the Skill activates …
    cite: https://docs.mistral.ai/vibe/work/skills#create-from-ui

[5] https://docs.mistral.ai/vibe/work/custom-instructions | section: setup
    Set custom instructions > Setting up custom instructions
    1. In the left sidebar, click `Context` then `Instructions`. 2. The Custom instructions pop-up opens. 3. Choose a **Tone** and enter your instructions: describe your role, output format, or any context you want Work to assume. 4. Save your changes. Your instructions take effect in all new tasks from that point on. Existing tasks aren't affected. > **Info** > > Custom instructions are included in t …
    cite: https://docs.mistral.ai/vibe/work/custom-instructions#setup

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/work/custom-instructions") to read hit 1 on its page
```

## Answer

Yes, you can set **Custom Instructions** on a conversation, but when an **Agent** is active, **its instructions take precedence** over your Custom Instructions.

### How it works in Work:
- **Custom Instructions** apply globally to all your tasks/conversations as persistent preferences (tone, role, formatting, etc.) custom instructions > Setting up custom instructions.
- **Agents** override Custom Instructions when active in a conversation. This is explicitly stated: *"Agents override these when active"* > Related features.
- **Projects** can also have their own instructions, which apply to all chats within them alongside other context tasks with Projects > Project instructions and context.
- **Skills** similarly take precedence over Custom Instructions when activated for a task custom instructions > Interactions with other features.

### Practical implication:
If you start a conversation with an Agent, the Agent's instructions will be used instead of your Custom Instructions. If you want the Agent to follow additional rules, you should include them in the **Agent's own instructions** rather than relying on Custom Instructions.

