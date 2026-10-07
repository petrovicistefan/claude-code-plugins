# E2E Test Generator: Playwright and Cypress Tests

Write Playwright or Cypress end-to-end tests from your real routes, forms and buttons, using stable selectors, and find the pages that need test hooks first.

## What it does

- A bundled Python script maps the app without running it: the E2E runner already installed (Playwright, Cypress, WebdriverIO or TestCafe), routes for Next.js, Nuxt, SvelteKit, React Router and Vue Router, forms, inputs and buttons per page, existing E2E specs, and which pages already have stable selectors such as `data-testid`.
- Claude writes the test for the flow you describe using role-based, label-based and test-id selectors, never brittle CSS paths, and adds missing `data-testid` attributes where a control has no stable handle.
- It runs the test headless, reads the failure and fixes the test or reports a real bug in the app.

## Use it

- `/e2e-test-generator:e2e-map`
- `/e2e-test-generator:e2e-write sign up, verify email page, log in`
- Or ask: "Write a Playwright test for checkout."

## Requirements

Python 3. Playwright or Cypress in the project to run the tests (Claude can add Playwright if it is missing).

## Data

The map runs locally on your files. Tests run against the URL you choose, usually your own dev server. The plugin sends nothing anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
