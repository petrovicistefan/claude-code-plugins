# Integration Test Helper: Services, Contracts, Mocks

Find every database, queue, cache and outside API your service uses, then write integration tests with real containers and contract tests with mocks for what you cannot run.

## What it does

- A bundled Python script reads your code and manifests and lists the infrastructure the service uses (PostgreSQL, MySQL, MongoDB, Redis, Kafka, RabbitMQ, SQS, S3, Elasticsearch, SMTP, Stripe, gRPC), the outbound HTTP calls with literal URLs, the environment variables that hold service URLs, the docker-compose images, and the integration and contract tests that already exist.
- Claude then picks the right approach per integration point: real containers (Testcontainers or docker-compose) for databases and queues you control, contract tests (Pact) or recorded mocks (WireMock, MSW, nock, responses) for services you do not control.
- It writes the tests in your language and test runner, runs them, and reports what they cover.

## Use it

- `/integration-test-helper:integration-map`
- `/integration-test-helper:integration-test the orders repository against Postgres`
- Or ask: "How should I test our calls to the billing API?"

## Requirements

Python 3. Docker if you want real containers in tests.

## Data

Runs locally on your files. Tests you ask for run against local containers or mocks. The plugin sends nothing anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
