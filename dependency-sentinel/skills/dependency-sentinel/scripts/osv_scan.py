#!/usr/bin/env python3
"""Check the exact dependency versions in your lockfiles against the OSV.dev vulnerability database.

  osv_scan.py [dir]                 find lockfiles in dir (default: current) and query OSV
  osv_scan.py [dir] --offline       only list the packages that would be sent
  osv_scan.py [dir] --json out.json save the full result

Supported: package-lock.json / npm-shrinkwrap.json, yarn.lock, pnpm-lock.yaml,
requirements*.txt (pinned with ==), poetry.lock, Pipfile.lock, uv.lock, go.sum,
Cargo.lock, Gemfile.lock, composer.lock.

Only package names, versions and ecosystems are sent to https://api.osv.dev.
No source code and no credentials leave the machine.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

API = "https://api.osv.dev/v1"
SKIP_DIRS = {"node_modules", ".git", "vendor", "venv", ".venv", "dist", "build", "target", "__pycache__"}


def npm_lock(path):
    data = json.load(open(path))
    out = set()
    for key, v in (data.get("packages") or {}).items():
        if not key or "version" not in v or v.get("link"):
            continue
        name = v.get("name") or key.split("node_modules/")[-1]
        out.add(("npm", name, v["version"], bool(v.get("dev"))))
    if not out:
        def walk(deps):
            for name, v in (deps or {}).items():
                if "version" in v:
                    out.add(("npm", name, v["version"], bool(v.get("dev"))))
                walk(v.get("dependencies"))
        walk(data.get("dependencies"))
    return out


def yarn_lock(path):
    out, names = set(), []
    for line in open(path, encoding="utf-8"):
        if line and not line[0].isspace() and line.rstrip().endswith(":"):
            names = []
            for spec in line.rstrip()[:-1].split(","):
                spec = spec.strip().strip('"')
                m = re.match(r"^(@?[^@]+)@", spec)
                if m:
                    names.append(m.group(1))
        m = re.match(r'^\s+version:?\s+"?([^"\s]+)"?', line)
        if m and names:
            for n in set(names):
                out.add(("npm", n, m.group(1), False))
            names = []
    return out


def pnpm_lock(path):
    out = set()
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\s{2}['\"]?/?(@?[^@\s'\"(]+)[@/](\d[^:('\"\s]*)", line)
        if m and line.rstrip().endswith(":"):
            out.add(("npm", m.group(1), m.group(2), False))
    return out


def requirements(path):
    out = set()
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\s*([A-Za-z0-9_.\-\[\]]+)\s*==\s*([\w.!+\-]+)", line)
        if m:
            out.add(("PyPI", re.sub(r"\[.*\]", "", m.group(1)), m.group(2), False))
    return out


def toml_packages(path, eco):
    out, name = set(), None
    for line in open(path, encoding="utf-8"):
        if line.startswith("[[package]]"):
            name = None
        m = re.match(r'^name\s*=\s*"([^"]+)"', line)
        if m:
            name = m.group(1)
        m = re.match(r'^version\s*=\s*"([^"]+)"', line)
        if m and name:
            out.add((eco, name, m.group(1), False))
            name = None
    return out


def pipfile_lock(path):
    data = json.load(open(path))
    out = set()
    for section, dev in (("default", False), ("develop", True)):
        for name, v in (data.get(section) or {}).items():
            ver = (v.get("version") or "").lstrip("=")
            if ver:
                out.add(("PyPI", name, ver, dev))
    return out


def go_sum(path):
    out = set()
    for line in open(path, encoding="utf-8"):
        parts = line.split()
        if len(parts) >= 2 and not parts[1].endswith("/go.mod"):
            out.add(("Go", parts[0], parts[1].split("/")[0].lstrip("v").replace("+incompatible", ""), False))
    return out


def gemfile_lock(path):
    out, in_specs = set(), False
    for line in open(path, encoding="utf-8"):
        if line.strip() == "specs:":
            in_specs = True
            continue
        if not line.startswith(" "):
            in_specs = False
        m = re.match(r"^    ([\w.\-]+) \(([\w.\-]+)\)", line)
        if in_specs and m:
            out.add(("RubyGems", m.group(1), m.group(2), False))
    return out


def composer_lock(path):
    data = json.load(open(path))
    out = set()
    for section, dev in (("packages", False), ("packages-dev", True)):
        for p in data.get(section) or []:
            out.add(("Packagist", p["name"], p["version"].lstrip("v"), dev))
    return out


PARSERS = {
    "package-lock.json": npm_lock, "npm-shrinkwrap.json": npm_lock, "yarn.lock": yarn_lock,
    "pnpm-lock.yaml": pnpm_lock, "poetry.lock": lambda p: toml_packages(p, "PyPI"),
    "uv.lock": lambda p: toml_packages(p, "PyPI"), "Pipfile.lock": pipfile_lock, "go.sum": go_sum,
    "Cargo.lock": lambda p: toml_packages(p, "crates.io"), "Gemfile.lock": gemfile_lock, "composer.lock": composer_lock,
}


def find_lockfiles(root):
    for dirpath, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for n in sorted(names):
            if n in PARSERS or re.fullmatch(r"requirements[\w.\-]*\.txt", n):
                yield os.path.join(dirpath, n)


def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def severity(v):
    s = (v.get("database_specific") or {}).get("severity")
    if s:
        return s.upper()
    for a in v.get("affected") or []:
        s = (a.get("ecosystem_specific") or {}).get("severity") or (a.get("database_specific") or {}).get("severity")
        if s:
            return str(s).upper()
    return "UNKNOWN" if not v.get("severity") else "SEE " + v["severity"][0].get("type", "CVSS")


def fixed_versions(v, eco, name):
    fixed = []
    for a in v.get("affected") or []:
        pkg = a.get("package") or {}
        if pkg.get("ecosystem") != eco or pkg.get("name", "").lower() != name.lower():
            continue
        for r in a.get("ranges") or []:
            for e in r.get("events") or []:
                if "fixed" in e:
                    fixed.append(e["fixed"])
    return sorted(set(fixed))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", nargs="?", default=".")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--prod-only", action="store_true", help="skip packages marked as dev in the lockfile")
    ap.add_argument("--json")
    a = ap.parse_args()

    pkgs = {}
    files = list(find_lockfiles(a.dir))
    if not files:
        sys.exit("No supported lockfile found. Run the package manager's install once to create one.")
    for f in files:
        name = os.path.basename(f)
        parser = PARSERS.get(name, requirements)
        try:
            found = parser(f)
        except (ValueError, KeyError, OSError) as e:
            print(f"Could not read {f}: {e}", file=sys.stderr)
            continue
        print(f"{f}: {len(found)} packages")
        for eco, n, ver, dev in found:
            key = (eco, n, ver)
            pkgs[key] = pkgs.get(key, True) and dev
    if a.prod_only:
        pkgs = {k: d for k, d in pkgs.items() if not d}
    keys = sorted(pkgs)
    print(f"{len(keys)} unique package versions")
    if a.offline:
        for eco, n, ver in keys:
            print(f"  {eco:10} {n} {ver}")
        return

    hits = {}
    try:
        for i in range(0, len(keys), 1000):
            chunk = keys[i:i + 1000]
            res = post(f"{API}/querybatch", {"queries": [{"package": {"ecosystem": e, "name": n}, "version": v} for e, n, v in chunk]})
            for key, r in zip(chunk, res.get("results", [])):
                ids = [x["id"] for x in r.get("vulns") or []]
                if ids:
                    hits[key] = ids
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach api.osv.dev: {e}. Use --offline to list packages without the lookup.")

    details = {}
    for ids in hits.values():
        for vid in ids:
            if vid not in details:
                try:
                    details[vid] = get(f"{API}/vulns/{vid}")
                except urllib.error.URLError:
                    details[vid] = {"id": vid}

    rank = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "MEDIUM": 2, "LOW": 3}
    rows = []
    for (eco, n, ver), ids in hits.items():
        for vid in ids:
            v = details[vid]
            aliases = [x for x in v.get("aliases") or [] if x.startswith("CVE-")]
            rows.append({"ecosystem": eco, "package": n, "version": ver, "dev": pkgs[(eco, n, ver)], "id": vid,
                         "cve": aliases[0] if aliases else "", "severity": severity(v),
                         "summary": (v.get("summary") or v.get("details") or "").strip().split("\n")[0][:140],
                         "fixed": fixed_versions(v, eco, n)})
    rows.sort(key=lambda r: (rank.get(r["severity"], 4), r["package"]))

    print(f"\n{len(rows)} known vulnerabilities in {len(hits)} package versions\n")
    for r in rows:
        fix = ("fixed in " + ", ".join(r["fixed"][-3:])) if r["fixed"] else "no fixed version listed"
        print(f"[{r['severity']}] {r['package']} {r['version']} ({r['ecosystem']}{', dev' if r['dev'] else ''})  {r['id']} {r['cve']}")
        print(f"    {r['summary']}")
        print(f"    {fix}   https://osv.dev/vulnerability/{r['id']}")
    if a.json:
        json.dump(rows, open(a.json, "w"), indent=2)
    sys.exit(1 if rows else 0)


if __name__ == "__main__":
    main()
