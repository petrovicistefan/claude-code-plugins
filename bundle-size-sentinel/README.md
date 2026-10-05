# Bundle Size Sentinel: JavaScript Bundle Analyzer

Keep JavaScript bundles small: check dependencies before adding them and measure the gzip size of every file in your build.

## What it does

- Before adding an npm package, Claude looks for a built-in or lighter option and explains the trade-off.
- After a build, a bundled Python script lists every JavaScript and CSS file with raw and gzip size, the largest files and the total.
- It can save a report and compare the next build against it to show what changed.

## Use it

- `/bundle-size-sentinel:bundle-size` or `/bundle-size-sentinel:bundle-size dist`
- Or ask: "Why did our bundle get bigger?"

## Requirements

Python 3 and a project with a build command. The script uses only the Python standard library.

## Data

Everything runs locally. The plugin reads your build folder and sends nothing anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
