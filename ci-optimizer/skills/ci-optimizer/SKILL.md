---
name: ci-optimizer
description: "Use when a GitHub Actions or GitLab CI pipeline is slow, expensive, flaky or being written, to find missing caches, wasted runs, unsafe settings and the slowest jobs."
---

# CI Optimizer

Make CI pipelines faster, cheaper and safer, based on the real workflow files and real run times.

## 1. Check the workflow files

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/ci_check.py                       # .github/workflows and .gitlab-ci.yml
python3 ${CLAUDE_SKILL_DIR}/scripts/ci_check.py .github/workflows/ci.yml
```

Each finding has a file, line, category and fix:

- **speed**: setup-node, setup-python and setup-java without a dependency cache, `npm install` instead of `npm ci`, no `concurrency` with `cancel-in-progress`, no `paths` filters, full-history clones, Docker builds without layer cache, GitLab jobs without `cache`, `needs` or `interruptible`
- **cost**: jobs without a timeout, macOS and Windows runners, artifacts kept for the default retention
- **safety**: actions pinned to a moving branch, no `permissions` block, untrusted PR text expanded inside `run:`, `pull_request_target` that checks out PR code, unpinned images

The checks read text, so confirm each one in context before changing it. For example, `fetch-depth: 0` is right when a step needs tags or history.

## 2. Measure real run times (GitHub)

If the `gh` CLI is installed and logged in, get real numbers instead of guessing:

```bash
gh run list --workflow <file.yml> --limit 20 --json databaseId,conclusion,createdAt,updatedAt,event,headBranch
gh run view <run-id> --json jobs --jq '.jobs[] | {name, conclusion, startedAt, completedAt, steps: [.steps[] | {name, startedAt, completedAt}]}'
```

Compute the duration of each job and step from the timestamps, and the median over recent successful runs. Report the critical path: the longest chain of jobs that must run one after another, since that sets the wall-clock time.

For GitLab, use `glab ci list` and `glab ci view` if installed, or ask the user for pipeline durations.

## 3. Find flaky tests

With `gh`:

```bash
gh run list --workflow <file.yml> --limit 50 --json databaseId,conclusion,headSha,attempt
```

Runs on the same `headSha` that failed and then passed on a re-run point to flakiness. Open the failed attempt's log (`gh run view <id> --log-failed`) and collect which test failed. A test that fails on unrelated commits and passes on retry is flaky. Look in the test for timing (`sleep`, fixed timeouts), shared state between tests, order dependence, real network calls, unseeded random data and dates.

## 4. Improve

Apply changes in this order, because the first ones are cheap and safe:

1. Dependency caches (`cache: npm` in setup-node, `cache: pip`, `actions/cache` keyed on the lockfile hash) and `npm ci`.
2. `concurrency` with `cancel-in-progress: true` for pull requests, and `paths` / `paths-ignore` filters.
3. `timeout-minutes` on every job and `retention-days` on artifacts.
4. Split slow test suites across a `matrix` with the test runner's sharding (`jest --shard=${{ matrix.shard }}/4`, `vitest --shard`, `playwright test --shard`, `pytest-split`), and run independent jobs in parallel instead of in one long job.
5. Build caches: `docker/build-push-action` with `cache-from: type=gha` and `cache-to: type=gha,mode=max`, Turborepo or Nx remote cache if the repo already uses them.
6. Least-privilege `permissions`, actions pinned to a version tag or SHA, untrusted input passed through `env:`.

Keep behaviour the same: do not remove jobs, checks or deployments to save time. Show the diff of each workflow change and, when there are run times, the expected saving based on the measured step durations. Do not quote saving percentages without measurements.
