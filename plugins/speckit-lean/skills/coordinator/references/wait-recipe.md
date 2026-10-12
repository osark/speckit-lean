# Wait recipe for long commands

Use this for any command that runs longer than 270 seconds: an eval, an ingest, a model pull, a full test run.

1. Start the command in the background. Send all output to a log file:
   `<command> > /tmp/<name>.log 2>&1 &`
2. Spawn `speckit-lean:waiter`. Give it the log path, the process to watch, and the success pattern.
3. The waiter checks the log at most every 4 minutes. It returns the exit status, the last 10 log lines, and every FAIL or ERROR line.
4. Continue from that short result. Read more of the log only with `grep -n FAIL <log> | head -20`.

Never use `until ...; do sleep` loops with a timeout over 270 seconds. A hook blocks them in subagents.
