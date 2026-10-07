# DB Migration Safety: Lock and Data-Loss Check

Check SQL, Rails, Alembic, Knex, Sequelize and Django migrations for table locks, data loss, missing rollbacks and unsafe renames, and get the safe expand-and-contract version.

## What it does

- A bundled Python script reads migration files as text and flags `DROP TABLE` and `DROP COLUMN`, renames, `NOT NULL` columns without a default, `CREATE INDEX` without `CONCURRENTLY`, column type changes, foreign keys and checks added without `NOT VALID`, `SET NOT NULL`, `TRUNCATE`, table locks, and `UPDATE` or `DELETE` without `WHERE`. It also notes migrations with no down/rollback step.
- It understands raw SQL, Rails, Alembic, Knex, Sequelize, TypeORM, Django and Prisma folders.
- For each risky migration Claude writes the safe version as separate deploys (expand, backfill in batches, switch, contract) and a rollback plan.

## Use it

- `/db-migration-safety:migration-check`
- `/db-migration-safety:migration-plan db/migrate/20260101_add_status.rb`
- Or ask: "Is this migration safe to run on production?"

## Requirements

Python 3.

## Data

Everything runs locally on your files. The plugin never connects to a database and sends nothing anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
