# Env Setup Wizard: Get a Repo Running Locally

Find out what a freshly cloned project needs in order to run, and set it up step by step.

## What it does

A bundled Python script reads the project's manifests and lockfiles and reports: the runtime versions it asks for (`.nvmrc`, `.python-version`, `go.mod`, `.tool-versions`, `engines`) and whether each tool is installed, which package manager the lockfile points to, whether dependencies are installed, which keys from `.env.example` are missing in your `.env`, the Docker Compose services, and the start, test and migration commands it finds. Claude then compares real versions, gives an ordered checklist and, after you agree, runs the safe steps such as installing dependencies and copying `.env.example` to `.env`.

## Use it

- `/env-setup-wizard:setup`
- Or ask: "I just cloned this repo, get it running."

## Requirements

Python 3. The script uses only the standard library.

## Data

Everything runs locally. Nothing is sent anywhere. The script reads only the names of keys in `.env` files and never prints their values. It does not overwrite an existing `.env` and does not run `sudo`.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
