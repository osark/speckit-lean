---
name: coordinator
description: Rules for a coordinator session that runs Spec Kit specs through subagents with low token cost. Load at the start of a coordinator session, or before spawning spec subagents.
---

# Lean coordinator rules

You coordinate Spec Kit work through subagents. The quota is shared by the coordinator and every subagent. These rules keep the cost low. The data behind them is in `references/why.md`.

## Pick the agent

| Work | Agent | Model |
|---|---|---|
| Search, summarize, check code against spec | `speckit-lean:scout` | small |
| Run or watch a long command | `speckit-lean:waiter` | small |
| New spec, clarify | `speckit-lean:specifier` | medium |
| Plan for a NEW feature | `speckit-lean:planner` | large |
| Change to an existing spec, plan, or tasks | `speckit-lean:amender` | medium |
| Tasks, analyze | `speckit-lean:tasker` | medium |
| One task phase | `speckit-lean:implementer` | medium |
| Converge, review | `speckit-lean:reviewer` | medium |

Do not use the built-in `Explore` agent for Spec Kit searches. Use `scout`.

## Run the stages

1. Use one agent per stage: specify, plan, tasks. Use one agent per task phase in implement.
2. Pass state through files: `tasks.md` check marks and the coordination file. Do not pass state through a long context.
3. Give each agent a short prompt. Name the feature directory, the stage, and the phase.
4. End each subagent prompt with the block in `references/lean-prompt.md`.
5. Start a new agent for the next phase. Do not resume a finished one.

## Control context

1. A hook warns each subagent at its ceiling (150K tokens by default). The subagent commits, writes a checkpoint, and ends. Start a fresh agent from that checkpoint.
2. A hook warns this session at 120K tokens. When you see the warning, write state to the coordination files and tell the user to restart the session.
3. `tasker` must split phases to at most 8 tasks and under 120K tokens of work. If a phase is larger, ask `tasker` to split it.

## Control waits

1. A prompt cache lasts 5 minutes unless the user set 1 hour. A longer idle wait makes the next turn pay for the full context.
2. Run long commands in the background. Follow `references/wait-recipe.md`.
3. A hook blocks `until ... sleep` polling loops in subagents.

## Run work in parallel

1. Run up to 3 `scout` agents at once for read-only work. Each returns 15 lines or fewer.
2. Run tasks marked `[P]` as parallel implementers, at most 2 at once, each in its own worktree.
3. Parallel runs save time, not quota.

## Measure

Run the `speckit-lean:usage` skill after each spec. Targets: peak context under 150K per subagent, no spike above 150K, coordinator share under 25% of cost.
