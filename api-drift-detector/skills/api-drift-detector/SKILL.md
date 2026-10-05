---
name: api-drift-detector
description: "Use when frontend, backend and database types may have drifted apart, to find TypeScript contract mismatches before release."
---

# API Drift Detector

Find places where the frontend, the backend and the database disagree about the shape of the same data.

## 1. Find the type sources

Look for, in this order, and tell the user which ones you found:

- Frontend types: `src/types/`, `types/`, `*.d.ts`, API client files (`api.ts`, `client.ts`), generated clients (`openapi`, `graphql` codegen output)
- Backend types: route handlers, DTOs, validation schemas (zod, yup, class-validator), OpenAPI specs
- Database schema: `prisma/schema.prisma`, `drizzle` schema files, SQL migrations, `supabase/migrations/`

If one side is missing, say so and compare the sides that exist.

## 2. Compare the same entity across sources

Match entities by name (for example `User`, `UserDto`, `users` table). For each pair, check:

1. **Field names**: renamed or missing fields (`name` vs `fullName`)
2. **Field types**: `string` vs `number`, `Date` vs ISO `string`, `bigint` columns typed as `number`
3. **Optionality**: required on one side, optional or nullable on the other
4. **Enums and unions**: values present on one side only
5. **Nesting**: an object on one side, a flat field or an ID on the other

## 3. Confirm with the compiler

If the project has a `tsconfig.json`, run the type checker that the project already uses, for example `npx tsc --noEmit` when TypeScript is a project dependency. Do not install anything. Use compiler errors to confirm or rule out each finding.

## 4. Report

Group findings by severity:

- **Breaks at runtime**: missing or renamed required fields, wrong types for values that are read
- **Risky**: optional vs required, enum values missing on one side
- **Cosmetic**: naming style only

For each finding give the entity, the two files with line numbers, and the suggested fix. Do not change files until the user agrees. After a fix, run the type checker again.
