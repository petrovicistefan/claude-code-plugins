# A11y Enforcer: WCAG Accessibility Checker

Find and fix accessibility problems in your UI code against WCAG 2.2 level AA, for HTML, React, Vue, Svelte and Astro.

## What it does

- A bundled Python script scans your markup and reports images without alt text, buttons and links without a name, form fields without labels, clickable `div`s that the keyboard cannot reach, positive `tabindex`, blocked zoom, autoplaying media and skipped headings, each with file, line and WCAG criterion.
- A contrast script calculates the WCAG contrast ratio of any two colors and says which levels pass.
- Claude then checks what a static scan cannot see, such as focus management in dialogs, live regions, target size and reduced motion, and fixes issues with native HTML first.

## Use it

- `/a11y-enforcer:a11y-check` or `/a11y-enforcer:a11y-check src/components`
- `/a11y-enforcer:contrast #6b7280 #ffffff`
- Or ask: "Is this form accessible?"

## Requirements

Python 3. The scripts use only the standard library.

## Data

Everything runs locally. Nothing is sent anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
