---
name: exa-search
description: "Use when an answer depends on current documentation, recent library releases, changelogs or error messages that may be newer than Claude's training data."
---

# Exa Search

Look things up on the live web with the Exa connector before answering questions about fast-moving tools and libraries.

## When to search

- The user asks about a library version, API or feature released recently
- An error message or deprecation warning you do not recognize
- Pricing, limits, or "what is the latest" questions
- Before recommending a package, to check it is maintained

Do not search for things the project's own code or installed docs already answer.

## How

1. Use the Exa connector's search tool with a specific query: library name, version, and the exact error or API name. Prefer official docs, changelogs, GitHub issues and release notes.
2. Fetch the most relevant pages with the connector's content tool and read the parts that answer the question.
3. Check the date of each source and the version it describes against the version in the project (`package.json`, `requirements.txt`, lockfiles).

If the Exa tools are not available, tell the user to connect the Exa connector (run `/mcp` in Claude Code to sign in) and answer from what you know, stating that it may be out of date.

## Answer

Give the answer first, then the sources as links with their dates. Say clearly when sources disagree or when the information applies to a different version than the one in use.
