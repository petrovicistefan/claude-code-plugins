---
name: rls-schema-explorer
description: "Use when building features on Supabase or Postgres, to read the real tables, columns, RLS policies and functions before writing queries, migrations or client code."
---

# RLS Schema Explorer

Work from the real Supabase database instead of guessing its schema.

The plugin connects the official Supabase MCP server in **read-only mode**. If the Supabase tools are not available, tell the user to run `/mcp` in Claude Code and sign in to Supabase, and meanwhile read `supabase/migrations/` and generated types (`database.types.ts`) from the project.

## Before writing code

1. Confirm the project: list projects and ask which one to use if there is more than one. Prefer a development or branch project over production.
2. List the tables in the relevant schemas (usually `public`) and read the columns, types, defaults and foreign keys of the tables involved.
3. Check Row Level Security: is it enabled on each table, and which policies exist for `select`, `insert`, `update` and `delete`? Many "no rows returned" bugs are missing policies.
4. Check database functions, triggers and enums the feature touches.

## Testing queries

Run `select` queries to check that a query returns what you expect, with a `limit`. Read-only mode blocks writes. Never print secrets such as the service role key.

## Changing the schema

Write the change as a new SQL migration file in `supabase/migrations/` in the project, following the existing naming, and include RLS policies for new tables. Let the user apply it with their usual workflow (`supabase db push` or `supabase migration up`). Regenerate types afterwards if the project uses `database.types.ts`.

## Client code

Use the column names and types you read. Handle the `{ data, error }` result of every `supabase-js` call. Never use the service role key in browser code.
