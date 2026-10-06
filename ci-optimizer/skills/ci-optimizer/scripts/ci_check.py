#!/usr/bin/env python3
"""Check GitHub Actions and GitLab CI files for common speed, cost and safety problems.

  ci_check.py                      scan .github/workflows and .gitlab-ci.yml in the current folder
  ci_check.py <file-or-dir> ...    scan specific files or folders

The checks are text based, so no YAML library is needed. Each finding names the
file, the line and a concrete fix.
"""
import os
import re
import sys

def find_files(args):
    if not args:
        args = [".github/workflows", ".gitlab-ci.yml"]
    for a in args:
        if os.path.isdir(a):
            for n in sorted(os.listdir(a)):
                if n.endswith((".yml", ".yaml")):
                    yield os.path.join(a, n)
        elif os.path.isfile(a):
            yield a


def jobs_of(lines):
    """Return [(job_name, start, end)] for GitHub Actions `jobs:` blocks."""
    jobs, in_jobs, job_indent = [], False, None
    for i, line in enumerate(lines):
        if re.match(r"^jobs:\s*$", line):
            in_jobs = True
            continue
        if in_jobs and re.match(r"^\S", line):
            in_jobs = False
        if not in_jobs:
            continue
        m = re.match(r"^(\s+)([\w-]+):\s*$", line)
        if m and (job_indent is None or len(m.group(1)) == job_indent):
            job_indent = len(m.group(1))
            if jobs:
                jobs[-1][2] = i
            jobs.append([m.group(2), i, len(lines)])
    return [tuple(j) for j in jobs]


def check_github(path, text, lines):
    out = []

    def add(i, sev, msg):
        out.append((path, i + 1, sev, msg))

    whole = text
    if not re.search(r"^concurrency:", whole, re.M) and re.search(r"pull_request", whole):
        add(0, "speed", "no top-level `concurrency:`; add `concurrency: {group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true}` so new pushes cancel outdated PR runs")
    if re.search(r"^\s*(push|pull_request):\s*$", whole, re.M) and not re.search(r"paths(-ignore)?:", whole):
        add(0, "speed", "runs on every push/PR with no `paths:` or `paths-ignore:` filter; docs-only changes still run the whole pipeline")
    if not re.search(r"^permissions:", whole, re.M) and not re.search(r"^\s+permissions:", whole, re.M):
        add(0, "safety", "no `permissions:` block; the GITHUB_TOKEN gets the repository default (often write). Add `permissions: contents: read` and widen per job")
    if re.search(r"pull_request_target", whole) and re.search(r"ref:\s*\$\{\{\s*github\.event\.pull_request\.head", whole):
        add(0, "safety", "pull_request_target checks out the PR head; untrusted code runs with secrets. Use pull_request or do not run PR code")

    for name, start, end in jobs_of(lines):
        block = "\n".join(lines[start:end])
        if "timeout-minutes" not in block:
            add(start, "cost", f"job `{name}` has no `timeout-minutes`; a hung step runs for the 360 minute default")
        if re.search(r"uses:\s*actions/setup-node@", block) and not re.search(r"\bcache:\s*['\"]?(npm|yarn|pnpm)", block) and "actions/cache@" not in block:
            add(start, "speed", f"job `{name}` uses setup-node without `cache:`; add `cache: npm` (or yarn/pnpm) to reuse the package cache")
        if re.search(r"uses:\s*actions/setup-python@", block) and not re.search(r"\bcache:\s*['\"]?(pip|pipenv|poetry)", block) and "actions/cache@" not in block:
            add(start, "speed", f"job `{name}` uses setup-python without `cache: pip`")
        if re.search(r"uses:\s*actions/setup-java@", block) and not re.search(r"\bcache:\s*['\"]?(maven|gradle|sbt)", block) and "actions/cache@" not in block and "gradle/actions/setup-gradle" not in block:
            add(start, "speed", f"job `{name}` uses setup-java without `cache: maven` or `cache: gradle`")
        if re.search(r"uses:\s*actions/setup-go@", block) and re.search(r"cache:\s*false", block):
            add(start, "speed", f"job `{name}` disables the Go module cache")
        if re.search(r"docker/build-push-action@", block) and not re.search(r"cache-from:", block):
            add(start, "speed", f"job `{name}` builds a Docker image without `cache-from`/`cache-to` (for example `type=gha`)")
        if re.search(r"fetch-depth:\s*0", block) and not re.search(r"(changelog|semantic-release|release-please|git describe|git tag|--tags|sonar|nx affected|turbo|lerna|gitversion|commitlint)", block, re.I):
            add(start, "speed", f"job `{name}` clones the full git history (`fetch-depth: 0`); a shallow clone is enough unless a step needs history")

    for i, line in enumerate(lines):
        s = line.strip()
        m = re.search(r"uses:\s*([\w.-]+/[\w./-]+)@([\w.-]+)", s)
        if m and not m.group(1).startswith("./"):
            ref = m.group(2)
            if ref in ("master", "main", "latest", "dev", "develop"):
                add(i, "safety", f"`{m.group(1)}@{ref}` follows a moving branch; pin to a release tag or a commit SHA")
        if re.search(r"(^|\s|-\s+run:\s*|&&\s*)npm install(\s|$)", s) and not re.search(r"npm install\s+(-g|--global)", s):
            add(i, "speed", "`npm install` in CI; `npm ci` is faster and installs exactly the lockfile")
        if re.search(r"\byarn( install)?\s*$", s) and "--frozen-lockfile" not in s and "--immutable" not in s:
            add(i, "safety", "yarn install without `--frozen-lockfile` / `--immutable`")
        if re.search(r"\bpnpm install\b", s) and "--frozen-lockfile" not in s:
            add(i, "safety", "pnpm install without `--frozen-lockfile`")
        if re.search(r"runs-on:\s*(macos|windows)", s):
            add(i, "cost", f"`{s}` bills at a higher per-minute rate than Linux on GitHub-hosted runners; use it only for platform-specific jobs")
        if re.search(r"\$\{\{\s*github\.event\.(issue|pull_request|comment|review)\.[\w.]*(title|body|head_ref|label)", s) and "run:" in "\n".join(lines[max(0, i - 3):i + 1]):
            add(i, "safety", "untrusted event text is expanded directly inside `run:`; pass it through `env:` to avoid script injection")
        if re.search(r"actions/upload-artifact@", s):
            block = "\n".join(lines[i:i + 8])
            if "retention-days" not in block:
                add(i, "cost", "upload-artifact without `retention-days`; artifacts are kept for the repository default (90 days) and count toward storage")
    return out


def check_gitlab(path, text, lines):
    out = []

    def add(i, sev, msg):
        out.append((path, i + 1, sev, msg))

    if "cache:" not in text:
        add(0, "speed", "no `cache:` anywhere; cache dependency folders keyed on the lockfile (`cache: key: files: [package-lock.json]`)")
    if "interruptible:" not in text:
        add(0, "speed", "no `interruptible: true`; with auto-cancel redundant pipelines enabled, outdated pipelines keep running")
    if not re.search(r"^\s*(rules|only|except):", text, re.M) and not re.search(r"^workflow:", text, re.M):
        add(0, "speed", "no `rules:` or `workflow:` filters; every push runs every job")
    if "needs:" not in text and len(re.findall(r"^\s*stage:", text, re.M)) > 3:
        add(0, "speed", "no `needs:`; each stage waits for the whole previous stage. `needs:` lets jobs start as soon as their inputs are ready")
    if "timeout:" not in text:
        add(0, "cost", "no `timeout:` on jobs; a hung job runs until the project timeout")
    for i, line in enumerate(lines):
        s = line.strip()
        if re.search(r"\bnpm install(\s|$)", s) and "-g" not in s:
            add(i, "speed", "`npm install` in CI; use `npm ci`")
        m = re.match(r"image:\s*['\"]?([\w./-]+)(?::(\S+?))?['\"]?$", s)
        if m and (m.group(2) in (None, "latest")):
            add(i, "safety", f"image `{m.group(1)}` is not pinned to a version")
        if re.match(r"artifacts:\s*$", s) and "expire_in" not in "\n".join(lines[i:i + 8]):
            add(i, "cost", "artifacts without `expire_in`")
    return out


def main():
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print(__doc__)
        return
    files = list(find_files(sys.argv[1:]))
    if not files:
        sys.exit("No CI files found. Pass a workflow file or folder (.github/workflows, .gitlab-ci.yml).")
    findings = []
    for f in files:
        text = open(f, encoding="utf-8", errors="replace").read()
        lines = text.splitlines()
        if os.path.basename(f).startswith(".gitlab-ci") or "stages:" in text and "jobs:" not in text:
            findings += check_gitlab(f, text, lines)
        else:
            findings += check_github(f, text, lines)
    order = {"safety": 0, "speed": 1, "cost": 2}
    for path, line, sev, msg in sorted(findings, key=lambda x: (x[0], x[1], order[x[2]])):
        print(f"{path}:{line}: [{sev}] {msg}")
    counts = {k: sum(1 for x in findings if x[2] == k) for k in order}
    print(f"\n{len(files)} files, {len(findings)} findings: " + ", ".join(f"{v} {k}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
