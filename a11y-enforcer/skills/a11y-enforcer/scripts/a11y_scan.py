#!/usr/bin/env python3
"""Static accessibility scan of HTML, JSX, TSX, Vue, Svelte and Astro files.

Finds common WCAG failures that can be seen in the markup: images without alt,
buttons and links without an accessible name, form fields without a label,
clickable elements that are not keyboard accessible, positive tabindex,
missing lang, skipped heading levels, autoplaying media and more.
"""
import argparse
import json
import os
import re
import sys

EXTS = (".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro")
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", "coverage", ".svelte-kit", "vendor"}

TAG_RE = re.compile(r"<([A-Za-z][\w.-]*)((?:\s+(?:\{[^}]*\}|[^\s>=/]+(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|\{(?:[^{}]|\{[^{}]*\})*\}|[^\s>]+))?))*)\s*(/?)>", re.S)
ATTR_RE = re.compile(r"([^\s=/{}]+)(?:\s*=\s*(\"[^\"]*\"|'[^']*'|\{(?:[^{}]|\{[^{}]*\})*\}|[^\s>]+))?")


def attrs_of(raw):
    out = {}
    for m in ATTR_RE.finditer(raw or ""):
        name = m.group(1)
        val = m.group(2)
        if val and val[0] in "\"'":
            val = val[1:-1]
        out[name.lower()] = val if val is not None else True
    return out


def has_any(a, *names):
    return any(n in a for n in names)


def has_spread(raw):
    return "{..." in (raw or "")


def inner_text(src, start, tag):
    """Text between an opening tag ending at start and its closing tag (same name, no nesting check beyond depth)."""
    close = re.compile(r"<(/?)%s\b[^>]*?(/?)>" % re.escape(tag), re.I)
    depth = 1
    for m in close.finditer(src, start):
        if m.group(1):
            depth -= 1
            if depth == 0:
                return src[start:m.start()]
        elif not m.group(2):
            depth += 1
    return src[start:start + 400]


def visible_text(fragment):
    if re.search(r"<(img|svg)\b[^>]*\b(alt|aria-label|title)\s*=\s*[\"'{][^\"'}]", fragment, re.I):
        return True
    if re.search(r"<title>\s*\S", fragment, re.I):
        return True
    if re.search(r"\baria-label(ledby)?\s*=", fragment, re.I):
        return True
    text = re.sub(r"<[^>]*>", " ", fragment)
    text = re.sub(r"\{\s*/\*.*?\*/\s*\}", " ", text, flags=re.S)
    return bool(re.search(r"[\w{]", text))


def line_of(src, pos):
    return src.count("\n", 0, pos) + 1


def scan_file(path):
    src = open(path, encoding="utf-8", errors="replace").read()
    is_html = path.endswith((".html", ".htm"))
    issues = []

    def add(pos, rule, wcag, msg, level="error"):
        issues.append({"file": path, "line": line_of(src, pos), "rule": rule, "wcag": wcag, "level": level, "message": msg})

    label_for = set(re.findall(r"<label\b[^>]*\b(?:for|htmlFor)\s*=\s*[\"'{]\s*[\"']?([\w:-]+)", src))
    headings = []

    for m in TAG_RE.finditer(src):
        tag, raw, selfclose = m.group(1), m.group(2), m.group(3)
        t = tag.lower()
        a = attrs_of(raw)
        pos = m.start()
        spread = has_spread(raw)
        hidden = a.get("aria-hidden") in ("true", "{true}", True) or "hidden" in a
        named = has_any(a, "aria-label", "aria-labelledby", "title")

        if t == "html" and is_html and "lang" not in a:
            add(pos, "html-lang", "3.1.1", "<html> has no lang attribute")

        elif t in ("img", "image") and tag[0].islower() or tag in ("Image", "NextImage"):
            if "alt" not in a and not spread and not hidden and a.get("role") not in ("presentation", "none"):
                add(pos, "img-alt", "1.1.1", f"<{tag}> has no alt text (use alt=\"\" for decorative images)")

        elif t == "input" and tag[0].islower():
            typ = str(a.get("type", "text")).lower()
            if typ == "hidden":
                continue
            if typ == "image" and "alt" not in a:
                add(pos, "input-image-alt", "1.1.1", "<input type=image> has no alt")
            if typ in ("submit", "button", "reset", "image"):
                continue
            if not named and not spread and str(a.get("id", "")) not in label_for and not _wrapped_in_label(src, pos):
                add(pos, "form-label", "1.3.1 / 4.1.2", f"<input type={typ}> has no label, aria-label or aria-labelledby")

        elif t in ("select", "textarea") and tag[0].islower():
            if not named and not spread and str(a.get("id", "")) not in label_for and not _wrapped_in_label(src, pos):
                add(pos, "form-label", "1.3.1 / 4.1.2", f"<{t}> has no label, aria-label or aria-labelledby")

        elif t == "button" and tag[0].islower():
            if not named and not spread and not selfclose and not visible_text(inner_text(src, m.end(), tag)):
                add(pos, "button-name", "4.1.2", "<button> has no text or aria-label (icon-only button?)")
            if selfclose and not named and not spread:
                add(pos, "button-name", "4.1.2", "<button/> has no text or aria-label")

        elif t == "a" and tag[0].islower():
            if not named and not spread and not selfclose:
                body = inner_text(src, m.end(), tag)
                if not visible_text(body):
                    add(pos, "link-name", "2.4.4 / 4.1.2", "<a> has no text or aria-label")
                elif re.fullmatch(r"\s*(click here|here|read more|more|link)\s*", re.sub(r"<[^>]*>", "", body), re.I):
                    add(pos, "link-purpose", "2.4.4", "link text does not describe the target", "warning")
            if "href" not in a and has_any(a, "onclick", "@click", "v-on:click", "on:click") and "role" not in a:
                add(pos, "anchor-is-button", "4.1.2", "<a> without href used as a button; use <button>")

        elif t in ("div", "span", "li", "td", "p", "section", "img") and tag[0].islower():
            if has_any(a, "onclick", "@click", "v-on:click", "on:click", "(click)"):
                if "role" not in a:
                    add(pos, "click-no-role", "4.1.2", f"clickable <{t}> has no role; use <button> or add role and tabindex")
                if "tabindex" not in a:
                    add(pos, "click-no-focus", "2.1.1", f"clickable <{t}> cannot be reached with the keyboard (no tabindex)")
                if not has_any(a, "onkeydown", "onkeyup", "onkeypress", "@keydown", "@keyup", "v-on:keydown", "on:keydown", "(keydown)"):
                    add(pos, "click-no-key", "2.1.1", f"clickable <{t}> has no keyboard handler")

        elif t in ("video", "audio") and tag[0].islower():
            if "autoplay" in a and "muted" not in a:
                add(pos, "media-autoplay", "1.4.2", f"<{t}> autoplays with sound")
            if t == "video" and not selfclose and "<track" not in inner_text(src, m.end(), tag):
                add(pos, "video-captions", "1.2.2", "<video> has no <track> for captions", "warning")

        elif t == "iframe" and "title" not in a and not spread:
            add(pos, "iframe-title", "4.1.2", "<iframe> has no title")

        elif re.fullmatch(r"h[1-6]", t):
            headings.append((pos, int(t[1])))

        if t == "meta" and str(a.get("name", "")).lower() == "viewport":
            content = str(a.get("content", "")).replace(" ", "").lower()
            if "user-scalable=no" in content or "user-scalable=0" in content or re.search(r"maximum-scale=1(\.0)?(,|$)", content):
                add(pos, "viewport-zoom", "1.4.4", "viewport meta blocks zoom")

        ti = a.get("tabindex")
        if isinstance(ti, str):
            num = re.sub(r"[^\d-]", "", ti)
            if num.lstrip("-").isdigit() and int(num) > 0:
                add(pos, "tabindex-positive", "2.4.3", f"tabindex={num} changes the natural focus order")

        if "accesskey" in a:
            add(pos, "accesskey", "2.1.4", "accesskey can clash with screen reader shortcuts", "warning")

        if a.get("role") in ("button", "link", "checkbox", "tab", "menuitem", "switch") and t not in ("button", "a", "input") and "tabindex" not in a:
            add(pos, "role-no-focus", "2.1.1", f"role={a.get('role')} on <{t}> without tabindex")

        if "outline" in str(a.get("style", "")).replace(" ", "") and re.search(r"outline:(none|0)", str(a.get("style", "")).replace(" ", "")):
            add(pos, "focus-outline", "2.4.7", "inline style removes the focus outline", "warning")

    prev = 0
    for pos, level in headings:
        if prev and level > prev + 1:
            add(pos, "heading-order", "1.3.1", f"heading jumps from h{prev} to h{level}", "warning")
        prev = level

    for m in re.finditer(r"outline\s*:\s*(none|0)\b", src) if path.endswith((".vue", ".svelte", ".astro", ".html", ".htm")) else []:
        if not re.search(r":focus-visible|:focus", src):
            add(m.start(), "focus-outline", "2.4.7", "CSS removes the focus outline and no :focus style was found", "warning")
            break

    issues.sort(key=lambda i: i["line"])
    return issues


def _wrapped_in_label(src, pos):
    before = src[max(0, pos - 600):pos]
    return before.rfind("<label") > before.rfind("</label>")


def iter_files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for dirpath, dirs, names in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            for n in sorted(names):
                if n.endswith(EXTS):
                    yield os.path.join(dirpath, n)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--json", help="write all issues to this JSON file")
    ap.add_argument("--errors-only", action="store_true")
    a = ap.parse_args()

    all_issues, count = [], 0
    for f in iter_files(a.paths):
        count += 1
        all_issues.extend(scan_file(f))
    if a.errors_only:
        all_issues = [i for i in all_issues if i["level"] == "error"]

    if not count:
        sys.exit("No HTML, JSX, TSX, Vue, Svelte or Astro files found.")

    by_rule = {}
    for i in all_issues:
        by_rule.setdefault(i["rule"], []).append(i)
    for i in all_issues:
        print(f"{i['file']}:{i['line']}: {i['level']} [{i['rule']}] WCAG {i['wcag']}: {i['message']}")
    errors = sum(1 for i in all_issues if i["level"] == "error")
    print(f"\nScanned {count} files: {errors} errors, {len(all_issues) - errors} warnings")
    for rule, items in sorted(by_rule.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(items):4}  {rule}")
    if a.json:
        json.dump(all_issues, open(a.json, "w"), indent=2)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
