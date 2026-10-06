# Test Coverage Intelligence: Risk-Ranked Coverage Gaps

Find the untested code that matters most and write tests for it, instead of chasing a coverage percentage.

## What it does

- A bundled Python script reads lcov, Cobertura XML (pytest-cov, .NET), Istanbul JSON, JaCoCo XML and Go cover profiles and ranks files by uncovered lines weighted by how often each file changed in git.
- It lists files with no coverage, often-changed files no test loads, and for one file the uncovered line ranges and the functions no test calls.
- Claude writes tests in your existing style for the riskiest branches, re-runs coverage to show the gain, and can track coverage over time or suggest mutation testing for critical code.

## Use it

- `/test-coverage-intelligence:coverage-gaps` or `/test-coverage-intelligence:coverage-gaps coverage/lcov.info`
- `/test-coverage-intelligence:suggest-tests src/billing/charge.ts`
- Or ask: "What should we test next?"

## Requirements

Python 3 and your test runner with coverage enabled.

## Data

Everything runs locally. Nothing is sent anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
