---
name: usage
description: Report token use and estimated cost per agent for a Claude Code session, with peak context and cache-rewrite spikes. Use to check a Spec Kit run or to compare two runs.
argument-hint: "<session-id | path to .jsonl>"
---

# Usage report

Run `speckit-usage $ARGUMENTS`. If the user gives no argument, ask for the session ID. The ID is the file name of the `.jsonl` file under `~/.claude/projects/<project>/`.

The script prints, for the main session and each subagent: turns, peak context, cache writes, cache reads, spikes above 150K tokens, and an estimated cost in dollars. The cost is a rough API-equivalent figure. It is not your subscription quota.

After the table, give the user these facts:
1. Which agents passed the context ceiling (150K for subagents, 120K for the coordinator).
2. Which agents cost the most, and which model each ran on.
3. Any spike above 150K. A spike means a long idle gap rewrote the cache.
4. Whether the coordinator share of the total cost is above 25%.
