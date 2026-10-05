# Legacy Refactor Pilot: Safe Code Modernization

Modernize legacy code step by step, with tests and type checks after every change.

## What it does

Claude surveys dependency versions, deprecation warnings, outdated patterns and test coverage, then writes a plan with the order, risk and verification of each step and waits for your agreement. Where tests are missing it proposes characterization tests first. It changes one kind of thing at a time, follows official migration guides and codemods for framework upgrades, and runs your type checker, linter and tests after every step, stopping if anything breaks.

## Use it

- `/legacy-refactor-pilot:modernize`
- `/legacy-refactor-pilot:modernize upgrade React 16 to 18`

## Data

Works on your local files with your own tools. The plugin sends nothing to any external service.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
