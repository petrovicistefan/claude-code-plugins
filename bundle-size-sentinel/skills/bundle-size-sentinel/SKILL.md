---
name: bundle-size-sentinel
description: "Use when adding an npm dependency or when a JavaScript bundle grew, to measure the size impact and suggest lighter options."
---

# Bundle Size Sentinel

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Keep JavaScript bundles small: check dependencies before they are added and measure build output.

## Before adding a dependency

When you are about to add a package, or the user asks for one:

1. Ask whether the feature can be done with the platform or code already in the project (for example `Intl.DateTimeFormat` instead of `moment`, a 10-line `debounce` instead of all of `lodash`, `fetch` instead of `axios`).
2. If a package is needed, prefer small, tree-shakable ones with ES module builds, and per-function imports (`lodash-es/debounce`).
3. Tell the user the trade-off before installing.

## Measure the build

Run the project's own build command first (look in `package.json` scripts). Then run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/bundle_report.py <build-dir>
```

The default build directory is `dist`. Common ones are `dist`, `build`, `.next/static`, `out`. The script prints each JavaScript and CSS file with raw and gzip size, the total, and the largest files.

To compare with a previous build, save the report with `--json before.json`, rebuild, and run again with `--compare before.json`.

## Find what makes a chunk large

- Check `package.json` for heavy packages: `moment`, `lodash` (full import), `rxjs`, chart and icon libraries, polyfills.
- Search imports: `import _ from 'lodash'`, `import * as`, whole icon sets.
- Look for the same library in two versions in the lockfile.

## Report

Give the total gzip size, the change from before if known, the three largest files, and specific fixes with the expected saving when you can estimate it.
