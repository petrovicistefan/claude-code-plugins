# Security Policy

## Supported versions

Only the latest version of each plugin on the `main` branch is supported. Fixes are released there.

## Reporting a vulnerability

Please do not open a public issue for a security problem.

Report it privately in one of these ways:

- Use [private vulnerability reporting](https://github.com/petrovicistefan/claude-code-plugins/security/advisories/new) on this repository.
- Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro).

Please include:

- the name of the plugin
- what the problem is and how to reproduce it
- the impact you expect, for example secrets exposed, files changed or data sent to a third party

You will get a first reply within 7 days. If the report is confirmed, I will work on a fix and credit you in the release notes unless you prefer to stay anonymous.

## Scope

These plugins are Markdown instructions and small local scripts. Reports about the following are in scope:

- scripts that run commands or read files in ways the plugin's README does not describe
- data sent to a third party that the README does not list
- instructions that could make an agent leak secrets or run destructive commands

Problems in Claude Code, Cursor, other agents or the third-party services some plugins connect to (Exa, Figma, Supabase, OSV.dev, PageSpeed Insights) should be reported to their own vendors.
