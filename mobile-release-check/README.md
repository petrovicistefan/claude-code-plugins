# Mobile Release Check: Play and App Store Readiness

Check React Native, Flutter, Android and iOS projects before release: target SDK, debug signing, cleartext traffic, missing permission texts, hardcoded keys and version numbers.

## What it does

- A bundled Python script reads Gradle files, `AndroidManifest.xml`, `Info.plist`, `pubspec.yaml`, `app.json` and `package.json` and flags a low `targetSdk`, release builds signed with the debug key, signing passwords in Gradle, `debuggable`, cleartext HTTP, `allowBackup`, sensitive Android permissions, App Transport Security turned off, missing iOS permission descriptions for APIs the code uses, version and build number problems, keystores inside the repo and hardcoded keys.
- It works for React Native, Expo, Flutter, native Android (Kotlin, Java) and native iOS (Swift).
- Claude fixes the findings and walks you through the release steps for each platform, but you do the signing and the upload yourself.

## Use it

- `/mobile-release-check:mobile-check`
- `/mobile-release-check:mobile-release android`
- Or ask: "Will Google Play accept this build?"

## Requirements

Python 3.

## Data

Runs locally on your project files. It never prints password or key values. The plugin sends nothing anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
