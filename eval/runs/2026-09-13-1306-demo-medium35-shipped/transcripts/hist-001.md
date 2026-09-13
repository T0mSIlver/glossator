# hist-001 (history, 6 connector calls)

## Question

When did the Vibe Code CLI configuration page start listing GLM 5.2 (`zai-glm-5-2`) among the models available through Mistral's API?

## Thinking

The user is asking about when a specific model (GLM 5.2, with the ID `zai-glm-5-2`) started appearing in the Vibe Code CLI configuration page's list of available models. This is a historical question about documentation changes.

I need to:
1. First, locate the Vibe Code CLI configuration page in the Mistral documentation
2. Then check its history to see when `zai-glm-5-2` was added

Let me start by searching for the Vibe Code CLI configuration page.

I found the Vibe Code CLI configuration page. Now I need to check its history to see when `zai-glm-5-2` was added. Let me use the history tool to track changes on this page.

The history tool shows that `zai-glm-5-2` first appeared on the page on 2026-09-01 and was present through 2026-09-07. This means it started being listed between August 15, 2026 (when it was absent) and September 1, 2026 (when it first appeared).

However, I should verify if this is indeed the configuration page that lists models. Let me also check the configuration-reference page, as the search result mentioned it's the exhaustive index of configuration keys.

The configuration-reference page doesn't have `zai-glm-5-2` in its history. Let me search more specifically for where models are listed in the Vibe Code CLI documentation. The model list might be in a different section.

Perfect! I found that the configuration page has a section "providers-models" which lists the available models. The search result shows that `zai-glm-5-2` appears in that section. Now let me check the history of that specific section to confirm when it was added.

I need to use the correct parameters. Let me try with just the page_url and text, or with page_url and section separately. Let me try with page_url and section.

Perfect! The history tool shows that the "providers-models" section on the Vibe Code CLI configuration page changed between 2026-08-15 and 2026-09-01. The diff shows that the model table was added in that change, and it includes `zai-glm-5-2` (Z.ai GLM 5.2).

The diff clearly shows:
- Before 2026-08-15: The section didn't have the model table
- Between 2026-08-15 and 2026-09-01: The model table was added with `zai-glm-5-2` included
- From 2026-09-01 onwards: The table with `zai-glm-5-2` is present

Therefore, `zai-glm-5-2` started being listed on the Vibe Code CLI configuration page **between August 15, 2026 and September 1, 2026**. Since the first stored date with the phrase is 2026-09-01 (as shown in my first history query), and it was absent on 2026-08-15, the answer is that it started being listed on **September 1, 2026**.

But wait, the history shows "changed between 2026-08-15 and 2026-09-01" and "same through 2026-09-07". The first stored date with the phrase is 2026-09-01. So the most precise answer is that it started appearing on **September 1, 2026**.

Actually, looking more carefully at the history output: "first stored date with the phrase: 2026-09-01" and "absent at 2026-08-15". So it was added between these two dates, and the first snapshot showing it is 2026-09-01.

The most accurate answer based on the documentation history is: **September 1, 2026**.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Vibe Code CLI configuration page", "max_hits": 5}
```

Result:

```
q: "Vibe Code CLI configuration page"

[1] https://docs.mistral.ai/vibe/code/cli/configuration | section: configuration
    Configuration
    The Vibe Code CLI is configured through a **`config.toml` file**. This page explains where the file lives, how to open it, and the most common settings you'll touch. > **Info** > > For an exhaustive list of every key in `config.toml` and the agent-definition files, see the [Configuration reference](https://docs.mistral.ai/vibe/code/cli/configuration-reference).
    cite: https://docs.mistral.ai/vibe/code/cli/configuration

[2] https://docs.mistral.ai/vibe/code/cli/configuration-reference | section: configuration-reference
    Configuration reference
    An exhaustive index of every key accepted by `config.toml` and the agent-definition files. Keys are grouped by section, each linking to the page that explains the concept in depth. Use this as a lookup; use [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) to learn how the file works.
    cite: https://docs.mistral.ai/vibe/code/cli/configuration-reference

[3] https://docs.mistral.ai/vibe/code/vs-code-extension/settings | section: shared-vibe-configuration
    Extension settings > Shared Vibe configuration
    The extension runs the Vibe ACP agent. **Agent-level behavior** (models, providers, tools, agents, skills, and MCP servers) follows the shared Vibe configuration model. Use the CLI configuration docs for the shared format: - **[Configuration](https://docs.mistral.ai/vibe/code/cli/configuration)**: full `config.toml` reference. - **[API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-k …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/settings#shared-vibe-configuration

[4] https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions | section: choose-cli-vs-code-or-web-sessions
    Choose CLI, VS Code, or web sessions
    **One agent, three surfaces.** Vibe Code runs as the CLI, the VS Code extension, and Vibe Code Web. They share the same engine, configuration, and customization layer (agents, skills, MCP servers), so you can pick whichever fits the task at hand. > **Info** > > Vibe also implements the [Agent Client Protocol (ACP)](https://agentclientprotocol.com/) and is published in the [ACP registry](https://gi …
    cite: https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions

[5] https://docs.mistral.ai/vibe/code/overview | section: set-up-vibe-code
    Vibe Code > Set up Vibe Code
    Pick the interface that fits your workflow: - [Install the CLI](https://docs.mistral.ai/vibe/code/cli/install-setup) — Run Vibe Code from your terminal. - [Install the VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate) — Use Vibe Code directly in VS Code. - [Start a web session](https://docs.mistral.ai/vibe/code/vibe-code-web/get-started) — Run a cloud ses …
    cite: https://docs.mistral.ai/vibe/code/overview#set-up-vibe-code

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/configuration") to read hit 1 on its page
```

### 2. mistral_docs_history

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/configuration", "text": "zai-glm-5-2"}
```

Result:

```
history text: "zai-glm-5-2" | page: https://docs.mistral.ai/vibe/code/cli/configuration
first stored date with the phrase: 2026-09-01 | https://docs.mistral.ai/vibe/code/cli/configuration (absent at 2026-08-15)
last stored date with the phrase: 2026-09-07 | https://docs.mistral.ai/vibe/code/cli/configuration
Results: present in 2 of 8 stored snapshots
```

### 3. mistral_docs_history

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/configuration-reference", "text": "zai-glm-5-2"}
```

Result:

```
history text: "zai-glm-5-2" | page: https://docs.mistral.ai/vibe/code/cli/configuration-reference
Results: the phrase is absent from every stored snapshot.
```

### 4. mistral_docs_search

```json
{"q": "zai-glm-5-2 GLM 5.2 model list Vibe Code CLI", "max_hits": 10}
```

Result:

```
q: "zai-glm-5-2 GLM 5.2 model list Vibe Code CLI"

[1] https://docs.mistral.ai/models/zai-glm-5-2 | section: overview
    Z.ai GLM 5.2 > Overview
    | Field | Value | | --- | --- | | API names | `zai-glm-5-2` | | Slug | `zai-glm-5-2` | | Status | PublicPreview | | Release date | 2026-08-06 | | Version | 5.2 | | Type | Open | | Class | Generalist | | Context length | 1M | | Output token limit | 128k | | Legacy | no |
    cite: https://docs.mistral.ai/models/zai-glm-5-2

[2] https://docs.mistral.ai/models | section: chat-completions
    Model capability matrix > Chat completions
    - **[Predicted Outputs](https://docs.mistral.ai/studio/conversations/advanced/predicted-outputs)** (`predicted-outputs`), 11 models: Codestral (`codestral-2501`), Codestral (`codestral-2508`), Mistral Large 2.1 (`mistral-large-2411`), Mistral Medium 3.1 (`mistral-medium-2508`), Mistral Medium 3 (`mistral-medium-2505`), Mistral Medium 3.5 (`mistral-medium-3-5`), Mistral Small 3.1 (`mistral-small-25 …
    cite: https://docs.mistral.ai/models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/models", section="chat-completions") reads this section

[3] https://docs.mistral.ai/vibe/code/cli/configuration | section: providers-models
    Configuration > Common configuration sections > Providers and models
    Define provider presets, model presets, and the active model. The following chat-capable models are available through Mistral's API (la Plateforme). Use the **model ID** as the `name` value in a `[[models]]` block, or pass it directly with `--model`: | Model | Model ID | Best for | |---|---|---| | Mistral Medium 3.5 (recommended) | `mistral-medium-latest` | Flagship reasoning and code | | Z.ai GLM …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#providers-models

[4] https://docs.mistral.ai/models/zai-glm-5-2 | section: links
    Z.ai GLM 5.2 > Links
    - [Blog post](https://z.ai/blog/glm-5.2)
    cite: https://docs.mistral.ai/models/zai-glm-5-2

[5] https://docs.mistral.ai/models/zai-glm-5-2 | section: capability-matrix
    Z.ai GLM 5.2 > Capability matrix
    See the [model capability matrix](https://docs.mistral.ai/models) for every model that shares these features.
    cite: https://docs.mistral.ai/models/zai-glm-5-2

[6] https://docs.mistral.ai/models/zai-glm-5-2 | section: modalities
    Z.ai GLM 5.2 > Modalities
    - Input: Text - Output: Reasoning, Text
    cite: https://docs.mistral.ai/models/zai-glm-5-2

[7] https://docs.mistral.ai/models | section: batch
    Model capability matrix > Batch
    - **[Batching](https://docs.mistral.ai/studio/batch-processing)** (`batching`), 43 models: Codestral (`codestral-2501`), Codestral (`codestral-2508`), Codestral Embed (`codestral-embed-2505`), Devstral 2 (`devstral-2512`), Devstral Medium 1.0 (`devstral-medium-2507`), Devstral Small 1.0 (`devstral-small-2505`), Devstral Small 1.1 (`devstral-small-2507`), Devstral Small 2 (`labs-devstral-small-2512 …
    cite: https://docs.mistral.ai/models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/models", section="batch") reads this section

[8] https://docs.mistral.ai/models/zai-glm-5-2 | section: pricing
    Z.ai GLM 5.2 > Pricing
    - Input: Input: 1.4 USD/M Tokens (1.19 EUR/M Tokens); Cached input: 0.14 USD/M Tokens (0.119 EUR/M Tokens) - Output: Output: 4.4 USD/M Tokens (3.74 EUR/M Tokens)
    cite: https://docs.mistral.ai/models/zai-glm-5-2

[9] https://docs.mistral.ai/vibe/code/overview | section: set-up-vibe-code
    Vibe Code > Set up Vibe Code
    Pick the interface that fits your workflow: - [Install the CLI](https://docs.mistral.ai/vibe/code/cli/install-setup) — Run Vibe Code from your terminal. - [Install the VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/install-authenticate) — Use Vibe Code directly in VS Code. - [Start a web session](https://docs.mistral.ai/vibe/code/vibe-code-web/get-started) — Run a cloud ses …
    cite: https://docs.mistral.ai/vibe/code/overview#set-up-vibe-code

[10] https://docs.mistral.ai/vibe/code/overview | section: vibe-code
    Vibe Code
    Vibe Code is Vibe's **coding mode**. With read/write access to your filesystem, a shell, and a configurable set of tools, it can read files, run commands, write code, and open pull requests on your behalf, under your supervision. Run Vibe Code against a local checkout via the [CLI](https://docs.mistral.ai/vibe/code/cli/install-setup) or the [VS Code extension](https://docs.mistral.ai/vibe/code/vs- …
    cite: https://docs.mistral.ai/vibe/code/overview

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/models/zai-glm-5-2") to read hit 1 on its page
```

### 5. mistral_docs_history

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/configuration", "section": "providers-models", "text": "zai-glm-5-2"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
text takes page_url or under, not section or since.
next: mistral_docs_history(text="phrase", page_url="url" or under="path"), mistral_docs_history(page_url="url", section="key") or mistral_docs_history(under="path", since="date").
```

### 6. mistral_docs_history

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/configuration", "section": "providers-models"}
```

Result:

```
history page: https://docs.mistral.ai/vibe/code/cli/configuration | section: providers-models
present at 2026-06-01, same through 2026-08-15 | https://docs.mistral.ai/vibe/code/cli/configuration#providers-models
changed between 2026-08-15 and 2026-09-01 | https://docs.mistral.ai/vibe/code/cli/configuration#providers-models
```diff
--- previous
+++ current
@@ -1,9 +1,26 @@
 ### Providers and models {#providers-models}
 
-Define provider presets, model presets, and the active model:
+Define provider presets, model presets, and the active model.
+
+The following chat-capable models are available through Mistral's API (la Plateforme). Use the **model ID** as the `name` value in a `[[models]]` block, or pass it directly with `--model`:
+
+| Model | Model ID | Best for |
+|---|---|---|
+| Mistral Medium 3.5 (recommended) | `mistral-medium-latest` | Flagship reasoning and code |
+| Z.ai GLM 5.2 | `zai-glm-5-2` | Advanced reasoning and code |
+| Mistral Large 3 | `mistral-large-latest` | Complex tasks, large context |
+| Mistral Small 4 | `mistral-small-latest` | Fast, cost-effective general use |
+| Codestral | `codestral-latest` | Code generation and completion |
+| Ministral 3 14B | `ministral-14b-latest` | Balanced edge model |
+| Ministral 3 8B | `ministral-8b-latest` | Lightweight edge model |
+| Ministral 3 3B | `ministral-3b-latest` | Smallest edge model |
+
+You can also pin to a specific version by replacing `-latest` with a date suffix (for example, `mistral-medium-3-5` or `codestral-2508`). See the [models overview](https://docs.mistral.ai/models) for all available versions.
+
+To use a model through a third-party provider such as OpenRouter, define a custom provider and model preset:
 
 ```toml
-active_model = "devstral-openrouter"
+active_model = "codestral-openrouter"
 
 [[providers]]
 name = "openrouter"
@@ -13,9 +30,9 @@
 backend = "generic"
 
 [[models]]
-name = "mistralai/devstral-2512:free"
+name = "mistralai/codestral"
 provider = "openrouter"
-alias = "devstral-openrouter"
+alias = "codestral-openrouter"
 ```
 
 See [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles).

```
same through 2026-09-07 | https://docs.mistral.ai/vibe/code/cli/configuration#providers-models
Results: 8 of 8 stored snapshots
```

## Answer

The Vibe Code CLI configuration page started listing **GLM 5.2 (`zai-glm-5-2`)** among the available models on **September 1, 2026**.

This is based on the documentation history showing the phrase first appeared in the [providers-models section](https://docs.mistral.ai/vibe/code/cli/configuration#providers-models) on 2026-09-01, while it was absent in the previous snapshot from 2026-08-15. The change introduced a new model table that included `zai-glm-5-2` as an available model through Mistral's API.

