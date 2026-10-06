#!/usr/bin/env python3
"""Find flaky tests by comparing several runs of the same suite.

Reads result files written by repeated test runs and reports tests that
passed in some runs and failed in others. Standard library only, runs no
other programs.

Supported result files in the folder:
  *.xml    JUnit XML (pytest --junitxml, Maven Surefire, many others)
  *.json   Jest or Vitest JSON report, or `go test -json` output

Usage: analyze.py <results_dir> [--json]
"""
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET


def parse_junit(path):
    out = {}
    for case in ET.parse(path).getroot().iter("testcase"):
        name = "%s::%s" % (case.get("classname") or case.get("file") or "", case.get("name") or "")
        status, msg = "pass", ""
        for child in case:
            tag = child.tag.lower()
            if tag in ("failure", "error"):
                status = "fail"
                msg = (child.get("message") or (child.text or "")).strip().splitlines()[0:1]
                msg = msg[0] if msg else ""
            elif tag == "skipped" and status != "fail":
                status = "skip"
        out[name.strip(":")] = (status, msg)
    return out


def parse_jest(data):
    out = {}
    for suite in data.get("testResults", []):
        file_name = os.path.basename(suite.get("name", ""))
        for t in suite.get("assertionResults", []):
            status = {"passed": "pass", "failed": "fail"}.get(t.get("status"), "skip")
            msgs = t.get("failureMessages") or []
            msg = msgs[0].strip().splitlines()[0] if msgs and msgs[0].strip() else ""
            out["%s::%s" % (file_name, t.get("fullName") or t.get("title", ""))] = (status, msg)
    return out


def parse_go(text):
    out = {}
    outputs = {}
    for line in text.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        test = ev.get("Test")
        if not test:
            continue
        key = "%s::%s" % (ev.get("Package", ""), test)
        action = ev.get("Action")
        if action == "output":
            outputs.setdefault(key, []).append(ev.get("Output", "").strip())
        elif action in ("pass", "fail", "skip"):
            msg = ""
            if action == "fail":
                msg = next((o for o in reversed(outputs.get(key, [])) if o and not o.startswith(("---", "=== "))), "")
            out[key] = ({"pass": "pass", "fail": "fail", "skip": "skip"}[action], msg)
    return out


def parse_file(path):
    if path.endswith(".xml"):
        return parse_junit(path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "testResults" in data:
            return parse_jest(data)
    except ValueError:
        pass
    return parse_go(text)


def analyze(folder):
    files = sorted(glob.glob(os.path.join(folder, "*.xml")) + glob.glob(os.path.join(folder, "*.json")))
    if not files:
        sys.exit("no .xml or .json result files in " + folder)
    runs, skipped_files = [], []
    for f in files:
        try:
            parsed = parse_file(f)
        except (ET.ParseError, OSError, ValueError):
            parsed = {}
        if parsed:
            runs.append(parsed)
        else:
            skipped_files.append(os.path.basename(f))
    tests = {}
    for run in runs:
        for name, (status, msg) in run.items():
            t = tests.setdefault(name, {"pass": 0, "fail": 0, "skip": 0, "message": ""})
            t[status] += 1
            if status == "fail" and msg and not t["message"]:
                t["message"] = msg[:200]
    flaky, always_fail = [], []
    for name, t in tests.items():
        executed = t["pass"] + t["fail"]
        if t["fail"] and t["pass"]:
            flaky.append({"test": name, "runs": executed, "failed": t["fail"],
                          "fail_rate": round(100.0 * t["fail"] / executed, 1), "message": t["message"]})
        elif t["fail"] and not t["pass"]:
            always_fail.append({"test": name, "runs": executed, "message": t["message"]})
    flaky.sort(key=lambda x: (-x["fail_rate"], x["test"]))
    always_fail.sort(key=lambda x: x["test"])
    present_in_all = sum(1 for t in tests.values() if t["pass"] + t["fail"] + t["skip"] == len(runs))
    return {
        "runs_analyzed": len(runs),
        "unreadable_files": skipped_files,
        "tests_seen": len(tests),
        "tests_missing_in_some_runs": len(tests) - present_in_all,
        "flaky": flaky,
        "always_failing": always_fail,
    }


def render(r):
    lines = ["Runs analyzed: %d   Tests seen: %d" % (r["runs_analyzed"], r["tests_seen"])]
    if r["unreadable_files"]:
        lines.append("Could not read: " + ", ".join(r["unreadable_files"]))
    if r["runs_analyzed"] < 2:
        lines.append("Need at least 2 readable runs to compare.")
    if r["tests_missing_in_some_runs"]:
        lines.append("%d tests did not appear in every run (a run may have crashed or been cut off)." %
                     r["tests_missing_in_some_runs"])
    lines.append("")
    lines.append("Flaky (passed and failed across runs): %d" % len(r["flaky"]))
    for t in r["flaky"]:
        lines.append("  %5.1f%%  %d/%d failed  %s" % (t["fail_rate"], t["failed"], t["runs"], t["test"]))
        if t["message"]:
            lines.append("           " + t["message"])
    lines.append("")
    lines.append("Always failing (broken, not flaky): %d" % len(r["always_failing"]))
    for t in r["always_failing"][:20]:
        lines.append("  %s" % t["test"])
        if t["message"]:
            lines.append("      " + t["message"])
    if len(r["always_failing"]) > 20:
        lines.append("  ... and %d more" % (len(r["always_failing"]) - 20))
    return "\n".join(lines)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args or not os.path.isdir(args[0]):
        sys.exit("usage: analyze.py <results_dir> [--json]")
    result = analyze(args[0])
    print(json.dumps(result, indent=2) if "--json" in argv else render(result))


if __name__ == "__main__":
    main(sys.argv)
