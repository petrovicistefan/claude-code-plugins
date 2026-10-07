#!/usr/bin/env python3
"""Check dbt projects and Airflow DAGs for missing tests, docs, retries and unsafe patterns.

  pipeline_check.py [folder]     default: current folder

dbt: models without tests or descriptions, sources without freshness, SELECT *,
hardcoded table names instead of ref()/source(), missing primary-key tests.
Airflow: DAGs without retries, catchup left on, heavy code at import time,
credentials in code, no schedule or owner, bare except.
Text based; reads files only.
"""
import os
import re
import sys

SKIP = {".git", "node_modules", "venv", ".venv", "target", "dbt_packages", "logs", "__pycache__"}


def walk(root, exts):
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in fs:
            if f.endswith(exts):
                yield os.path.join(d, f)


def text(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def check_dbt(root, add):
    projects = [d for d, _, fs in os.walk(root) if "dbt_project.yml" in fs and not any(s in d for s in SKIP)]
    for proj in projects:
        models = {os.path.splitext(os.path.basename(p))[0]: p for p in walk(os.path.join(proj, "models"), (".sql",))}
        yml = "\n".join(text(p) for p in walk(os.path.join(proj, "models"), (".yml", ".yaml")))
        documented = set(re.findall(r"^\s*-\s*name:\s*(\S+)", yml, re.M))
        for name, path in models.items():
            t = text(path)
            if re.search(r"select\s+\*", t, re.I) and "/staging/" not in path.replace("\\", "/"):
                add("low", path, "SELECT * outside staging: new upstream columns silently flow downstream. List columns.")
            if name not in documented:
                add("medium", path, f"model {name} is not described in any schema .yml (no tests, no docs).")
                continue
            block = re.search(r"-\s*name:\s*%s\b(.*?)(?=\n\s*-\s*name:|\Z)" % re.escape(name), yml, re.S)
            b = block.group(1) if block else ""
            if "description" not in b:
                add("low", path, f"model {name} has no description.")
            if not re.search(r"\b(unique|not_null|relationships|accepted_values|dbt_utils\.\w+)\b", b):
                add("medium", path, f"model {name} has no tests. At least add unique and not_null on its key.")
            elif not re.search(r"\bunique\b", b):
                add("low", path, f"model {name} has no `unique` test on its key.")
            if re.search(r"\b(from|join)\s+[a-z_]+\.[a-z_]+\b(?!\s*\()", re.sub(r"\{\{.*?\}\}", "", t), re.I):
                add("medium", path, "hardcoded schema.table in FROM/JOIN. Use ref() or source() so dbt can build the dependency graph.")
        for src in re.finditer(r"sources:(.*?)(?=\nmodels:|\Z)", yml, re.S):
            if "freshness" not in src.group(1) and "loaded_at_field" not in src.group(1):
                add("low", proj, "sources have no `freshness` check, so stale loads go unnoticed.")
                break


def check_airflow(root, add):
    for p in walk(root, (".py",)):
        t = text(p)
        if not re.search(r"\bfrom airflow|import airflow", t) or not re.search(r"\bDAG\(|@dag\b", t):
            continue
        if "retries" not in t:
            add("medium", p, "no `retries` in the DAG or default_args: one network blip fails the run.")
        if re.search(r"\bDAG\(|@dag\b", t) and "catchup" not in t:
            add("medium", p, "`catchup` not set. Airflow 2 defaults to True and will backfill every interval since start_date.")
        if re.search(r"schedule(_interval)?\s*=\s*None", t) is None and not re.search(r"schedule(_interval)?\s*=", t):
            add("low", p, "no schedule given.")
        if "owner" not in t:
            add("low", p, "no `owner` in default_args, so nobody is paged or tagged.")
        if re.search(r"(password|secret|api_key|token)\s*=\s*[\"'][^\"']{4,}[\"']", t, re.I):
            add("high", p, "credential written in the DAG file. Use an Airflow Connection or Variable backed by a secrets backend.")
        top = re.split(r"\n(?:with DAG|@dag|def )", t, 1)[0]
        if re.search(r"requests\.(get|post)|pd\.read_|\.connect\(|Variable\.get\(|open\(", top):
            add("medium", p, "network, file or Variable access at import time. The scheduler runs this every few seconds. Move it inside a task.")
        if re.search(r"except\s*:\s*\n\s*pass", t):
            add("medium", p, "bare `except: pass` hides task failures.")
        if re.search(r"datetime\.(now|today)\(\)", t):
            add("medium", p, "datetime.now() in a task or start_date breaks reruns. Use the data interval (logical_date / data_interval_start).")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    out = []
    add = lambda sev, path, msg: out.append((sev, os.path.relpath(path, root), msg))
    check_dbt(root, add)
    check_airflow(root, add)
    order = {"high": 0, "medium": 1, "low": 2}
    for sev, path, msg in sorted(out, key=lambda x: (order[x[0]], x[1])):
        print(f"[{sev.upper():6}] {path}  {msg}")
    print(f"\n{len(out)} findings, {sum(1 for o in out if o[0] == 'high')} high")
    if not out:
        print("No dbt project or Airflow DAG problems found (or none exist in this folder).")
    return 1 if any(o[0] == "high" for o in out) else 0


if __name__ == "__main__":
    sys.exit(main())
