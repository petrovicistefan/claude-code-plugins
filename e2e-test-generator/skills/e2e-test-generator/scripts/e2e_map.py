#!/usr/bin/env python3
"""Map the pages, forms and test hooks of a web app so end-to-end tests can be written from facts.

  e2e_map.py [folder]     default: current folder

Reports the existing E2E framework, the pages/routes found, the forms and buttons in
each page file, and which elements already have a stable selector (data-testid, role,
aria-label, id). Reads files only; runs nothing and opens no network connections.
"""
import json
import os
import re
import sys

SKIP = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "coverage", ".svelte-kit", "out"}
SRC_EXT = (".tsx", ".jsx", ".vue", ".svelte", ".html", ".astro", ".ts", ".js")


def walk(root):
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in files:
            yield os.path.join(d, f)


def detect_framework(root):
    info = {"runner": None, "config": None, "app": None}
    pkg = os.path.join(root, "package.json")
    deps = {}
    if os.path.isfile(pkg):
        try:
            j = json.load(open(pkg))
            deps = {**j.get("dependencies", {}), **j.get("devDependencies", {})}
            info["scripts"] = {k: v for k, v in j.get("scripts", {}).items() if re.search(r"test|e2e|dev|start", k)}
        except Exception:
            pass
    for name, marker in (("playwright", "@playwright/test"), ("cypress", "cypress"), ("webdriverio", "webdriverio"), ("testcafe", "testcafe")):
        if marker in deps:
            info["runner"] = name
    for cfg in ("playwright.config.ts", "playwright.config.js", "cypress.config.ts", "cypress.config.js"):
        if os.path.isfile(os.path.join(root, cfg)):
            info["config"] = cfg
    for name, marker in (("Next.js", "next"), ("Nuxt", "nuxt"), ("SvelteKit", "@sveltejs/kit"), ("Remix", "@remix-run/react"), ("Astro", "astro"),
                         ("React Router", "react-router-dom"), ("Vue Router", "vue-router"), ("Angular", "@angular/core")):
        if marker in deps:
            info["app"] = (info["app"] + ", " if info["app"] else "") + name
    return info


def routes(root):
    out = []
    for p in walk(root):
        rel = os.path.relpath(p, root).replace("\\", "/")
        if re.search(r"(^|/)app/(.+/)?page\.(tsx|jsx|ts|js)$", rel):
            out.append((re.sub(r"(^|.*/)app", "", os.path.dirname(rel)) or "/", rel))
        elif re.search(r"(^|/)pages/.+\.(tsx|jsx|ts|js|vue)$", rel) and "/api/" not in rel and not re.search(r"/_(app|document)", rel):
            r = re.sub(r"^.*?pages", "", re.sub(r"\.(tsx|jsx|ts|js|vue)$", "", rel)).replace("/index", "") or "/"
            out.append((r, rel))
        elif re.search(r"src/routes/.+\+page\.svelte$", rel):
            out.append((re.sub(r"^.*?src/routes", "", os.path.dirname(rel)) or "/", rel))
        elif p.endswith(SRC_EXT):
            try:
                t = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for m in re.finditer(r"<Route[^>]*\bpath=[\"']([^\"']+)[\"']|\bpath:\s*[\"'](/[^\"']*)[\"']\s*,\s*(?:component|element)", t):
                out.append((m.group(1) or m.group(2), rel))
    return sorted(set(out))


def inspect_file(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    forms = len(re.findall(r"<form\b|<Form\b", t))
    inputs = re.findall(r"<(?:input|Input|textarea|select)\b[^>]*>", t)
    buttons = re.findall(r"<(?:button|Button)\b[^>]*>([^<{]{1,40})", t)
    testids = re.findall(r"data-testid=[\"']([^\"']+)", t) + re.findall(r"data-cy=[\"']([^\"']+)", t)
    labelled = sum(1 for i in inputs if re.search(r"aria-label|id=|name=|data-testid|placeholder", i))
    return {"forms": forms, "inputs": len(inputs), "labelled_inputs": labelled, "buttons": [b.strip() for b in buttons if b.strip()][:8], "testids": testids[:10]}


def existing_tests(root):
    tests = []
    for p in walk(root):
        rel = os.path.relpath(p, root).replace("\\", "/")
        if re.search(r"(e2e|cypress|playwright|tests?)/.*\.(spec|test|cy)\.(ts|js)$|\.(spec|cy)\.(ts|js)$", rel) and "node_modules" not in rel:
            if re.search(r"page\.goto|cy\.visit|browser\.url|\.goto\(", open(p, encoding="utf-8", errors="replace").read()):
                tests.append(rel)
    return tests


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    fw = detect_framework(root)
    print("# E2E map\n")
    print(f"App framework: {fw['app'] or 'unknown'}")
    print(f"E2E runner: {fw['runner'] or 'none installed'}  config: {fw['config'] or 'none'}")
    if fw.get("scripts"):
        print("Scripts:", ", ".join(f"{k}={v}" for k, v in fw["scripts"].items()))
    tests = existing_tests(root)
    print(f"Existing E2E specs: {len(tests)}")
    for t in tests[:10]:
        print(f"  - {t}")
    rs = routes(root)
    print(f"\n## Routes ({len(rs)})")
    no_hook = 0
    for route, rel in rs:
        info = inspect_file(os.path.join(root, rel))
        flag = ""
        if info["inputs"] and not info["testids"] and info["labelled_inputs"] < info["inputs"]:
            flag = "  <- inputs without label/name/testid, add stable selectors first"
            no_hook += 1
        print(f"- {route}  ({rel})  forms={info['forms']} inputs={info['inputs']} buttons={info['buttons']} testids={info['testids']}{flag}")
    print(f"\nPages with weak selectors: {no_hook}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
