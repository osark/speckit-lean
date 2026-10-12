---
name: setup
description: Set the one user setting that speckit-lean cannot set from a plugin, the 1-hour subagent prompt cache. Use when the user asks to set up or check speckit-lean.
disable-model-invocation: true
---

# Set up speckit-lean

A plugin cannot set `subagentPromptCacheTtl`. This setting gives subagents a 1-hour prompt cache instead of 5 minutes. The longer cache avoids full-context rewrites when an agent waits.

1. Run `speckit-lean-setup` with no arguments. It shows the current value and the change.
2. Tell the user the cost: each subagent cache write costs 2x instead of 1.25x. Short agents that never wait pay this extra for nothing.
3. Tell the user the setting does nothing while their subscription draws on usage credits.
4. Ask the user to confirm. Do not continue without a yes.
5. If the user confirms, run `speckit-lean-setup --apply`. The script saves a backup first.
6. Tell the user the change applies to the next session.
