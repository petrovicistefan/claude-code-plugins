# Project Memory: Long-Term Memory for Claude Code

Give Claude Code long-term memory per project, so you stop re-explaining decisions and conventions in every session.

## What it does

Claude stores short facts in a SQLite database at `.project-memory/memory.db` in your project, using a small bundled Python script. It saves a memory when you ask it to remember something or state a lasting decision, searches memories before answering questions about past choices, and lists them when you start work on the project. You can update or delete any memory. The folder is git-ignored by default. Claude refuses to store secrets.

## Use it

- `/project-memory:remember we use pnpm, never npm`
- `/project-memory:recall deploy`
- Or say: "Remember that the staging database is read-only."

## Requirements

Python 3. The script uses only the Python standard library.

## Data

Memories stay in a file inside your project. Nothing is sent anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
