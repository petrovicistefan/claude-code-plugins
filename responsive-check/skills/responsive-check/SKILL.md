---
name: responsive-check
description: "Use when checking a web page or UI change at several screen sizes, to capture screenshots and find layout problems such as overflow or overlapping elements."
---

# Responsive Check

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Capture a page at several viewport sizes and find layout problems.

## 1. Choose the target

A local dev server URL (start it with the project's own dev command if needed) or a URL the user gives. Default viewports: 375x812 (phone), 768x1024 (tablet), 1280x800 (laptop), 1920x1080 (desktop).

## 2. Capture

If a browser tool is available in this session (for example a built-in browser or browser extension), use it: resize to each viewport, take a screenshot and run the overflow check below in the page.

Otherwise use the bundled script. It needs only Python 3 and a Chrome, Chromium, Edge or Brave browser that is already installed; it installs nothing:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/shoot.py <url> [--out screenshots] [--sizes 375x812,768x1024,1280x800] [--wait 1] [--browser <path>]
```

It saves one full-page PNG per size and prints, for each size, horizontal overflow and the elements wider than the viewport. It exits with code 1 when a size overflows. If no browser is found, it says so; ask the user to install one or to give the browser's path with `--browser`.

## 3. Review

Look at every screenshot and check:

- Horizontal scroll or content cut off at the edge
- Overlapping or clipped text, buttons or images
- Tap targets smaller than about 44x44 px on phone sizes
- Text too small to read, lines too long on desktop
- Navigation that does not collapse, images that stretch or blur
- Fixed headers covering content

## 4. Report and fix

For each problem give the viewport, the element (selector) and the likely CSS cause. Propose fixes in the project's styling system, then capture again to confirm.
