#!/usr/bin/env python3
"""Summarise a Lighthouse report: scores, Core Web Vitals, the biggest savings and what causes them.

  perf_report.py report.json                       a report saved with `lighthouse <url> --output=json`
  perf_report.py --psi https://example.com         run PageSpeed Insights (public URLs only), mobile
  perf_report.py --psi https://example.com --desktop
  perf_report.py --psi https://example.com --key-file ~/.psi-key   use your own free API key (higher quota)
  perf_report.py new.json --compare old.json       show what changed between two runs
  perf_report.py --psi URL --save run.json         keep the raw Lighthouse result for a later --compare

--psi sends the URL to Google's PageSpeed Insights API (googleapis.com). Nothing else is sent.
PageSpeed Insights also returns real-user Core Web Vitals (Chrome UX Report) when Google has enough data.
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

PSI = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
METRICS = [
    ("largest-contentful-paint", "LCP", "ms", 2500, 4000),
    ("cumulative-layout-shift", "CLS", "", 0.1, 0.25),
    ("total-blocking-time", "TBT", "ms", 200, 600),
    ("first-contentful-paint", "FCP", "ms", 1800, 3000),
    ("speed-index", "Speed Index", "ms", 3400, 5800),
    ("interactive", "TTI", "ms", 3800, 7300),
    ("server-response-time", "TTFB (server)", "ms", 600, 1800),
]
FIELD = [
    ("LARGEST_CONTENTFUL_PAINT_MS", "LCP", "ms"),
    ("INTERACTION_TO_NEXT_PAINT", "INP", "ms"),
    ("CUMULATIVE_LAYOUT_SHIFT_SCORE", "CLS", ""),
    ("FIRST_CONTENTFUL_PAINT_MS", "FCP", "ms"),
    ("EXPERIMENTAL_TIME_TO_FIRST_BYTE", "TTFB", "ms"),
]
DIAG = ["render-blocking-resources", "render-blocking-insight", "unused-javascript", "unused-css-rules", "legacy-javascript",
        "uses-optimized-images", "modern-image-formats", "uses-responsive-images", "offscreen-images", "efficient-animated-content",
        "uses-text-compression", "uses-long-cache-ttl", "cache-insight", "total-byte-weight", "dom-size", "dom-size-insight",
        "bootup-time", "mainthread-work-breakdown", "third-party-summary", "third-parties-insight", "font-display", "font-display-insight",
        "largest-contentful-paint-element", "lcp-discovery-insight", "lcp-phases-insight", "prioritize-lcp-image",
        "layout-shifts", "cls-culprits-insight", "unsized-images", "redirects", "uses-rel-preconnect", "duplicated-javascript",
        "long-tasks", "image-delivery-insight", "network-dependency-tree-insight"]


def fmt(v, unit):
    if v is None:
        return "-"
    if unit == "ms":
        return f"{v / 1000:.2f} s" if v >= 1000 else f"{v:.0f} ms"
    return f"{v:.3f}" if isinstance(v, float) else str(v)


def rate(v, good, poor):
    if v is None:
        return ""
    return "good" if v <= good else ("needs improvement" if v <= poor else "POOR")


def load(args):
    if args.psi:
        q = [("url", args.psi), ("strategy", "desktop" if args.desktop else "mobile")]
        q += [("category", c) for c in ("performance", "accessibility", "best-practices", "seo")]
        if args.key_file:
            q.append(("key", open(args.key_file, encoding="utf-8").read().strip()))
        url = PSI + "?" + urllib.parse.urlencode(q)
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                data = json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                sys.exit("PageSpeed Insights quota exceeded. Without a key the API shares a small daily quota. "
                         "Create a free key in Google Cloud (PageSpeed Insights API), save it to a file and pass --key-file, "
                         "or run Lighthouse locally and pass the JSON file.")
            body = e.read().decode(errors="replace")[:300]
            sys.exit(f"PageSpeed Insights returned {e.code}: {body}\nThe URL must be public. For localhost, run Lighthouse locally and pass the JSON file.")
        except urllib.error.URLError as e:
            sys.exit(f"Could not reach PageSpeed Insights: {e}")
        return data.get("lighthouseResult", {}), data.get("loadingExperience") or {}, data.get("originLoadingExperience") or {}
    data = json.load(open(args.report, encoding="utf-8"))
    if "lighthouseResult" in data:
        return data["lighthouseResult"], data.get("loadingExperience") or {}, data.get("originLoadingExperience") or {}
    return data, {}, {}


def savings(audit):
    d = audit.get("details") or {}
    ms = d.get("overallSavingsMs") or (audit.get("metricSavings") or {}).get("LCP") or 0
    b = d.get("overallSavingsBytes") or 0
    return ms or 0, b or 0


def items_preview(audit, n=4):
    d = audit.get("details") or {}
    items = d.get("items") or []
    out = []
    for it in items[:n]:
        if not isinstance(it, dict):
            continue
        src, node, ent = it.get("source"), it.get("node"), it.get("entity")
        label = (it.get("url")
                 or (src.get("url") if isinstance(src, dict) else None)
                 or (node.get("snippet") or node.get("nodeLabel") if isinstance(node, dict) else None)
                 or (ent.get("text") if isinstance(ent, dict) else ent)
                 or it.get("groupLabel") or it.get("label"))
        extra = []
        for k, unit in (("wastedMs", "ms"), ("wastedBytes", "B"), ("transferSize", "B"), ("totalBytes", "B"), ("blockingTime", "ms"), ("duration", "ms"), ("total", "ms"), ("score", "")):
            if isinstance(it.get(k), (int, float)) and it.get(k):
                v = it[k]
                extra.append(f"{v / 1024:.0f} KB" if unit == "B" else (f"{v:.0f} ms" if unit == "ms" else f"{v:.3f}"))
                break
        if label:
            out.append(f"{str(label)[:110]}" + (f"  ({extra[0]})" if extra else ""))
    return out


def summary(lh):
    audits = lh.get("audits", {})
    cats = {k: round((v.get("score") or 0) * 100) for k, v in (lh.get("categories") or {}).items()}
    metrics = {k: (audits.get(k) or {}).get("numericValue") for k, *_ in METRICS}
    return cats, metrics


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", nargs="?")
    ap.add_argument("--psi", metavar="URL")
    ap.add_argument("--desktop", action="store_true")
    ap.add_argument("--key-file", help="file that contains a PageSpeed Insights API key (optional)")
    ap.add_argument("--compare", metavar="OLD_JSON")
    ap.add_argument("--save", metavar="FILE")
    a = ap.parse_args()
    if not a.report and not a.psi:
        sys.exit(__doc__)

    lh, field, origin = load(a)
    if not lh.get("audits"):
        sys.exit("No Lighthouse audits in this input.")
    if a.save:
        json.dump(lh, open(a.save, "w"))
    audits = lh["audits"]
    cats, metrics = summary(lh)

    env = lh.get("configSettings", {}).get("formFactor", "")
    print(f"{lh.get('finalDisplayedUrl') or lh.get('finalUrl') or lh.get('requestedUrl')}  ({env}, Lighthouse {lh.get('lighthouseVersion', '?')})")
    if lh.get("runtimeError"):
        print(f"Runtime error: {lh['runtimeError'].get('message')}")
    print("Scores: " + "   ".join(f"{k} {v}" for k, v in cats.items()))

    print("\nLab metrics (this one run):")
    for key, label, unit, good, poor in METRICS:
        v = metrics.get(key)
        if v is not None:
            print(f"  {label:14} {fmt(v, unit):>9}  {rate(v, good, poor)}")

    for title, exp in (("Real users, this URL", field), ("Real users, whole origin", origin)):
        m = exp.get("metrics") or {}
        if m:
            print(f"\n{title} (Chrome UX Report, 75th percentile, overall {exp.get('overall_category', '?')}):")
            for key, label, unit in FIELD:
                if key in m:
                    p = m[key].get("percentile")
                    if key == "CUMULATIVE_LAYOUT_SHIFT_SCORE" and p is not None:
                        p = p / 100
                    print(f"  {label:6} {fmt(p, unit):>9}  {m[key].get('category', '')}")
            break

    opps = []
    for k, au in audits.items():
        if au.get("scoreDisplayMode") in ("notApplicable", "manual", "informative", "error") and k not in DIAG:
            continue
        if au.get("score") is not None and au.get("score") >= 0.9:
            continue
        ms, b = savings(au)
        if ms or b:
            opps.append((ms, b, k, au))
    opps.sort(key=lambda x: (-x[0], -x[1]))
    if opps:
        print("\nBiggest estimated savings:")
        for ms, b, k, au in opps[:8]:
            s = " / ".join(x for x in ((f"{ms:.0f} ms" if ms else ""), (f"{b / 1024:.0f} KB" if b else "")) if x)
            print(f"  {au.get('title')}  [{k}]  ~{s}")
            for line in items_preview(au, 3):
                print(f"      {line}")

    print("\nDiagnostics:")
    shown = 0
    for k in DIAG:
        au = audits.get(k)
        if not au or (au.get("score") is not None and au.get("score") >= 0.9) or any(k == o[2] for o in opps[:8]):
            continue
        if au.get("scoreDisplayMode") == "notApplicable":
            continue
        dv = au.get("displayValue") or ""
        print(f"  {au.get('title')}  {dv}  [{k}]")
        for line in items_preview(au, 3):
            print(f"      {line}")
        shown += 1
    if not shown:
        print("  nothing notable")

    if a.compare:
        old = json.load(open(a.compare, encoding="utf-8"))
        old = old.get("lighthouseResult", old)
        oc, om = summary(old)
        if old.get("configSettings", {}).get("formFactor") != lh.get("configSettings", {}).get("formFactor"):
            print("\nNote: the two reports use different form factors (mobile vs desktop); the numbers are not comparable.")
        print("\nChange since the previous report:")
        for k, v in cats.items():
            if k in oc:
                print(f"  {k:16} {oc[k]:>4} -> {v:<4} ({v - oc[k]:+})")
        for key, label, unit, *_ in METRICS:
            if metrics.get(key) is not None and om.get(key) is not None:
                d = metrics[key] - om[key]
                print(f"  {label:16} {fmt(om[key], unit):>9} -> {fmt(metrics[key], unit):<9} ({'+' if d >= 0 else '-'}{fmt(abs(d), unit)})")
    print("\nLab numbers vary between runs by 10% or more; compare medians of 3 runs before drawing conclusions.")


if __name__ == "__main__":
    main()
