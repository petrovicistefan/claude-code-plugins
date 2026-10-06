---
name: perf-profiler
description: "Use when a web page is slow, when asked about Lighthouse, Core Web Vitals (LCP, INP, CLS) or page speed, or when looking for render bottlenecks and memory leaks in a frontend app."
---

# Perf Profiler

Measure web performance with Lighthouse, explain the result and fix the biggest causes first.

## 1. Measure

Pick one:

- **Local Lighthouse** (works for localhost, staging and production). If `lighthouse` is installed, run:
  ```bash
  lighthouse <url> --output=json --output-path=./lh-mobile.json --chrome-flags="--headless=new" --quiet
  lighthouse <url> --output=json --output-path=./lh-desktop.json --chrome-flags="--headless=new" --quiet --preset=desktop
  ```
  It needs Chrome and Node. If it is not installed, ask the user before running `npx lighthouse` (it downloads the package) or installing it.
- **PageSpeed Insights** (public URLs only, nothing to install, also returns real-user data from the Chrome UX Report):
  ```bash
  python3 ${CLAUDE_SKILL_DIR}/scripts/perf_report.py --psi https://example.com
  python3 ${CLAUDE_SKILL_DIR}/scripts/perf_report.py --psi https://example.com --desktop --save psi.json
  ```
  Without a key the API shares a small daily quota. If it says the quota is exceeded, ask the user to create a free PageSpeed Insights API key, save it in a file outside the repository, and pass `--key-file`. Do not ask for the key in the chat.

Measure a production build (`npm run build && npm run start`, not the dev server), and run three times when comparing, since lab results vary.

## 2. Read the report

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/perf_report.py lh-mobile.json
python3 ${CLAUDE_SKILL_DIR}/scripts/perf_report.py lh-after.json --compare lh-before.json
```

It prints the category scores, lab metrics rated against the Core Web Vitals thresholds (LCP 2.5 s, CLS 0.1, TBT 200 ms as a lab stand-in for INP), real-user metrics when available, the audits with the largest estimated savings and the resources behind them, and diagnostics such as the LCP element, layout shift culprits, long JavaScript execution and third parties.

## 3. Fix by metric

- **LCP**: find the LCP element in the report. If it is an image: serve it in the HTML (not injected by JavaScript), add `fetchpriority="high"`, never `loading="lazy"`, right-size it and use AVIF or WebP. Cut render-blocking CSS and fonts, reduce server time (TTFB), preconnect to the image origin.
- **INP / TBT**: split long tasks, defer non-critical JavaScript, remove unused JavaScript (dynamic `import()` for routes and heavy widgets), load third-party scripts after interaction or with `async`, avoid large re-renders on input (see below).
- **CLS**: set `width` and `height` or `aspect-ratio` on images, video and ads, reserve space for banners and late content, use `font-display: optional` or size-adjusted fallback fonts, do not insert content above existing content.
- **Bytes**: compression (Brotli or gzip), long cache lifetimes for hashed assets, responsive images.

## 4. React and Vue rendering

When interactions are slow, look in the code for: state lifted too high so a keystroke re-renders a whole page; new object, array or function props on every render passed to memoized children; large lists without virtualization (`@tanstack/react-virtual`, `vue-virtual-scroller`); context values that change on every render; expensive work in render without `useMemo`/`computed`. Confirm with the React DevTools Profiler ("Highlight updates") or Vue DevTools performance tab, which the user runs in their browser.

## 5. Memory leaks

Look for listeners, intervals, timeouts, subscriptions, observers and WebSocket handlers added in effects or `mounted` without cleanup; module-level caches and arrays that only grow; detached DOM nodes kept in variables. To confirm, the user takes heap snapshots in Chrome DevTools (Memory tab) before and after repeating an action several times and compares "Objects allocated between snapshots".

## Report

Lead with the metric that fails and its cause from the report (the actual element, script or image), then the fixes in order of estimated saving, then the before and after numbers once re-measured. Never promise a score; report measurements.
