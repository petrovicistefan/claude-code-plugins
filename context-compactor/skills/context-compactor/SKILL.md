---
name: context-compactor
description: "Use when a long Claude Code session slows down or nears the context limit, or before a large task, to keep only the context that is still needed."
---

# Context Compactor

Keep the conversation context small so long sessions stay fast and accurate.

## Read less in the first place

- Search before reading: use Grep or Glob to find the exact place, then read only that range of lines.
- For large files, read the part you need (offset and limit) instead of the whole file.
- For logs and command output, filter first: `tail -n 100`, `grep -n ERROR`, `head`.
- Do not read lockfiles, build output, minified files, `node_modules`, or generated code unless the task is about them.
- Delegate wide searches to a subagent when one is available, so only its conclusion enters the main context.

## When the session gets long

1. Write a short state summary in the chat: goal, decisions made, files changed, open problems, next step.
2. Tell the user they can run `/compact` with that summary as focus, for example `/compact keep the auth refactor plan and the failing test names`, or `/clear` and paste the summary when switching to an unrelated task.
3. After compacting, re-read only the files needed for the next step.

## Handoff note

When the user asks, save the state summary to a file such as `NOTES.md` or `.claude/handoff.md` so a new session can pick up the work.

Do not claim to free memory or close editor tabs; the context changes only through `/compact`, `/clear` or a new session.
