# Headroom: Large File and Log Reader

Work with huge logs, long documents and big JSON or CSV files without filling Claude's context.

## What it does

A bundled Python script measures the file and prints an outline: Markdown headings with line numbers, the most frequent log line patterns and log levels, the structure of a JSON file, or CSV columns with sample rows. Claude then reads only the sections the task needs, filters logs before reading them, computes totals with code instead of reading rows, and keeps a short digest with line references so it does not re-read the source.

## Use it

- `/headroom:peek logs/server.log`
- Or ask: "Summarize the errors in this 300 MB log."

## Requirements

Python 3. The script uses only the standard library.

## Data

Everything runs locally on your files. Nothing is sent anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
