# Mock Data Hydrator: Seed and Test Data Generator

Generate realistic seed and test data that matches your real schema, foreign keys included.

## What it does

Claude reads your schema or types (Prisma, Drizzle, SQL migrations, ORM models, TypeScript, zod or OpenAPI), respects required fields, enums, unique constraints and foreign keys, and inserts parents before children. It writes the data in the format your project already uses, such as a Prisma seed script, Django fixtures, Rails seeds, SQL inserts or JSON fixtures, with a fixed random seed for reproducible output. It adds edge cases for tests, never uses real personal data and only runs seeds against local or test databases.

## Use it

- `/mock-data-hydrator:seed 20 users with 3 orders each`

## Data

Works on your local files. The plugin sends nothing to any external service.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
