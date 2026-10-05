# DB Schema Spy: Database Schema Explorer and ERD

See your real database schema before writing SQL: tables, relations and indexes, with Mermaid ER diagrams.

## What it does

Claude finds the schema in your project (Prisma, Drizzle, TypeORM, Django, Rails, SQL migrations or dumps) and shows tables, columns, types, foreign keys and indexes. It can draw a Mermaid entity relationship diagram and point out problems such as unindexed foreign keys or money stored as floats, with migration SQL that you decide whether to run. If you ask, it can also run read-only catalog queries on a database you connect with your own client.

## Use it

- `/db-schema-spy:schema` or `/db-schema-spy:schema orders`
- `/db-schema-spy:erd`

## Data

Reads your project files. Live queries run only when you ask, with your own database client, and are read-only. Nothing is sent to other services.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
