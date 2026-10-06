# API Doc Generator: OpenAPI from Your Code

Write OpenAPI documentation from the routes that really exist in your code, and keep it in sync.

## What it does

- A bundled Python script lists every HTTP route with method, path and file:line for Express, Fastify, Koa, Hono, NestJS, Next.js route handlers and API routes, FastAPI, Flask, Spring and Go routers.
- Claude reads each handler for parameters, request bodies, responses and auth, reuses your existing Zod, Pydantic or DTO types, and writes an OpenAPI 3.1 file with examples.
- The same script compares the code with an existing spec and lists undocumented routes and documented routes that no longer exist. It exits with code 1 when they differ, so it can run in CI.

## Use it

- `/api-doc-generator:api-docs` or `/api-doc-generator:api-docs src/server`
- `/api-doc-generator:api-docs-check openapi.yaml`
- Or ask: "Document our REST API."

## Requirements

Python 3. The script uses only the standard library.

## Data

Everything runs locally. Nothing is sent anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
