# PR Story Aligner: Pull Request vs Ticket Check

Check a pull request against its ticket's acceptance criteria before merge.

## What it does

Claude reads the ticket (a GitHub issue through the `gh` CLI, or Jira and Linear through connectors you already have or pasted text) and turns it into a numbered list of acceptance criteria. It compares them with the PR diff or local branch and marks each one as done, partial or not found, with file references and tests. It also flags changes outside the ticket's scope and missing tests, and can draft a PR description. It never posts or edits anything unless you ask.

## Use it

- `/pr-story-aligner:align 42`
- `/pr-story-aligner:align PROJ-123`

## Requirements

Git. The GitHub CLI (`gh`) for GitHub issues and PRs. A Jira or Linear connector is optional.

## Data

GitHub data is read with your own `gh` login. The plugin itself sends nothing anywhere and stores nothing.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
