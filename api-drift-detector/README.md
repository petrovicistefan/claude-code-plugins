# API Drift Detector: TypeScript Contract Checker

Catch breaking API changes before production by comparing TypeScript types across your frontend, backend and database schema.

## What it does

Claude locates your type definitions (TypeScript types, DTOs, validation schemas, Prisma, Drizzle or SQL migrations), compares the same entities across them and reports renamed fields, type changes, optional vs required mismatches and missing enum values. It confirms findings with your project's own TypeScript compiler and proposes fixes, which it applies only after you agree.

## Use it

- Run `/api-drift-detector:check-drift`
- Or ask: "Did the backend change break any frontend types?"

## Requirements

A TypeScript project. Compiler checks need TypeScript installed in the project.

## Data

Everything runs locally on your files. The plugin sends nothing to any external service.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
