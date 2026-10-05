---
name: db-schema-spy
description: "Use when writing database queries or migrations, to look up table names, column types, indexes and relationships from the project's schema."
---

# DB Schema Spy

Understand a database schema before writing queries or migrations, so table and column names are never guessed.

## 1. Find the schema in the project

Check these sources, newest information first:

- ORM schema: `prisma/schema.prisma`, Drizzle `schema.ts`, TypeORM or Sequelize models, Django `models.py`, Rails `db/schema.rb`, SQLAlchemy models
- SQL migrations: `migrations/`, `db/migrate/`, `supabase/migrations/` (apply them in order in your head; later ones override earlier ones)
- Dumps: `schema.sql`, `structure.sql`

## 2. Or ask the live database

Only if the user asks and gives a connection, run read-only catalog queries with the client they already use (`psql`, `mysql`, `sqlite3`). Never run `INSERT`, `UPDATE`, `DELETE` or DDL. Never print connection strings or passwords.

PostgreSQL:

```sql
SELECT table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

SELECT conrelid::regclass AS table_name, conname, pg_get_constraintdef(oid)
FROM pg_constraint WHERE connamespace = 'public'::regnamespace;

SELECT tablename, indexname, indexdef FROM pg_indexes WHERE schemaname = 'public';
```

MySQL: `information_schema.COLUMNS`, `KEY_COLUMN_USAGE`, `STATISTICS`. SQLite: `.schema` and `PRAGMA table_info(<table>)`.

## 3. Present it

- Per table: columns with type, nullability, default, primary key
- Relationships: foreign keys as `orders.user_id -> users.id`
- Indexes and unique constraints
- On request, a Mermaid `erDiagram`

## 4. Review

Point out real problems you can see: foreign keys without an index, missing `NOT NULL` on required fields, money stored as float, missing unique constraints on natural keys, tables without a primary key. Give the migration SQL to fix each, and do not run it.
