# RLS Schema Explorer for Supabase

Let Claude read your real Supabase tables and RLS policies before writing queries or migrations.

## What it does

The plugin connects the official Supabase MCP server in read-only mode. Claude confirms which project to use, reads the schema and RLS policies of the tables involved, tests `select` queries, and writes schema changes as new migration files in `supabase/migrations/` for you to apply. In client code it uses the real column names, handles errors and keeps the service role key out of the browser.

## Use it

- `/rls-schema-explorer:schema`
- Or ask: "Why does this query return no rows for logged-in users?"

## Requirements

A Supabase account. The first time, run `/mcp` in Claude Code and sign in to Supabase. Point it at a development project when you can.

## Data

Schema details and query results come from Supabase (mcp.supabase.com) under your account, in read-only mode. The plugin stores nothing.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
