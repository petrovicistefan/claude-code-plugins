---
name: smart-commits
description: "Use when committing changes, to write a clear conventional commit message from the staged diff."
---

# Smart Commits

Write commit messages that say what changed and why, based on the real diff.

## 1. Read the changes

```bash
git status --short
git diff --cached --stat
git diff --cached
```

If nothing is staged, show `git status` and ask the user which files to stage. Do not stage everything on your own. Never commit files that look like secrets (`.env`, `*.pem`, `credentials.*`); warn the user instead.

Read `git log --oneline -10` to match the project's existing style (Conventional Commits, ticket prefixes, language, capitalization).

## 2. Write the message

Default format, unless the project uses another one:

```
<type>(<scope>): <summary in imperative mood, max 72 chars>

<why the change was needed, and anything a reviewer must know>

<footer: BREAKING CHANGE: ..., Refs #123>
```

- `type`: feat, fix, refactor, perf, test, docs, build, ci, chore
- `scope`: the main area touched, taken from paths (`auth`, `api`, `ui`)
- The summary says what the change does, not which files changed
- The body explains why. Skip it for trivial changes
- Add `BREAKING CHANGE:` when a public API, config or schema changes incompatibly
- If the diff mixes unrelated changes, suggest splitting it into separate commits and say which files go where

## 3. Commit

Show the message and ask before running `git commit`. Use a heredoc so newlines survive:

```bash
git commit -F - <<'EOF'
<message>
EOF
```

Never push, amend published commits or use `--no-verify` unless the user asks.
