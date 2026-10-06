# Code Metrics: Complexity and Duplication Report

See where your code is complex, long or duplicated, decide what to refactor first and track the numbers over time.

## What it does

- A bundled Python script reports code lines, functions, average and maximum cyclomatic complexity, the most complex and longest functions, the largest files and duplicated blocks of code.
- Python is measured exactly; JavaScript, TypeScript, Java, Kotlin, C#, Go, PHP, Rust, Swift, C and C++ are measured by counting branches in each function.
- Save a snapshot and compare later to see whether totals went up and which functions got more complex. Claude combines complexity with git change frequency to pick the refactoring that pays off.

## Use it

- `/code-metrics-tracker:metrics` or `/code-metrics-tracker:metrics src`
- `/code-metrics-tracker:refactor-targets`
- Or ask: "Which parts of this codebase are the most complex?"

## Requirements

Python 3. The script uses only the standard library.

## Data

Everything runs locally. Nothing is sent anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
