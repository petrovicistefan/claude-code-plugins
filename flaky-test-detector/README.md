# Flaky Test Detector: Find Unstable Tests

Find the tests that pass and fail at random, and fix the cause instead of re-running CI.

## What it does

Claude runs your test suite several times with a machine-readable reporter (pytest JUnit XML, Jest or Vitest JSON, `go test -json`) and saves each run to `.flaky-runs/`. A bundled Python script compares the runs and lists the tests that passed in some runs and failed in others, with the failure rate and the first error line. Tests that fail every time are listed apart as broken. For each flaky test Claude reads the code, names the likely cause (timing, shared state, time or randomness, environment) and proposes a fix. After you approve a fix it re-runs that test 20 times to prove it.

## Use it

- `/flaky-test-detector:flaky`
- `/flaky-test-detector:flaky 10 tests/api`
- Or ask: "Which of our tests are flaky?"

## Requirements

Python 3 for the comparison script (standard library only), and your project's own test runner.

## Data

Everything runs locally. Nothing is sent anywhere. Results are written to `.flaky-runs/` in your project, which Claude deletes when it is done unless you ask to keep it. Claude asks before editing any test.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
