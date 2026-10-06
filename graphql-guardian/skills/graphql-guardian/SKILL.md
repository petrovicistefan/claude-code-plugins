---
name: graphql-guardian
description: "Use when changing a GraphQL schema or resolvers, reviewing a GraphQL pull request, or investigating slow GraphQL queries, N+1 database calls or breaking schema changes."
---

# GraphQL Guardian

Catch breaking schema changes before clients see them, and find N+1 queries and unbounded queries in resolvers.

## 1. Breaking changes

Get the schema before and after the change. For a schema file in git:

```bash
git show origin/main:path/to/schema.graphql > /tmp/schema-old.graphql
python3 ${CLAUDE_SKILL_DIR}/scripts/schema_diff.py /tmp/schema-old.graphql path/to/schema.graphql
```

Both arguments can be folders of `.graphql` / `.graphqls` / `.gql` files. For code-first schemas (Nest, Pothos, TypeGraphQL, Strawberry, graphene, gqlgen), print the SDL with the project's own script or `printSchema(schema)` for both versions first.

Every change is classified:

- **breaking**: removed types, fields, arguments or enum values; changed field types; output fields that became nullable; new required arguments or input fields; arguments and input fields that became required; types removed from a union or interface
- **dangerous**: enum values or union members added (exhaustive client switches break), fields added to an interface, removed argument defaults
- **safe**: additions, optional arguments, output fields that became non-null, deprecations

The exit code is 1 when anything is breaking. Before removing a field, deprecate it with `@deprecated(reason: "Use X")` and check usage (GraphOS, Hive or Inigo field usage, or the server's own operation logs) before deleting it.

## 2. Lint the schema

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/schema_diff.py --lint path/to/schema.graphql
```

It lists list fields that return object types without a `first`/`limit` argument (a single query can fetch everything) and deprecations without a reason.

## 3. N+1 queries in resolvers

For each field resolver on a type that appears inside a list (for example `User.posts` when `Query.users` returns a list), read the resolver:

- A database call or HTTP request per parent object (`prisma.post.findMany({ where: { authorId: parent.id } })`, `Post.objects.filter(author=parent)`, `fetch(...)`) runs once per item in the list: 100 users means 101 queries.
- Fix with a per-request DataLoader (`dataloader` in Node, `aiodataloader` or Strawberry's DataLoader in Python, `graph-gophers/dataloader` in Go) that batches keys into one `WHERE id IN (...)` query, created in the request context, never shared between requests.
- Alternatives: Prisma's fluent API batching, `select_related`/`prefetch_related` in Django, join-monster or look-ahead with `info` to load relations in the parent resolver.

To confirm, turn on query logging in development (Prisma `log: ['query']`, Django `connection.queries`, SQLAlchemy `echo=True`, Sequelize `logging`), run one representative operation, and count the queries.

## 4. Query cost and depth

Check whether the server limits abuse: max depth (`graphql-depth-limit`, Apollo `validationRules`), query complexity or cost (`graphql-query-complexity`, `@cost` / `@listSize` directives), max page size enforced in the resolver, persisted queries or an allow list for public APIs, and introspection disabled in production if the API is private.

## 5. Operation-level monitoring

All operations go to one `/graphql` endpoint and errors often return HTTP 200, so endpoint metrics hide problems. Check that the server records per operation name: latency, error count from `errors[]`, and resolver timings (OpenTelemetry instrumentation for GraphQL, Apollo usage reporting, or a plugin that logs `operationName`, duration and error count). Suggest the option that fits the existing stack; ask before adding packages.

## Report

Start with breaking changes and their clients' impact, then N+1 risks with the resolver file:line and the fix, then missing limits.
