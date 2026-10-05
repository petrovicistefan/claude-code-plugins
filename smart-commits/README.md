# Smart Commits: Git Commit Message Generator

Generate clear git commit messages from your staged diff, in Conventional Commits format and in your repository's own style.

## What it does

Claude reads `git status`, the staged diff and your recent history so the message matches your project's style. It picks the type and scope, flags breaking changes, suggests splitting mixed changes into separate commits and warns about files that look like secrets. It shows the message and commits only after you confirm. It never pushes on its own.

## Use it

- `/smart-commits:commit` to write and commit
- `/smart-commits:commit-message` to draft only

## Requirements

Git.

## Data

Runs locally with your git repository. The plugin sends nothing to any external service.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
