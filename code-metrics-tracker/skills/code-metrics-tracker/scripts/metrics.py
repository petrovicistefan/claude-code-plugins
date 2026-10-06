#!/usr/bin/env python3
"""Code metrics: lines, functions, cyclomatic complexity and duplicated blocks.

  metrics.py [dir]                          report for a folder (default: current)
  metrics.py [dir] --save snap.json         also save a snapshot
  metrics.py [dir] --compare snap.json      show what changed since a snapshot
  metrics.py [dir] --threshold 10           complexity limit for the "complex functions" list
  metrics.py [dir] --dup-lines 6            minimum size of a duplicated block

Python is measured exactly with the ast module. JavaScript, TypeScript, Java,
Kotlin, C#, Go, PHP, Ruby, Rust, Swift, C and C++ are measured by counting
branch keywords inside each function body, which is close to what ESLint's
`complexity` rule reports but not identical.
"""
import argparse
import ast
import hashlib
import json
import os
import re
import sys

SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", "coverage", "vendor", "venv", ".venv",
             "__pycache__", "target", "bin", "obj", ".gradle", ".idea", "Pods", "migrations", "generated", "__generated__"}
BRACE_EXTS = (".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".java", ".kt", ".cs", ".go", ".php", ".rs", ".swift", ".c", ".cc", ".cpp", ".h", ".hpp", ".scala", ".dart")
EXTS = BRACE_EXTS + (".py", ".rb", ".vue", ".svelte")

BRANCH_RE = re.compile(r"\b(if|for|while|case|catch|elif|elsif|unless|until|when|foreach|guard)\b|&&|\|\||\?\?|\?(?![.:?])(?=[^;\n]*:)")
FUNC_RE = re.compile(
    r"(?:function\s*\*?\s*([A-Za-z_$][\w$]*)?\s*\([^)]*\)"            # function foo(...)
    r"|([A-Za-z_$][\w$]*)\s*[:=]\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*(?::\s*[^=]+?)?=>"  # foo = (...) =>
    r"|(?:(?:public|private|protected|static|async|override|final|virtual|internal|suspend|fun|func|fn|def|pub)\s+)+[\w<>\[\],.? *&]*?\b([A-Za-z_$][\w$]*)\s*(?:<[^>]*>)?\s*\([^)]*\)"
    r"|^\s*([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*(?::\s*[\w<>\[\]|, .]+)?\s*(?=\{)"  # class method foo(...) {
    r")[^{;]*?\{", re.M)
KEYWORDS = {"if", "for", "while", "switch", "catch", "elif", "foreach", "using", "lock", "synchronized", "when", "guard", "match", "return", "else", "do", "try", "new", "typeof", "await", "with", "constructor"}


def strip_strings_comments(src, py=False):
    if py:
        return src
    src = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), src, flags=re.S)
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"`(?:\\.|[^`\\])*`", lambda m: "``" + "\n" * m.group(0).count("\n"), src, flags=re.S)
    src = re.sub(r"\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'", "''", src)
    return src


def py_functions(src):
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    out = []

    class V(ast.NodeVisitor):
        def __init__(self):
            self.stack = []

        def visit_ClassDef(self, node):
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def handle(self, node):
            c = 1
            for n in ast.walk(node):
                if n is not node and isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                    continue
                if isinstance(n, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler, ast.With, ast.AsyncWith, ast.Assert)):
                    c += 1 if not isinstance(n, (ast.With, ast.AsyncWith)) else 0
                elif isinstance(n, ast.BoolOp):
                    c += len(n.values) - 1
                elif isinstance(n, ast.comprehension):
                    c += 1 + len(n.ifs)
                elif hasattr(ast, "match_case") and isinstance(n, ast.match_case):
                    c += 1
            end = getattr(node, "end_lineno", node.lineno)
            out.append({"name": ".".join(self.stack + [node.name]), "line": node.lineno, "lines": end - node.lineno + 1, "complexity": c})
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_FunctionDef = handle
        visit_AsyncFunctionDef = handle

    V().visit(tree)
    return out


def brace_functions(src):
    clean = strip_strings_comments(src)
    out = []
    for m in FUNC_RE.finditer(clean):
        name = next((g for g in m.groups() if g), "<anonymous>")
        if name in KEYWORDS:
            continue
        start = m.end() - 1
        depth, i = 0, start
        while i < len(clean):
            ch = clean[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        body = clean[start:i + 1]
        # do not count nested function bodies twice: remove them from this body
        inner = body[1:-1]
        nested_spans = []
        for nm in FUNC_RE.finditer(inner):
            if next((g for g in nm.groups() if g), "") in KEYWORDS:
                continue
            s = nm.end() - 1
            d, j = 0, s
            while j < len(inner):
                if inner[j] == "{":
                    d += 1
                elif inner[j] == "}":
                    d -= 1
                    if d == 0:
                        break
                j += 1
            nested_spans.append((s, j))
        own = inner
        for s, j in reversed(nested_spans):
            own = own[:s] + own[j + 1:]
        c = 1 + len(BRANCH_RE.findall(own))
        line = clean.count("\n", 0, m.start()) + 1
        out.append({"name": name, "line": line, "lines": body.count("\n") + 1, "complexity": c})
    return out


def ruby_functions(src):
    out = []
    lines = src.splitlines()
    for i, l in enumerate(lines):
        m = re.match(r"\s*def\s+([\w.?!]+)", l)
        if not m:
            continue
        indent = len(l) - len(l.lstrip())
        j = i + 1
        while j < len(lines) and not (re.match(r"\s*end\b", lines[j]) and len(lines[j]) - len(lines[j].lstrip()) == indent):
            j += 1
        body = "\n".join(lines[i + 1:j])
        out.append({"name": m.group(1), "line": i + 1, "lines": j - i + 1, "complexity": 1 + len(BRANCH_RE.findall(body))})
    return out


def code_lines(src, py):
    n = 0
    in_block = False
    for l in src.splitlines():
        s = l.strip()
        if not s:
            continue
        if not py:
            if in_block:
                if "*/" in s:
                    in_block = False
                continue
            if s.startswith("/*"):
                in_block = "*/" not in s
                continue
            if s.startswith("//"):
                continue
        elif s.startswith("#"):
            continue
        n += 1
    return n


def norm_line(l):
    l = l.strip()
    l = re.sub(r"\"[^\"]*\"|'[^']*'", "S", l)
    l = re.sub(r"\b\d+\b", "N", l)
    return l


def duplicates(file_lines, min_lines):
    """Return [(pathA, startA, endA, pathB, startB, endB)] for blocks repeated in two places."""
    norm_by_file, index = {}, {}
    for path, lines in file_lines.items():
        norm = [(i + 1, norm_line(l)) for i, l in enumerate(lines)]
        norm = [(n, l) for n, l in norm if len(l) > 3 and l not in ("});", "end;", "else {", "} else {", "return;", "break;")
                and not l.startswith(("import ", "from ", "#include", "using ", "package ", "//", "#", "*", "/*", "require(", "export {"))]
        norm_by_file[path] = norm
        for k in range(len(norm) - min_lines + 1):
            h = hashlib.sha1("\n".join(l for _, l in norm[k:k + min_lines]).encode()).hexdigest()
            index.setdefault(h, []).append((path, k))
    pairs = set()
    for locs in index.values():
        if len(locs) > 20:
            continue  # boilerplate repeated everywhere
        for i in range(len(locs)):
            for j in range(i + 1, len(locs)):
                (pa, ka), (pb, kb) = locs[i], locs[j]
                if pa == pb and abs(ka - kb) < min_lines:
                    continue
                pairs.add((pa, ka, pb, kb))
    out = []
    for pa, ka, pb, kb in pairs:
        if (pa, ka - 1, pb, kb - 1) in pairs:
            continue  # not the start of a run
        n = 0
        while (pa, ka + n + 1, pb, kb + n + 1) in pairs:
            n += 1
        A, B = norm_by_file[pa], norm_by_file[pb]
        out.append((pa, A[ka][0], A[ka + n + min_lines - 1][0], pb, B[kb][0], B[kb + n + min_lines - 1][0]))
    out.sort(key=lambda d: -(d[2] - d[1]))
    return out


def analyse(root, min_dup):
    files, all_lines = {}, {}
    for dirpath, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for n in sorted(names):
            if not n.endswith(EXTS) or re.search(r"\.(min|d|generated|pb)\.\w+$", n):
                continue
            path = os.path.join(dirpath, n)
            rel = os.path.relpath(path, root)
            try:
                src = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if src.count("\n") > 20000:
                continue
            py = n.endswith(".py")
            if py:
                funcs = py_functions(src)
                if funcs is None:
                    funcs = []
            elif n.endswith(".rb"):
                funcs = ruby_functions(src)
            else:
                funcs = brace_functions(src)
            files[rel] = {"loc": code_lines(src, py), "functions": funcs}
            all_lines[rel] = src.splitlines()
    return files, duplicates(all_lines, min_dup)


def summary(files):
    funcs = [f["complexity"] for v in files.values() for f in v["functions"]]
    return {
        "files": len(files),
        "loc": sum(v["loc"] for v in files.values()),
        "functions": len(funcs),
        "avg_complexity": round(sum(funcs) / len(funcs), 2) if funcs else 0,
        "max_complexity": max(funcs) if funcs else 0,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", nargs="?", default=".")
    ap.add_argument("--threshold", type=int, default=10)
    ap.add_argument("--dup-lines", type=int, default=6)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--save")
    ap.add_argument("--compare")
    a = ap.parse_args()

    files, dups = analyse(a.dir, a.dup_lines)
    if not files:
        sys.exit("No source files found.")
    s = summary(files)
    dup_lines = sum(d[2] - d[1] + 1 for d in dups)
    s["duplicate_blocks"] = len(dups)
    s["duplicated_lines"] = dup_lines
    complex_fns = sorted(((f["complexity"], rel, f) for rel, v in files.items() for f in v["functions"] if f["complexity"] > a.threshold),
                         key=lambda x: -x[0])
    s["functions_over_threshold"] = len(complex_fns)

    print(f"Files {s['files']}   code lines {s['loc']}   functions {s['functions']}   "
          f"avg complexity {s['avg_complexity']}   max {s['max_complexity']}")
    print(f"\nFunctions with complexity over {a.threshold} ({len(complex_fns)}):")
    for c, rel, f in complex_fns[:a.top]:
        print(f"  {c:4}  {rel}:{f['line']}  {f['name']}  ({f['lines']} lines)")

    big = sorted(((v["loc"], rel) for rel, v in files.items()), reverse=True)[:min(a.top, 10)]
    print("\nLargest files:")
    for loc, rel in big:
        print(f"  {loc:6}  {rel}")

    long_fns = sorted(((f["lines"], rel, f) for rel, v in files.items() for f in v["functions"] if f["lines"] > 60), key=lambda x: -x[0])
    if long_fns:
        print(f"\nFunctions longer than 60 lines ({len(long_fns)}):")
        for n, rel, f in long_fns[:min(a.top, 10)]:
            print(f"  {n:6}  {rel}:{f['line']}  {f['name']}")

    print(f"\nDuplicated blocks of {a.dup_lines}+ lines: {len(dups)} ({dup_lines} repeated lines)")
    for pa, sa, ea, pb, sb, eb in dups[:min(a.top, 10)]:
        print(f"  {pa}:{sa}-{ea}  ==  {pb}:{sb}-{eb}")

    if a.compare:
        old = json.load(open(a.compare))
        os_ = old["summary"]
        print("\nChange since snapshot" + (f" from {old.get('label')}" if old.get("label") else "") + ":")
        for k in ("files", "loc", "functions", "avg_complexity", "max_complexity", "functions_over_threshold", "duplicated_lines"):
            if k in os_:
                d = round(s[k] - os_[k], 2)
                print(f"  {k:26} {os_[k]:>10} -> {s[k]:<10} ({d:+})")
        oldf = {(r, f["name"]): f["complexity"] for r, v in old["files"].items() for f in v["functions"]}
        worse = sorted(((f["complexity"] - oldf[(r, f["name"])], r, f) for r, v in files.items() for f in v["functions"]
                        if (r, f["name"]) in oldf and f["complexity"] > oldf[(r, f["name"])]), key=lambda x: -x[0])
        if worse:
            print("  Functions that got more complex:")
            for d, r, f in worse[:10]:
                print(f"    +{d}  {r}:{f['line']}  {f['name']} (now {f['complexity']})")

    if a.save:
        json.dump({"summary": s, "files": files}, open(a.save, "w"), indent=1)
        print(f"\nSnapshot saved to {a.save}")


if __name__ == "__main__":
    main()
