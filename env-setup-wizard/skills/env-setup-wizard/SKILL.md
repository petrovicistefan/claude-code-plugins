---
name: env-setup-wizard
description: "Use when a project will not start, a new developer is onboarding, or a setup script or README setup section is needed, to find what is missing and write a verified setup."
---

# Env Setup Wizard

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Make a project easy to start: find what it needs, compare with this machine, and leave behind a setup that works from a clean clone.

## 1. Audit

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/env_audit.py          # current folder
python3 ${CLAUDE_SKILL_DIR}/scripts/env_audit.py services/api
```

The report lists required tools with the version the project wants and whether each is on PATH (the script does not run them; run `node --version`, `python3 --version` and so on yourself to compare versions), compose services and ports, environment variables that the code reads but `.env.example` lacks (and the reverse), and the project scripts. Variable names only; values are never printed. Do not open real `.env` files; if the user wants a value checked, ask them to confirm it exists.

## 2. Fix the gaps

- Missing tool: tell the user the install command for their OS (nvm, pyenv, brew, apt); install it only if asked.
- Variables read but not in `.env.example`: add them with an empty or safe placeholder value and a one-line comment on what they are and where to get them. Never invent real-looking secrets.
- Version files disagree (for example `.nvmrc` says 18 and `engines` says 20): point it out and ask which one is right before changing either.
- Ports already in use on the host (`lsof -i :PORT`): report and suggest a different host port in an override file.

## 3. Write the setup

Create `scripts/setup.sh` (or a `make setup` target if the project already has a Makefile) that is:

- **Idempotent**: safe to run twice. Check before install (`command -v`, existing `.env`).
- **Fail-fast**: `set -euo pipefail` and clear messages naming the missing tool and how to install it.
- **Complete**: right language version check, dependency install with the lockfile (`npm ci`, `pip install -r`, `bundle install`), `cp -n .env.example .env`, start of services (`docker compose up -d --wait`), database migrate and seed if the project has those scripts, and a final smoke check (a health URL or a test command).
- **Free of secrets**: it copies the example file and tells the user which values to fill in.

Add a "Getting started" section to the README with the single command, the prerequisites and the URL to open.

## 4. Prove it

Run the script. For a strong test, do it in a clean state: `git clone` to a temp folder (or `git worktree add`) and run only what the README says. Fix whatever breaks, and report honestly what you could not verify (for example, steps that need credentials or a Docker daemon that is not running).
