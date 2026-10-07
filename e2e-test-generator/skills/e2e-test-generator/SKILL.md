---
name: e2e-test-generator
description: "Use when asked to write, fix or plan end-to-end browser tests (Playwright, Cypress), to map the real pages and flows first and write stable tests."
---

# E2E Test Generator

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Write end-to-end tests that match how the app really works, from its actual routes and elements.

## 1. Map the app

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/e2e_map.py            # current folder
python3 ${CLAUDE_SKILL_DIR}/scripts/e2e_map.py apps/web
```

The map shows the framework, the E2E runner and config (if any), the dev/start scripts, existing specs, and each route with its forms, inputs, button labels and test ids. Pages marked "weak selectors" have inputs that have no label, name, id or `data-testid`.

If there is no E2E runner, recommend Playwright and ask before installing (`npm init playwright@latest` or `npm i -D @playwright/test` and `npx playwright install chromium`). Keep to the runner already in the project when there is one.

## 2. Pick the flow

Ask for the user's most important journeys if they did not name one (sign up, log in, the main create/edit action, checkout or payment, search). Do not try to cover every page: five stable tests on the money paths beat fifty brittle ones. Do not duplicate flows listed under existing specs.

## 3. Write the test

- Selectors in this order: `getByRole` with name, `getByLabel`, `getByText` for static copy, then `getByTestId`. Never use generated class names or long CSS/XPath chains. If a control has none of these, add a `data-testid` to the component in the same change.
- Use auto-waiting and web-first assertions (`await expect(locator).toBeVisible()`); no `waitForTimeout` or fixed sleeps. For Cypress, assert on elements and use `cy.intercept` aliases instead of `cy.wait(ms)`.
- Each test starts from a known state: create data through the API or a seed script, log in through a saved `storageState` (Playwright) or `cy.session`, and clean up. Tests must not depend on each other's order.
- Set `baseURL` in the config and use relative `goto('/path')`. Configure `webServer` (Playwright) to start the dev server.
- Credentials and tokens come from environment variables or the test environment; never write real credentials into a test. Never point tests at production.
- Stub third-party services you do not own (payments, email, maps) with `route.fulfill` / `cy.intercept`, and say what was stubbed.

## 4. Run and fix

Run headless: `npx playwright test path/to/spec.ts` or `npx cypress run --spec path`. Read the failure and trace. Decide honestly whether the test or the app is wrong: fix a wrong selector or missing wait in the test; report a real bug in the app instead of weakening the assertion. Run the test three times (`--repeat-each=3` in Playwright) to catch flakiness before handing it over, and summarize what each test covers and what it does not.
