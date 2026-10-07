#!/usr/bin/env python3
"""Work out what a project needs to run and compare it with what this machine has.

  env_audit.py [folder]     default: current folder

Reads version files, package manifests, docker-compose services, .env.example and
the environment variables the code reads. Looks tools up on PATH without running them.
Never prints the values of any variable.
"""
import json
import os
import re
import shutil
import sys

SKIP = {"node_modules", ".git", "venv", ".venv", "dist", "build", "__pycache__", ".next", "target", "vendor"}


def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def installed(cmd):
    """Return the path of the tool if it is on PATH, else None. Nothing is executed."""
    return shutil.which(cmd[0])


def requirements(root):
    req = []  # (tool, wanted, source, version command)
    f = lambda n: os.path.join(root, n)
    for n in (".nvmrc", ".node-version"):
        if os.path.isfile(f(n)):
            req.append(("node", read(f(n)).strip().lstrip("v"), n, ["node", "--version"]))
    if os.path.isfile(f("package.json")):
        try:
            j = json.load(open(f("package.json")))
            eng = j.get("engines", {})
            if not eng.get("node") and not any(r[0] == "node" for r in req):
                req.append(("node", "any", "package.json", ["node", "--version"]))
            if "node" in eng and not any(r[0] == "node" for r in req):
                req.append(("node", eng["node"], "package.json engines", ["node", "--version"]))
            pm = j.get("packageManager", "")
            for tool in ("pnpm", "yarn", "npm"):
                if pm.startswith(tool) or os.path.isfile(f({"pnpm": "pnpm-lock.yaml", "yarn": "yarn.lock", "npm": "package-lock.json"}[tool])):
                    req.append((tool, pm.split("@")[1] if "@" in pm else "any", "lockfile/packageManager", [tool, "--version"]))
                    break
        except Exception:
            pass
    for n in (".python-version", "runtime.txt"):
        if os.path.isfile(f(n)):
            req.append(("python3", re.sub(r"[^\d.]", "", read(f(n))), n, ["python3", "--version"]))
    if os.path.isfile(f("pyproject.toml")):
        m = re.search(r"requires-python\s*=\s*\"([^\"]+)\"", read(f("pyproject.toml")))
        if m:
            req.append(("python3", m.group(1), "pyproject.toml", ["python3", "--version"]))
    if os.path.isfile(f("go.mod")):
        m = re.search(r"^go\s+(\S+)", read(f("go.mod")), re.M)
        req.append(("go", m.group(1) if m else "any", "go.mod", ["go", "version"]))
    if os.path.isfile(f("Gemfile")) or os.path.isfile(f(".ruby-version")):
        req.append(("ruby", read(f(".ruby-version")).strip() or "any", ".ruby-version/Gemfile", ["ruby", "--version"]))
    if os.path.isfile(f("Cargo.toml")):
        req.append(("cargo", "any", "Cargo.toml", ["cargo", "--version"]))
    if os.path.isfile(f("pom.xml")) or os.path.isfile(f("build.gradle")) or os.path.isfile(f("build.gradle.kts")):
        req.append(("java", "any", "pom/gradle", ["java", "-version"]))
    for n in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml", "Dockerfile"):
        if os.path.isfile(f(n)):
            req.append(("docker", "any", n, ["docker", "--version"]))
            break
    return req


def compose_services(root):
    for n in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
        t = read(os.path.join(root, n))
        if t:
            svc, ports = [], []
            in_services = False
            for line in t.splitlines():
                if re.match(r"^services:\s*$", line):
                    in_services = True
                    continue
                if in_services and re.match(r"^\S", line):
                    in_services = False
                m = re.match(r"^  ([\w.-]+):\s*$", line)
                if in_services and m:
                    svc.append(m.group(1))
                p = re.match(r"^\s+-\s*[\"']?(\d+):(\d+)", line)
                if p:
                    ports.append(p.group(1))
            return n, svc, ports
    return None, [], []


def env_vars(root):
    declared = set()
    for n in (".env.example", ".env.sample", ".env.template", "example.env"):
        for line in read(os.path.join(root, n)).splitlines():
            m = re.match(r"^\s*(?:export\s+)?([A-Z][A-Z0-9_]*)\s*=", line)
            if m:
                declared.add(m.group(1))
    used = set()
    pat = re.compile(r"process\.env\.([A-Z][A-Z0-9_]*)|process\.env\[[\"']([A-Z][A-Z0-9_]*)|os\.environ(?:\.get)?\(?\[?[\"']([A-Z][A-Z0-9_]*)|os\.getenv\([\"']([A-Z][A-Z0-9_]*)|import\.meta\.env\.([A-Z][A-Z0-9_]*)|ENV\[[\"']([A-Z][A-Z0-9_]*)|os\.Getenv\(\"([A-Z][A-Z0-9_]*)")
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for fn in files:
            if fn.endswith((".js", ".ts", ".tsx", ".jsx", ".py", ".rb", ".go", ".mjs", ".vue", ".svelte")):
                for m in pat.finditer(read(os.path.join(d, fn))):
                    used.add(next(g for g in m.groups() if g))
    return declared, used


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    print("# Environment audit\n\n## Tools")
    missing = 0
    for tool, wanted, src, cmd in requirements(root):
        have = installed(cmd)
        status = "MISSING" if have is None else f"found at {have}"
        if have is None:
            missing += 1
        print(f"- {tool}: wants {wanted} ({src}), {status}")
    name, svc, ports = compose_services(root)
    if name:
        print(f"\n## Services in {name}\n- {', '.join(svc) or 'none parsed'}; host ports: {', '.join(ports) or 'none'}")
    declared, used = env_vars(root)
    print("\n## Environment variables")
    print(f"- Declared in the example env file: {len(declared)}")
    print(f"- Read by the code but not in the example file: {', '.join(sorted(used - declared)) or 'none'}")
    print(f"- In the example file but never read: {', '.join(sorted(declared - used)) or 'none'}")
    scripts = os.path.join(root, "package.json")
    if os.path.isfile(scripts):
        try:
            s = json.load(open(scripts)).get("scripts", {})
            print("\n## Scripts\n" + "\n".join(f"- {k}: {v}" for k, v in s.items() if re.search(r"dev|start|build|test|setup|migrate|seed", k)))
        except Exception:
            pass
    for mk in ("Makefile", "justfile"):
        if os.path.isfile(os.path.join(root, mk)):
            targets = re.findall(r"^([a-zA-Z][\w-]*):", read(os.path.join(root, mk)), re.M)
            print(f"\n## {mk} targets\n- " + ", ".join(targets[:20]))
    print(f"\n{missing} required tool(s) missing")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
