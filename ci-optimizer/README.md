# CI Optimizer: Faster GitHub Actions and GitLab CI

Make your CI pipelines faster, cheaper and safer, based on your real workflow files and run times.

## What it does

- A bundled Python script checks GitHub Actions and GitLab CI files for missing dependency caches, `npm install` instead of `npm ci`, no `concurrency` cancel, no path filters, missing timeouts and artifact retention, expensive runners, unpinned actions, missing `permissions` and script injection risks.
- With the GitHub CLI, Claude reads recent runs to find the slowest jobs and steps, the critical path and tests that fail and then pass on retry.
- Claude then proposes workflow changes in order of safety and shows the expected saving from measured step times.

## Use it

- `/ci-optimizer:ci-check`
- `/ci-optimizer:ci-timings .github/workflows/ci.yml`
- Or ask: "Why is our CI so slow?"

## Requirements

Python 3. For run times and flaky tests on GitHub, the `gh` CLI signed in to your account.

## Data

The workflow check runs locally. `/ci-optimizer:ci-timings` uses your own `gh` CLI to read workflow runs and logs from GitHub with your credentials. The plugin sends nothing anywhere else.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
