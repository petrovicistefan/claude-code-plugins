---
name: figma-to-code
description: "Use when implementing a Figma design as UI code from a Figma link or selected frame, or when checking a component against its design."
---

# Figma to Code

Turn a Figma frame into components that fit the existing codebase.

## 1. Get the design

Use the Figma connector's tools with the frame link the user gives (a URL with `node-id`): fetch the design context or code for that node, its screenshot, and the variables (colors, spacing, typography) it uses.

If the Figma tools are not available, tell the user to connect the Figma connector (run `/mcp` in Claude Code and sign in) or to paste a screenshot, and work from the screenshot.

## 2. Learn the project before writing code

- Framework and styling: React, Vue, Svelte or HTML; Tailwind, CSS modules, styled-components, plain CSS
- Existing components to reuse: buttons, inputs, cards, layout primitives
- Design tokens: Tailwind config, CSS variables, theme files. Map Figma variables to these tokens instead of hardcoding hex values and pixel sizes

The output of the Figma tools is a reference, not final code. Rewrite it in the project's conventions.

## 3. Build

- Use semantic HTML and accessible names (labels, `alt`, button text)
- Use flexbox or grid that matches the Figma auto layout, not absolute positioning
- Make it responsive: ask which breakpoints matter if the design shows only one size
- Export images and icons through the connector's asset tools or ask the user for them; do not invent placeholder assets silently

## 4. Check

Compare your result with the Figma screenshot: spacing, font sizes, colors, states (hover, disabled, error). List anything you could not match and why.
