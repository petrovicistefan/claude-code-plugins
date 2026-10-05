# i18n Sync: Missing Translations Finder

Find missing, extra and untranslated keys in your locale files and detect hardcoded strings, for react-i18next, next-intl, vue-i18n and other JSON-based setups.

## What it does

A bundled Python script compares every JSON locale file with your base language, with nested keys and namespace folders supported, and reports missing keys, extra keys, values that were never translated and placeholders such as `{name}` or `{{count}}` that differ from the base text. Claude also searches your components for hardcoded user-facing strings, proposes keys that follow your naming pattern and fills in missing keys while keeping placeholders intact. It marks translations it is not sure about.

## Use it

- `/i18n-sync:i18n-check` or `/i18n-sync:i18n-check public/locales en`

## Requirements

Python 3 and JSON locale files.

## Data

Everything runs locally. Nothing is sent anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
