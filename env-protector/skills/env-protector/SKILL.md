---
name: env-protector
description: "Use before reading .env or config files, before committing, or when the user asks to check a project for leaked API keys, passwords or tokens."
---

# Env Protector

Keep secrets out of the conversation and out of git.

## Rules while working

- Do not open `.env`, `.env.*` (except `.env.example`), `*.pem`, `*.key`, `id_rsa*`, `credentials*`, `secrets.*` or `*.tfvars` unless the user explicitly asks. If you need to know which variables exist, read `.env.example` or list only the names:
  ```bash
  python3 ${CLAUDE_SKILL_DIR}/scripts/scan_secrets.py --env-names .env
  ```
- Never echo, print or paste a secret value. When referring to one, use the variable name, or a masked form like `sk_live_****9f2a`.
- Never put secrets into code, commit messages, logs or examples. Use environment variables instead.

## Scan for leaked secrets

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/scan_secrets.py [path]          # whole project
python3 ${CLAUDE_SKILL_DIR}/scripts/scan_secrets.py $(git diff --cached --name-only --diff-filter=ACM)   # staged files
```

The script finds common key formats (AWS, GitHub, Stripe, Slack, Google, OpenAI, Anthropic, private keys, JWTs, passwords in URLs, generic `secret = "..."` assignments). It prints file, line and rule with the value masked, and exits with code 1 when it finds something.

## When something is found

1. Tell the user the file, line and type, never the value.
2. Move the value to an environment variable and add the variable name to `.env.example`.
3. Make sure `.env` and similar files are in `.gitignore`.
4. If the secret was ever committed or pushed, say that removing it from the code is not enough: the key must be revoked and rotated at the provider.
