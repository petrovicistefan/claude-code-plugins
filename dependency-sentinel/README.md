# Dependency Sentinel: Vulnerability and License Scanner

Find known vulnerabilities and license risks in the exact dependency versions your project uses, and fix them safely.

## What it does

- A bundled Python script reads your lockfiles (npm, yarn, pnpm, pip, Poetry, uv, Pipenv, Go, Cargo, Bundler, Composer) and checks every exact version against the public OSV.dev vulnerability database. It reports severity, CVE, summary and the versions that fix each issue.
- Claude judges each finding by real risk (production or dev, reachable or not) and applies the smallest safe upgrade or override, then runs your tests.
- A second script lists the licenses of installed npm and Python packages and flags strong copyleft, non-commercial and missing licenses.

## Use it

- `/dependency-sentinel:dep-scan`
- `/dependency-sentinel:dep-licenses`
- Or ask: "Is it safe to add this package?"

## Requirements

Python 3 and a lockfile. The license check needs dependencies installed (`node_modules` or a virtualenv).

## Data

The vulnerability scan sends package names, versions and ecosystems to the OSV.dev API (api.osv.dev, run by Google). No source code, file contents or credentials are sent. Use `--offline` to see the list without sending it. The license check runs locally.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
