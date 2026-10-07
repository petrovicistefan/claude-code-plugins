---
name: db-migration-safety
description: "Use when writing or reviewing a database migration, to find table locks, data loss and missing rollbacks and produce a safe multi-step rollout."
---

# DB Migration Safety

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Find migrations that lock a table, lose data or cannot be rolled back, and rewrite them so they can be deployed without downtime.

## 1. Run the check

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/migration_check.py                 # finds migration folders
python3 ${CLAUDE_SKILL_DIR}/scripts/migration_check.py db/migrate/20260101_add_status.rb
```

The script only reads files. It does not know table sizes or which database you use, so ask: which database engine and version, and is the table large or busy? The same statement is harmless on a new or tiny table and an outage on a big one. State that assumption in the report.

## 2. Decide per finding

- **Adds a NOT NULL column without a default**: fails on any table with rows. Safe version: add nullable, backfill in batches, then `SET NOT NULL` (PostgreSQL 12+: add `CHECK (col IS NOT NULL) NOT VALID`, `VALIDATE CONSTRAINT`, then `SET NOT NULL`).
- **Index without CONCURRENTLY (PostgreSQL)**: blocks writes while it builds. Use `CREATE INDEX CONCURRENTLY`, which cannot run inside a transaction (Rails `disable_ddl_transaction!`, Alembic `autocommit_block`, Flyway non-transactional script). MySQL 5.6+ InnoDB builds most indexes online.
- **Foreign key or CHECK**: add `NOT VALID`, then `VALIDATE CONSTRAINT` in a second step; validation does not block writes.
- **Rename column or table**: a rolling deploy runs old and new code together. Add the new column, write to both, backfill, switch reads, stop writing the old one, drop it later.
- **Drop column or table**: first deploy code that no longer reads or writes it, wait a release, then drop. Take a backup or `CREATE TABLE ... AS` copy for anything irreplaceable.
- **Change column type**: usually rewrites the table under an exclusive lock. Use a new column, a trigger or dual write, a batched backfill and a swap. Widening `varchar(n)` on PostgreSQL and `int` to `bigint` on a small table can be metadata-only; check the engine docs for the version in use.
- **UPDATE or DELETE without WHERE / large backfills**: run in batches (for example 1000 to 10000 rows) with a pause, outside the schema migration, so locks stay short and replication keeps up.
- **Missing down step**: write one, or say clearly that the migration is irreversible and what to restore from.

Also recommend `SET lock_timeout = '5s'` (PostgreSQL) or the framework equivalent on every DDL migration, with a retry, so a migration that cannot get its lock fails fast instead of queuing behind a long query and blocking everything.

## 3. Output

For each risky migration give: what is risky and why, the safe sequence as separate deploys (each its own migration file), the rollback for each step, and the order relative to the application deploy. Write the new migration files in the project's own framework style. Do not run migrations; tell the user which command to run and recommend trying it first on a copy of production data.
