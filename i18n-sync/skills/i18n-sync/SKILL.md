---
name: i18n-sync
description: "Use when adding or changing user-facing text in a translated app, or when checking locale files for missing, extra or untranslated keys."
---

# i18n Sync

Keep translation files complete and in sync with the code.

## 1. Find the locale files

Common places: `locales/<lang>.json`, `public/locales/<lang>/<ns>.json`, `src/i18n/`, `messages/<lang>.json`. Identify the source language (usually `en`) from the i18n config.

## 2. Compare keys

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/i18n_check.py <locales-dir> --base en
```

The script handles flat and nested JSON, and both `<dir>/<lang>.json` and `<dir>/<lang>/<namespace>.json` layouts. For each language it reports:

- **missing**: keys in the base language but not in this one
- **extra**: keys not in the base language (often renamed or removed)
- **untranslated**: values identical to the base language
- **placeholder mismatch**: `{name}`, `{{count}}` or `%s` placeholders that differ from the base value

## 3. Find hardcoded strings

Search components for user-visible text outside the translation function (`t(`, `$t(`, `<Trans>`, `FormattedMessage`): JSX text nodes, `placeholder=`, `title=`, `aria-label=`, `alert(` and toast messages. List them with file and line and propose keys that follow the existing naming pattern.

## 4. Fix

- Add missing keys to every language. For languages you can translate, give a translation and mark it for review in your answer. Never invent translations for languages you are not confident in; copy the base text and say so.
- Keep placeholders and HTML tags unchanged.
- Remove extra keys only after checking they are unused in the code.
- Keep the files' existing ordering and formatting.
