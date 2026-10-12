# Why these rules exist

Measured on a real Spec Kit project (Spec 012 and Spec 013, Oct 2026). Costs are rough API-equivalent estimates.

| Problem | Evidence | Rule |
|---|---|---|
| One agent held plan, tasks, implement, and eval | Peak context 454K, 12.6M cache-write tokens, about $43 | One agent per stage and per task phase |
| Idle waits expired the 5-minute cache | 31 full rewrites of 280K to 450K tokens | 270-second wait limit, background commands, waiter agent |
| Coordinator ran for hours in one session | Grew from 50K to 428K tokens, 38% of the spec cost | Restart at 120K, resume from files |
| Amendments planned on the largest model | 6 Opus planners cost 36% of one session | `amender` on a medium model |
| Rules lived only on one branch | The working branch never saw them | A SessionStart hook injects the rules in any branch |
| Written ceilings were not followed | 4 subagents passed 150K | Hooks tell the agent when it passes the ceiling |

After the fixes: no subagent cache spike above 150K, and the largest subagent cost fell from about $43 to about $5.
