# Prompt Optimizer: Clearer, Shorter LLM Prompts

Make your prompts clearer and shorter without changing what they do, and measure the difference.

## What it does

- A bundled Python script measures a prompt (estimated tokens, template variables, XML tags) and flags repeated sentences, filler words, all-caps emphasis, piles of negative rules, missing output format, examples or context, and long prompts without structure.
- Claude rewrites the prompt following current prompting guidance: instructions with reasons, explicit output format, XML sections, long documents first, a few good examples, and stable content first for prompt caching.
- The script compares the old and new versions, warns if a template variable or tag disappeared, and estimates input cost at the price you give it.

## Use it

- `/prompt-optimizer:prompt-review prompts/support.md`
- `/prompt-optimizer:prompt-compare old.md new.md 3`
- Or ask: "Can this system prompt be shorter?"

## Requirements

Python 3. The script uses only the standard library.

## Data

Everything runs locally. Nothing is sent anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
