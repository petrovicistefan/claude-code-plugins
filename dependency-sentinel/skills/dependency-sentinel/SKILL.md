---
name: dependency-sentinel
description: "Use when checking dependencies for known vulnerabilities (CVEs), license problems or risky packages, before adding a package, or when asked to fix npm audit or Dependabot alerts."
---

# Dependency Sentinel

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Find known vulnerabilities and license risks in the exact dependency versions a project uses, and fix them safely.

## 1. Vulnerabilities

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/osv_scan.py <project-dir>
python3 ${CLAUDE_SKILL_DIR}/scripts/osv_scan.py . --prod-only
```

The script reads lockfiles (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, pinned `requirements*.txt`, `poetry.lock`, `uv.lock`, `Pipfile.lock`, `go.sum`, `Cargo.lock`, `Gemfile.lock`, `composer.lock`) and asks the public OSV.dev database (Google's open source vulnerability database, which includes the GitHub advisories) about each exact version. For every hit it prints severity, package, version, advisory and CVE id, summary, the versions that fix it and a link. It sends only package names, versions and ecosystems. With `--offline` it only lists what it would send.

A `requirements.txt` without `==` pins has no exact versions; say so and suggest a lockfile.

## 2. Judge each finding

Severity alone is not the risk. For each finding check:

- **Is it in production?** Dev-only packages (marked `dev`) matter less unless they run in CI with secrets or in the build of shipped code.
- **Is the vulnerable code reachable?** Read the advisory: a ReDoS in a function the project never calls with user input is low risk. Search the code and the dependency tree (`npm ls <pkg>`, `pip show`, `go mod why <module>`) to see why it is installed.
- **Is there a fixed version?** If the fix is a patch or minor update inside the allowed range, it is safe to apply. A major version needs a changelog check.

## 3. Fix

- npm: update the direct dependency that pulls it in. For a transitive package with no fixed parent, use `overrides` (npm), `resolutions` (yarn) or `pnpm.overrides`, pinned to the fixed version, and note it so it can be removed later.
- Python: raise the pin and re-lock with the project's tool (`pip-compile`, `poetry lock`, `uv lock`).
- Go: `go get <module>@<fixed>` then `go mod tidy`. Rust: `cargo update -p <crate>`.
- Run the install, the tests and the build after each change. Do not run `npm audit fix --force`: it can apply breaking major upgrades.

## 4. Licenses

Install dependencies first, then:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/licenses.py <project-dir>
python3 ${CLAUDE_SKILL_DIR}/scripts/licenses.py . --site-packages .venv/lib/python3.12/site-packages --csv licenses.csv
```

It reads license fields from `node_modules` and Python virtualenvs on disk and groups packages into permissive, weak copyleft (LGPL, MPL, EPL), strong copyleft (GPL, AGPL), source-available or non-commercial (BUSL, Commons Clause, Elastic, PolyForm) and unknown. Packages with no license field need a look at their LICENSE file. Strong copyleft in software you distribute, and AGPL in any network service, should go to whoever owns licensing decisions. You are not giving legal advice; say so when the question is legal.

## 5. Before adding a package

Check it before installing: last publish date and release activity, number of maintainers, weekly downloads, open security advisories (run the scan after adding it), install scripts (`preinstall`/`postinstall` in its `package.json`), and whether the name is a near-miss of a popular package (typosquatting). Prefer the standard library or a package already in the tree.

## Report

List findings by real risk, not only by severity: what to fix now, what can wait, and what is not reachable. For each fix give the exact version change and the command.
