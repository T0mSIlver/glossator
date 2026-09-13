# mined2-036 (single_page, 2 connector calls)

## Question

Which setting wins when the same option is set in the project config, an environment variable, a command-line flag and my organization's admin config?

## Thinking

The user asks about configuration precedence: which setting wins when the same option is set in project config, environment variable, command-line flag, and organization admin config. I need to find the official documentation that describes the precedence order for Mistral's configuration. I'll search the Mistral docs for "precedence" or "priority" related to configuration.

The search returned a hit for the configuration precedence section. I need to read the full page to get the exact precedence order. I'll fetch the configuration page.

Now I have the configuration precedence order from the documentation. The order is: Admin config > Command-line flags > Environment variables > Project config > User config. The user asked specifically about project config, environment variable, command-line flag, and organization admin config. According to this, the admin config has the highest priority, followed by command-line flags, then environment variables, then project config. So the command-line flag does not win; the admin config wins. I need to answer: the organization's admin config wins. I should also mention the full order for clarity.

## Tool calls

### 1. mistral_docs_search

```json
{"q": "precedence order for configuration settings: project config, environment variable, command-line flag, organization admin config", "max_hits": 5}
```

Result:

```
q: "precedence order for configuration settings: project config, environment variable, command-line flag, organization admin config"

[1] https://docs.mistral.ai/vibe/code/cli/configuration | section: precedence
    Configuration > Configuration precedence
    When the same setting is defined in multiple places, the CLI applies them in this order, from **highest to lowest priority**: 1. **Admin config**, when your Organization provides one. See [Admin config](https://docs.mistral.ai/vibe/code/cli/admin-config). 2. **Command-line flags** (for example, `--agent`, `--workdir`). 3. **Environment variables** (for example, `MISTRAL_API_KEY`, `VIBE_HOME`). 4. …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#precedence

[2] https://docs.mistral.ai/vibe/code/cli/admin-config | section: precedence
    Admin config > Precedence
    Admin config is the **highest-priority** layer. It takes precedence over command-line flags, environment variables, and both project and user `config.toml`: ```text admin config > CLI flags > env vars > project config.toml > user config.toml ``` This precedence means the admin-provided values take effect for users by default, without them needing to update their own `config.toml`.
    cite: https://docs.mistral.ai/vibe/code/cli/admin-config#precedence

[3] https://docs.mistral.ai/vibe/code/cli/configuration | section: admin-config
    Configuration > Admin-managed configuration
    Your Organization can distribute a Vibe Code CLI configuration to all users. Admin-managed settings take precedence over command-line flags, environment variables, and the project and user `config.toml` files. When admin config is active: - Admin-managed settings in `/config` appear dim with a `⚿` lock glyph and list `your administrator` as the origin. A legend at the bottom of the screen reads `⚿ …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#admin-config

[4] https://docs.mistral.ai/vibe/code/cli/admin-config | section: admin-config
    Admin config
    Admin config, also called **managed config**, lets Organization and Workspace administrators distribute Vibe Code CLI settings to all users. You define it once in the Admin Panel, and the CLI applies it to users in the Organization or Workspace. Use it to distribute models, providers, MCP servers, and tool policies without requiring users to edit `config.toml`. > **Info** > > Admin config is a **d …
    cite: https://docs.mistral.ai/vibe/code/cli/admin-config

[5] https://docs.mistral.ai/vibe/code/cli/configuration-reference | section: environment-variables
    Configuration reference > Environment variables
    Not `config.toml` keys, but part of the configuration model. They sit at precedence level 3 (env vars). | Variable | Purpose | |---|---| | `VIBE_HOME` | Overrides the `~/.vibe/` home directory for all state (config, prompts, agents, skills, logs) | | `MISTRAL_API_KEY` | Primary Mistral API key | | `<PROVIDER>_API_KEY` | API key referenced by a `[[providers]]` `api_key_env_var` (for example `OPENRO …
    cite: https://docs.mistral.ai/vibe/code/cli/configuration-reference#environment-variables

Results: 5 hits
next: mistral_docs_read_page(page_url="https://docs.mistral.ai/vibe/code/cli/configuration") to read hit 1 on its page
```

### 2. mistral_docs_read_page

```json
{"page_url": "https://docs.mistral.ai/vibe/code/cli/configuration", "section": "precedence"}
```

Result:

```
page: https://docs.mistral.ai/vibe/code/cli/configuration | "Configuration" | section: precedence

## section: precedence
    Configuration > Configuration precedence
    cite: https://docs.mistral.ai/vibe/code/cli/configuration#precedence
## Configuration precedence {#precedence}

When the same setting is defined in multiple places, the CLI applies them in this order, from **highest to lowest priority**:

1. **Admin config**, when your Organization provides one. See [Admin config](https://docs.mistral.ai/vibe/code/cli/admin-config).
2. **Command-line flags** (for example, `--agent`, `--workdir`).
3. **Environment variables** (for example, `MISTRAL_API_KEY`, `VIBE_HOME`).
4. **Project** `./.vibe/config.toml`.
5. **User** `~/.vibe/config.toml`.

Results: the whole section.
```

## Answer

The **organization's admin config** wins.
The CLI applies settings in this order (highest → lowest priority):

1. Admin config
2. Command-line flags
3. Environment variables
4. Project config (`./.vibe/config.toml`)

[Configuration precedence](https://docs.mistral.ai/vibe/code/cli/configuration#precedence)

