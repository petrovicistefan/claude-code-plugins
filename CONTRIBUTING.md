# Contributing

## Plugin layout

```
<plugin>/
  .claude-plugin/plugin.json   name, displayName, version, description, author, license
  skills/<plugin>/SKILL.md     frontmatter with name and a "Use when..." description
  skills/<plugin>/scripts/     optional, Python standard library only
  commands/<command>.md        slash commands with a description in frontmatter
  .mcp.json                    optional, only official https MCP servers
  README.md                    at least 40 words: what it does, how to use it, what data it sends
  LICENSE
```

## Rules

- Describe only what the plugin really does. No invented commands, numbers or features.
- No secrets in any file. No package launchers such as `npx` or `uvx` in hooks or MCP commands.
- Scripts must be readable source and must not install packages.
- Raise `version` in `plugin.json` and `.claude-plugin/marketplace.json` with every change.

## Before opening a pull request

```bash
claude plugin validate ./<plugin>
claude plugin validate .
claude --plugin-dir ./<plugin>
```

Try the plugin's command on a real project and check the result.
