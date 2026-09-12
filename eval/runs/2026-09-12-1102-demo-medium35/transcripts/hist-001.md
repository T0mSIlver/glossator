# hist-001 (history, 5 connector calls)

## Question

When did the Vibe Code CLI configuration page start listing GLM 5.2 (`zai-glm-5-2`) among the models available through Mistral's API?

## Thinking

The user is asking about when a specific model (GLM 5.2, identified as `zai-glm-5-2`) first appeared in the Vibe Code CLI configuration page's list of available models. This is a historical question about documentation changes.

I need to:
1. First find the Vibe Code CLI configuration page in the Mistral documentation
2. Then check its history to see when `zai-glm-5-2` was added

Let me start by searching for the Vibe Code CLI configuration page.

The search results show that the Vibe Code CLI configuration page is at `https://docs.mistral.ai/vibe/code/cli/configuration`. Hit [4] specifically mentions the "Providers and models" section which lists models available through Mistral's API. This is likely where `zai-glm-5-2` would be listed.

Now I need to:
1. Read the current configuration page to confirm it's the right place
2. Check the history of that page (or specifically the providers-models section) to see when `zai-glm-5-2` was added

Let me first read the page to understand its structure, then check its history.

Good, I can see that the current page does list `zai-glm-5-2` (Z.ai GLM 5.2) in the models table. Now I need to find out when this was added. I should check the history of this specific section on the configuration page.

Let me use the mistral_docs_history tool to track when "zai-glm-5-2" first appeared in the configuration page.

I made an error - the tool requires exactly one of text, page_url, or under. Let me try again with just the text parameter to find when "zai-glm-5-2" first appeared in the documentation.

Interesting - the history shows that "zai-glm-5-2" first appeared on 2026-08-15, but it was on the page `https://docs.mistral.ai/models/zai-glm-5-2`, not on the Vibe Code CLI configuration page. This suggests the model was added to the models documentation first.

Now I need to check specifically when it appeared on the Vibe Code CLI configuration page. Let me check the history of that specific page.

Perfect! The history shows that the `providers-models` section of the Vibe Code CLI configuration page changed between 2026-08-15 and 2026-09-01. The diff clearly shows that `zai-glm-5-2` (Z.ai GLM 5.2) was added in that change, along with the entire models table.

The change occurred between August 15, 2026 and September 1, 2026. Since the history shows it was "present at 2026-06-01, same through 2026-08-15" and then "changed between 2026-08-15 and 2026-09-01", the addition happened sometime after August 15, 2026 and before or on September 1, 2026.

The most precise answer I can give is that it was added between August 15 and September 1, 2026. However, looking at the snapshot dates, it seems the change was captured in the September 1, 2026 snapshot, so the addition likely happened on or before September 1, 2026.

But the question asks "when did it start listing" - the history shows it first appears in the snapshot taken after September 1, 2026. So the answer would be that it started being listed on September 1, 2026 (or the change was made between August 15 and September 1, with September 1 being the first snapshot showing it).

Let me verify if there's a more precise date. The history shows:
- Last snapshot before change: 2026-08-15
- First snapshot with the change: 2026-09-01

So the change was made between these dates. The most accurate answer is that it started being listed on **September 1, 2026** (the date of the first snapshot where it appears).

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Vibe Code CLI configuration page models available", "max_hits": 5}
```

Result:

```
q: "Vibe Code CLI configuration page models available"

[1] https://docs.mistral.ai/vibe/code/cli/configuration | section: configuration
    Configuration
    The Vibe Code CLI is configured through a **`config.toml` file**. This page explains where the file lives, how to open it, and the most common settings you'll touch. > **Info** > > For an exhaustive list of every key in `config.toml` and the agent-definition files, see the [Configuration reference](https://docs.mistral.ai/vibe/code/cli/configuration-reference).
    cite: https://docs.mistral.ai/vibe/code/cli/configuration

[2] https://docs.mistral.ai/vibe/code/vs-code-extension/settings | section: shared-vibe-configuration
    Extension settings > Shared Vibe configuration
    The extension runs the Vibe ACP agent. **Agent-level behavior** (models, providers, tools, agents, skills, and MCP servers) follows the shared Vibe configuration model. Use the CLI configuration docs for the shared format: - **[Configuration](https://docs.mistral.ai/vibe/code/cli/configuration)**: full `config.toml` reference. - **[API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-k …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/settings#shared-vibe-configuration

[3] https://docs.mistral.ai/vibe/code/cli/configuration-reference | section: configuration-reference
    Configuration reference
    An exhaustive index of every key accepted by `config.toml` and the agent-definition files. Keys are grouped by section, each linking to the page that explains the concept in depth. Use this as a lookup; use [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) to learn how the file works.
    cite: https://docs.mistral.ai/vibe/code/cli/configuration-reference

[4] https://docs.mistral.ai/vibe/code/cli/configuration | section: providers-models
    Configuration > Common configuration sections > Providers and models
    Define provider presets, model presets, and the active model. The following chat-capable models are available through Mistral's API (la Plateforme). Use the **model ID** as the `name` value in a `[[models]]` block, or pass it directly with `--model`: | Model | Model ID | Best for | |---|---|---| | Mistral Medium 3.5 (recommended) | `mistral-medium-latest` | Flagship reasoning and code | | Z.ai GLM …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#providers-models

[5] https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions | section: choose-cli-vs-code-or-web-sessions
    Choose CLI, VS Code, or web sessions
    **One agent, three surfaces.** Vibe Code runs as the CLI, the VS Code extension, and Vibe Code Web. They share the same engine, configuration, and customization layer (agents, skills, MCP servers), so you can pick whichever fits the task at hand. > **Info** > > Vibe also implements the [Agent Client Protocol (ACP)](https://agentclientprotocol.com/) and is published in the [ACP registry](https://gi …
    cite: https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/configuration") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/configuration", "section": "providers-models"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/configuration | "Configuration" | section: providers-models

## section: providers-models
    Configuration > Common configuration sections > Providers and models
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#providers-models
### Providers and models {#providers-models}

Define provider presets, model presets, and the active model.

The following chat-capable models are available through Mistral's API (la Plateforme). Use the **model ID** as the `name` value in a `[[models]]` block, or pass it directly with `--model`:

| Model | Model ID | Best for |
|---|---|---|
| Mistral Medium 3.5 (recommended) | `mistral-medium-latest` | Flagship reasoning and code |
| Z.ai GLM 5.2 | `zai-glm-5-2` | Advanced reasoning and code |
| Mistral Large 3 | `mistral-large-latest` | Complex tasks, large context |
| Mistral Small 4 | `mistral-small-latest` | Fast, cost-effective general use |
| Codestral | `codestral-latest` | Code generation and completion |
| Ministral 3 14B | `ministral-14b-latest` | Balanced edge model |
| Ministral 3 8B | `ministral-8b-latest` | Lightweight edge model |
| Ministral 3 3B | `ministral-3b-latest` | Smallest edge model |

You can also pin to a specific version by replacing `-latest` with a date suffix (for example, `mistral-medium-3-5` or `codestral-2508`). See the [models overview](https://docs.mistral.ai/models) for all available versions.

To use a model through a third-party provider such as OpenRouter, define a custom provider and model preset:

```toml
active_model = "codestral-openrouter"

[[providers]]
name = "openrouter"
api_base = "https://openrouter.ai/api/v1"
api_key_env_var = "OPENROUTER_API_KEY"
api_style = "openai"
backend = "generic"

[[models]]
name = "mistralai/codestral"
provider = "openrouter"
alias = "codestral-openrouter"
```

See [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles).

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/configuration", section="mcp-servers") for the section after it
```

### 3. mistral_docs_history

```json
{"text": "zai-glm-5-2", "page_url": "https://docs.mistral.ai/vibe/code/cli/configuration", "section": "providers-models"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
history takes exactly one of text, page_url or under.
next: mistral_docs_history(text="phrase"), mistral_docs_history(page_url="url", section="key") or mistral_docs_history(under="path", since="date").
```

### 4. mistral_docs_history

```json
{"text": "zai-glm-5-2"}
```

Result:

```
history text: "zai-glm-5-2"
first stored date with the phrase: 2026-08-15 | https://docs.mistral.ai/models/zai-glm-5-2
last stored date with the phrase: 2026-09-07 | https://docs.mistral.ai/models/zai-glm-5-2
Results: present in 3 of 8 stored snapshots
```

### 5. mistral_docs_history

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

The Vibe Code CLI configuration page started listing **GLM 5.2 (`zai-glm-5-2`)** in its **Providers and models** section between **August 15, 2026** and **September 1, 2026**. The change was first captured in the documentation snapshot on **September 1, 2026**, where the model appears in the table of available models through Mistral's API.

[Providers and models section history](https://docs.mistral.ai/vibe/code/cli/configuration#providers-models)

