---
name: service-boundary-tests
description: "Use when writing or planning integration or contract tests, to find the databases, queues and outside APIs a service uses and pick containers, contracts or mocks."
---

# Integration Test Helper

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Test the seams between a service and what it talks to, with the cheapest approach that gives real confidence.

## 1. Map the integration points

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/integration_map.py            # current folder
python3 ${CLAUDE_SKILL_DIR}/scripts/integration_map.py services/orders
```

The map lists infrastructure used, outbound HTTP calls (literal URLs only; calls built from variables are listed through their `*_URL` env names), docker-compose images, and existing integration or contract tests. Text-based detection can miss dynamic usage and over-report from dependency lists, so confirm in the code before building on it.

## 2. Choose the approach per integration point

| What it is | Use | Why |
|---|---|---|
| Database, cache, queue, object store you run | Real container: Testcontainers or `docker compose` | Mocks of a database hide the bugs that matter (SQL dialect, constraints, transactions) |
| Another team's service, internal API | Consumer-driven contract test (Pact) or a shared OpenAPI schema check | Catches breaking changes without running both services |
| Third-party SaaS (payments, email, maps) | Recorded or hand-written mock (WireMock, MSW, nock, `responses`, `httpx_mock`), plus one occasional test against their sandbox | Fast, deterministic, no cost or rate limits |
| Time, randomness, filesystem | Fake clock, seeded random, temp directories | Removes flakiness |

Match what the project already uses (see "tooling already present" in the map) before adding a new library, and ask before adding a dependency.

## 3. Write the tests

- Spin up the container once per test run (or per file), apply the real migrations, and isolate tests with transactions that roll back or truncate between tests. Wait for readiness (health check), not a sleep.
- Test the behaviour of the boundary: a repository saves and reads back, a unique constraint raises the expected error, a consumer handles a duplicate message, a client retries on 503 and gives up on 400.
- For a client of an outside API: assert the request you send (method, path, headers, body) and handle the responses it can return: success, 4xx, 5xx, timeout, malformed body. Keep fixtures small and name the real API version they came from.
- For a provider you own: verify the published contracts or OpenAPI document against the running service.
- Never connect tests to production or to a shared environment with real data. Credentials in tests are fake values from the test config.
- Mark integration tests (a folder, tag or marker) so they can run separately from unit tests, and add the CI step with the services they need.

## 4. Run and report

Run the new tests, three times if they use containers or timing. Report what is covered, what is mocked and therefore unproven, and what would only be caught in a real environment.
