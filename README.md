# Claude Code Plugins by Stefan Petrovici

Thirty-three focused plugins for Claude Code that cover everyday development work: API types and docs, cloud costs, bundle size, commits, secrets, databases, translations, refactoring, test data and coverage, pull requests, responsive layouts, accessibility, performance, CI, Docker, GraphQL, dependencies, prompts, migrations, flaky tests and local setup. Each plugin is a folder with its own README, skill and slash commands.

## Install

Add this repository as a marketplace, then install the plugins you want:

```
/plugin marketplace add petrovicistefan/claude-code-plugins
/plugin install env-protector@petrovici-plugins
```

To try one plugin from a local clone without installing it:

```bash
claude --plugin-dir ./env-protector
```

## Use the skills in other agents

The skills in this repository follow the open Agent Skills format (`SKILL.md`), so they also work outside Claude Code, for example in Cursor, Codex CLI, Gemini CLI, GitHub Copilot and Windsurf:

```bash
npx skills add petrovicistefan/claude-code-plugins
```

Pick the skills and agents you want when the installer asks. To install by hand, copy a skill folder, for example `env-protector/skills/env-protector`, into your agent's skills directory (`.cursor/skills/`, `.agents/skills/` or the equivalent for your tool).

Only the skills travel to other agents. The slash commands in each `commands/` folder are specific to Claude Code. The three plugins that declare an MCP server (`exa-search`, `figma-to-code`, `rls-schema-explorer`) use a standard MCP connection, so the same server also works in any MCP client.

## Plugins

| Plugin | What it helps with | Command |
|---|---|---|
| [a11y-enforcer](a11y-enforcer) | WCAG accessibility problems and color contrast | `/a11y-enforcer:a11y-check` |
| [api-doc-generator](api-doc-generator) | OpenAPI docs from the routes in your code | `/api-doc-generator:api-docs` |
| [api-drift-detector](api-drift-detector) | Mismatched types between frontend, backend and database | `/api-drift-detector:check-drift` |
| [aws-cost-guard](aws-cost-guard) | AWS costs by service, idle resources, failing Kubernetes pods | `/aws-cost-guard:costs` |
| [bundle-size-sentinel](bundle-size-sentinel) | Heavy dependencies and bundle size per build | `/bundle-size-sentinel:bundle-size` |
| [caveman](caveman) | Short, direct answers | `/caveman:caveman` |
| [ci-optimizer](ci-optimizer) | Slow, costly or unsafe GitHub Actions and GitLab CI | `/ci-optimizer:ci-check` |
| [code-metrics-tracker](code-metrics-tracker) | Complexity, long functions and duplicated code | `/code-metrics-tracker:metrics` |
| [context-compactor](context-compactor) | Keeping long sessions small and fast | `/context-compactor:compact-plan` |
| [db-migration-safety](db-migration-safety) | Migrations that lock tables, lose data or break the running app | `/db-migration-safety:check-migration` |
| [db-schema-spy](db-schema-spy) | Tables, relations, indexes and ER diagrams | `/db-schema-spy:schema` |
| [dependency-sentinel](dependency-sentinel) | Known vulnerabilities and licenses of dependencies | `/dependency-sentinel:dep-scan` |
| [dockerfile-optimizer](dockerfile-optimizer) | Smaller, faster and safer Docker images | `/dockerfile-optimizer:docker-check` |
| [env-protector](env-protector) | Keeping secrets out of the chat and out of git | `/env-protector:scan-secrets` |
| [env-setup-wizard](env-setup-wizard) | Getting a freshly cloned repo to run locally | `/env-setup-wizard:setup` |
| [exa-search](exa-search) | Current docs and releases through Exa | `/exa-search:search` |
| [figma-to-code](figma-to-code) | Figma frames to components in your stack | `/figma-to-code:implement` |
| [flaky-test-detector](flaky-test-detector) | Tests that pass and fail at random | `/flaky-test-detector:flaky` |
| [graphql-guardian](graphql-guardian) | Breaking GraphQL schema changes and N+1 queries | `/graphql-guardian:graphql-diff` |
| [headroom](headroom) | Very large logs, documents, JSON and CSV files | `/headroom:peek` |
| [i18n-sync](i18n-sync) | Missing and untranslated keys in locale files | `/i18n-sync:i18n-check` |
| [legacy-refactor-pilot](legacy-refactor-pilot) | Step-by-step modernization of old code | `/legacy-refactor-pilot:modernize` |
| [mock-data-hydrator](mock-data-hydrator) | Seed and test data that matches your schema | `/mock-data-hydrator:seed` |
| [omniout](omniout) | Retries and model fallback in your app's LLM calls | `/omniout:add-fallback` |
| [perf-profiler](perf-profiler) | Lighthouse results and Core Web Vitals causes | `/perf-profiler:perf-audit` |
| [pr-story-aligner](pr-story-aligner) | Pull requests checked against ticket criteria | `/pr-story-aligner:align` |
| [project-memory](project-memory) | Local project memory across sessions (SQLite) | `/project-memory:remember` |
| [prompt-tightener](prompt-tightener) | Clearer, shorter prompts for LLM features | `/prompt-tightener:prompt-review` |
| [responsive-check](responsive-check) | Screenshots and layout problems at several screen sizes | `/responsive-check:responsive` |
| [rls-schema-explorer](rls-schema-explorer) | Real Supabase schema and RLS policies, read-only | `/rls-schema-explorer:schema` |
| [smart-commits](smart-commits) | Commit messages from the staged diff | `/smart-commits:commit` |
| [task-observer](task-observer) | Turning your corrections into lasting project rules | `/task-observer:learn` |
| [test-coverage-intelligence](test-coverage-intelligence) | Riskiest untested code and the tests it needs | `/test-coverage-intelligence:coverage-gaps` |

You can also just describe the task. Each plugin's skill tells Claude when to use it.

## External services

Most plugins run only on your machine. Three connect to the official hosted MCP server of a service and need you to sign in once with `/mcp`: `exa-search` (Exa), `figma-to-code` (Figma) and `rls-schema-explorer` (Supabase, read-only). `aws-cost-guard`, `pr-story-aligner` and `ci-optimizer` use the `aws`, `kubectl` and `gh` command line tools you already have configured. `dependency-sentinel` sends package names and versions to the public OSV.dev vulnerability database, and `perf-profiler` can send a public URL you choose to Google PageSpeed Insights. Each plugin's README lists exactly what it sends and where.

## Check the plugins

```bash
for d in */; do [ -f "$d.claude-plugin/plugin.json" ] && claude plugin validate "./$d"; done
```

## About the author

<a href="https://petrovicistefan.ro"><img src="assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro). See the [privacy policy](PRIVACY.md).
