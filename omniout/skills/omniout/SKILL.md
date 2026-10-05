---
name: omniout
description: "Use when building or fixing an app that calls LLM APIs and needs retries, timeouts, rate-limit handling or fallback to another model or provider."
---

# Omniout

Make an application's LLM calls reliable: retries, timeouts, rate limits and fallback between models and providers.

This skill changes the user's application code. It does not change which model Claude Code itself uses.

## 1. Find the current calls

Search for SDK usage (`@anthropic-ai/sdk`, `anthropic`, `openai`, `ai` from the Vercel AI SDK, `@google/genai`, LangChain, LiteLLM, raw `fetch` to an LLM endpoint). Note where keys come from, current timeouts, error handling and whether calls stream.

## 2. Choose the approach that fits the stack

- **Already uses a gateway or router** (Vercel AI Gateway, OpenRouter, LiteLLM, a cloud provider's routing): configure fallback models there instead of writing new code
- **Single SDK**: add a small wrapper around the call
- Ask the user which providers and models are allowed and in what order; never add a provider they do not have an account for

## 3. Implement the wrapper

- Timeouts on every call
- Retry only retryable errors: HTTP 429, 500, 502, 503, 504, 529 and network errors. Do not retry 400, 401, 403 or validation errors
- Exponential backoff with jitter, and honor the `retry-after` header
- After retries are exhausted, move to the next model in the list. Keep prompts compatible: adjust parameter names and limits per provider
- For streaming, fall back only if no tokens were sent yet
- Log which model answered and why a fallback happened; never log API keys or full prompts with user data
- Read keys from environment variables

## 4. Test

Add tests that simulate 429, 5xx and timeouts with a mocked client and check that retries and fallback happen in the right order and stop at the right time.
