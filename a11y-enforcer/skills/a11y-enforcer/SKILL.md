---
name: a11y-enforcer
description: "Use when building or reviewing UI in HTML, React, Vue, Svelte or Astro, or when asked about accessibility, WCAG, screen readers, keyboard navigation or color contrast."
---

# A11y Enforcer

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Find and fix accessibility problems against WCAG 2.2 level AA.

## 1. Scan the markup

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/a11y_scan.py <path>            # folder or files
python3 ${CLAUDE_SKILL_DIR}/scripts/a11y_scan.py src --errors-only
```

It reads `.html`, `.jsx`, `.tsx`, `.vue`, `.svelte` and `.astro` files and reports, with file, line and WCAG criterion:

- images without `alt`, icon-only buttons and empty links without an accessible name
- inputs, selects and textareas without a label, `aria-label` or `aria-labelledby`
- `div`/`span` click handlers without a role, `tabindex` and keyboard handler, and `<a>` without `href` used as a button
- positive `tabindex`, `role="button"` and similar without focus, `accesskey`
- missing `lang` on `<html>`, viewport meta that blocks zoom, iframes without a title
- autoplaying media with sound, video without captions, skipped heading levels, removed focus outlines

The scan is static, so it cannot see text added at runtime, props passed into custom components (`<Icon>`, `<Button>`), or CSS from stylesheets. Check those by reading the component: if a custom `Button` renders a native `<button>` and forwards `aria-label`, an icon-only usage still needs that prop.

## 2. Check color contrast

Read the colors from the theme, CSS variables or Tailwind config and check each text and background pair:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/contrast.py "#6b7280" "#ffffff" "#9ca3af" "#111827"
```

Requirements: 4.5:1 for normal text, 3:1 for large text (24px, or 18.66px bold) and for icons, borders of inputs and focus indicators. Check both light and dark themes, and hover, disabled-looking-but-enabled and placeholder text.

## 3. Check behaviour the scan cannot see

Review the code for:

- **Keyboard**: every action works with Tab, Enter, Space and Escape; focus order follows the visual order; no keyboard trap.
- **Focus management**: dialogs move focus inside on open, trap it while open and return it to the trigger on close; route changes in single-page apps move focus to the main heading or announce the page.
- **Visible focus**: `:focus-visible` styles exist wherever `outline: none` is used; the focused element is not hidden under a sticky header (WCAG 2.4.11).
- **Live updates**: toasts, form errors and loading states use `role="status"`, `role="alert"` or `aria-live`; errors are linked to fields with `aria-describedby`.
- **Forms**: required fields are marked in text, not only by color; errors say how to fix them; `autocomplete` is set on personal data fields.
- **Target size**: interactive targets are at least 24 by 24 CSS pixels (WCAG 2.5.8).
- **Motion**: animations respect `prefers-reduced-motion`.
- **ARIA**: no ARIA is better than wrong ARIA. Prefer native elements; do not put `role` on elements that already have it; `aria-hidden="true"` never on focusable elements.

If the user wants a browser check, an installed `axe-core` setup (`@axe-core/playwright`, `jest-axe`, `vitest-axe`) or Lighthouse's accessibility category gives runtime results. Use what the project already has; ask before adding a dependency.

## 4. Fix and report

- Fix with the smallest change: native element over ARIA, visible label over `aria-label`, real `alt` text that says what the image means in context (empty `alt=""` only for decoration).
- Do not change visual design without saying so; when contrast fails, propose the nearest passing color and its ratio.
- Report grouped by severity: blockers (cannot use with keyboard or screen reader), errors (WCAG AA failures), and warnings. Include file:line and the WCAG criterion for each, then what was fixed and what still needs a manual check with a screen reader (VoiceOver, NVDA).
