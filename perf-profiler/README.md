# Perf Profiler: Lighthouse and Core Web Vitals

Measure your page speed with Lighthouse, see the real causes behind LCP, INP and CLS, and fix the biggest ones first.

## What it does

- A bundled Python script summarises any Lighthouse JSON report: scores, lab metrics rated against Core Web Vitals thresholds, the audits with the largest estimated savings and the exact scripts, images and elements behind them. It compares two runs.
- For public URLs it can run Google PageSpeed Insights, which also returns real-user Core Web Vitals from the Chrome UX Report.
- Claude fixes by metric (LCP image priority, long tasks, layout shifts, unused JavaScript) and reviews React and Vue code for needless re-renders and memory leaks.

## Use it

- `/perf-profiler:perf-audit https://example.com`
- `/perf-profiler:perf-compare lh-after.json lh-before.json`
- Or ask: "Why is our LCP so high on mobile?"

## Requirements

Python 3. For local and localhost tests, Lighthouse with Chrome and Node. PageSpeed Insights needs nothing installed but only works for public URLs.

## Data

Reading reports runs locally. With `--psi`, the URL you test is sent to Google's PageSpeed Insights API (googleapis.com), with your API key if you provide a key file. Local Lighthouse runs load the page you choose. Nothing else is sent.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
