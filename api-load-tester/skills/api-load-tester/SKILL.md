---
name: api-load-tester
description: "Use when asked how fast or how much load an API can take, to run a safe load test on a local or owned system and explain latency, errors and bottlenecks."
---

# API Load Tester

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Measure how an API behaves under load, safely, and explain the result.

## Rules before any test

1. **Only test systems the user owns or has written permission to test.** Load testing someone else's service can be treated as an attack. The runner refuses non-local targets unless `--allow-remote` is passed; add that flag only after the user confirms ownership or permission.
2. **Never test production** without the user explicitly saying so and choosing a low rate. Prefer a local run or a staging copy with production-like data size.
3. Do not send real customer data or real payment calls. Use test accounts and stubbed third parties.
4. Start small, then double: 5 workers, then 10, 20, 50. Stop at the first sign of errors or sharply rising latency.

## 1. Run a test

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/loadtest.py http://localhost:3000/api/items --concurrency 10 --duration 20 --ramp 5
python3 ${CLAUDE_SKILL_DIR}/scripts/loadtest.py http://localhost:3000/api/orders --method POST \
  --header "Content-Type: application/json" --header "Authorization: Bearer $TOKEN" --body '{"sku":"test-1","qty":1}'
```

(Take the token from the user; do not invent or hardcode one.) Options: `--concurrency`, `--duration`, `--ramp`, `--max-rps` (cap, default 200), `--header` (repeatable), `--body`, `--method`.

## 2. Read the result

- **Success rate below 99%**: look at the status codes. 429 means a rate limiter (expected, note it), 5xx means the system is failing, `0` means connection errors or timeouts (pool exhausted, port limits, or the server fell over).
- **p50 vs p99**: a big gap means a tail problem (GC pauses, a slow query on some inputs, lock contention, cold cache). Report the percentiles that matter for the user's goal, not just the mean.
- **Latency grows during the run**: the system is saturating or leaking (connections, memory, queue backlog).
- **Throughput stops growing as concurrency grows**: that plateau is the capacity of the current setup. Name the likely bottleneck and how to confirm it (database slow-query log, CPU on the app and DB hosts, connection pool size, event loop lag).
- The Python runner is itself a client with limits: above a few hundred requests per second, or with HTTP/2 or WebSockets, use k6 and say that the numbers from the built-in runner are a floor for the server, not a ceiling.

## 3. k6 for heavier or multi-step tests

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/loadtest.py https://staging.example.test/api/items --k6 --concurrency 50 --duration 60 > load.js
k6 run load.js
```

Edit the generated script for multi-step journeys (log in, then create, then read), add `thresholds` that encode the target (for example `p(95)<300`), and keep the test data unique per virtual user. Report results against a target the user stated (for example "100 req/s with p95 under 300 ms"); if they have none, ask for one rather than inventing it.
