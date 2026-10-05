# Env Protector: Secret Scanner

Find leaked API keys, passwords and tokens before they reach git, and keep `.env` secrets out of Claude's context.

## What it does

- Tells Claude not to open `.env`, key and credential files unless you ask, and to list only variable names when it needs to know what is configured.
- Masks secret values whenever Claude has to refer to them.
- Includes a scanner (Python standard library only) that finds common key formats from AWS, GitHub, Stripe, Slack, Google, OpenAI and Anthropic, private keys, JWTs, passwords in URLs and hardcoded secrets, with values masked in the output. It can scan the whole project or only staged files before a commit.
- Explains how to move a leaked secret to an environment variable and reminds you to rotate keys that were already pushed.

## Use it

- `/env-protector:scan-secrets` or `/env-protector:scan-secrets staged`

## Limits

Pattern matching can miss unusual secret formats and can flag test values. It complements a dedicated secret scanner in CI and does not replace it.

## Data

Everything runs locally. Found values are masked and nothing is sent anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
