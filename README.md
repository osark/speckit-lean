# speckit-lean

A Claude Code plugin that cuts the token cost of Spec Kit runs. It works in any repo that has a `.specify/` directory. It has no project-specific code.

Built from measured data on two real specs. Read [`why.md`](plugins/speckit-lean/skills/coordinator/references/why.md) for the evidence.

## What it adds

| Part | What it does |
|---|---|
| 8 agents | `scout` and `waiter` (small model), `specifier`, `tasker`, `implementer`, `reviewer`, `amender` (medium model), `planner` (large model). |
| SessionStart hook | Injects the lean rules into any branch of a Spec Kit repo. |
| UserPromptSubmit hook | Warns the coordinator when its context passes 120K tokens. |
| PostToolUse hook | Tells a subagent to checkpoint and end when its context passes 150K tokens. |
| PreToolUse hook | Blocks `until ... sleep` polling loops in subagents. |
| `speckit-lean:coordinator` skill | The rules, the wait recipe, and a lean prompt block. |
| `speckit-lean:usage` skill and `speckit-usage` command | Token and cost report per agent, from the session logs. |
| `speckit-lean:setup` skill | Sets `subagentPromptCacheTtl` to `1h` after you confirm. |

## Install

The repository is public. Each team member installs the plugin from GitHub.

1. Add the marketplace:

   ```bash
   claude plugin marketplace add osark/speckit-lean
   ```

2. Install the plugin:

   ```bash
   claude plugin install speckit-lean@arkdev-tools
   ```

3. Restart Claude Code.
4. In a session, run `/speckit-lean:setup`. A plugin cannot set `subagentPromptCacheTtl`, so the setup skill does it for you after you confirm.

If you also have user-level agents named `speckit-*` in `~/.claude/agents/`, delete them after you install the plugin. The plugin agents replace them under the names `speckit-lean:<agent>`.

To test a local copy, add the marketplace from the path of your clone. For example: `claude plugin marketplace add ./speckit-lean`.

## Share with a team

Option 1: Send the install steps above to each team member.

Option 2: Add the marketplace to a project, so Claude Code offers the plugin to everyone who opens it. Put this in the `.claude/settings.json` file of the project and commit the file:

```json
{
  "extraKnownMarketplaces": {
    "arkdev-tools": { "source": { "source": "github", "repo": "osark/speckit-lean" } }
  },
  "enabledPlugins": { "speckit-lean@arkdev-tools": true }
}
```

Each team member must trust the project folder. Each team member must still run `/speckit-lean:setup`, because the setting is per user.

## Update

Team members get changes from the `master` branch on GitHub. Run these commands to update:

```bash
claude plugin marketplace update arkdev-tools
claude plugin update speckit-lean@arkdev-tools
```

Before you publish a change, push your commits to `origin`. Increase the `version` in `plugins/speckit-lean/.claude-plugin/plugin.json`, so that Claude Code detects the update.

## Settings

Claude Code asks for these when you enable the plugin.

| Option | Default | Meaning |
|---|---|---|
| `coordinator_ceiling` | 120000 | Context size at which the main session gets a warning. |
| `subagent_ceiling` | 150000 | Context size at which a subagent gets told to end. |
| `wait_guard` | `deny` | `deny` blocks polling loops in subagents. `off` allows them. |

## Limits

- The ceilings use the size of the last assistant turn in the transcript. A hook runs after a tool call. A very large single turn can pass the ceiling before the warning arrives.
- The warnings are advice to the model. A subagent can ignore them. The 8-task phase limit in `tasker` is the more reliable control.
- The cost figures are rough API-equivalent estimates. They are not your subscription quota.
- Hooks run on every tool call. They read only the last 256 KB of a transcript, and they exit silently on any error.

## Layout

```text
.claude-plugin/marketplace.json
plugins/speckit-lean/
  .claude-plugin/plugin.json
  agents/        8 agent files
  hooks/hooks.json
  scripts/lean_hook.py
  bin/           speckit-usage, speckit-lean-setup
  skills/        coordinator, usage, setup
```

## License

MIT. Copyright (c) 2026 ArkDev.
