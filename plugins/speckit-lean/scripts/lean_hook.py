#!/usr/bin/env python3
"""Hook handler for speckit-lean. Usage: lean_hook.py <session|prompt|tool|bash>

Reads the hook JSON from stdin. Never fails the session: on any error it exits 0 silently.
It acts only in Spec Kit projects (a `.specify` directory in the project tree).
"""
import json, os, re, sys

TAIL_BYTES = 262_144


def cfg(name, default):
    raw = os.environ.get("CLAUDE_PLUGIN_OPTION_" + name.upper())
    try:
        return type(default)(raw) if raw not in (None, "") else default
    except ValueError:
        return default


def is_speckit_project(cwd):
    d = os.path.abspath(os.environ.get("CLAUDE_PROJECT_DIR") or cwd or ".")
    while True:
        if os.path.isdir(os.path.join(d, ".specify")):
            return True
        parent = os.path.dirname(d)
        if parent == d:
            return False
        d = parent


def last_context(path):
    """Context size of the newest assistant turn in a transcript file, or None."""
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            f.seek(max(0, size - TAIL_BYTES))
            lines = f.read().decode("utf-8", "ignore").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if '"usage"' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        m = d.get("message")
        if isinstance(m, dict) and m.get("role") == "assistant" and m.get("model") != "<synthetic>":
            u = m.get("usage") or {}
            return (u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                    + u.get("cache_read_input_tokens", 0))
    return None


def subagent_transcript(main_path, agent_id):
    base = main_path[:-6] + "/subagents/"
    p = base + "agent-" + agent_id + ".jsonl"
    if os.path.isfile(p):
        return p
    try:
        for name in os.listdir(base):
            if agent_id in name and name.endswith(".jsonl"):
                return base + name
    except OSError:
        pass
    return None


def state_path(key):
    root = os.environ.get("CLAUDE_PLUGIN_DATA") or "/tmp"
    os.makedirs(root, exist_ok=True)
    return os.path.join(root, "warned-" + re.sub(r"[^A-Za-z0-9_-]", "_", key) + ".txt")


def should_warn(key, ctx, step):
    """True once per `step` tokens of growth, so a warning does not repeat every turn."""
    p, bucket = state_path(key), ctx // step
    try:
        last = int(open(p).read().strip() or 0)
    except (OSError, ValueError):
        last = 0
    if bucket <= last:
        return False
    try:
        open(p, "w").write(str(bucket))
    except OSError:
        pass
    return True


def emit(obj):
    print(json.dumps(obj))


def do_session(inp):
    if not is_speckit_project(inp.get("cwd")):
        return
    tip = ""
    settings = os.path.expanduser("~/.claude/settings.json")
    try:
        if "subagentPromptCacheTtl" not in json.load(open(settings)):
            tip = " Tip: run /speckit-lean:setup to set the 1-hour subagent cache."
    except (OSError, ValueError):
        pass
    emit({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": (
        "Spec Kit Lean is active. Use the speckit-lean:* agents: scout and waiter (small model), "
        "specifier, tasker, implementer, reviewer, amender (changes to an existing plan), "
        "planner (new features only). One agent per stage and one per task phase. "
        "Restart this coordinator session near %dK tokens and resume from the coordination files. "
        "Load the speckit-lean:coordinator skill for the full rules." % (cfg("coordinator_ceiling", 120000) // 1000)
        + tip)}})


def do_prompt(inp):
    if inp.get("agent_id") or not is_speckit_project(inp.get("cwd")):
        return
    ctx = last_context(inp.get("transcript_path", ""))
    ceiling = cfg("coordinator_ceiling", 120000)
    if ctx is None or ctx < ceiling or not should_warn("main-" + inp.get("session_id", ""), ctx, 40000):
        return
    msg = ("Context is %dK tokens, over the %dK ceiling. Every turn now pays for this context. "
           "Write state to the coordination files, then restart the session." % (ctx // 1000, ceiling // 1000))
    emit({"systemMessage": "speckit-lean: " + msg,
          "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": msg}})


def do_tool(inp):
    agent_id = inp.get("agent_id")
    if not agent_id or not is_speckit_project(inp.get("cwd")):
        return
    path = subagent_transcript(inp.get("transcript_path", ""), agent_id)
    ctx = last_context(path) if path else None
    ceiling = cfg("subagent_ceiling", 150000)
    if ctx is None or ctx < ceiling or not should_warn("sub-" + agent_id, ctx, 20000):
        return
    emit({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": (
        "Your context is %dK tokens, over the %dK ceiling. Commit your work, write one checkpoint line "
        "(what is done, what is next), and end your run now. The coordinator starts a fresh agent."
        % (ctx // 1000, ceiling // 1000))}})


POLL = re.compile(r"\b(until|while)\b.*\bsleep\b", re.S)
LONG_SLEEP = re.compile(r"\bsleep\s+(\d+)\b")


def do_bash(inp):
    if not inp.get("agent_id") or cfg("wait_guard", "deny") != "deny" or not is_speckit_project(inp.get("cwd")):
        return
    ti = inp.get("tool_input") or {}
    if ti.get("run_in_background"):
        return
    cmd = ti.get("command", "")
    long_timeout = (ti.get("timeout") or 0) > 270000
    long_sleep = any(int(s) >= 270 for s in LONG_SLEEP.findall(cmd))
    if (POLL.search(cmd) and long_timeout) or long_sleep:
        emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
              "permissionDecisionReason": (
                  "Blocked by speckit-lean: a foreground wait over 270 seconds lets the prompt cache expire, "
                  "and the next turn pays for the whole context again. Run the command with "
                  "run_in_background and write output to a log file, then hand the wait to the "
                  "speckit-lean:waiter agent, or poll with commands that end in 270 seconds or less.")}})


def main():
    try:
        inp = json.load(sys.stdin)
        {"session": do_session, "prompt": do_prompt, "tool": do_tool, "bash": do_bash}[sys.argv[1]](inp)
    except Exception:
        pass


main()
