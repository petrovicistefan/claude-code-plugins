# Figma to Code: Design to React, Vue and HTML

Turn Figma frames into React, Vue or HTML components that reuse your design tokens and existing components.

## What it does

Claude reads the frame you link through the Figma connector (structure, screenshot and variables), studies your project's framework, styling approach, existing components and design tokens, and then writes components that reuse them instead of hardcoding colors and sizes. It builds with semantic, accessible and responsive markup and finishes by comparing the result with the design and listing anything it could not match.

## Use it

- `/figma-to-code:implement https://www.figma.com/design/...?node-id=1-2`

## Requirements

A Figma account with access to the file. The first time, run `/mcp` in Claude Code and sign in to Figma. Some Figma MCP features depend on your Figma plan.

## Data

Design data is fetched from Figma (mcp.figma.com) under Figma's terms. Your code stays local, and the plugin stores nothing.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
