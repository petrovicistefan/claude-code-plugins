# Exa Search: Live Web and Docs Search

Give Claude live web search for current docs, releases and error messages, with dated sources.

## What it does

The plugin connects Claude Code to Exa's hosted MCP server and adds a skill that tells Claude when a search is worth it and how to do it: specific queries, official docs and changelogs first, and a check that each source matches the library version your project uses. Answers come with linked, dated sources.

## Use it

- `/exa-search:search next.js 16 middleware changes`
- Or ask: "Is this deprecation warning from the latest React version?"

## Requirements

An Exa account. The first time the connector is used, run `/mcp` in Claude Code and sign in to Exa.

## Data

Search queries and the URLs Claude fetches are sent to Exa (mcp.exa.ai) under Exa's terms and privacy policy. The plugin stores nothing itself.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
