# GraphQL Guardian: Breaking Changes and N+1 Check

Catch breaking GraphQL schema changes before clients see them, and find N+1 queries and unbounded lists in your resolvers.

## What it does

- A bundled Python script compares two SDL schemas (files or folders) and classifies every change as breaking, dangerous or safe: removed fields and enum values, changed types, nullability changes, new required arguments and input fields, union and interface changes. It exits with code 1 on breaking changes, so it can gate CI.
- A lint mode lists list fields without pagination arguments and deprecations without a reason.
- Claude reviews resolvers for per-item database calls (N+1) and fixes them with DataLoader or eager loading, and checks depth, cost and page size limits and per-operation monitoring.

## Use it

- `/graphql-guardian:graphql-diff` or `/graphql-guardian:graphql-diff origin/develop`
- `/graphql-guardian:graphql-review`
- Or ask: "Will this schema change break the mobile app?"

## Requirements

Python 3 and a GraphQL schema in SDL (or a way to print it from a code-first schema).

## Data

Everything runs locally. Nothing is sent anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
