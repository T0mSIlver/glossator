# mined2-052 (cross_page, 2 connector calls)

## Question

Where do I set up a hook that runs before every tool call in the Vibe CLI?

## Thinking

The user is asking about setting up a hook that runs before every tool call in the Vibe CLI. This is a specific technical question about Mistral's Vibe CLI configuration. I need to search the documentation to find where this is configured. Let me search for relevant terms like "hook", "before", "tool call", and "Vibe CLI".

The search returned results pointing to the hooks documentation. The first hit is specifically about `pre_tool` hooks which run before tool calls. This looks very relevant. I should read the full hooks page to understand the complete setup process and provide accurate information.

I've read the hooks documentation page. The information is clear: to set up a hook that runs before every tool call in the Vibe CLI, you need to use the `pre_tool` hook type. The configuration goes in a `hooks.toml` file. There are two possible locations: project-level at `./.vibe/hooks.toml` or user-level at `~/.vibe/hooks.toml`. Project-level hooks take precedence if there's a naming conflict. I should provide a complete answer with an example configuration, explain the key fields, and mention the file locations. I need to make sure to cite the documentation properly.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "hook that runs before every tool call in the Vibe CLI", "max_hits": 10}
```

Result:

```
q: "hook that runs before every tool call in the Vibe CLI"

[1] https://docs.mistral.ai/vibe/code/cli/hooks | section: pre-tool
    Hooks > `pre_tool`
    Fires per tool call, **before** the user permission prompt. The first deny short-circuits the remaining `pre_tool` hooks for that call. **Receives** (in addition to the session context): `tool_name`, `tool_call_id`, `tool_input` (the model's raw arguments). **Can return**: - `decision: "deny"` + `reason` — denies the tool call; `reason` becomes the tool error that the LLM sees. - `hook_specific_ou …
    cite: https://docs.mistral.ai/vibe/code/cli/hooks#pre-tool

[2] https://docs.mistral.ai/vibe/code/cli/hooks | section: contract
    Hooks > Hook contract
    Every hook is spawned with a UTF-8 JSON object on `stdin` containing the session context: `session_id`, `parent_session_id`, `transcript_path`, `cwd`, and `hook_event_name`. Tool hooks add tool-specific fields (see below). Hooks respond through their **exit code** and **stdout**. Use `stderr` for diagnostics and debug logs. | Exit / stdout | Effect | |---|---| | Exit `0`, empty `stdout` | Passthro …
    cite: https://docs.mistral.ai/vibe/code/cli/hooks#contract

[3] https://docs.mistral.ai/vibe/code/cli/hooks | section: declare
    Hooks > Declare a hook
    Each hook is a `[[hooks]]` table: ```toml [[hooks]] name = "deny-rm-rf" type = "pre_tool" match = "bash" command = "uv run python /path/to/guard-bash" timeout = 60.0 strict = false description = "Reject dangerous shell commands." ``` | Field | Required | Details | |---|---|---| | `name` | yes | Unique identifier. Used to deduplicate between project and user files. | | `type` | yes | One of `pre_to …
    cite: https://docs.mistral.ai/vibe/code/cli/hooks#declare

[4] https://docs.mistral.ai/vibe | section: how-vibe-works
    Vibe > How Vibe works
    Across every mode, you interact with Vibe **the same way**: same Mistral models, same patterns, same control. A typical Vibe workflow looks like this: 1. **You describe the outcome you want** in natural language. 2. **Vibe gathers context** from your prompt, attached files, connected tools, or the web. 3. **Vibe plans and acts**: it breaks the task into steps, calls the right tools, and shows its …
    cite: https://docs.mistral.ai/vibe#how-vibe-works

[5] https://docs.mistral.ai/vibe/code/cli/hooks | section: post-tool
    Hooks > `post_tool`
    Fires per tool call **if and only if the tool body actually ran**. It does not fire when the tool never executed: `pre_tool` denial, user denial at the approval prompt, permission set to `NEVER`, or cancellation before the body started. Cancellation during the tool body is shielded, so audit hooks still run. **Receives** (in addition to the session context): - `tool_name`, `tool_call_id` - `tool_i …
    cite: https://docs.mistral.ai/vibe/code/cli/hooks#post-tool

[6] https://docs.mistral.ai/vibe/code/cli/teleport-cli-web | section: prerequisites
    Teleport from CLI to web > Prerequisites
    Before you teleport, make sure that: - You use an API key tied to a **Pro, Team, or Enterprise** account. - The **[Mistral GitHub App](https://github.com/apps/mistralai/installations/new)** is installed on the repository you're working in. - Your local session runs on a **Mistral model** (for example, Mistral Medium 3.5 or Devstral). Sessions on third-party models cannot be teleported. - You run t …
    cite: https://docs.mistral.ai/vibe/code/cli/teleport-cli-web#prerequisites

[7] https://docs.mistral.ai/vibe/code/cli/hooks | section: hooks
    Hooks
    Hooks wire arbitrary shell commands into the Vibe Code CLI's lifecycle to **gate, audit, or rewrite** agent behavior. Use them to block dangerous tool calls, redact arguments before a tool runs, append context after a tool returns, or force the agent to retry an unsatisfactory answer. Declare them in a `hooks.toml` file and they take effect on the next run.
    cite: https://docs.mistral.ai/vibe/code/cli/hooks

[8] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/scaffold-a-project | section: prerequisites
    Scaffold a project with Vibe Code > Prerequisites
    - Vibe CLI installed and configured. If you haven't done that yet, run the [Install the Vibe CLI](https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli) quickstart first. > **Tip** > > Scaffolding is a good use case for the **`plan`** or **`accept-edits`** [agents](https://docs.mistral.ai/vibe/code/cli/agents). `plan` asks Vibe to outline what it will do before generating anyth …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/scaffold-a-project#prerequisites

[9] https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli | section: step-2
    Install the Vibe CLI and send your first prompt > Step 2: Launch and configure
    1. Open a terminal in any project directory. 2. Run: ```bash vibe ``` ![Vibe CLI running in a terminal](https://docs.mistral.ai/assets/quickstarts/vibe/home.png) On first launch, the CLI runs a **setup wizard** to register your API key. By default it opens a browser to sign you in with your Mistral account; credentials are stored locally so you don't need to enter them again. For non-Mistral provi …
    cite: https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli#step-2

[10] https://docs.mistral.ai/studio/connectors/tool_calling | section: direct-tool-calling
    Direct tool calling with Connectors > Direct tool calling
    The `call_tool` method lets you call a specific MCP tool on a Connector directly, **without starting a conversation or involving the model**. This is useful when you: - Already know which tool to call and what arguments to pass - Want the raw tool output for downstream processing - Are building pipelines that chain tool calls programmatically - Want to debug or verify Connector tools before using …
    cite: https://docs.mistral.ai/studio/connectors/tool_calling

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/hooks") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/hooks"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/hooks | "Hooks"

## section: hooks
    Hooks
    cite: https://docs.mistral.ai/vibe/code/cli/hooks
# Hooks

Hooks wire arbitrary shell commands into the Vibe Code CLI's lifecycle to **gate, audit, or rewrite** agent behavior. Use them to block dangerous tool calls, redact arguments before a tool runs, append context after a tool returns, or force the agent to retry an unsatisfactory answer.

Declare them in a `hooks.toml` file and they take effect on the next run.

## section: file-locations
    Hooks > Configuration file locations
    cite: https://docs.mistral.ai/vibe/code/cli/hooks#file-locations
## Configuration file locations {#file-locations}

Hooks are declared in `hooks.toml`. The CLI looks in this order:

1. `./.vibe/hooks.toml` in the working directory (**project-level**, loaded first, **trusted folders only**).
2. `~/.vibe/hooks.toml` in your home directory (**user-level**, loaded second).

When the same `name` appears in both files, the **project entry wins**. Project-level hooks load only when the working directory is [trusted](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders).

Subagents inherit the parent's hook configuration, so policies apply transitively.

## section: declare
    Hooks > Declare a hook
    cite: https://docs.mistral.ai/vibe/code/cli/hooks#declare
## Declare a hook {#declare}

Each hook is a `[[hooks]]` table:

```toml
[[hooks]]
name = "deny-rm-rf"
type = "pre_tool"
match = "bash"
command = "uv run python /path/to/guard-bash"
timeout = 60.0
strict = false
description = "Reject dangerous shell commands."
```

| Field | Required | Details |
|---|---|---|
| `name` | yes | Unique identifier. Used to deduplicate between project and user files. |
| `type` | yes | One of `pre_tool`, `post_tool`, `post_agent`. |
| `command` | yes | Shell command to spawn. Receives the hook payload on `stdin`. |
| `match` | `pre_tool` / `post_tool` | Tool-name matcher: fnmatch glob, or regex with the `re:` prefix. Case-insensitive. |
| `timeout` | no | Seconds before the hook is killed. Default: `60`. |
| `strict` | tool hooks only | When `true`, parse and runtime failures become denials (`pre_tool`) or text clears (`post_tool`) instead of warnings. Default: `false`. |
| `description` | no | Free text shown in diagnostics. |

## section: contract
    Hooks > Hook contract
    cite: https://docs.mistral.ai/vibe/code/cli/hooks#contract
## Hook contract {#contract}

Every hook is spawned with a UTF-8 JSON object on `stdin` containing the session context: `session_id`, `parent_session_id`, `transcript_path`, `cwd`, and `hook_event_name`. Tool hooks add tool-specific fields (see below).

Hooks respond through their **exit code** and **stdout**. Use `stderr` for diagnostics and debug logs.

| Exit / stdout | Effect |
|---|---|
| Exit `0`, empty `stdout` | Passthrough. |
| Exit `0`, valid JSON object on `stdout` | Structured response (see fields below). |
| Exit `0`, non-empty but non-conforming `stdout` | Hook failure. Warning by default; deny / clear under `strict = true` on a tool hook. |
| Non-zero exit, timeout, or spawn failure | Hook failure. Diagnostic taken from `stderr` (fallback to `stdout`, then the exit code). |

Universal top-level fields in the JSON response:

- **`system_message`** (string, optional) — shown to the user in the UI.
- **`decision`** (`"allow"` | `"deny"`, optional, default `"allow"`) — the effect of `"deny"` depends on the hook type.
- **`reason`** (string, optional) — accompanies `decision: "deny"`.
- **`hook_specific_output`** (object, optional) — event-specific payload.

Unknown JSON fields are tolerated at every level (forward-compatible). Fields that are not meaningful for the current hook type are silently ignored.

## section: pre-tool
    Hooks > `pre_tool`
    cite: https://docs.mistral.ai/vibe/code/cli/hooks#pre-tool
## `pre_tool` {#pre-tool}

Fires per tool call, **before** the user permission prompt. The first deny short-circuits the remaining `pre_tool` hooks for that call.

**Receives** (in addition to the session context): `tool_name`, `tool_call_id`, `tool_input` (the model's raw arguments).

**Can return**:

- `decision: "deny"` + `reason` — denies the tool call; `reason` becomes the tool error that the LLM sees.
- `hook_specific_output.tool_input` (object) — **full replacement** of the model's arguments. The replacement is re-validated against the tool's schema; a validation failure becomes a synthesized denial. Rewrites compose left-to-right across hooks. The rewritten arguments are also what the permission prompt displays, what the tool runs with, and what subsequent LLM turns see on the assistant message.
- `system_message` — UI-only.

## section: post-tool
    Hooks > `post_tool`
    cite: https://docs.mistral.ai/vibe/code/cli/hooks#post-tool
## `post_tool` {#post-tool}

Fires per tool call **if and only if the tool body actually ran**. It does not fire when the tool never executed: `pre_tool` denial, user denial at the approval prompt, permission set to `NEVER`, or cancellation before the body started. Cancellation during the tool body is shielded, so audit hooks still run.

**Receives** (in addition to the session context):

- `tool_name`, `tool_call_id`
- `tool_input` (post-rewrite)
- `tool_status` — `success`, `failure`, or `cancelled`
- `tool_output` — structured result dict; `null` on failure
- `tool_output_text` — the running text the LLM will see, mutable by prior hooks
- `tool_error`
- `duration_ms`

**Can return**:

- `decision: "deny"` + `reason` — replaces `tool_output_text` with `reason`. The pipeline continues; subsequent hooks see the replacement.
- `hook_specific_output.additional_context` (string) — **appended** (with a `\n` separator) to `tool_output_text`. Composes with a same-hook deny: deny replaces first, then `additional_context` is appended to the replacement.
- `system_message` — UI-only.

## section: post-agent
    Hooks > `post_agent`
    cite: https://docs.mistral.ai/vibe/code/cli/hooks#post-agent
## `post_agent` {#post-agent}

Fires after every assistant turn that ends without pending tool calls.

**Receives** (in addition to the session context): no extra fields.

**Can return**:

- `decision: "deny"` + `reason` — `reason` is injected as a new user message asking the agent to retry. Capped at **3 retries per hook per user turn**; further denies become terminal warnings.
- `system_message` — UI-only.

## section: example
    Hooks > Example: block destructive shell commands
    cite: https://docs.mistral.ai/vibe/code/cli/hooks#example
## Example: block destructive shell commands {#example}

`./.vibe/hooks.toml`:

```toml
[[hooks]]
name = "deny-rm-rf"
type = "pre_tool"
match = "bash"
command = "python ./.vibe/hooks/guard-bash.py"
strict = true
description = "Reject rm -rf and other destructive shell commands."
```

`./.vibe/hooks/guard-bash.py`:

```python
import json
import sys

payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")

if "rm -rf" in command:
    print(json.dumps({
        "decision": "deny",
        "reason": "rm -rf is blocked by the deny-rm-rf hook.",
    }))
    sys.exit(0)

# Passthrough: empty stdout, exit 0.
```

With `strict = true`, any script crash or malformed JSON output also denies the call instead of degrading to a warning.

Results: 8 sections, the whole page.
```

## Answer

To set up a hook that runs **before every tool call** in the Vibe CLI, you use the **`pre_tool`** hook type in a `hooks.toml` file.

Declare it in one of these locations (project-level takes precedence):
- `./.vibe/hooks.toml` (project-level, trusted folders only)
- `~/.vibe/hooks.toml` (user-level)

Example configuration:
```toml
[[hooks]]
name = "my-pre-tool-hook"
type = "pre_tool"
match = "*"  # Applies to all tools; use a specific tool name or glob pattern to filter
command = "python /path/to/your/hook_script.py"
timeout = 60.0
strict = false
description = "Runs before every tool call"
```

Key points:
- The `pre_tool` hook fires **before the user permission prompt** for each tool call.
- It receives the tool name, call ID, and raw input arguments via stdin as a JSON payload.
- It can **deny** the call (with a `reason`) or **rewrite** the tool input via `hook_specific_output.tool_input`.
- The first `deny` short-circuits remaining `pre_tool` hooks for that call.

[Hooks overview](https://docs.mistral.ai/vibe/code/cli/hooks)
[Declare a hook](https://docs.mistral.ai/vibe/code/cli/hooks#declare)
[pre_tool behavior](https://docs.mistral.ai/vibe/code/cli/hooks#pre-tool)
[File locations](https://docs.mistral.ai/vibe/code/cli/hooks#file-locations)

