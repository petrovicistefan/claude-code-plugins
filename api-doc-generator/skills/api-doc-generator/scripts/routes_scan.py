#!/usr/bin/env python3
"""List HTTP routes in a codebase and compare them with an OpenAPI file.

Detects Express, Fastify, Koa/Hono style routers, NestJS decorators, Next.js
route handlers (app/**/route.ts and pages/api), FastAPI, Flask, Django REST
`@api_view`, Spring `@GetMapping`-style annotations and Go net/http, chi, gin and echo.

  routes_scan.py <src-dir>                         list routes
  routes_scan.py <src-dir> --openapi openapi.json  show routes missing from the spec and spec paths with no route
  routes_scan.py <src-dir> --json routes.json      save the list
"""
import argparse
import json
import os
import re
import sys

SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", "coverage", "vendor", "venv", ".venv", "__pycache__", "target"}
CODE_EXTS = (".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".py", ".go", ".java", ".kt")
METHODS = ("get", "post", "put", "patch", "delete", "head", "options")
M = "|".join(METHODS)

PATTERNS = [
    # app.get('/x', ...), router.post("/x"), fastify.put(`/x`), hono, koa-router
    ("js", re.compile(r"\b(?:app|router|server|api|fastify|route[rs]?|r|v\d)\s*\.\s*(%s)\s*(?:<[^>]*>)?\s*\(\s*['\"`]([^'\"`]+)['\"`]" % M, re.I)),
    # fastify.route({ method: 'GET', url: '/x' })
    ("js", re.compile(r"method\s*:\s*['\"](%s)['\"][^}]{0,200}?url\s*:\s*['\"]([^'\"]+)['\"]" % M, re.I | re.S)),
    # NestJS @Get('x')
    ("nest", re.compile(r"@(Get|Post|Put|Patch|Delete|Head|Options)\(\s*(?:['\"`]([^'\"`]*)['\"`])?\s*\)")),
    # FastAPI / APIRouter / Flask 2 shortcuts: @app.get("/x"), @router.post("/x"), @bp.get
    ("py", re.compile(r"@\w+\.(%s)\(\s*[rf]?['\"]([^'\"]+)['\"]" % M, re.I)),
    # Flask @app.route("/x", methods=["GET","POST"])
    ("flask", re.compile(r"@\w+\.route\(\s*['\"]([^'\"]+)['\"](?:[^)]*methods\s*=\s*\[([^\]]*)\])?")),
    # Spring
    ("spring", re.compile(r"@(Get|Post|Put|Patch|Delete)Mapping\(\s*(?:value\s*=\s*|path\s*=\s*)?\"([^\"]*)\"")),
    # Go: r.Get("/x"), e.GET("/x"), router.HandleFunc("/x", h).Methods("GET"), http.HandleFunc("GET /x")
    ("go", re.compile(r"\b\w+\.(Get|Post|Put|Patch|Delete|GET|POST|PUT|PATCH|DELETE)\(\s*\"(/[^\"]*)\"")),
    ("gohttp", re.compile(r"\bHandleFunc\(\s*\"(?:(GET|POST|PUT|PATCH|DELETE)\s+)?(/[^\"]*)\"[^\n]*?(?:\.Methods\(\s*\"(\w+)\")?")),
]

NEST_CONTROLLER = re.compile(r"@Controller\(\s*(?:['\"`]([^'\"`]*)['\"`])?")
NEXT_EXPORT = re.compile(r"export\s+(?:async\s+)?(?:function|const)\s+(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b")


def norm(path):
    """Turn :id, {id}, <id>, <int:id>, [id] and [...slug] into {id} and drop trailing slash."""
    p = "/" + path.strip().strip("/")
    p = re.sub(r"\[\.\.\.(\w+)\]", r"{\1}", p)
    p = re.sub(r"\[\[?\.{0,3}(\w+)\]?\]", r"{\1}", p)
    p = re.sub(r":(\w+)\??", r"{\1}", p)
    p = re.sub(r"<(?:\w+:)?(\w+)>", r"{\1}", p)
    p = re.sub(r"\{(\w+):[^}]*\}", r"{\1}", p)
    return p if p != "" else "/"


def shape(path):
    return re.sub(r"\{[^}]+\}", "{}", norm(path)).lower()


def next_route(rel):
    parts = rel.replace(os.sep, "/").split("/")
    if "pages" in parts and "api" in parts:
        i = parts.index("pages")
        segs = parts[i + 1:]
        segs[-1] = re.sub(r"\.(t|j)sx?$", "", segs[-1])
        if segs[-1] == "index":
            segs = segs[:-1]
        return norm("/".join(segs))
    if "app" in parts and re.fullmatch(r"route\.(t|j)sx?", parts[-1]):
        i = len(parts) - 1 - parts[::-1].index("app")
        segs = [s for s in parts[i + 1:-1] if not (s.startswith("(") and s.endswith(")")) and not s.startswith("@")]
        return norm("/".join(segs))
    return None


def scan(root):
    routes = []
    for dirpath, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for n in sorted(names):
            if not n.endswith(CODE_EXTS) or ".test." in n or ".spec." in n:
                continue
            path = os.path.join(dirpath, n)
            rel = os.path.relpath(path, root)
            try:
                src = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue

            def add(method, route, pos):
                routes.append({"method": method.upper(), "path": norm(route), "file": rel, "line": src.count("\n", 0, pos) + 1})

            nr = next_route(rel)
            if nr is not None:
                found = False
                for m in NEXT_EXPORT.finditer(src):
                    add(m.group(1), nr, m.start())
                    found = True
                if not found and "/pages/" in "/" + rel.replace(os.sep, "/") and "export default" in src:
                    add("ANY", nr, src.find("export default"))
                continue

            prefix = ""
            if n.endswith((".ts", ".js")):
                c = NEST_CONTROLLER.search(src)
                prefix = (c.group(1) or "") if c else ""

            for kind, rx in PATTERNS:
                if kind == "nest" and not NEST_CONTROLLER.search(src):
                    continue
                if kind in ("py", "flask") and not n.endswith(".py"):
                    continue
                if kind in ("go", "gohttp") and not n.endswith(".go"):
                    continue
                if kind == "spring" and not n.endswith((".java", ".kt")):
                    continue
                if kind == "js" and not n.endswith((".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx")):
                    continue
                for m in rx.finditer(src):
                    if kind == "flask":
                        methods = re.findall(r"['\"](\w+)['\"]", m.group(2) or "") or ["GET"]
                        for meth in methods:
                            add(meth, m.group(1), m.start())
                    elif kind == "nest":
                        add(m.group(1), prefix + "/" + (m.group(2) or ""), m.start())
                    elif kind == "gohttp":
                        add(m.group(1) or m.group(3) or "ANY", m.group(2), m.start())
                    elif kind == "js" and not m.group(2).startswith("/"):
                        continue
                    else:
                        add(m.group(1), m.group(2), m.start())
    seen, out = set(), []
    for r in routes:
        key = (r["method"], r["path"], r["file"], r["line"])
        if key not in seen:
            seen.add(key)
            out.append(r)
    return sorted(out, key=lambda r: (r["path"], r["method"]))


def load_openapi(path):
    text = open(path, encoding="utf-8").read()
    ops = set()
    base = ""
    if path.endswith(".json") or text.lstrip().startswith("{"):
        spec = json.loads(text)
        for p, item in (spec.get("paths") or {}).items():
            for meth in item:
                if meth.lower() in METHODS:
                    ops.add((meth.upper(), p))
        servers = spec.get("servers") or []
        if servers:
            base = re.sub(r"^[a-z]+://[^/]+", "", servers[0].get("url", ""))
        return ops, base.rstrip("/")
    # Minimal YAML reader for the paths section: path keys and the method keys under them.
    in_paths, cur, path_indent = False, None, None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            in_paths = line.startswith("paths:")
            m = re.match(r"servers:", line)
            continue
        if in_paths:
            key = line.strip().split(":")[0].strip("'\"")
            if key.startswith("/"):
                path_indent, cur = indent, key
            elif cur and path_indent is not None and indent > path_indent and key.lower() in METHODS:
                ops.add((key.upper(), cur))
        m = re.match(r"\s*-\s*url:\s*['\"]?([^'\"\s]+)", line)
        if m and not base:
            base = re.sub(r"^[a-z]+://[^/]+", "", m.group(1))
    return ops, base.rstrip("/")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="?", default=".")
    ap.add_argument("--openapi", help="OpenAPI 3 or Swagger 2 file (JSON or YAML) to compare with")
    ap.add_argument("--json", help="write the routes to this JSON file")
    a = ap.parse_args()

    routes = scan(a.src)
    if a.json:
        json.dump(routes, open(a.json, "w"), indent=2)

    if not a.openapi:
        if not routes:
            sys.exit("No routes found. Pass the folder that contains the server code.")
        for r in routes:
            print(f"{r['method']:7} {r['path']:45} {r['file']}:{r['line']}")
        print(f"\n{len(routes)} routes")
        return

    ops, base = load_openapi(a.openapi)
    spec = {(m, shape(p)): p for m, p in ops}
    code = {}
    for r in routes:
        path = r["path"]
        if base and path.startswith(base + "/"):
            path = path[len(base):]
        code[(r["method"], shape(path))] = r
    missing = [r for k, r in code.items() if k not in spec and not (k[0] == "ANY" and any(s[1] == k[1] for s in spec))]
    stale = [(m, p) for (m, s), p in spec.items() if (m, s) not in code and ("ANY", s) not in code]

    print(f"Code routes: {len(code)}   Spec operations: {len(spec)}" + (f"   (server base path {base})" if base else ""))
    print(f"\nIn code, not documented ({len(missing)}):")
    for r in sorted(missing, key=lambda r: r["path"]):
        print(f"  {r['method']:7} {r['path']:45} {r['file']}:{r['line']}")
    print(f"\nIn spec, no matching route found ({len(stale)}):")
    for m, p in sorted(stale, key=lambda x: x[1]):
        print(f"  {m:7} {p}")
    sys.exit(1 if missing or stale else 0)


if __name__ == "__main__":
    main()
