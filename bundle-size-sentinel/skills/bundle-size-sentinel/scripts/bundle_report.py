#!/usr/bin/env python3
"""Print raw and gzip sizes of JS and CSS files in a build directory."""
import argparse
import gzip
import json
import os
import sys

EXTS = (".js", ".mjs", ".cjs", ".css")


def scan(root):
    files = {}
    for dirpath, _, names in os.walk(root):
        for name in names:
            if name.endswith(EXTS) and not name.endswith(".map"):
                path = os.path.join(dirpath, name)
                data = open(path, "rb").read()
                files[os.path.relpath(path, root)] = {
                    "raw": len(data),
                    "gzip": len(gzip.compress(data, compresslevel=9)),
                }
    return files


def kb(n):
    return f"{n / 1024:8.1f} KB"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dir", nargs="?", default="dist")
    p.add_argument("--json", help="write the report to this file")
    p.add_argument("--compare", help="previous report written with --json")
    p.add_argument("--top", type=int, default=15)
    a = p.parse_args()

    if not os.path.isdir(a.dir):
        sys.exit(f"Build directory not found: {a.dir}. Run the build first or pass the right path.")

    files = scan(a.dir)
    if not files:
        sys.exit(f"No .js or .css files in {a.dir}")

    old = json.load(open(a.compare)) if a.compare else {}
    rows = sorted(files.items(), key=lambda kv: kv[1]["gzip"], reverse=True)

    print(f"{'file':60} {'raw':>11} {'gzip':>11}" + (f" {'gzip diff':>11}" if old else ""))
    for name, s in rows[: a.top]:
        line = f"{name[-60:]:60} {kb(s['raw'])} {kb(s['gzip'])}"
        if old:
            before = old.get(name, {}).get("gzip", 0)
            line += f" {(s['gzip'] - before) / 1024:+10.1f}K"
        print(line)

    total_raw = sum(s["raw"] for s in files.values())
    total_gz = sum(s["gzip"] for s in files.values())
    print(f"\nTotal: {len(files)} files, {kb(total_raw).strip()} raw, {kb(total_gz).strip()} gzip")
    if old:
        old_gz = sum(s["gzip"] for s in old.values())
        print(f"Change vs previous: {(total_gz - old_gz) / 1024:+.1f} KB gzip")
        removed = sorted(set(old) - set(files))
        if removed:
            print("Files no longer present: " + ", ".join(removed[:10]))

    if a.json:
        json.dump(files, open(a.json, "w"), indent=2)
        print(f"Saved report to {a.json}")


if __name__ == "__main__":
    main()
