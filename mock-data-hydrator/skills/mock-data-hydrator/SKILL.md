---
name: mock-data-hydrator
description: "Use when the user needs realistic sample or seed data for development, tests or demos that matches a database schema, TypeScript types or an API shape."
---

# Mock Data Hydrator

Generate realistic, consistent test data that fits the project's real data model.

## 1. Read the model

Find the shapes to fill: Prisma or Drizzle schema, SQL migrations, ORM models, TypeScript interfaces, zod schemas, OpenAPI specs. Note types, required fields, enums, unique constraints, lengths and foreign keys.

## 2. Plan the data

- Insert order follows foreign keys: parents before children
- Counts per entity (ask if not given; default to a small set, such as 10 users)
- Realistic values: names, emails on `example.com`, addresses, prices with two decimals, dates in a sensible range, statuses from the real enum
- Edge cases when the data is for tests: empty strings, maximum lengths, nulls on optional fields, unicode names
- Never use real people's personal data

## 3. Produce it in the project's format

Prefer the tools the project already has:

- A seed script in the project's stack (`prisma/seed.ts`, Django fixtures, Rails `seeds.rb`, Knex seeds)
- If `@faker-js/faker` or `Faker` is already a dependency, use it with a fixed seed so output is reproducible; otherwise write plain deterministic data, or ask before adding a dependency
- SQL `INSERT` statements or JSON fixtures when no seed tooling exists

## 4. Verify

Run the seed against a local or test database only, never production. Check that row counts match and foreign keys resolve. Tell the user how to re-run and reset it.
