#!/usr/bin/env python3
"""Scan a project and report what is needed to run it locally.

Standard library only. Never runs other programs and never prints the values
from .env files, only key names.

Usage: scan_env.py [project_dir] [--json]
"""
import json
import os
import re
import shutil
import sys

ENV_EXAMPLES = (".env.example", ".env.sample", ".env.template", ".env.dist", "example.env")
ENV_REAL = (".env", ".env.local", ".env.development", ".env.development.local")
LOCKFILES = {
    "pnpm-lock.yaml": "pnpm", "yarn.lock": "yarn", "package-lock.json": "npm",
    "bun.lockb": "bun", "bun.lock": "bun", "poetry.lock": "poetry", "uv.lock": "uv",
    "Pipfile.lock": "pipenv", "Cargo.lock": "cargo", "go.sum": "go",
    "Gemfile.lock": "bundler", "composer.lock": "composer",
}
KEY_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$")


def read(path, limit=200_000):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(limit)
    except OSError:
        return None


def first_line(path):
    text = read(path, 2000)
    return text.strip().splitlines()[0].strip() if text and text.strip() else None


def env_keys(path):
    """Return {key: has_value}. Values are reduced to a boolean and dropped."""
    text = read(path)
    keys = {}
    if text is None:
        return keys
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        m = KEY_RE.match(line)
        if m:
            keys[m.group(1)] = bool(m.group(2).strip().strip("\"'"))
    return keys


def detect_runtimes(root):
    found = []

    def add(name, version, source):
        found.append({"runtime": name, "required": version, "source": source,
                      "on_path": shutil.which(name if name != "node" else "node") is not None})

    pkg = None
    pkg_text = read(os.path.join(root, "package.json"))
    if pkg_text:
        try:
            pkg = json.loads(pkg_text)
        except ValueError:
            pkg = None
    for fname in (".nvmrc", ".node-version"):
        v = first_line(os.path.join(root, fname))
        if v:
            add("node", v, fname)
            break
    else:
        if pkg and isinstance(pkg.get("engines"), dict) and pkg["engines"].get("node"):
            add("node", pkg["engines"]["node"], "package.json engines")
        elif pkg:
            add("node", None, "package.json (no version pinned)")

    v = first_line(os.path.join(root, ".python-version"))
    if v:
        add("python3", v, ".python-version")
    else:
        pyproject = read(os.path.join(root, "pyproject.toml")) or ""
        m = re.search(r"requires-python\s*=\s*[\"']([^\"']+)", pyproject)
        if m:
            add("python3", m.group(1), "pyproject.toml requires-python")
        elif os.path.exists(os.path.join(root, "requirements.txt")) or pyproject:
            add("python3", None, "python project (no version pinned)")

    gomod = read(os.path.join(root, "go.mod")) or ""
    m = re.search(r"^go\s+(\S+)", gomod, re.M)
    if m:
        add("go", m.group(1), "go.mod")

    v = first_line(os.path.join(root, ".ruby-version"))
    if v:
        add("ruby", v, ".ruby-version")
    elif os.path.exists(os.path.join(root, "Gemfile")):
        add("ruby", None, "Gemfile")

    for fname in ("rust-toolchain", "rust-toolchain.toml"):
        t = read(os.path.join(root, fname))
        if t:
            m = re.search(r"channel\s*=\s*[\"']([^\"']+)", t)
            add("cargo", m.group(1) if m else t.strip().splitlines()[0], fname)
            break
    else:
        if os.path.exists(os.path.join(root, "Cargo.toml")):
            add("cargo", None, "Cargo.toml")

    if os.path.exists(os.path.join(root, "composer.json")):
        add("php", None, "composer.json")

    tv = read(os.path.join(root, ".tool-versions"))
    if tv:
        for line in tv.splitlines():
            parts = line.split()
            if len(parts) >= 2 and not line.lstrip().startswith("#"):
                found.append({"runtime": parts[0], "required": parts[1], "source": ".tool-versions",
                              "on_path": shutil.which(parts[0]) is not None})
    return found, pkg


def detect_package_manager(root, pkg):
    names = [LOCKFILES[f] for f in LOCKFILES if os.path.exists(os.path.join(root, f))]
    declared = pkg.get("packageManager") if pkg else None
    if os.path.exists(os.path.join(root, "requirements.txt")) and "poetry" not in names and "uv" not in names:
        names.append("pip")
    result = []
    for n in names:
        result.append({"tool": n, "on_path": shutil.which(n) is not None})
    return {"lockfiles": result, "declared": declared}


def detect_installed(root):
    checks = {
        "node_modules": os.path.isdir(os.path.join(root, "node_modules")),
        "python venv": any(os.path.isdir(os.path.join(root, d)) for d in (".venv", "venv", "env")),
        "vendor": os.path.isdir(os.path.join(root, "vendor")),
        "target": os.path.isdir(os.path.join(root, "target")),
    }
    needs = {
        "node_modules": os.path.exists(os.path.join(root, "package.json")),
        "python venv": os.path.exists(os.path.join(root, "requirements.txt")) or os.path.exists(os.path.join(root, "pyproject.toml")),
        "vendor": os.path.exists(os.path.join(root, "Gemfile")) or os.path.exists(os.path.join(root, "composer.json")),
        "target": os.path.exists(os.path.join(root, "Cargo.toml")),
    }
    return [{"item": k, "needed": needs[k], "present": checks[k]} for k in checks if needs[k]]


def detect_env(root):
    example = next((f for f in ENV_EXAMPLES if os.path.exists(os.path.join(root, f))), None)
    real = [f for f in ENV_REAL if os.path.exists(os.path.join(root, f))]
    out = {"example": example, "real_files": real, "missing_keys": [], "empty_in_real": [], "needs_values": []}
    if not example:
        return out
    ex = env_keys(os.path.join(root, example))
    out["needs_values"] = sorted(k for k, has in ex.items() if not has)
    if not real:
        out["missing_keys"] = sorted(ex)
        return out
    have = {}
    for f in real:
        for k, has in env_keys(os.path.join(root, f)).items():
            have[k] = have.get(k, False) or has
    out["missing_keys"] = sorted(k for k in ex if k not in have)
    out["empty_in_real"] = sorted(k for k in ex if k in have and not have[k] and ex[k] is False)
    return out


def detect_docker(root):
    compose = next((f for f in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")
                    if os.path.exists(os.path.join(root, f))), None)
    services = []
    if compose:
        text = read(os.path.join(root, compose)) or ""
        in_services = False
        indent = None
        for line in text.splitlines():
            if re.match(r"^services:\s*$", line):
                in_services = True
                continue
            if in_services:
                if line and not line.startswith((" ", "\t", "#")):
                    break
                m = re.match(r"^(\s+)([A-Za-z0-9_.-]+):\s*$", line)
                if m and (indent is None or len(m.group(1)) == indent):
                    indent = len(m.group(1))
                    services.append(m.group(2))
    return {"compose_file": compose, "services": services,
            "dockerfile": os.path.exists(os.path.join(root, "Dockerfile")),
            "docker_on_path": shutil.which("docker") is not None}


def detect_commands(root, pkg):
    cmds = []
    if pkg and isinstance(pkg.get("scripts"), dict):
        for name in ("setup", "bootstrap", "dev", "start", "build", "test", "migrate", "seed"):
            if name in pkg["scripts"]:
                cmds.append({"source": "package.json", "name": name, "command": pkg["scripts"][name]})
    make = read(os.path.join(root, "Makefile"))
    if make:
        for name in ("setup", "install", "bootstrap", "dev", "run", "up", "test", "migrate", "seed"):
            if re.search(r"^%s:" % re.escape(name), make, re.M):
                cmds.append({"source": "Makefile", "name": name, "command": "make " + name})
    for name in ("manage.py", "artisan", "bin/rails"):
        if os.path.exists(os.path.join(root, name)):
            cmds.append({"source": name, "name": "framework entry", "command": name})
    if os.path.exists(os.path.join(root, "prisma", "schema.prisma")):
        cmds.append({"source": "prisma/schema.prisma", "name": "database schema", "command": "prisma migrate dev / generate"})
    if os.path.exists(os.path.join(root, ".pre-commit-config.yaml")):
        cmds.append({"source": ".pre-commit-config.yaml", "name": "git hooks", "command": "pre-commit install"})
    if os.path.isdir(os.path.join(root, ".husky")):
        cmds.append({"source": ".husky", "name": "git hooks", "command": "installed by the prepare script"})
    return cmds


def scan(root):
    runtimes, pkg = detect_runtimes(root)
    return {
        "project": os.path.abspath(root),
        "runtimes": runtimes,
        "package_managers": detect_package_manager(root, pkg),
        "dependencies_installed": detect_installed(root),
        "env": detect_env(root),
        "docker": detect_docker(root),
        "commands": detect_commands(root, pkg),
        "readme": next((f for f in ("README.md", "README", "README.rst") if os.path.exists(os.path.join(root, f))), None),
        "contributing": os.path.exists(os.path.join(root, "CONTRIBUTING.md")),
    }


def mark(ok):
    return "OK     " if ok else "MISSING"


def render(r):
    lines = ["Project: " + r["project"], ""]
    lines.append("Runtimes")
    if not r["runtimes"]:
        lines.append("  none detected")
    for rt in r["runtimes"]:
        req = rt["required"] or "any version"
        lines.append("  [%s] %-8s needs %-16s (%s)" % (mark(rt["on_path"]), rt["runtime"], req, rt["source"]))
    lines.append("")
    lines.append("Package managers")
    pm = r["package_managers"]
    if pm["declared"]:
        lines.append("  package.json declares: " + pm["declared"])
    if not pm["lockfiles"]:
        lines.append("  no lockfile found")
    for p in pm["lockfiles"]:
        lines.append("  [%s] %s (lockfile present)" % (mark(p["on_path"]), p["tool"]))
    lines.append("")
    lines.append("Dependencies installed")
    if not r["dependencies_installed"]:
        lines.append("  nothing to check")
    for d in r["dependencies_installed"]:
        lines.append("  [%s] %s" % (mark(d["present"]), d["item"]))
    lines.append("")
    e = r["env"]
    lines.append("Environment variables (names only, values are never read out)")
    if not e["example"]:
        lines.append("  no .env.example found")
    else:
        lines.append("  template: " + e["example"])
        lines.append("  your files: " + (", ".join(e["real_files"]) or "none, copy the template to .env"))
        if e["missing_keys"]:
            lines.append("  missing keys: " + ", ".join(e["missing_keys"]))
        if e["empty_in_real"]:
            lines.append("  present but empty: " + ", ".join(e["empty_in_real"]))
        if e["needs_values"]:
            lines.append("  empty in the template, you must supply: " + ", ".join(e["needs_values"]))
        if not e["missing_keys"] and not e["empty_in_real"]:
            lines.append("  all template keys are set")
    lines.append("")
    d = r["docker"]
    lines.append("Docker")
    if not (d["compose_file"] or d["dockerfile"]):
        lines.append("  not used")
    else:
        if d["compose_file"]:
            lines.append("  %s services: %s" % (d["compose_file"], ", ".join(d["services"]) or "none parsed"))
        if d["dockerfile"]:
            lines.append("  Dockerfile present")
        lines.append("  [%s] docker on PATH" % mark(d["docker_on_path"]))
    lines.append("")
    lines.append("Commands found")
    if not r["commands"]:
        lines.append("  none found, check the README")
    for c in r["commands"]:
        lines.append("  %-22s %-14s %s" % (c["source"], c["name"], c["command"]))
    lines.append("")
    docs = [x for x in (r["readme"], "CONTRIBUTING.md" if r["contributing"] else None) if x]
    lines.append("Docs: " + (", ".join(docs) or "none"))
    return "\n".join(lines)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    root = args[0] if args else "."
    if not os.path.isdir(root):
        sys.exit("not a directory: " + root)
    result = scan(root)
    print(json.dumps(result, indent=2) if "--json" in argv else render(result))


if __name__ == "__main__":
    main(sys.argv)
