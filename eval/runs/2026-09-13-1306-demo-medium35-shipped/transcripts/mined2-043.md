# mined2-043 (single_page, 4 connector calls)

## Question

My skills are not loading even though the files look right — where does the CLI look for them and how do the enable and disable lists interact?

## Thinking

The user is asking about the Mistral CLI, specifically where it looks for skills and how the enable/disable lists interact. This is a specific technical question about configuration. I need to search the Mistral documentation for information about the CLI's skill loading mechanism, file locations, and the behavior of enable/disable lists.

Let me start by searching for relevant documentation about skills and CLI configuration.

The search returned several relevant hits. The most relevant ones appear to be:
- Hit 1: Skills > Enable, disable, or filter skills (filtering section)
- Hit 2: Configuration > Common configuration sections > Skills
- Hit 4: Skills > Skill locations

These should contain the information about where the CLI looks for skills and how enable/disable lists work. Let me read the main skills page first to get the complete picture.

Good, I have the locations information. Now I need to read the filtering section to understand how enable/disable lists interact.

Perfect. Now I have both pieces of information:
1. The CLI looks for skills in: custom paths (from config.toml), project-level (./.vibe/skills/ or ./.agents/skills/), and user-level (~/.vibe/skills/)
2. The enable/disable lists interaction: If enabled_skills is non-empty, it acts as an allow-list (only matching skills load). Otherwise, all discovered skills are available except those matched by disabled_skills.

Let me also check the configuration section to see if there's any additional detail about the skill_paths setting.

Excellent. Now I have all the information needed to answer the user's question. Let me synthesize:

**Where the CLI looks for skills:**
1. Custom paths defined in config.toml via `skill_paths = ["/path/to/custom/skills"]`
2. Project-level skills in `./.vibe/skills/` or `./.agents/skills/` (when the working directory is trusted)
3. User-level skills in `~/.vibe/skills/`

**How enable/disable lists interact:**
- If `enabled_skills` is **set and non-empty**: it acts as an allow-list. Only skills whose names match patterns in this list are loaded.
- If `enabled_skills` is **empty or not set**: all discovered skills are available, EXCEPT those whose names match patterns in `disabled_skills`.

The patterns support:
- Exact names
- Glob patterns (e.g., `test-*`)
- Regex patterns with `re:` prefix

This explains why skills might not be loading - either they're not in the search paths, or they're being filtered out by the enable/disable lists.

I should structure this answer clearly with sections for the locations and the interaction logic.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "CLI skills loading path enable disable lists", "max_hits": 10}
```

Result:

```
q: "CLI skills loading path enable disable lists"

[1] https://docs.mistral.ai/vibe/code/cli/skills | section: filtering
    Skills > Enable, disable, or filter skills
    Use patterns to control which skills load: ```toml enabled_skills = ["code-review", "test-*"] disabled_skills = ["experimental-*"] ``` Skill filters support **exact names**, **glob patterns**, and **regex** with the `re:` prefix, just like tool filters. If `enabled_skills` is non-empty, it acts as an allow-list; otherwise every discovered skill is available minus those matched by `disabled_skills` …
    cite: https://docs.mistral.ai/vibe/code/cli/skills#filtering

[2] https://docs.mistral.ai/vibe/code/cli/configuration | section: skills
    Configuration > Common configuration sections > Skills
    Enable, disable, or add skill paths: ```toml skill_paths = ["/path/to/custom/skills"] enabled_skills = ["code-review", "test-*"] disabled_skills = ["experimental-*"] ``` `enabled_skills` and `disabled_skills` interact as follows: - If `enabled_skills` is **set and non-empty**, only skills whose name matches a pattern in that list are available. - Otherwise, every discovered skill is available, min …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#skills

[3] https://docs.mistral.ai/vibe/code/safety-approvals-permissions | section: enable-disable-tools
    Safety, approvals, and permissions > Per-tool permissions > Enable or disable tools
    Toggle tools globally using exact names, globs, or regex patterns: ```toml # Only allow read-only and search tools enabled_tools = ["read_file", "grep", "task"] # Or disable a specific class of tools disabled_tools = ["bash"] ```
    cite: https://docs.mistral.ai/vibe/code/safety-approvals-permissions#enable-disable-tools

[4] https://docs.mistral.ai/vibe/code/cli/skills | section: locations
    Skills > Skill locations
    The CLI discovers skills from several locations, in order: 1. **Custom paths** defined in `config.toml` → `skill_paths = ["/path/to/custom/skills"]` 2. **Project-level** skills in `./.vibe/skills/` or `./.agents/skills/` when the working directory is [trusted](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders). 3. **User-level** skills in `~/.vibe/skills/`.
    cite: https://docs.mistral.ai/vibe/code/cli/skills#locations

[5] https://docs.mistral.ai/vibe/code/cli/skills | section: stay-in-control
    Skills > Stay in control
    - **Review a skill before enabling it** if it can call write-capable tools. - Prefer **narrow `allowed-tools` lists** over disabling tools elsewhere. - Keep project-specific skills in `./.vibe/skills/` so collaborators can review them in code review.
    cite: https://docs.mistral.ai/vibe/code/cli/skills#stay-in-control

[6] https://docs.mistral.ai/vibe/code/cli/work-with-cli | section: trust-folders
    Work with the CLI > Trust folders
    The CLI checks whether the current working directory is trusted before loading project-level configuration, skills, or agent files. The first time you run the CLI in **interactive mode** from a new directory that contains trustable files, it asks you to confirm the folder. Trust enforcement applies in **both** interactive and programmatic modes, but the confirmation prompt only appears interactive …
    cite: https://docs.mistral.ai/vibe/code/cli/work-with-cli#trust-folders

[7] https://docs.mistral.ai/studio/search/search-toolkit/ingestion/loaders | section: batch-loading
    File loaders > Batch loading
    Load multiple files with concurrency control: ```python import asyncio from mistralai.search.toolkit.ingestion.loaders import FileLoader from mistralai.search.toolkit.plugins.storage.s3 import S3FileLoader async def load_files_batch( loader: FileLoader, paths: list[str], max_concurrent: int = 10, ) -> list: """Load multiple files concurrently with semaphore.""" semaphore = asyncio.Semaphore(max_co …
    cite: https://docs.mistral.ai/studio/search/search-toolkit/ingestion/loaders#batch-loading

[8] https://docs.mistral.ai/vibe/code/cli/skills | section: slash-commands
    Skills > Custom slash commands
    Skills are the recommended way to add your own slash commands. Set `user-invocable: true` in the frontmatter and the skill name becomes available with `/skill-name` autocompletion in the CLI prompt, and in the [VS Code extension](https://docs.mistral.ai/vibe/code/vs-code-extension/commands-slash-commands#slash-commands) slash picker too. Pair custom skills with `allowed-tools` to keep their access …
    cite: https://docs.mistral.ai/vibe/code/cli/skills#slash-commands

[9] https://docs.mistral.ai/vibe/code/cli/configuration-reference | section: top-level
    Configuration reference > Top-level keys
    | Key | Type | Default | Description | |---|---|---|---| | `default_agent` | string | | Default interactive agent, for example `"plan"`. Ignored in programmatic mode, which falls back to `auto-approve`. See [Agents](https://docs.mistral.ai/vibe/code/cli/agents) | | `active_model` | string | | Model alias currently in use. Set to a `[[models]]` `alias` or a built-in model ID | | `log_interactions` …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration-reference#top-level

[10] https://docs.mistral.ai/vibe/work/skills | section: how-skills-work
    Reuse work with Skills > How Skills work
    Work loads Skills through **progressive disclosure** in three stages: 1. **Discovery**: at session start, Work loads only each Skill's name and description (~100 tokens each), just enough to know when it might be relevant. 2. **Activation**: when a task matches a Skill's description, Work reads the full `SKILL.md` instructions into context. 3. **Execution**: Work follows the instructions, optional …
    cite: https://docs.mistral.ai/vibe/work/skills#how-skills-work

Results: 10 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/skills") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/skills", "section": "locations"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/skills | "Skills" | section: locations

## section: locations
    Skills > Skill locations
    cite: https://docs.mistral.ai/vibe/code/cli/skills#locations
## Skill locations {#locations}

The CLI discovers skills from several locations, in order:

1. **Custom paths** defined in `config.toml` → `skill_paths = ["/path/to/custom/skills"]`
2. **Project-level** skills in `./.vibe/skills/` or `./.agents/skills/` when the working directory is [trusted](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders).
3. **User-level** skills in `~/.vibe/skills/`.

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/skills", section="filtering") for the section after it
```

### 3. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/skills", "section": "filtering"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/skills | "Skills" | section: filtering

## section: filtering
    Skills > Enable, disable, or filter skills
    cite: https://docs.mistral.ai/vibe/code/cli/skills#filtering
## Enable, disable, or filter skills {#filtering}

Use patterns to control which skills load:

```toml
enabled_skills = ["code-review", "test-*"]
disabled_skills = ["experimental-*"]
```

Skill filters support **exact names**, **glob patterns**, and **regex** with the `re:` prefix, just like tool filters. If `enabled_skills` is non-empty, it acts as an allow-list; otherwise every discovered skill is available minus those matched by `disabled_skills`.

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/skills", section="slash-commands") for the section after it
```

### 4. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/configuration", "section": "skills"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/configuration | "Configuration" | section: skills

## section: skills
    Configuration > Common configuration sections > Skills
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#skills
### Skills {#skills}

Enable, disable, or add skill paths:

```toml
skill_paths = ["/path/to/custom/skills"]
enabled_skills = ["code-review", "test-*"]
disabled_skills = ["experimental-*"]
```

`enabled_skills` and `disabled_skills` interact as follows:

- If `enabled_skills` is **set and non-empty**, only skills whose name matches a pattern in that list are available.
- Otherwise, every discovered skill is available, minus any skill whose name matches a pattern in `disabled_skills`.

See [Skills](https://docs.mistral.ai/vibe/code/cli/skills).

Results: the whole section.
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/configuration", section="tool-permissions") for the section after it
```

## Answer

The CLI looks for skills in this order:

1. **Custom paths** you define in `config.toml` via `skill_paths = ["/path/to/custom/skills"]`
2. **Project-level** skills in `./.vibe/skills/` or `./.agents/skills/` (only when the current working directory is [trusted](https://docs.mistral.ai/vibe/code/safety-approvals-permissions#trusted-folders))
3. **User-level** skills in `~/.vibe/skills/`
   *[Skill locations](https://docs.mistral.ai/vibe/code/cli/skills#locations)*

---

**How the enable / disable lists interact:**

- If **`enabled_skills` is set and non-empty**, it acts as an **allow-list**: only skills whose names match a pattern in that list are loaded.
- If **`enabled_skills` is empty or not set**, every discovered skill is available **except** those whose names match a pattern in `disabled_skills`.

Patterns can be exact names, globs (`test-*`), or regex with the `re:` prefix.
*[Enable, disable, or filter skills](https://docs.mistral.ai/vibe/code/cli/skills#filtering)*
*[Configuration: Skills](https://docs.mistral.ai/vibe/code/cli/configuration#skills)*

So, if your skills aren’t loading, check:
- They’re in one of the discovered paths.
- Either `enabled_skills` includes a matching pattern, or it’s empty and the skill name isn’t matched by `disabled_skills`.

