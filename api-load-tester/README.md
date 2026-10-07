# API Load Tester: Latency and Throughput Tests

Load test your own API with a safe built-in runner or a generated k6 script: ramp-up, p50/p95/p99 latency, error rates and where it starts to saturate.

## What it does

- A bundled Python script sends HTTP requests with a ramp-up and reports requests per second, success rate, and min, mean, p50, p90, p95, p99 and max latency, plus errors by status code and a warning when latency grows during the run.
- It refuses to hit anything but localhost and private addresses unless you pass `--allow-remote`, meaning you own the target or have written permission, and it caps the request rate (200 per second by default).
- Claude can also generate a k6 script with stages and thresholds for heavier tests, then explains where the system saturates and what to look at first (connection pool, slow query, CPU, rate limits).

## Use it

- `/api-load-tester:load-test http://localhost:3000/api/items --concurrency 20 --duration 30`
- `/api-load-tester:load-k6 POST /api/orders`
- Or ask: "How many requests per second can this endpoint take?"

## Requirements

Python 3. Optional: `k6` to run generated scripts.

## Data

Requests go only to the URL you give. The plugin sends nothing else anywhere. Never test systems you do not own.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
