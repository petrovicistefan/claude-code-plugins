# Privacy Policy

Last updated: 3 October 2026

This policy covers the Claude Code plugins published by Stefan Petrovici in this repository.

## What the plugins collect

Nothing. The author does not run any server for these plugins and receives no data, analytics or telemetry from them.

## What stays on your machine

Most plugins only contain instructions for Claude and small scripts that run locally on your files. Anything they create stays in your project, for example:

- `project-memory` stores memories in `.project-memory/memory.db` in your project
- `task-observer` writes preferences to `CLAUDE.md` or `CLAUDE.local.md`, only after you agree
- `bundle-size-sentinel`, `headroom`, `i18n-sync`, `env-protector` and `responsive-check` write reports or screenshots only to the folders you choose
- `code-metrics-tracker`, `test-coverage-intelligence`, `dependency-sentinel` and `perf-profiler` write snapshots or reports only to the files you name

## Third-party services

Some plugins use services that you connect and sign in to yourself. Data goes directly from your machine to that service under its own terms and privacy policy:

| Plugin | Service | Data sent |
|---|---|---|
| exa-search | Exa (mcp.exa.ai) | Search queries and URLs to fetch |
| figma-to-code | Figma (mcp.figma.com) | Requests for the Figma files and frames you link |
| rls-schema-explorer | Supabase (mcp.supabase.com), read-only | Schema and read-only query requests for your project |
| aws-cost-guard | AWS and your Kubernetes cluster, through your own CLI tools | Read-only API calls with your own credentials |
| pr-story-aligner | GitHub, through your own `gh` CLI | Requests for the issues and pull requests you name |
| ci-optimizer | GitHub, through your own `gh` CLI | Requests for workflow runs and logs of your repository |
| iac-reviewer | Your cloud provider, through your own `terraform` or `tofu` CLI, only for `plan` | Read-only plan requests with your own credentials |
| dependency-sentinel | OSV.dev (api.osv.dev, run by Google) | Package names, versions and ecosystems from your lockfiles. No code or credentials |
| perf-profiler | Google PageSpeed Insights (googleapis.com), only with `--psi` | The public URL you ask it to test, and your API key if you provide one |

Your conversations with Claude are handled by Anthropic under Anthropic's own privacy policy.

## Contact

Questions about this policy: email hello@petrovicistefan.ro or open an issue at https://github.com/petrovicistefan/claude-code-plugins/issues
