---
name: project-memory
description: "Use when the user asks Claude to remember, recall or forget a project fact, decision or convention across sessions, or at the start of work on a project that has stored memories."
---

# Project Memory

Keep project facts across sessions in a local SQLite database at `.project-memory/memory.db` in the project root.

All operations go through one script:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/mem.py <command> [args]
```

| Command | Use |
|---|---|
| `add <key> <text> [--tag TAG]` | Store or update a memory |
| `get <key>` | Show one memory |
| `search <words>` | Find memories whose key, text or tag contains all the words |
| `list [--tag TAG]` | List memories, newest first |
| `forget <key>` | Delete one memory |

## When to store

Store a memory when the user says "remember", or when they state a lasting fact: an architecture decision and its reason, a naming convention, an environment detail, a command that must be used. Use a short kebab-case key (`auth-strategy`, `deploy-command`) and a one or two sentence text. Use tags such as `decision`, `convention`, `env`.

Never store passwords, API keys, tokens or personal data. If the user asks, explain that and suggest a password manager or `.env` file instead.

Tell the user what you stored.

## When to recall

- At the start of work on a project with a `.project-memory/` folder, run `list` once and use what is relevant.
- Before answering a question about past decisions, run `search`.
- Say when an answer comes from memory, so the user can correct stale facts with `add` or `forget`.

## Housekeeping

The first `add` creates `.project-memory/` and adds a `.gitignore` inside it so memories are not committed. If the user wants to share memories with the team, they can delete that `.gitignore`.
