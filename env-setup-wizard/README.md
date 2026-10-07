# Env Setup Wizard: Project Setup and Onboarding

Work out what a project needs to run (Node, Python, Go, Docker, services, env vars), compare it with your machine and write a verified one-command setup script.

## What it does

- A bundled Python script reads `.nvmrc`, `package.json` engines, `.python-version`, `pyproject.toml`, `go.mod`, `Gemfile`, `Cargo.toml`, Docker and docker-compose files, then checks which of those tools are installed on your machine and reports what is missing. Claude compares versions with simple `--version` commands.
- It lists the services and host ports in docker-compose, the environment variables the code reads that are missing from `.env.example`, example variables nobody reads, and the useful scripts and Makefile targets.
- Claude then writes a `scripts/setup.sh` (or Makefile target) and the README setup section, and runs it to prove that a fresh clone works.

## Use it

- `/env-setup-wizard:env-audit`
- `/env-setup-wizard:env-setup`
- Or ask: "Why does this repo not start on my machine?"

## Requirements

Python 3.

## Data

Runs locally. It reads variable names only and never prints their values. The script runs no other program. The plugin sends nothing anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
