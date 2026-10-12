# Lean prompt block

Paste this at the end of every subagent prompt. It replaces loading a long writing-style skill. The skill body costs about 6K tokens on every turn. This block costs under 300.

```text
Writing rules for all prose (chat, docs, comments, commit messages):
- Use short sentences: 20 words for instructions, 25 for explanations.
- Give one instruction per sentence. Put the condition first.
- Use active voice. Use "must", "can", "will". Do not use "should" or "may".
- Use one word for one meaning (for example "check", not "verify").
- Do not use filler such as "simply", "just", "ensure", or "leverage".
- Do not change code, identifiers, commands, file paths, or quoted output.
```
