# hist-001 (history, 11 connector calls)

## Question

When did the Vibe Code CLI configuration page start listing GLM 5.2 (`zai-glm-5-2`) among the models available through Mistral's API?

## Thinking

The user is asking about when a specific model (GLM 5.2, also known as zai-glm-5-2) started appearing in the Vibe Code CLI configuration page's list of available models. This is a historical question about documentation changes.

I need to:
1. First find the Vibe Code CLI configuration page in Mistral's documentation
2. Then check its history to see when GLM 5.2 was added

Let me start by searching for the Vibe Code CLI configuration page.

Good, I found the Vibe Code CLI configuration page at `https://docs.mistral.ai/vibe/code/cli/configuration`. Now I need to check its history to see when GLM 5.2 (`zai-glm-5-2`) was added. Let me use the history tool to track changes on this page.

I need to use the correct parameters. Let me try with just the text parameter to find when "zai-glm-5-2" first appeared in the documentation.

The history shows that "zai-glm-5-2" first appeared on 2026-08-15 in the models documentation. But the user is specifically asking about the Vibe Code CLI configuration page, not the models page. Let me search more specifically for where models are listed in the CLI configuration.

Let me search for model listings in the CLI configuration or related pages.

Perfect! I found a section in the Vibe Code CLI configuration page that lists models available through Mistral's API. The section is `providers-models` and it mentions "Z.ai GLM" which is likely where GLM 5.2 would be listed. Let me read this page to see the current content and then track its history.

Great! I can see that the current version of the page does list "Z.ai GLM 5.2" with model ID `zai-glm-5-2` in the table. Now I need to find out when this was added. Let me check the history of this specific section on the configuration page.

Perfect! The history shows that the `providers-models` section changed between 2026-08-15 and 2026-09-01. The diff shows that the table with models (including Z.ai GLM 5.2 with model ID `zai-glm-5-2`) was added in this change.

The change occurred between 2026-08-15 and 2026-09-01. Since the history shows it was present at 2026-08-15 in the models documentation but the CLI configuration page changed between 2026-08-15 and 2026-09-01, the most precise answer is that it started appearing **between August 15, 2026 and September 1, 2026**.

However, looking more carefully at the history output: it says "changed between 2026-08-15 and 2026-09-01" and then "same through 2026-09-07". This means the change was made sometime after August 15 and before September 1, and it remained the same through September 7.

So the answer is: **between August 15, 2026 and September 1, 2026**.

But wait, let me check if there's a more precise date. The history shows snapshots at specific dates. The change happened between two snapshots: one on or before 2026-08-15, and the next on or after 2026-09-01. So the earliest it could have appeared is August 16, 2026, and the latest is August 31, 2026.

Actually, re-reading the history output more carefully:
- "present at 2026-06-01, same through 2026-08-15" - this means the section existed from June 1 to August 15
- "changed between 2026-08-15 and 2026-09-01" - this means the change occurred after August 15 and before September 1
- "same through 2026-09-07" - this means it stayed the same from the change date through September 7

So the GLM 5.2 model was added to the Vibe Code CLI configuration page's model list **between August 15, 2026 and September 1, 2026**.

Since the user asks for when it "started listing", the most accurate answer based on the documentation history is that it was added in the period between August 15 and September 1, 2026. The exact date would be sometime in that window, but we can only narrow it down to that range based on the snapshot dates.

Let me verify if there's any more precise information by checking the models page history as well.

Let me try with just the text parameter again for the models page.

The tool requires exactly one of the parameters. Let me try with just the `under` parameter to see the history of the models path.

The history shows that under the models path, there were changes between 2026-08-15 and 2026-09-01 (2 changed). But I need to find specifically when the zai-glm-5-2 model page was added. Let me search for that specific model page.

Good! I found that the model page for zai-glm-5-2 exists and shows a release date of 2026-08-06. Now let me check the history of this specific model page to see when it was added to the documentation.

Perfect! Now I have the key information:

1. The zai-glm-5-2 model page was **added between 2026-08-01 and 2026-08-15** to the models documentation.
2. The Vibe Code CLI configuration page's `providers-models` section was **changed between 2026-08-15 and 2026-09-01**, and this change added the model table including Z.ai GLM 5.2 with model ID `zai-glm-5-2`.

So the answer is: The Vibe Code CLI configuration page started listing GLM 5.2 (`zai-glm-5-2`) **between August 15, 2026 and September 1, 2026**.

The model itself was added to Mistral's API/models documentation between August 1 and August 15, 2026, but it specifically appeared in the Vibe Code CLI configuration page's model list between August 15 and September 1, 2026.

Since the user asks specifically about when the **Vibe Code CLI configuration page** started listing it, the answer is the latter date range.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "Vibe Code CLI configuration page"}
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
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
history takes exactly one of text, page_url or under.
next: mistral_docs_history(text="phrase"), mistral_docs_history(page_url="url", section="key") or mistral_docs_history(under="path", since="date").
```

### 3. mistral_docs_history

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

### 4. mistral_docs_search

```json
{"q": "models available through Mistral's API Vibe Code CLI configuration"}
```

Result:

```
q: "models available through Mistral's API Vibe Code CLI configuration"

[1] https://docs.mistral.ai/vibe/code/cli/configuration | section: providers-models
    Configuration > Common configuration sections > Providers and models
    Define provider presets, model presets, and the active model. The following chat-capable models are available through Mistral's API (la Plateforme). Use the **model ID** as the `name` value in a `[[models]]` block, or pass it directly with `--model`: | Model | Model ID | Best for | |---|---|---| | Mistral Medium 3.5 (recommended) | `mistral-medium-latest` | Flagship reasoning and code | | Z.ai GLM …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#providers-models

[2] https://docs.mistral.ai/vibe/code/cli/configuration | section: configuration
    Configuration
    The Vibe Code CLI is configured through a **`config.toml` file**. This page explains where the file lives, how to open it, and the most common settings you'll touch. > **Info** > > For an exhaustive list of every key in `config.toml` and the agent-definition files, see the [Configuration reference](https://docs.mistral.ai/vibe/code/cli/configuration-reference).
    cite: https://docs.mistral.ai/vibe/code/cli/configuration

[3] https://docs.mistral.ai/vibe/code/vs-code-extension/settings | section: shared-vibe-configuration
    Extension settings > Shared Vibe configuration
    The extension runs the Vibe ACP agent. **Agent-level behavior** (models, providers, tools, agents, skills, and MCP servers) follows the shared Vibe configuration model. Use the CLI configuration docs for the shared format: - **[Configuration](https://docs.mistral.ai/vibe/code/cli/configuration)**: full `config.toml` reference. - **[API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-k …
    cite: https://docs.mistral.ai/vibe/code/vs-code-extension/settings#shared-vibe-configuration

[4] https://docs.mistral.ai/vibe/code/overview | section: vibe-code
    Vibe Code
    Vibe Code is Vibe's **coding mode**. With read/write access to your filesystem, a shell, and a configurable set of tools, it can read files, run commands, write code, and open pull requests on your behalf, under your supervision. Run Vibe Code against a local checkout via the [CLI](https://docs.mistral.ai/vibe/code/cli/install-setup) or the [VS Code extension](https://docs.mistral.ai/vibe/code/vs- …
    cite: https://docs.mistral.ai/vibe/code/overview

[5] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/scaffold-a-project | section: whats-next
    Scaffold a project with Vibe Code > What's next
    - [Work with the CLI](https://docs.mistral.ai/vibe/code/cli/work-with-cli) — Master `@` file refs, `/` slash commands, `!` shell, `&` cloud send, and `resume`. - [CLI agents](https://docs.mistral.ai/vibe/code/cli/agents) — Pick the right agent (default, plan, accept-edits, auto-approve). - [CLI Skills](https://docs.mistral.ai/vibe/code/cli/skills) - [Choose CLI, VS Code, or web sessions](https://d …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/scaffold-a-project#whats-next

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/configuration") to read hit 1 on its page
```

### 5. mistral_docs_read_page

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

### 7. mistral_docs_history

```json
{"page_url": "https://docs.mistral.ai/models", "text": "zai-glm-5-2"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
history takes exactly one of text, page_url or under.
next: mistral_docs_history(text="phrase"), mistral_docs_history(page_url="url", section="key") or mistral_docs_history(under="path", since="date").
```

### 8. mistral_docs_history

```json
{"text": "zai-glm-5-2", "under": "https://docs.mistral.ai/models"}
```

Result:

```
Error executing tool mistral_docs_ca30_mistral_docs_history: error: E_BAD_PARAM
history takes exactly one of text, page_url or under.
next: mistral_docs_history(text="phrase"), mistral_docs_history(page_url="url", section="key") or mistral_docs_history(under="path", since="date").
```

### 9. mistral_docs_history

```json
{"under": "https://docs.mistral.ai/models"}
```

Result:

```
history under: https://docs.mistral.ai/models | since: 2026-06-01
between 2026-06-01 and 2026-06-15: 15 changed
  changed | https://docs.mistral.ai/models | section: all-models
    cite: https://docs.mistral.ai/models
  changed | https://docs.mistral.ai/models | section: audio
    cite: https://docs.mistral.ai/models
  changed | https://docs.mistral.ai/models/devstral-2-25-12 | section: overview
    cite: https://docs.mistral.ai/models/devstral-2-25-12
  changed | https://docs.mistral.ai/models/leanstral-26-03 | section: overview
    cite: https://docs.mistral.ai/models/leanstral-26-03
  changed | https://docs.mistral.ai/models/magistral-medium-1-2-25-09 | section: overview
    cite: https://docs.mistral.ai/models/magistral-medium-1-2-25-09
  changed | https://docs.mistral.ai/models/mistral-medium-3-1-25-08 | section: overview
    cite: https://docs.mistral.ai/models/mistral-medium-3-1-25-08
  changed | https://docs.mistral.ai/models/mistral-medium-3-25-05 | section: overview
    cite: https://docs.mistral.ai/models/mistral-medium-3-25-05
  changed | https://docs.mistral.ai/models/mistral-nemo-12b-24-07 | section: overview
    cite: https://docs.mistral.ai/models/mistral-nemo-12b-24-07
  changed | https://docs.mistral.ai/models/voxtral-mini-transcribe-25-07 | section: overview
    cite: https://docs.mistral.ai/models/voxtral-mini-transcribe-25-07
  changed | https://docs.mistral.ai/models/voxtral-mini-transcribe-25-07 | section: voxtral-mini-transcribe
    cite: https://docs.mistral.ai/models/voxtral-mini-transcribe-25-07
  changed | https://docs.mistral.ai/models/voxtral-mini-transcribe-26-02 | section: voxtral-mini-transcribe-2
    cite: https://docs.mistral.ai/models/voxtral-mini-transcribe-26-02
  changed | https://docs.mistral.ai/models/voxtral-mini-transcribe-realtime-26-02 | section: features
    cite: https://docs.mistral.ai/models/voxtral-mini-transcribe-realtime-26-02
  changed | https://docs.mistral.ai/models/voxtral-mini-transcribe-realtime-26-02 | section: links
    cite: https://docs.mistral.ai/models/voxtral-mini-transcribe-realtime-26-02
  changed | https://docs.mistral.ai/models/voxtral-mini-transcribe-realtime-26-02 | section: voxtral-mini-transcribe-realtime
    cite: https://docs.mistral.ai/models/voxtral-mini-transcribe-realtime-26-02
  changed | https://docs.mistral.ai/models/voxtral-tts-26-03 | section: overview
    cite: https://docs.mistral.ai/models/voxtral-tts-26-03
between 2026-06-15 and 2026-07-01: 3 added, 34 changed
  changed | https://docs.mistral.ai/models | section: agents-and-conversations
    cite: https://docs.mistral.ai/models
  changed | https://docs.mistral.ai/models | section: all-models
    cite: https://docs.mistral.ai/models
  changed | https://docs.mistral.ai/models | section: batch
    cite: https://docs.mistral.ai/models
  changed | https://docs.mistral.ai/models | section: chat-completions
    cite: https://docs.mistral.ai/models
  changed | https://docs.mistral.ai/models | section: document-processing
    cite: https://docs.mistral.ai/models
  changed | https://docs.mistral.ai/models/best-practices/sampling | section: available-sampling-parameters/output-table
    cite: https://docs.mistral.ai/models/best-practices/sampling#available-sampling-parameters:~:text=model%20generates%20a
  changed | https://docs.mistral.ai/models/deployment/cloud-deployments/azure | section: azure-ai
    cite: https://docs.mistral.ai/models/deployment/cloud-deployments/azure
  changed | https://docs.mistral.ai/models/devstral-small-1-0-25-05 | section: lifecycle
    cite: https://docs.mistral.ai/models/devstral-small-1-0-25-05
  changed | https://docs.mistral.ai/models/devstral-small-2-25-12 | section: lifecycle
    cite: https://docs.mistral.ai/models/devstral-small-2-25-12
  added | https://docs.mistral.ai/models/leanstral-1-5 | 9 sections
    cite: https://docs.mistral.ai/models/leanstral-1-5
  changed | https://docs.mistral.ai/models/leanstral-26-03 | section: lifecycle
    cite: https://docs.mistral.ai/models/leanstral-26-03
  changed | https://docs.mistral.ai/models/leanstral-26-03 | section: overview
    cite: https://docs.mistral.ai/models/leanstral-26-03
  changed | https://docs.mistral.ai/models/magistral-medium-1-0-25-06 | section: lifecycle
    cite: https://docs.mistral.ai/models/magistral-medium-1-0-25-06
  changed | https://docs.mistral.ai/models/magistral-medium-1-1-25-07 | section: lifecycle
    cite: https://docs.mistral.ai/models/magistral-medium-1-1-25-07
  changed | https://docs.mistral.ai/models/magistral-small-1-0-25-06 | section: lifecycle
    cite: https://docs.mistral.ai/models/magistral-small-1-0-25-06
  changed | https://docs.mistral.ai/models/magistral-small-1-1-25-07 | section: lifecycle
    cite: https://docs.mistral.ai/models/magistral-small-1-1-25-07
  changed | https://docs.mistral.ai/models/mathstral-7b-0-1 | section: lifecycle
    cite: https://docs.mistral.ai/models/mathstral-7b-0-1
  changed | https://docs.mistral.ai/models/mistral-medium-1-0-23-12 | section: lifecycle
    cite: https://docs.mistral.ai/models/mistral-medium-1-0-23-12
  changed | https://docs.mistral.ai/models/mistral-medium-3-1-25-08 | section: overview
    cite: https://docs.mistral.ai/models/mistral-medium-3-1-25-08
  changed | https://docs.mistral.ai/models/mistral-medium-3-5-26-04 | section: overview
    cite: https://docs.mistral.ai/models/mistral-medium-3-5-26-04
  changed | https://docs.mistral.ai/models/mistral-saba-25-02 | section: lifecycle
    cite: https://docs.mistral.ai/models/mistral-saba-25-02
  changed | https://docs.mistral.ai/models/mistral-small-1-0-24-02 | section: lifecycle
    cite: https://docs.mistral.ai/models/mistral-small-1-0-24-02
  changed | https://docs.mistral.ai/models/mistral-small-2-0-24-09 | section: lifecycle
    cite: https://docs.mistral.ai/models/mistral-small-2-0-24-09
  changed | https://docs.mistral.ai/models/mistral-small-3-0-25-01 | section: lifecycle
    cite: https://docs.mistral.ai/models/mistral-small-3-0-25-01
  changed | https://docs.mistral.ai/models/mistral-small-3-1-25-03 | section: lifecycle
    cite: https://docs.mistral.ai/models/mistral-small-3-1-25-03
  changed | https://docs.mistral.ai/models/mistral-small-creative-25-12 | section: lifecycle
    cite: https://docs.mistral.ai/models/mistral-small-creative-25-12
  changed | https://docs.mistral.ai/models/mixtral-8x22b-0-1-0-3 | section: lifecycle
    cite: https://docs.mistral.ai/models/mixtral-8x22b-0-1-0-3
  changed | https://docs.mistral.ai/models/mixtral-8x7b-0-1 | section: lifecycle
    cite: https://docs.mistral.ai/models/mixtral-8x7b-0-1
  changed | https://docs.mistral.ai/models/ocr-2-25-05 | section: features
    cite: https://docs.mistral.ai/models/ocr-2-25-05
  changed | https://docs.mistral.ai/models/ocr-2-25-05 | section: lifecycle
    cite: https://docs.mistral.ai/models/ocr-2-25-05
  changed | https://docs.mistral.ai/models/ocr-25-03 | section: lifecycle
    cite: https://docs.mistral.ai/models/ocr-25-03
  changed | https://docs.mistral.ai/models/ocr-3-25-12 | section: features
    cite: https://docs.mistral.ai/models/ocr-3-25-12
  added | https://docs.mistral.ai/models/ocr-3-25-12 | section: lifecycle
    cite: https://docs.mistral.ai/models/ocr-3-25-12
  changed | https://docs.mistral.ai/models/ocr-3-25-12 | section: ocr-3
    cite: https://docs.mistral.ai/models/ocr-3-25-12
  changed | https://docs.mistral.ai/models/ocr-3-25-12 | section: overview
    cite: https://docs.mistral.ai/models/ocr-3-25-12
  added | https://docs.mistral.ai/models/ocr-4-0 | 7 sections
    cite: https://docs.mistral.ai/models/ocr-4-0
  changed | https://docs.mistral.ai/models/voxtral-tts-26-03 | section: weights
    cite: https://docs.mistral.ai/models/voxtral-tts-26-03
between 2026-07-01 and 2026-07-15: 9 changed
  changed | https://docs.mistral.ai/models/best-practices/sampling | section: available-sampling-parameters/api
    cite: https://docs.mistral.ai/models/best-practices/sampling#available-sampling-parameters:~:text=You%20can%20set
  changed | https://docs.mistral.ai/models/best-practices/sampling | section: available-sampling-parameters/example
    cite: https://docs.mistral.ai/models/best-practices/sampling#available-sampling-parameters
  changed | https://docs.mistral.ai/models/best-practices/sampling | section: available-sampling-parameters/example-2
    cite: https://docs.mistral.ai/models/best-practices/sampling#available-sampling-parameters
  changed | https://docs.mistral.ai/models/best-practices/sampling | section: available-sampling-parameters/presence-and-frequency-penalties-differences
    cite: https://docs.mistral.ai/models/best-practices/sampling#available-sampling-parameters:~:text=Presence%20Penalty%3A%20This
  changed | https://docs.mistral.ai/models/deployment/cloud-deployments/outscale | section: querying-the-model-chat
    cite: https://docs.mistral.ai/models/deployment/cloud-deployments/outscale#querying-the-model-chat
  changed | https://docs.mistral.ai/models/deployment/cloud-deployments/outscale | section: querying-the-model-fim
    cite: https://docs.mistral.ai/models/deployment/cloud-deployments/outscale#querying-the-model-fim
  changed | https://docs.mistral.ai/models/leanstral-1-5 | section: links
    cite: https://docs.mistral.ai/models/leanstral-1-5
  changed | https://docs.mistral.ai/models/leanstral-1-5 | section: overview
    cite: https://docs.mistral.ai/models/leanstral-1-5
  changed | https://docs.mistral.ai/models/leanstral-1-5 | section: weights
    cite: https://docs.mistral.ai/models/leanstral-1-5
between 2026-07-15 and 2026-08-01: 1 added, 23 changed
  changed | https://docs.mistral.ai/models | section: all-models
    cite: https://docs.mistral.ai/models
  changed | https://docs.mistral.ai/models | section: audio
    cite: https://docs.mistral.ai/models
  changed | https://docs.mistral.ai/models/codestral-25-08 | section: overview
    cite: https://docs.mistral.ai/models/codestral-25-08
  changed | https://docs.mistral.ai/models/codestral-embed-25-05 | section: overview
    cite: https://docs.mistral.ai/models/codestral-embed-25-05
  changed | https://docs.mistral.ai/models/leanstral-1-5 | section: overview
    cite: https://docs.mistral.ai/models/leanstral-1-5
  changed | https://docs.mistral.ai/models/ministral-3-14b-25-12 | section: overview
    cite: https://docs.mistral.ai/models/ministral-3-14b-25-12
  changed | https://docs.mistral.ai/models/ministral-3-3b-25-12 | section: overview
    cite: https://docs.mistral.ai/models/ministral-3-3b-25-12
  changed | https://docs.mistral.ai/models/ministral-3-8b-25-12 | section: overview
    cite: https://docs.mistral.ai/models/ministral-3-8b-25-12
  changed | https://docs.mistral.ai/models/mistral-embed-23-12 | section: overview
    cite: https://docs.mistral.ai/models/mistral-embed-23-12
  changed | https://docs.mistral.ai/models/mistral-large-3-25-12 | section: overview
    cite: https://docs.mistral.ai/models/mistral-large-3-25-12
  changed | https://docs.mistral.ai/models/mistral-medium-3-5-26-04 | section: overview
    cite: https://docs.mistral.ai/models/mistral-medium-3-5-26-04
  changed | https://docs.mistral.ai/models/mistral-moderation-26-03 | section: overview
    cite: https://docs.mistral.ai/models/mistral-moderation-26-03
  changed | https://docs.mistral.ai/models/mistral-small-4-0-26-03 | section: overview
    cite: https://docs.mistral.ai/models/mistral-small-4-0-26-03
  changed | https://docs.mistral.ai/models/ocr-3-25-12 | section: overview
    cite: https://docs.mistral.ai/models/ocr-3-25-12
  changed | https://docs.mistral.ai/models/ocr-4-0 | section: overview
    cite: https://docs.mistral.ai/models/ocr-4-0
between 2026-08-01 and 2026-08-15: 5 added, 2 removed, 40 changed, 30 moved
between 2026-08-15 and 2026-09-01: 2 changed
between 2026-09-01 and 2026-09-07: no change
Results: 164 changes over 7 intervals
next: narrow under or raise since; the rest was not rendered
```

### 10. mistral_docs_search

```json
{"q": "zai-glm-5-2 model page"}
```

Result:

```
q: "zai-glm-5-2 model page"

[1] https://docs.mistral.ai/models/zai-glm-5-2 | section: overview
    Z.ai GLM 5.2 > Overview
    | Field | Value | | --- | --- | | API names | `zai-glm-5-2` | | Slug | `zai-glm-5-2` | | Status | PublicPreview | | Release date | 2026-08-06 | | Version | 5.2 | | Type | Open | | Class | Generalist | | Context length | 1M | | Output token limit | 128k | | Legacy | no |
    cite: https://docs.mistral.ai/models/zai-glm-5-2

[2] https://docs.mistral.ai/models | section: chat-completions
    Model capability matrix > Chat completions
    - **[Predicted Outputs](https://docs.mistral.ai/studio/conversations/advanced/predicted-outputs)** (`predicted-outputs`), 11 models: Codestral (`codestral-2501`), Codestral (`codestral-2508`), Mistral Large 2.1 (`mistral-large-2411`), Mistral Medium 3.1 (`mistral-medium-2508`), Mistral Medium 3 (`mistral-medium-2505`), Mistral Medium 3.5 (`mistral-medium-3-5`), Mistral Small 3.1 (`mistral-small-25 …
    cite: https://docs.mistral.ai/models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/models", section="chat-completions") reads this section

[3] https://docs.mistral.ai/models | section: batch
    Model capability matrix > Batch
    - **[Batching](https://docs.mistral.ai/studio/batch-processing)** (`batching`), 43 models: Codestral (`codestral-2501`), Codestral (`codestral-2508`), Codestral Embed (`codestral-embed-2505`), Devstral 2 (`devstral-2512`), Devstral Medium 1.0 (`devstral-medium-2507`), Devstral Small 1.0 (`devstral-small-2505`), Devstral Small 1.1 (`devstral-small-2507`), Devstral Small 2 (`labs-devstral-small-2512 …
    cite: https://docs.mistral.ai/models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/models", section="batch") reads this section

[4] https://docs.mistral.ai/vibe/code/cli/configuration | section: providers-models
    Configuration > Common configuration sections > Providers and models
    Define provider presets, model presets, and the active model. The following chat-capable models are available through Mistral's API (la Plateforme). Use the **model ID** as the `name` value in a `[[models]]` block, or pass it directly with `--model`: | Model | Model ID | Best for | |---|---|---| | Mistral Medium 3.5 (recommended) | `mistral-medium-latest` | Flagship reasoning and code | | Z.ai GLM …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#providers-models

[5] https://docs.mistral.ai/models | section: all-models
    Model capability matrix > All models
    | Model | API names | Status | Context | Release date | | --- | --- | --- | --- | --- | | [Codestral](https://docs.mistral.ai/models/codestral-24-05) | `codestral-2405` | Retired | 32k | 2024-05-29 | | [Codestral](https://docs.mistral.ai/models/codestral-25-01) | `codestral-2501` | Retired | 128k | 2025-01-13 | | [Codestral](https://docs.mistral.ai/models/codestral-25-08) | `codestral-2508`, `code …
    cite: https://docs.mistral.ai/models
    large page: mistral_docs_read_page(page_url="https://docs.mistral.ai/models", section="all-models") reads this section

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/models/zai-glm-5-2") to read hit 1 on its page
```

### 11. mistral_docs_history

```json
{"page_url": "https://docs.mistral.ai/models/zai-glm-5-2"}
```

Result:

```
history page: https://docs.mistral.ai/models/zai-glm-5-2
absent at 2026-06-01
absent through 2026-08-01
added between 2026-08-01 and 2026-08-15 | https://docs.mistral.ai/models/zai-glm-5-2
same through 2026-09-07 | https://docs.mistral.ai/models/zai-glm-5-2
Results: 8 of 8 stored snapshots
```

## Answer

The Vibe Code CLI configuration page started listing **GLM 5.2 (`zai-glm-5-2`)** between **August 15, 2026 and September 1, 2026**.

This is based on the documentation history showing that the `providers-models` section of the [Vibe Code CLI configuration page](https://docs.mistral.ai/vibe/code/cli/configuration#providers-models) was updated during this period to include the model table with Z.ai GLM 5.2 and its model ID `zai-glm-5-2` -models section history.

