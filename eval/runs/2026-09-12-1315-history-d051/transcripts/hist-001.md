# hist-001 (history, 2 connector calls)

## Question

When did the Vibe Code CLI configuration page start listing GLM 5.2 (`zai-glm-5-2`) among the models available through Mistral's API?

## Thinking

The user is asking about when a specific model (GLM 5.2, identified as `zai-glm-5-2`) started appearing in the Vibe Code CLI configuration page's list of available models through Mistral's API. This is a historical question about documentation changes.

I need to:
1. First find the Vibe Code CLI configuration page in Mistral's documentation
2. Then check the history of that page to see when `zai-glm-5-2` was added

Let me start by searching for the Vibe Code CLI configuration page.

The search results show that the Vibe Code CLI configuration page is at `https://docs.mistral.ai/vibe/code/cli/configuration`. The second hit mentions "Providers and models" section which seems to list the models available through Mistral's API.

Now I need to check the history of this page to see when `zai-glm-5-2` was added. Let me use the history tool to track changes to this specific page.

The history tool shows that the "Providers and models" section of the Vibe Code CLI configuration page changed between 2026-08-15 and 2026-09-01. The diff shows that `zai-glm-5-2` (Z.ai GLM 5.2) was added in this change.

The key information is:
- The change occurred between 2026-08-15 and 2026-09-01
- The model `zai-glm-5-2` (Z.ai GLM 5.2) was added in this update

The history shows the interval when the change was made. Since the documentation snapshots are stored at specific dates, and the change appears between 2026-08-15 and 2026-09-01, this is the interval when `zai-glm-5-2` started being listed.

The answer should be the interval: between August 15, 2026 and September 1, 2026.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Vibe Code CLI configuration page models available through Mistral's API", "max_hits": 5}
```

Result:

```
q: "Vibe Code CLI configuration page models available through Mistral's API"

[1] https://docs.mistral.ai/vibe/code/cli/configuration | section: configuration
    Configuration
    The Vibe Code CLI is configured through a **`config.toml` file**. This page explains where the file lives, how to open it, and the most common settings you'll touch. > **Info** > > For an exhaustive list of every key in `config.toml` and the agent-definition files, see the [Configuration reference](https://docs.mistral.ai/vibe/code/cli/configuration-reference).
    cite: https://docs.mistral.ai/vibe/code/cli/configuration

[2] https://docs.mistral.ai/vibe/code/cli/configuration | section: providers-models
    Configuration > Common configuration sections > Providers and models
    Define provider presets, model presets, and the active model. The following chat-capable models are available through Mistral's API (la Plateforme). Use the **model ID** as the `name` value in a `[[models]]` block, or pass it directly with `--model`: | Model | Model ID | Best for | |---|---|---| | Mistral Medium 3.5 (recommended) | `mistral-medium-latest` | Flagship reasoning and code | | Z.ai GLM …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#providers-models

[3] https://docs.mistral.ai/vibe/code/vs-code-extension/settings | section: shared-vibe-configuration
    Extension settings > Shared Vibe configuration
    The extension runs the Vibe ACP agent. **Agent-level behavior** (models, providers, tools, agents, skills, and MCP servers) follows the shared Vibe configuration model. Use the CLI configuration docs for the shared format: - **[Configuration](https://docs.mistral.ai/vibe/code/cli/configuration)**: full `config.toml` reference. - **[API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-k …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/settings#shared-vibe-configuration

[4] https://docs.mistral.ai/vibe/code/cli/configuration-reference | section: configuration-reference
    Configuration reference
    An exhaustive index of every key accepted by `config.toml` and the agent-definition files. Keys are grouped by section, each linking to the page that explains the concept in depth. Use this as a lookup; use [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) to learn how the file works.
    cite: https://docs.mistral.ai/vibe/code/cli/configuration-reference

[5] https://docs.mistral.ai/vibe/code/overview | section: vibe-code
    Vibe Code
    Vibe Code is Vibe's **coding mode**. With read/write access to your filesystem, a shell, and a configurable set of tools, it can read files, run commands, write code, and open pull requests on your behalf, under your supervision. Run Vibe Code against a local checkout via the [CLI](https://docs.mistral.ai/vibe/code/cli/install-setup) or the [VS Code extension](https://docs.mistral.ai/vibe/code/vs- …
    cite: https://docs.mistral.ai/vibe/code/overview

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/configuration") to read hit 1 on its page
```

### 2. mistral_docs_history

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

The Vibe Code CLI configuration page started listing **GLM 5.2** (`zai-glm-5-2`) among the models available through Mistral's API **between August 15, 2026 and September 1, 2026**.

This is based on the documented change in the [Providers and models](https://docs.mistral.ai/vibe/code/cli/configuration#providers-models) section, where the model table was introduced and included `zai-glm-5-2` as a new entry.

