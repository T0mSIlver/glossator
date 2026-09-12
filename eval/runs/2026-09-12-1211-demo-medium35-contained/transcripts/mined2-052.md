# mined2-052 (cross_page, 2 connector calls)

## Question

Where do I set up a hook that runs before every tool call in the Vibe CLI?

## Thinking

The user is asking about setting up a hook that runs before every tool call in the Vibe CLI. This is a specific technical question about Mistral's Vibe CLI configuration. I need to search the documentation for information about hooks, pre-tool execution, or similar features in the Vibe CLI.

I'll use the mistral_docs_search tool to look for relevant documentation about Vibe CLI hooks.

The search results show that there is a `pre_tool` hook type in the Vibe CLI hooks documentation. This appears to be exactly what the user is looking for - a hook that runs before every tool call. The first result points to the hooks page with a section about pre-tool. I should read the full hooks page to provide a complete and accurate answer.

The user wants to know where to set up a hook that runs before every tool call in the Vibe CLI.

From the search results, I can see that:
1. There is a `pre_tool` hook type in the Vibe CLI hooks system
2. The documentation is at https://docs.mistral.ai/vibe/code/cli/hooks
3. The `pre_tool` hook fires before the user permission prompt for each tool call
4. It receives session context plus `tool_name`, `tool_call_id`, and `tool_input`
5. It can return decisions to deny, modify tool input, or add system messages

I should provide a clear, direct answer that:
- States the hook type is `pre_tool`
- Explains where to configure it (in the hooks section of the config)
- Provides an example configuration
- Links to the documentation

The user asked "where" so I need to be explicit about the configuration location. Based on the search results, hooks are declared in the `[[hooks]]` table in the configuration file.

Let me structure the answer:
1. Direct answer: Use the `pre_tool` hook type
2. Configuration location: In the Vibe CLI config file under `[[hooks]]`
3. Example configuration
4. Key capabilities
5. Documentation link

I should make sure to cite the documentation properly as shown in the search results.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "hook that runs before every tool call in the Vibe CLI", "max_hits": 5}
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

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/hooks") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/hooks", "section": "pre-tool"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/hooks | "Hooks" | section: pre-tool

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

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/hooks", section="post-tool") for the section after it
```

## Answer

To set up a hook that runs **before every tool call** in the Vibe CLI, you use the **`pre_tool`** hook type.

You declare it in your Vibe CLI configuration under a `[[hooks]]` table, for example:

```toml
[[hooks]]
name = "my-pre-tool-hook"
type = "pre_tool"
command = "uv run python /path/to/my_hook.py"
```

- It fires **before** the user permission prompt for each tool call.
- It receives the session context plus `tool_name`, `tool_call_id`, and `tool_input`.
- It can return a `decision: "deny"` to block the call, or rewrite `tool_input` before the tool runs.

[`pre_tool` hook](https://docs.mistral.ai/vibe/code/cli/hooks#pre-tool)

