# DB Migration Safety: Check Migrations Before You Run Them

Catch the migrations that lock a busy table, lose data or break the running app, before they reach production.

## What it does

A bundled Python script reads your SQL migration and flags dropped or renamed columns and tables, NOT NULL columns without a default, volatile defaults that rewrite the table, type changes, `SET NOT NULL`, foreign keys and checks added without `NOT VALID`, unique constraints, indexes built without `CONCURRENTLY`, UPDATE or DELETE without WHERE, TRUNCATE and a missing `lock_timeout`. Each finding has a line number and a safer way to write it. Claude gets the SQL from Prisma, Django, Alembic, Flyway or plain files, judges the real risk using table sizes you provide, writes the safer step-by-step migration, and a rollback plan that marks what cannot be undone.

## Use it

- `/db-migration-safety:check-migration`
- `/db-migration-safety:check-migration db/migrate/20261006_add_status.sql`
- Or ask: "Is this migration safe to run on production?"

The script also works on its own in CI and exits with code 1 when it finds a HIGH risk: `python3 lint_migration.py --dialect postgres migrations/*.sql`.

## Requirements

Python 3 for the script (standard library only). Postgres is the default dialect, MySQL is supported with `--dialect mysql`.

## Data

Everything runs locally on the files you name. The plugin never connects to a database and sends nothing anywhere. Claude asks before running any command that needs a database connection, and before editing a migration.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
