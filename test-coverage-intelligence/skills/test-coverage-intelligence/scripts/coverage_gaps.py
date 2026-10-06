#!/usr/bin/env python3
"""Rank untested code by risk: uncovered lines weighted by how often the file changes.

  coverage_gaps.py <report>                          rank files from a coverage report
  coverage_gaps.py <report> --churn churn.txt        weight by recent changes (see below)
  coverage_gaps.py <report> --file src/pay.ts        uncovered lines and functions of one file
  coverage_gaps.py <report> --save cov.json / --compare cov.json   track coverage over time

Reports: lcov.info, Cobertura coverage.xml (coverage.py, Jest cobertura, .NET),
Istanbul coverage-final.json, JaCoCo jacoco.xml, Go cover profiles (go test -coverprofile).

The churn file is the output of:
  git log --since="90 days ago" --name-only --format= > churn.txt
Each line is a changed file; files that change often and are poorly tested rank first.
"""
import argparse
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET


def ranges(nums):
    nums = sorted(set(nums))
    out, start, prev = [], None, None
    for n in nums:
        if start is None:
            start = prev = n
        elif n == prev + 1:
            prev = n
        else:
            out.append((start, prev))
            start = prev = n
    if start is not None:
        out.append((start, prev))
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in out)


def new_file():
    return {"lines": {}, "functions": {}, "branches": [0, 0]}


def parse_lcov(path):
    files, cur = {}, None
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith("SF:"):
            cur = files.setdefault(line[3:], new_file())
        elif cur is None:
            continue
        elif line.startswith("DA:"):
            ln, hits = line[3:].split(",")[:2]
            cur["lines"][int(ln)] = cur["lines"].get(int(ln), 0) + int(float(hits))
        elif line.startswith("FN:"):
            ln, name = line[3:].split(",", 1)
            cur["functions"].setdefault(name, [int(ln), 0])
        elif line.startswith("FNDA:"):
            hits, name = line[5:].split(",", 1)
            cur["functions"].setdefault(name, [0, 0])[1] += int(float(hits))
        elif line.startswith("BRDA:"):
            parts = line[5:].split(",")
            cur["branches"][1] += 1
            if parts[3] not in ("-", "0"):
                cur["branches"][0] += 1
        elif line == "end_of_record":
            cur = None
    return files


def parse_cobertura(root):
    files = {}
    sources = [s.text.strip() for s in root.iter("source") if s.text]
    for cls in root.iter("class"):
        fn = cls.get("filename")
        f = files.setdefault(fn, new_file())
        for ln in cls.iter("line"):
            n, hits = int(ln.get("number")), int(float(ln.get("hits", 0)))
            f["lines"][n] = f["lines"].get(n, 0) + hits
            cond = ln.get("condition-coverage")
            if cond:
                m = re.search(r"\((\d+)/(\d+)\)", cond)
                if m:
                    f["branches"][0] += int(m.group(1))
                    f["branches"][1] += int(m.group(2))
        for meth in cls.iter("method"):
            lines = [int(l.get("number")) for l in meth.iter("line")]
            hits = sum(int(float(l.get("hits", 0))) for l in meth.iter("line"))
            if lines:
                f["functions"][meth.get("name")] = [min(lines), hits]
    if sources:
        resolved = {}
        for fn, f in files.items():
            full = next((os.path.join(s, fn) for s in sources if os.path.exists(os.path.join(s, fn))), fn)
            resolved[full] = f
        files = resolved
    return files


def parse_jacoco(root):
    files = {}
    for pkg in root.iter("package"):
        pname = pkg.get("name", "")
        for sf in pkg.iter("sourcefile"):
            f = files.setdefault(f"{pname}/{sf.get('name')}", new_file())
            for ln in sf.iter("line"):
                n = int(ln.get("nr"))
                f["lines"][n] = int(ln.get("ci", 0))
                mb, cb = int(ln.get("mb", 0)), int(ln.get("cb", 0))
                f["branches"][0] += cb
                f["branches"][1] += mb + cb
        for cls in pkg.iter("class"):
            src = cls.get("sourcefilename")
            if not src:
                continue
            f = files.setdefault(f"{pname}/{src}", new_file())
            for m in cls.iter("method"):
                covered = any(c.get("type") == "METHOD" and int(c.get("covered", 0)) > 0 for c in m.iter("counter"))
                f["functions"][m.get("name")] = [int(m.get("line", 0)), 1 if covered else 0]
    return files


def parse_istanbul(data):
    files = {}
    for fn, d in data.items():
        if not isinstance(d, dict) or "statementMap" not in d:
            continue
        f = files.setdefault(d.get("path", fn), new_file())
        for sid, loc in d["statementMap"].items():
            ln = loc["start"]["line"]
            f["lines"][ln] = max(f["lines"].get(ln, 0), d["s"].get(sid, 0)) if ln in f["lines"] else d["s"].get(sid, 0)
        for fid, meta in (d.get("fnMap") or {}).items():
            f["functions"][meta.get("name") or f"(anonymous {fid})"] = [meta["loc"]["start"]["line"], d["f"].get(fid, 0)]
        for bid, counts in (d.get("b") or {}).items():
            f["branches"][1] += len(counts)
            f["branches"][0] += sum(1 for c in counts if c)
    return files


def parse_go(path):
    files = {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"(.+):(\d+)\.\d+,(\d+)\.\d+ (\d+) (\d+)", line.strip())
        if not m:
            continue
        f = files.setdefault(m.group(1), new_file())
        for ln in range(int(m.group(2)), int(m.group(3)) + 1):
            f["lines"][ln] = max(f["lines"].get(ln, 0), int(m.group(5)))
    return files


def load(path):
    if not os.path.isfile(path):
        sys.exit(f"Coverage report not found: {path}. Run the tests with coverage first.")
    text = open(path, encoding="utf-8", errors="replace").read(4096)
    if text.startswith("mode:"):
        return parse_go(path)
    if "SF:" in text or path.endswith(".info"):
        return parse_lcov(path)
    if text.lstrip().startswith("{"):
        data = json.load(open(path, encoding="utf-8"))
        if any(isinstance(v, dict) and "statementMap" in v for v in data.values()):
            return parse_istanbul(data)
        sys.exit("This JSON is not an Istanbul coverage-final.json (coverage-summary.json has no line data). Use the json reporter.")
    root = ET.parse(path).getroot()
    if root.tag == "report":
        return parse_jacoco(root)
    return parse_cobertura(root)


def rel(path, root):
    p = path.replace("\\", "/")
    r = os.path.abspath(root).replace("\\", "/")
    if p.startswith(r + "/"):
        p = p[len(r) + 1:]
    return p


def churn_counts(path):
    counts = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line:
            counts[line] = counts.get(line, 0) + 1
    return counts


def match_churn(f, churn):
    if f in churn:
        return churn[f]
    for k, v in churn.items():
        if f.endswith("/" + k) or k.endswith("/" + f):
            return v
    return 0


def stats(f):
    total = len(f["lines"])
    covered = sum(1 for h in f["lines"].values() if h > 0)
    return total, covered


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report")
    ap.add_argument("--root", default=".", help="project root used to shorten absolute paths")
    ap.add_argument("--churn")
    ap.add_argument("--file", help="show uncovered lines and functions for files matching this path")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--exclude", default=r"(\.test\.|\.spec\.|__tests__|(^|/)tests?/|(^|/)test_[^/]*\.py$|_test\.(go|py)$|(^|/)mocks?/|\.stories\.|(^|/)migrations/|conftest\.py$)")
    ap.add_argument("--save")
    ap.add_argument("--compare")
    a = ap.parse_args()

    raw = load(a.report)
    files = {rel(k, a.root): v for k, v in raw.items() if not re.search(a.exclude, rel(k, a.root))}
    if not files:
        sys.exit("No source files in the report.")
    churn = churn_counts(a.churn) if a.churn else {}

    T = sum(stats(f)[0] for f in files.values())
    C = sum(stats(f)[1] for f in files.values())
    BT = sum(f["branches"][1] for f in files.values())
    BC = sum(f["branches"][0] for f in files.values())
    print(f"{len(files)} files   line coverage {C / T * 100 if T else 0:.1f}% ({C}/{T})"
          + (f"   branch coverage {BC / BT * 100:.1f}% ({BC}/{BT})" if BT else ""))

    if a.file:
        for name, f in files.items():
            if a.file in name:
                total, cov = stats(f)
                unc = [ln for ln, h in f["lines"].items() if h == 0]
                print(f"\n{name}: {cov}/{total} lines covered")
                print(f"  uncovered lines: {ranges(unc) or 'none'}")
                fns = [(ln, n) for n, (ln, h) in f["functions"].items() if h == 0]
                if fns:
                    print("  functions never called by tests:")
                    for ln, n in sorted(fns):
                        print(f"    {n} (line {ln})")
        return

    rows = []
    for name, f in files.items():
        total, cov = stats(f)
        unc = total - cov
        if not unc:
            continue
        ch = match_churn(name, churn)
        risk = unc * (1 + math.log2(1 + ch)) if churn else unc
        untested_fns = sum(1 for _, h in f["functions"].values() if h == 0)
        rows.append((risk, name, cov, total, unc, ch, untested_fns))
    rows.sort(key=lambda r: -r[0])

    hdr = f"\n{'risk':>7}  {'cover':>6}  {'uncovered':>9}  " + (f"{'changes':>7}  " if churn else "") + f"{'untested fns':>12}  file"
    print(hdr)
    for risk, name, cov, total, unc, ch, fns in rows[:a.top]:
        print(f"{risk:7.0f}  {cov / total * 100:5.1f}%  {unc:9}  " + (f"{ch:7}  " if churn else "") + f"{fns:12}  {name}")
    zero = [r for r in rows if r[2] == 0]
    if zero:
        print(f"\n{len(zero)} files have no test coverage at all" + (", most changed first:" if churn else ":"))
        for r in sorted(zero, key=lambda r: (-r[5], -r[4]))[:10]:
            print(f"  {r[1]}  ({r[4]} lines" + (f", {r[5]} changes" if churn else "") + ")")
    if churn:
        hot_untracked = [(v, k) for k, v in churn.items() if not any(k == n or n.endswith("/" + k) or k.endswith("/" + n) for n in files)
                         and re.search(r"\.(js|jsx|ts|tsx|py|go|java|kt|rb|php|cs|rs|swift|vue|svelte)$", k) and not re.search(a.exclude, k)]
        if hot_untracked:
            print("\nOften changed source files that are missing from the coverage report (not loaded by any test?):")
            for v, k in sorted(hot_untracked, reverse=True)[:8]:
                print(f"  {k}  ({v} changes)")

    snap = {n: {"total": stats(f)[0], "covered": stats(f)[1]} for n, f in files.items()}
    if a.compare:
        old = json.load(open(a.compare))
        oT = sum(v["total"] for v in old.values())
        oC = sum(v["covered"] for v in old.values())
        print(f"\nLine coverage {oC / oT * 100 if oT else 0:.1f}% -> {C / T * 100:.1f}%")
        drops = []
        for n, v in snap.items():
            if n in old and old[n]["total"] and v["total"]:
                d = v["covered"] / v["total"] - old[n]["covered"] / old[n]["total"]
                if d < -0.02:
                    drops.append((d, n))
        for d, n in sorted(drops)[:10]:
            print(f"  {n}: {d * 100:+.1f} points")
    if a.save:
        json.dump(snap, open(a.save, "w"), indent=1)


if __name__ == "__main__":
    main()
