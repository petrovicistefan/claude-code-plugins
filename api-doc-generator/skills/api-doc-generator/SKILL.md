---
name: api-doc-generator
description: "Use when writing or updating OpenAPI or Swagger documentation for an HTTP API, when checking that API docs match the code, or when exporting an API to Postman or a typed client."
---

# API Doc Generator

Write an OpenAPI 3.1 file from the real routes in the code and keep it in sync.

## 1. Find the routes

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/routes_scan.py <server-dir>
python3 ${CLAUDE_SKILL_DIR}/scripts/routes_scan.py <server-dir> --json routes.json
```

It lists method, path and file:line for Express, Fastify, Koa and Hono routers, NestJS controllers, Next.js route handlers (`app/**/route.ts`) and API routes (`pages/api`), FastAPI, Flask, Spring and Go (net/http, chi, gin, echo). Path parameters are normalised to `{id}`.

Limits to check by reading the code:

- Router prefixes such as `app.use('/api', router)`, `APIRouter(prefix=...)`, `Blueprint(url_prefix=...)` and global prefixes (`app.setGlobalPrefix`) are not applied. Add them.
- Routes built dynamically (loops, config files) are not found.
- `pages/api` handlers are listed as `ANY`; read the handler to see which methods it accepts.

## 2. Read each handler

For every route, read the handler and what it calls to find:

- path, query and header parameters, and which are required
- the request body type (TypeScript types, Zod, class-validator DTOs, Pydantic models, Joi schemas)
- every response status the handler can return, with its body type, including validation and auth errors
- the auth it needs (middleware, guards, decorators)

If the project already declares schemas (Zod, Pydantic, DTO classes), mirror them exactly and reuse names in `components/schemas`. If a framework generates OpenAPI already (FastAPI's `/openapi.json`, `@nestjs/swagger`, `zod-openapi`, `springdoc`), say so and prefer improving the annotations over writing a separate file.

## 3. Write the spec

- `openapi: 3.1.0`, `info` with title and version from `package.json` or `pyproject.toml`, `servers` with the base path.
- One `operationId` per operation, in camelCase from the handler name. Group with `tags` by resource.
- Put shared models in `components/schemas` and use `$ref`. Mark `required` fields and `nullable` (3.1: `type: [string, "null"]`).
- Document error responses with one shared error schema.
- Add `securitySchemes` and `security` that match the real auth.
- Add one realistic `example` per request and response body. Never put real customer data or secrets in examples.
- Write YAML unless the project already uses JSON. Default path: `openapi.yaml` at the repository root or next to the server code.

Do not invent endpoints, fields or status codes. When something is unclear, write it with a `description` that says so and list it in your answer.

## 4. Check docs against code

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/routes_scan.py <server-dir> --openapi openapi.yaml
```

It prints routes that are in the code but not in the spec and spec operations with no matching route, and exits with code 1 when they differ, so it can run in CI. The `servers` base path is taken into account. Then compare parameters and schemas of changed handlers by reading them.

## 5. Optional outputs

Only when asked:

- **Postman**: Postman imports OpenAPI files directly (Import, then choose the file). No conversion is needed.
- **Typed client**: suggest the generator that fits the stack (`openapi-typescript` plus `openapi-fetch`, `orval`, or `openapi-generator`), and ask before installing anything.
- **Mock server**: suggest `prism mock openapi.yaml` (Stoplight Prism) if the user wants one, again asking before installing.
- **Validation**: if `@redocly/cli` or `swagger-cli` is already installed, run its lint command on the file.
