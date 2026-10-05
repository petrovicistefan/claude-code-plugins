---
name: legacy-refactor-pilot
description: "Use when modernizing old code: replacing deprecated APIs, upgrading a major framework or language version, or converting old patterns such as callbacks, var or class components."
---

# Legacy Refactor Pilot

Modernize old code in small, safe, verifiable steps.

## 1. Survey

- Versions in use: `package.json`, lockfile, `requirements.txt`, `pyproject.toml`, `go.mod`, `composer.json`, runtime version files
- Deprecation warnings from the build, tests or runtime
- Old patterns, for example: `var`, callbacks and `.then` chains where async/await fits, CommonJS in an ES module project, React class components and lifecycle methods, jQuery DOM code, Python 2 idioms, string-built SQL
- Test coverage of the areas to change

Write a short plan: what to change, in which order, the risk of each step and how it will be verified. Get the user's agreement before editing.

## 2. Make a safety net

If an area has no tests, propose adding characterization tests first that capture current behavior. Run the existing test suite and note the baseline (what already fails).

## 3. Change in small steps

- One kind of change per step (for example only `var` to `let`/`const`, or only one deprecated API)
- For framework upgrades, follow the official migration guide for each major version in turn and use the official codemods when they exist
- Behavior must not change unless the user asked for it
- After each step run the type checker, linter and tests. Stop and report if something breaks

## 4. Report

For each step: what changed, files touched, test results, and anything left for later. Suggest one commit per step.
