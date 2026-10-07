---
name: mobile-release-check
description: "Use before releasing or reviewing a React Native, Flutter, Android or iOS app, to find store rejection reasons, debug signing and leaked secrets."
---

# Mobile Release Check

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Catch what gets a mobile build rejected by the stores or leaks secrets, before the upload.

## 1. Run the check

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/mobile_check.py          # current folder
python3 ${CLAUDE_SKILL_DIR}/scripts/mobile_check.py apps/mobile
```

The header names the project types found (android, ios, flutter, react-native). Each finding has a severity, a file and a fix. Passwords and keys are never printed, only their location.

The script's `targetSdk` threshold is a constant that Google raises every year. Before telling the user the number is too low, confirm the current requirement on the Google Play "target API level" help page rather than trusting the script alone.

## 2. Fix

- **Debug signing on release**: create a release keystore, keep it outside the repo, and point Gradle to it through `~/.gradle/gradle.properties` or CI secrets. Recommend Play App Signing so the upload key can be reset. Do not generate or handle the user's real key and passwords; give the `keytool` command and let them run it.
- **Secrets in code**: a mobile app can be unpacked, so a key inside it is public. Move real secrets behind your own server; for public client keys (Maps, Firebase), restrict them by app id and API in the provider console.
- **Cleartext traffic / ATS off**: switch endpoints to HTTPS; if one legacy host needs HTTP, add a scoped exception (Android `network_security_config.xml`, iOS `NSExceptionDomains`) instead of a global switch.
- **Missing iOS usage descriptions**: add `NS...UsageDescription` strings that say why the permission is needed in plain language. Apple rejects vague texts like "needed for the app".
- **Sensitive permissions**: remove ones you do not use; for the rest, a Play Console declaration and a visible in-app reason are required.
- **Versions**: Android `versionCode` and iOS build number must increase for every upload; `versionName` and the marketing version are what users see. Flutter uses `version: 1.2.0+7` (name+build). Expo uses `version` plus `ios.buildNumber` and `android.versionCode`.
- **Minification**: enable R8/ProGuard for release and test the release build, since reflection and JSON libraries often need keep rules.

## 3. Release steps (user does the signing and the upload)

Android: `./gradlew bundleRelease` (or `flutter build appbundle`, `eas build -p android`) produces an `.aab`; test it on a real device with `bundletool` or an internal testing track before production.
iOS: archive in Xcode (or `flutter build ipa`, `eas build -p ios`), upload with Xcode Organizer or Transporter, test through TestFlight.

Never submit to the stores, tag a release or upload anything on the user's behalf without them asking. Also remind them of the non-code parts of review: privacy policy URL, data safety / privacy nutrition labels, screenshots and a demo account for reviewers if login is required. State clearly which checks could not be done from the files alone.
