# Responsive Check: Mobile Layout Tester

Screenshot any page at phone, tablet and desktop sizes and find layout bugs, with the browser you already have.

## What it does

Claude takes a screenshot of a local or public URL at each viewport size, using a browser tool in your session if one is available, or a bundled Python script that drives the Chrome, Edge, Chromium or Brave browser you already have. The script also reports horizontal overflow and lists the elements wider than the screen. Claude then reviews every screenshot for clipped or overlapping content, small tap targets, unreadable text and navigation that does not collapse, and proposes CSS fixes in your project's styling system before checking again.

## Use it

- `/responsive-check:responsive http://localhost:3000`

## Requirements

Python 3 and an installed Chrome, Chromium, Edge or Brave browser. Nothing else is installed: the script uses only the Python standard library. Pass `--browser <path>` to choose a specific browser.

## Data

Screenshots are saved locally in a `screenshots` folder. The browser loads only the URL you give. The plugin sends nothing else anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
