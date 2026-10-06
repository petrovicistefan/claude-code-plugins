---
name: test-coverage-intelligence
description: "Use when asked what to test next, where test coverage is weak, to read a coverage report, to raise coverage meaningfully, or to check test quality with mutation testing."
---

# Test Coverage Intelligence

Find the untested code that matters most and write tests for it, instead of chasing a coverage percentage.

## 1. Get a coverage report

Use the project's existing test command with coverage. Common ones:

| Stack | Command | Report |
|---|---|---|
| Jest | `npx jest --coverage --coverageReporters=lcov` | `coverage/lcov.info` |
| Vitest | `npx vitest run --coverage --coverage.reporter=lcov` | `coverage/lcov.info` |
| Node test runner | `node --test --experimental-test-coverage --test-reporter=lcov --test-reporter-destination=lcov.info` | `lcov.info` |
| pytest | `pytest --cov --cov-branch --cov-report=xml` | `coverage.xml` |
| Go | `go test ./... -coverprofile=cover.out` | `cover.out` |
| JVM | JaCoCo report task | `build/reports/jacoco/test/jacocoTestReport.xml` |
| .NET | `dotnet test --collect:"XPlat Code Coverage"` | `coverage.cobertura.xml` |

`npx` here runs the project's own installed binaries. If the coverage provider is missing (`@vitest/coverage-v8`, `pytest-cov`), ask before installing it.

## 2. Rank the gaps

```bash
git log --since="90 days ago" --name-only --format= > /tmp/churn.txt
python3 ${CLAUDE_SKILL_DIR}/scripts/coverage_gaps.py coverage/lcov.info --churn /tmp/churn.txt
```

It prints total line and branch coverage, then files ranked by risk: uncovered lines weighted by how often the file changed. It also lists files with no coverage at all, and often-changed source files that are missing from the report entirely (no test imports them). Test files, mocks, stories and migrations are excluded.

Then look at one file in detail:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/coverage_gaps.py coverage/lcov.info --file src/billing/charge.ts
```

It prints the uncovered line ranges and the functions no test calls.

## 3. Choose what to test

Rank by consequence, not by line count. Look first at code that handles money, auth and permissions, data deletion or migration, input validation and parsing, error handling paths (`catch`, fallback branches), and date, time zone and rounding logic. Skip generated code, trivial getters, and framework glue that integration tests already cover.

## 4. Write the tests

- Follow the project's test style: same framework, folder layout, naming, fixtures and mocking approach. Read two existing tests first.
- Test behaviour through the public function or endpoint, not private details.
- Cover the uncovered branches you found: the error path, the boundary values (0, empty, maximum, negative), the invalid input, the second branch of each condition.
- One behaviour per test, with a name that says the expected result.
- Mock only external boundaries (network, clock, randomness, third-party APIs).
- Run the new tests, confirm they pass, then re-run coverage to show the change for that file.

When a test reveals a bug, stop and report it instead of writing the test to match the wrong behaviour.

## 5. Test quality (mutation testing)

Coverage shows which lines ran, not whether tests would catch a bug. If the project uses or wants mutation testing, use the standard tool for the stack (StrykerJS, mutmut, cosmic-ray, PIT, go-mutesting) on the critical files only, since full runs are slow. Surviving mutants show assertions that are missing. Ask before installing a mutation tool.

## 6. Track over time

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/coverage_gaps.py coverage/lcov.info --save .coverage-snapshot.json
python3 ${CLAUDE_SKILL_DIR}/scripts/coverage_gaps.py coverage/lcov.info --compare .coverage-snapshot.json
```

`--compare` shows the total change and the files whose coverage dropped by more than 2 points.

## Report

List the top risks with file, coverage, changes and why they matter, the tests written for each, and the coverage before and after.
