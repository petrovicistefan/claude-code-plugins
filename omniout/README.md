# Omniout: LLM Retries and Model Fallback

Make your app's AI calls reliable with timeouts, retries, rate-limit handling and model fallback.

## What it does

Claude finds where your app calls Anthropic, OpenAI, Google, the Vercel AI SDK, LangChain or LiteLLM, and then either configures fallbacks in the gateway you already use or adds a small wrapper. The wrapper sets timeouts, retries only retryable errors with exponential backoff and `retry-after`, falls back through the models you approve, handles streaming safely, logs which model answered without logging keys, and comes with tests that simulate rate limits and outages.

It changes your application's code. It does not switch the model that Claude Code itself uses.

## Use it

- `/omniout:add-fallback claude-sonnet, gpt-5, gemini-pro`

## Data

Works on your local code. The plugin sends nothing to any external service.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
