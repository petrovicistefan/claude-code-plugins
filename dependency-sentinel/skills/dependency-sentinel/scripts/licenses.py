#!/usr/bin/env python3
"""List the licenses of installed dependencies and flag the ones that need a closer look.

  licenses.py [dir]                    read node_modules and Python site-packages under dir
  licenses.py [dir] --site-packages P  also read a specific Python site-packages folder
  licenses.py [dir] --csv out.csv      save the full list

Everything is read from files on disk. Nothing is sent anywhere.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys

COPYLEFT_STRONG = re.compile(r"\b(A?GPL|SSPL|EUPL|OSL|RPL|CPAL)\b", re.I)
COPYLEFT_WEAK = re.compile(r"\b(LGPL|MPL|EPL|CDDL|CC-BY-SA)\b", re.I)
PERMISSIVE = re.compile(r"\b(MIT|ISC|BSD|Apache|0BSD|Unlicense|CC0|Zlib|BlueOak|Python-2\.0|PSF|WTFPL|X11|Artistic|CC-BY-\d)\b", re.I)
NONCOMMERCIAL = re.compile(r"(BUSL|Business Source|Commons Clause|CC-BY-NC|Elastic License|PolyForm|non-?commercial)", re.I)


def classify(lic):
    if not lic or lic.upper() in ("UNKNOWN", "UNLICENSED", "SEE LICENSE IN LICENSE", "NONE"):
        return "unknown"
    if NONCOMMERCIAL.search(lic):
        return "restricted"
    if COPYLEFT_STRONG.search(lic) and not COPYLEFT_WEAK.search(lic) and not re.search(r"\bOR\b", lic):
        return "strong-copyleft"
    if COPYLEFT_STRONG.search(lic) and re.search(r"\bOR\b", lic) and PERMISSIVE.search(lic):
        return "permissive"  # dual licensed, a permissive option exists
    if COPYLEFT_WEAK.search(lic) or COPYLEFT_STRONG.search(lic):
        return "weak-copyleft"
    if PERMISSIVE.search(lic):
        return "permissive"
    return "unknown"


def npm_license(meta):
    lic = meta.get("license")
    if isinstance(lic, dict):
        lic = lic.get("type")
    if not lic and isinstance(meta.get("licenses"), list):
        lic = " OR ".join(x.get("type", "") if isinstance(x, dict) else str(x) for x in meta["licenses"])
    return str(lic or "")


def node_packages(root):
    out = []
    for pj in glob.glob(os.path.join(root, "**", "node_modules", "*", "package.json"), recursive=True) + \
            glob.glob(os.path.join(root, "**", "node_modules", "@*", "*", "package.json"), recursive=True):
        if "/.pnpm/" in pj.replace(os.sep, "/") and pj.count("node_modules") > 2:
            continue
        try:
            meta = json.load(open(pj, encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if "name" in meta and "version" in meta:
            out.append(("npm", meta["name"], meta["version"], npm_license(meta)))
    return out


def py_packages(site):
    out = []
    for meta_path in glob.glob(os.path.join(site, "*.dist-info", "METADATA")):
        name = ver = lic = classifier = ""
        expr = ""
        for line in open(meta_path, encoding="utf-8", errors="replace"):
            if line.strip() == "":
                break
            k, _, v = line.partition(":")
            v = v.strip()
            if k == "Name":
                name = v
            elif k == "Version":
                ver = v
            elif k == "License-Expression":
                expr = v
            elif k == "License" and len(v) < 80:
                lic = v
            elif k == "Classifier" and v.startswith("License ::") and not classifier:
                classifier = v.split("::")[-1].strip()
        out.append(("PyPI", name, ver, expr or lic or classifier))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", nargs="?", default=".")
    ap.add_argument("--site-packages", action="append", default=[])
    ap.add_argument("--csv")
    a = ap.parse_args()

    pkgs = node_packages(a.dir)
    sites = a.site_packages + glob.glob(os.path.join(a.dir, "*venv*", "lib", "python*", "site-packages")) + \
        glob.glob(os.path.join(a.dir, ".venv", "lib", "python*", "site-packages"))
    for s in sorted(set(sites)):
        pkgs += py_packages(s)
    pkgs = sorted(set(pkgs), key=lambda p: (p[0], p[1].lower()))
    if not pkgs:
        sys.exit("No installed packages found. Install dependencies first (node_modules or a virtualenv), or pass --site-packages.")

    groups = {}
    for p in pkgs:
        groups.setdefault(classify(p[3]), []).append(p)
    counts = {}
    for p in pkgs:
        counts[p[3] or "(none)"] = counts.get(p[3] or "(none)", 0) + 1

    print(f"{len(pkgs)} installed packages")
    for lic, n in sorted(counts.items(), key=lambda kv: -kv[1])[:15]:
        print(f"  {n:5}  {lic}")
    for cat, title in (("restricted", "Source-available or non-commercial (check before commercial use)"),
                       ("strong-copyleft", "Strong copyleft (GPL/AGPL family)"),
                       ("weak-copyleft", "Weak copyleft (LGPL, MPL, EPL)"),
                       ("unknown", "No license found")):
        items = groups.get(cat, [])
        if items:
            print(f"\n{title}: {len(items)}")
            for eco, n, v, lic in items[:60]:
                print(f"  {eco:5} {n} {v}  {lic or '-'}")
            if len(items) > 60:
                print(f"  ... {len(items) - 60} more (use --csv)")
    if a.csv:
        with open(a.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ecosystem", "package", "version", "license", "category"])
            for p in pkgs:
                w.writerow(list(p) + [classify(p[3])])


if __name__ == "__main__":
    main()
