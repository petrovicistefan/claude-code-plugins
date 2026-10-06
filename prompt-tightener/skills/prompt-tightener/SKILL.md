---
name: prompt-tightener
description: "Use when writing, reviewing or shortening a prompt or system prompt for Claude or another LLM, when an LLM feature gives inconsistent answers, or when estimating the token cost of a prompt."
---

# Prompt Tightener

Make prompts clearer and shorter without losing behaviour, and measure the difference.

## 1. Find the prompt

Prompts live in code (`system:` strings, `messages` arrays, template literals), in files (`prompts/*.md`, `.txt`, `.jinja`, YAML), or in agent instructions (`CLAUDE.md`, `SKILL.md`). Note the template variables and anything that parses the output (JSON parsing, regex on tags), because the rewrite must keep them working.

## 2. Measure

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/prompt_check.py prompts/support.md
```

It prints an estimated token count, template variables and XML tags, and flags repeated sentences, filler words, heavy all-caps emphasis, many negative instructions, missing output format, missing examples, missing context, long prompts without structure, and a question placed before a long document. Token counts are an estimate (about 4 characters per token in English). For exact counts, use the API's token counting endpoint.

## 3. Rewrite

Apply what helps current Claude models most:

- **Say what to do, and why.** Replace "NEVER use lists" with "Write in prose paragraphs, because the text is read aloud." A reason lets the model handle cases the rule did not list.
- **Drop shouting and filler.** "IMPORTANT", "MUST", "make sure to", "please", "you are a world-class expert" add tokens; modern models follow plain instructions, and heavy emphasis makes them over-apply a rule.
- **Be explicit about the output**: length, structure, tone, and the exact format if code parses it (a JSON schema, or tags such as `<answer>`). If the API supports structured outputs or tool schemas, prefer those for machine-read output.
- **Give context**: who the reader is, what the result is used for, what good looks like.
- **Separate parts with XML tags**: `<instructions>`, `<context>`, `<document>`, `<example>`. Put long documents first and the question or task last.
- **Use 1 to 3 short, varied examples** instead of many rules, wrapped in `<example>` tags. Make sure examples do not teach something you do not want copied.
- **Remove duplicates and contradictions.** When two instructions conflict, keep one and say which wins.
- **Stable content first** (instructions, documents, examples) and variable content last, so the API's prompt caching can reuse the prefix.

Keep every template variable, required tag and output contract. Do not change the meaning of rules. If a rule seems wrong, ask instead of removing it.

## 4. Compare

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/prompt_check.py old.md --compare new.md
python3 ${CLAUDE_SKILL_DIR}/scripts/prompt_check.py old.md --compare new.md --price 3 --calls 100000
```

It shows the token change and warns when template variables or tags disappeared. `--price` is the model's input price in USD per million tokens; take it from the provider's current pricing page instead of from memory.

Fewer tokens is not the goal by itself. Test the new prompt on a few real inputs, including hard cases, and compare the outputs with the old prompt before replacing it. If the project has evals or snapshot tests for the prompt, run them.

## 5. Reusable templates

When the same prompt shape appears in several places, propose one template with named variables in the project's existing format (f-string, Jinja, Handlebars, a function that builds `messages`), and keep the variable names already used in the code.

## Report

Show the main problems found, the rewritten prompt, the token difference, and what you tested or what the user should test.
