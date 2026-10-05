# Claude Code Plugins by Stefan Petrovici

Twenty focused plugins for Claude Code that cover everyday development work: API types, cloud costs, bundle size, commits, secrets, databases, translations, refactoring, test data, pull requests, responsive layouts and more. Each plugin is a folder with its own README, skill and slash commands.

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

## Plugins

| Plugin | What it helps with | Command |
|---|---|---|
| [api-drift-detector](api-drift-detector) | Mismatched types between frontend, backend and database | `/api-drift-detector:check-drift` |
| [aws-cost-guard](aws-cost-guard) | AWS costs by service, idle resources, failing Kubernetes pods | `/aws-cost-guard:costs` |
| [bundle-size-sentinel](bundle-size-sentinel) | Heavy dependencies and bundle size per build | `/bundle-size-sentinel:bundle-size` |
| [caveman](caveman) | Short, direct answers | `/caveman:caveman` |
| [context-compactor](context-compactor) | Keeping long sessions small and fast | `/context-compactor:compact-plan` |
| [db-schema-spy](db-schema-spy) | Tables, relations, indexes and ER diagrams | `/db-schema-spy:schema` |
| [env-protector](env-protector) | Keeping secrets out of the chat and out of git | `/env-protector:scan-secrets` |
| [exa-search](exa-search) | Current docs and releases through Exa | `/exa-search:search` |
| [figma-to-code](figma-to-code) | Figma frames to components in your stack | `/figma-to-code:implement` |
| [headroom](headroom) | Very large logs, documents, JSON and CSV files | `/headroom:peek` |
| [i18n-sync](i18n-sync) | Missing and untranslated keys in locale files | `/i18n-sync:i18n-check` |
| [legacy-refactor-pilot](legacy-refactor-pilot) | Step-by-step modernization of old code | `/legacy-refactor-pilot:modernize` |
| [mock-data-hydrator](mock-data-hydrator) | Seed and test data that matches your schema | `/mock-data-hydrator:seed` |
| [omniout](omniout) | Retries and model fallback in your app's LLM calls | `/omniout:add-fallback` |
| [pr-story-aligner](pr-story-aligner) | Pull requests checked against ticket criteria | `/pr-story-aligner:align` |
| [project-memory](project-memory) | Local project memory across sessions (SQLite) | `/project-memory:remember` |
| [responsive-check](responsive-check) | Screenshots and layout problems at several screen sizes | `/responsive-check:responsive` |
| [rls-schema-explorer](rls-schema-explorer) | Real Supabase schema and RLS policies, read-only | `/rls-schema-explorer:schema` |
| [smart-commits](smart-commits) | Commit messages from the staged diff | `/smart-commits:commit` |
| [task-observer](task-observer) | Turning your corrections into lasting project rules | `/task-observer:learn` |

You can also just describe the task. Each plugin's skill tells Claude when to use it.

## External services

Most plugins run only on your machine. Three connect to the official hosted MCP server of a service and need you to sign in once with `/mcp`: `exa-search` (Exa), `figma-to-code` (Figma) and `rls-schema-explorer` (Supabase, read-only). `aws-cost-guard` and `pr-story-aligner` use the `aws`, `kubectl` and `gh` command line tools you already have configured. Each plugin's README lists exactly what it sends and where.

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
