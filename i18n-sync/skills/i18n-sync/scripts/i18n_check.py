#!/usr/bin/env python3
"""Compare JSON locale files against a base language."""
import argparse
import json
import os
import re
import sys

PLACEHOLDER = re.compile(r"\{\{?\s*[\w.]+\s*\}?\}|%[sd]|%\(\w+\)s|:\w+")


def flatten(node, prefix=""):
    out = {}
    if isinstance(node, dict):
        for k, v in node.items():
            out.update(flatten(v, f"{prefix}{k}." if isinstance(v, dict) else f"{prefix}{k}"))
            if not isinstance(v, dict):
                out[f"{prefix}{k}"] = v
    return out


def load_languages(root):
    langs = {}
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if entry.endswith(".json") and os.path.isfile(path):
            langs.setdefault(entry[:-5], {}).update(flatten(json.load(open(path, encoding="utf-8"))))
        elif os.path.isdir(path):
            for ns in sorted(os.listdir(path)):
                if ns.endswith(".json"):
                    data = flatten(json.load(open(os.path.join(path, ns), encoding="utf-8")))
                    langs.setdefault(entry, {}).update({f"{ns[:-5]}:{k}": v for k, v in data.items()})
    return langs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dir")
    p.add_argument("--base", default="en")
    p.add_argument("--limit", type=int, default=50, help="max keys listed per section")
    a = p.parse_args()

    langs = load_languages(a.dir)
    if a.base not in langs:
        sys.exit(f"Base language '{a.base}' not found. Found: {', '.join(langs) or 'none'}")
    base = langs[a.base]
    print(f"Base {a.base}: {len(base)} keys")
    problems = 0

    for lang, keys in langs.items():
        if lang == a.base:
            continue
        missing = sorted(set(base) - set(keys))
        extra = sorted(set(keys) - set(base))
        same = sorted(k for k in set(base) & set(keys)
                      if isinstance(base[k], str) and base[k] == keys[k] and re.search(r"[A-Za-z]{3}", base[k]))
        ph = sorted(k for k in set(base) & set(keys)
                    if isinstance(base[k], str) and isinstance(keys[k], str)
                    and sorted(PLACEHOLDER.findall(base[k])) != sorted(PLACEHOLDER.findall(keys[k])))
        problems += len(missing) + len(extra) + len(ph)
        print(f"\n== {lang}: {len(keys)} keys, {len(missing)} missing, {len(extra)} extra, "
              f"{len(same)} untranslated, {len(ph)} placeholder mismatch")
        for title, items in (("missing", missing), ("extra", extra),
                             ("untranslated", same), ("placeholder mismatch", ph)):
            for k in items[: a.limit]:
                print(f"  {title}: {k}")
            if len(items) > a.limit:
                print(f"  ... {len(items) - a.limit} more {title}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
