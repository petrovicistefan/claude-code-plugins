# Context Compactor: Faster Long Sessions

Keep long Claude Code sessions fast and under the context limit, and get the exact `/compact` command that keeps what matters.

## What it does

It teaches Claude to read less: search before opening files, read only the needed line ranges, filter logs before reading them and skip lockfiles and build output. When a session gets long, Claude writes a short state summary (goal, decisions, changed files, open problems, next step) and gives you the exact `/compact` command to keep what matters, or saves a handoff note for a new session.

## Use it

- `/context-compactor:compact-plan`
- Or ask: "The session is getting slow, what should we keep?"

## Data

The plugin only contains instructions for Claude. It runs no code and sends nothing anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
