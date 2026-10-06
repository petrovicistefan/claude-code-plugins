#!/usr/bin/env python3
"""Compare two GraphQL SDL schemas and classify every change, or lint one schema.

  schema_diff.py old.graphql new.graphql     breaking, dangerous and safe changes
  schema_diff.py --lint schema.graphql       list fields without pagination, deprecations without a reason

Paths can be files or folders (all .graphql / .graphqls / .gql files are merged).
Exit code 1 when breaking changes are found, so it can gate CI.
"""
import os
import re
import sys

def read_sdl(path):
    if os.path.isdir(path):
        parts = []
        for dirpath, dirs, names in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
            for n in sorted(names):
                if n.endswith((".graphql", ".graphqls", ".gql")):
                    parts.append(open(os.path.join(dirpath, n), encoding="utf-8").read())
        return "\n".join(parts)
    return open(path, encoding="utf-8").read()


def strip(sdl):
    # keep only whether a deprecation has a reason, before string literals are blanked
    sdl = re.sub(r'@deprecated\(\s*reason\s*:\s*"((?:\\.|[^"\\])*)"\s*\)',
                 lambda m: "@deprecated(reason: R)" if m.group(1).strip() else "@deprecated", sdl)
    sdl = re.sub(r'"""(?:.|\n)*?"""', " ", sdl)
    sdl = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', sdl)
    sdl = re.sub(r"#[^\n]*", "", sdl)
    return sdl


def parse_args(s):
    args = {}
    # args are separated by commas or whitespace; split on "name:" boundaries
    for m in re.finditer(r"(\w+)\s*:\s*([\w\[\]!\s]+?)(?:\s*=\s*([^,)@]+?))?(?=\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:,|\s+\w+\s*:|$))", s.strip(), re.S):
        args[m.group(1)] = {"type": re.sub(r"\s+", "", m.group(2)), "default": m.group(3) is not None}
    return args


def parse(sdl):
    sdl = strip(sdl)
    types = {}
    pat = re.compile(r"\b(extend\s+)?(type|interface|input|enum|union|scalar)\s+(\w+)([^{=\n]*)(\{|=)?", re.S)
    pos = 0
    while True:
        m = pat.search(sdl, pos)
        if not m:
            break
        ext, kind, name, header, opener = m.groups()
        pos = m.end()
        t = types.setdefault(name, {"kind": kind, "fields": {}, "values": set(), "members": set(), "implements": set(), "deprecated": {}})
        imp = re.search(r"implements\s+([\w\s&,]+)", header or "")
        if imp:
            t["implements"] |= set(re.findall(r"\w+", imp.group(1)))
        if opener == "=":
            end = re.search(r"\n\s*(?:extend\s+)?(?:type|interface|input|enum|union|scalar|schema|directive)\b|\Z", sdl[pos:])
            body = sdl[pos:pos + end.start()]
            t["members"] |= set(re.findall(r"\w+", re.sub(r"@\w+(\([^)]*\))?", "", body)))
            pos += end.start()
            continue
        if opener != "{":
            continue
        depth, i = 1, pos
        while i < len(sdl) and depth:
            if sdl[i] == "{":
                depth += 1
            elif sdl[i] == "}":
                depth -= 1
            i += 1
        body = sdl[pos:i - 1].replace(",", " ")  # commas are insignificant in GraphQL
        pos = i
        if kind == "enum":
            for v in re.finditer(r"\b([A-Za-z_]\w*)\b(\s*@deprecated(\([^)]*\))?)?", re.sub(r"@(?!deprecated)\w+(\([^)]*\))?", "", body)):
                t["values"].add(v.group(1))
                if v.group(2):
                    t["deprecated"][v.group(1)] = v.group(3) or ""
            continue
        # fields: name(args)?: Type directives
        j = 0
        while j < len(body):
            fm = re.compile(r"\s*(\w+)\s*").match(body, j)
            if not fm or not fm.group(1):
                j += 1
                continue
            fname = fm.group(1)
            j = fm.end()
            args = ""
            if j < len(body) and body[j] == "(":
                d, k = 1, j + 1
                while k < len(body) and d:
                    d += {"(": 1, ")": -1}.get(body[k], 0)
                    k += 1
                args = body[j + 1:k - 1]
                j = k
            tm = re.compile(r"\s*:\s*([\w\[\]!\s]+?)(\s*=\s*[^\n@]+?)?\s*((?:@\w+(?:\([^)]*\))?\s*)*)(?=\s*\w+\s*[(:]|\s*$)", re.S).match(body, j)
            if not tm:
                break
            j = tm.end()
            ftype = re.sub(r"\s+", "", tm.group(1))
            t["fields"][fname] = {"type": ftype, "args": parse_args(args), "default": bool(tm.group(2))}
            dep = re.search(r"@deprecated(\(\s*reason\s*:\s*(R)\s*\))?", tm.group(3) or "")
            if dep:
                t["deprecated"][fname] = dep.group(2) or ""
    return types


def nonnull(t):
    return t.endswith("!")


def unwrap(t):
    return re.sub(r"[\[\]!]", "", t)


def tokens(t):
    return re.findall(r"\[|\]!?|\w+!?", t)


def type_change(old, new, is_input):
    """Classify a type change. Output positions may gain `!`; input positions may lose it."""
    if old == new:
        return None
    to, tn = tokens(old), tokens(new)
    if [x.rstrip("!") for x in to] != [x.rstrip("!") for x in tn]:
        return "breaking"
    for x, y in zip(to, tn):
        if is_input and y.endswith("!") and not x.endswith("!"):
            return "breaking"
        if not is_input and x.endswith("!") and not y.endswith("!"):
            return "breaking"
    return "safe"


def diff(a, b):
    changes = []

    def add(level, msg):
        changes.append((level, msg))

    for name in sorted(set(a) - set(b)):
        add("breaking", f"type {name} removed")
    for name in sorted(set(b) - set(a)):
        add("safe", f"{b[name]['kind']} {name} added")
    for name in sorted(set(a) & set(b)):
        ta, tb = a[name], b[name]
        if ta["kind"] != tb["kind"]:
            add("breaking", f"{name} changed from {ta['kind']} to {tb['kind']}")
            continue
        k = ta["kind"]
        for i in sorted(ta["implements"] - tb["implements"]):
            add("breaking", f"{name} no longer implements {i}")
        for i in sorted(tb["implements"] - ta["implements"]):
            add("safe", f"{name} now implements {i}")
        if k == "enum":
            for v in sorted(ta["values"] - tb["values"]):
                add("breaking", f"enum value {name}.{v} removed")
            for v in sorted(tb["values"] - ta["values"]):
                add("dangerous", f"enum value {name}.{v} added (clients with exhaustive switches may fail)")
        if k == "union":
            for v in sorted(ta["members"] - tb["members"]):
                add("breaking", f"{v} removed from union {name}")
            for v in sorted(tb["members"] - ta["members"]):
                add("dangerous", f"{v} added to union {name} (clients may not handle the new type)")
        for f in sorted(set(ta["fields"]) - set(tb["fields"])):
            dep = " (was deprecated)" if f in ta["deprecated"] else ""
            add("breaking", f"field {name}.{f} removed{dep}")
        for f in sorted(set(tb["fields"]) - set(ta["fields"])):
            fb = tb["fields"][f]
            if k == "input" and nonnull(fb["type"]) and not fb["default"]:
                add("breaking", f"required input field {name}.{f}: {fb['type']} added")
            elif k == "interface":
                add("dangerous", f"field {name}.{f} added to interface (every implementing type must add it)")
            else:
                add("safe", f"field {name}.{f} added")
        for f in sorted(set(ta["fields"]) & set(tb["fields"])):
            fa, fb = ta["fields"][f], tb["fields"][f]
            c = type_change(fa["type"], fb["type"], k == "input")
            if c:
                add(c, f"{name}.{f} type changed {fa['type']} -> {fb['type']}")
            for arg in sorted(set(fa["args"]) - set(fb["args"])):
                add("breaking", f"argument {name}.{f}({arg}) removed")
            for arg in sorted(set(fb["args"]) - set(fa["args"])):
                x = fb["args"][arg]
                if nonnull(x["type"]) and not x["default"]:
                    add("breaking", f"required argument {name}.{f}({arg}: {x['type']}) added")
                else:
                    add("safe", f"optional argument {name}.{f}({arg}) added")
            for arg in sorted(set(fa["args"]) & set(fb["args"])):
                c = type_change(fa["args"][arg]["type"], fb["args"][arg]["type"], True)
                if c:
                    add(c, f"argument {name}.{f}({arg}) type changed {fa['args'][arg]['type']} -> {fb['args'][arg]['type']}")
                if fa["args"][arg]["default"] and not fb["args"][arg]["default"]:
                    add("dangerous", f"default value of {name}.{f}({arg}) removed")
            if f in tb["deprecated"] and f not in ta["deprecated"]:
                add("safe", f"{name}.{f} deprecated")
    return changes


PAGINATION_ARGS = {"first", "last", "limit", "take", "top", "pageSize", "perPage", "page_size", "per_page", "count", "size"}


def lint(types):
    out = []
    for name, t in sorted(types.items()):
        if t["kind"] not in ("type", "interface"):
            continue
        for f, d in t["fields"].items():
            if d["type"].startswith("[") and not (set(d["args"]) & PAGINATION_ARGS) and name not in ("Mutation", "Subscription"):
                target = types.get(unwrap(d["type"]), {})
                if target.get("kind") in ("type", "interface", "union"):
                    out.append(f"{name}.{f}: {d['type']} returns an unbounded list (no first/limit argument); one query can fetch everything")
        for f, reason in t["deprecated"].items():
            if not reason or reason == '""':
                out.append(f"{name}.{f} is @deprecated without a reason; say what to use instead")
    for name, t in sorted(types.items()):
        if t["kind"] == "enum":
            for v, reason in t["deprecated"].items():
                if not reason or reason == '""':
                    out.append(f"enum {name}.{v} is @deprecated without a reason")
    return out


def main():
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "--lint":
        types = parse(read_sdl(args[1]))
        if not types:
            sys.exit("No GraphQL types found.")
        issues = lint(types)
        print(f"{len(types)} types parsed")
        for i in issues:
            print(f"  {i}")
        print(f"{len(issues)} findings")
        return
    if len(args) != 2:
        sys.exit(__doc__)
    a, b = parse(read_sdl(args[0])), parse(read_sdl(args[1]))
    if not a or not b:
        sys.exit("Could not find GraphQL types in one of the schemas.")
    changes = diff(a, b)
    order = {"breaking": 0, "dangerous": 1, "safe": 2}
    counts = {k: 0 for k in order}
    for level, msg in sorted(changes, key=lambda c: order[c[0]]):
        counts[level] += 1
        print(f"[{level}] {msg}")
    print(f"\n{len(a)} -> {len(b)} types: {counts['breaking']} breaking, {counts['dangerous']} dangerous, {counts['safe']} safe")
    sys.exit(1 if counts["breaking"] else 0)


if __name__ == "__main__":
    main()
