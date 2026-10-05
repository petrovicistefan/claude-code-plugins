#!/usr/bin/env python3
"""Find likely secrets in files. Prints masked matches; exit code 1 if any found."""
import argparse
import os
import re
import sys

RULES = [
    ("AWS access key", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{50,}\b")),
    ("Stripe key", re.compile(r"\b(sk|rk)_(live|test)_[A-Za-z0-9]{16,}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b")),
    ("OpenAI key", re.compile(r"\bsk-(proj-)?[A-Za-z0-9_\-]{32,}\b")),
    ("Private key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b")),
    ("Password in URL", re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s:/@]+:([^\s@/]{4,})@")),
    ("Hardcoded secret", re.compile(
        r"(?i)\b(api[_-]?key|secret|token|passw(or)?d|private[_-]?key|access[_-]?key)\w*\s*[:=]\s*['\"]([^'\"\s]{8,})['\"]")),
]
PLACEHOLDER = re.compile(r"(?i)(xxx|your[_-]|example|changeme|placeholder|dummy|<|\$\{|\benv(iron)?\b|getenv)")
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", "vendor", "__pycache__", ".venv", "venv"}
SKIP_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".woff", ".woff2",
            ".ttf", ".lock", ".min.js", ".map")


def mask(value):
    return value[:4] + "****" + value[-4:] if len(value) > 12 else "****"


def files_in(path):
    if os.path.isfile(path):
        yield path
        return
    for dirpath, dirs, names in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            if not n.endswith(SKIP_EXT):
                yield os.path.join(dirpath, n)


def scan(path):
    hits = []
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for no, line in enumerate(f, 1):
                if len(line) > 2000:
                    continue
                for name, rx in RULES:
                    m = rx.search(line)
                    if m and not PLACEHOLDER.search(m.group(0)):
                        value = m.group(m.lastindex) if m.lastindex else m.group(0)
                        hits.append((path, no, name, mask(value)))
                        break
    except OSError:
        pass
    return hits


def env_names(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=", 1)[0].replace("export ", "").strip()
                has_value = bool(line.split("=", 1)[1].strip().strip("'\""))
                print(f"{key}{'' if has_value else '  (empty)'}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("paths", nargs="*", default=["."], help="files or folders to scan")
    p.add_argument("--env-names", metavar="FILE", help="print variable names from an env file, never values")
    a = p.parse_args()

    if a.env_names:
        env_names(a.env_names)
        return

    targets = [f for path in a.paths for f in files_in(path)]
    hits = [h for t in targets for h in scan(t)]
    for path, no, name, masked in hits:
        print(f"{path}:{no}: {name}: {masked}")
    print(f"\n{len(hits)} possible secret(s) in {len(targets)} file(s) scanned.")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
