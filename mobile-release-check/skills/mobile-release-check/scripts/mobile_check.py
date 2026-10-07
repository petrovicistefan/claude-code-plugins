#!/usr/bin/env python3
"""Check a React Native, Flutter, native Android or native iOS project for release problems.

  mobile_check.py [folder]     default: current folder

Reads Gradle, AndroidManifest, Info.plist, pubspec.yaml, app.json and package.json as
text. Reports what would be rejected by Google Play or the App Store, or leak secrets.
Never prints the value of a password or key, only where it is.
"""
import json
import os
import re
import sys

SKIP = {"node_modules", ".git", "Pods", "build", ".gradle", ".dart_tool", "DerivedData", "vendor"}
CURRENT_TARGET_SDK = 35  # Google Play requires the latest or one below for updates; confirm each year.


def files(root, names=None, suffix=None):
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in fs:
            if (names and f in names) or (suffix and f.endswith(suffix)):
                yield os.path.join(d, f)


def text(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    out = []

    def add(sev, path, msg):
        out.append((sev, os.path.relpath(path, root), msg))

    kinds = set()
    for g in files(root, {"build.gradle", "build.gradle.kts"}):
        t = text(g)
        if "com.android.application" not in t and "applicationId" not in t:
            continue
        kinds.add("android")
        m = re.search(r"targetSdk(?:Version)?\s*[=(]?\s*(\d+)", t)
        if m and int(m.group(1)) < CURRENT_TARGET_SDK - 1:
            add("high", g, f"targetSdk {m.group(1)} is below what Google Play accepts for new apps and updates. Raise it.")
        if not m and "flutter.targetSdkVersion" not in t and "rootProject.ext" not in t:
            add("medium", g, "targetSdk not found.")
        if re.search(r"minSdk(?:Version)?\s*[=(]?\s*(\d+)", t) and int(re.search(r"minSdk(?:Version)?\s*[=(]?\s*(\d+)", t).group(1)) < 21:
            add("low", g, "minSdk below 21 drops modern security defaults and bloats the app.")
        rel = re.search(r"buildTypes\s*\{.*?release\s*\{(.*?)\n\s{4}\}", t, re.S)
        if rel and "signingConfigs.debug" in rel.group(1) or re.search(r"release\s*\{[^}]*signingConfig\s*=?\s*signingConfigs\.(getByName\(\"debug\"\)|debug)", t, re.S):
            add("high", g, "release build is signed with the debug key. Play and the stores will reject it or it will not update.")
        if re.search(r"(storePassword|keyPassword)\s*[=(]?\s*[\"'][^\"']+[\"']", t):
            add("high", g, "signing password written in the Gradle file. Read it from ~/.gradle/gradle.properties or the CI secret store.")
        if rel and not re.search(r"minifyEnabled\s*(=\s*)?true|isMinifyEnabled\s*=\s*true", rel.group(1)):
            add("low", g, "release build does not enable minification (R8). Smaller app, harder to reverse.")
        if "versionCode" in t and re.search(r"versionCode\s*[=(]?\s*1\b", t):
            add("low", g, "versionCode is 1. Each Play upload needs a higher number than the last one.")
    for mf in files(root, {"AndroidManifest.xml"}):
        t = text(mf)
        if "src/main" not in mf.replace("\\", "/"):
            continue
        if re.search(r"android:debuggable=\"true\"", t):
            add("high", mf, "android:debuggable=\"true\" in the main manifest.")
        if re.search(r"usesCleartextTraffic=\"true\"", t):
            add("medium", mf, "cleartext HTTP traffic allowed. Use HTTPS and a network security config for exceptions.")
        if re.search(r"android:allowBackup=\"true\"", t):
            add("low", mf, "allowBackup=\"true\" lets app data be copied with adb backup. Set false or define backup rules.")
        for perm in re.findall(r"uses-permission[^>]*android:name=\"android\.permission\.(READ_SMS|SEND_SMS|READ_CALL_LOG|ACCESS_BACKGROUND_LOCATION|MANAGE_EXTERNAL_STORAGE|READ_CONTACTS)\"", t):
            add("medium", mf, f"permission {perm} needs a declaration form in Play Console and a clear in-app reason.")
    for pl in files(root, {"Info.plist"}):
        t = text(pl)
        if "Pods" in pl or "CFBundleIdentifier" not in t:
            continue
        kinds.add("ios")
        if re.search(r"NSAllowsArbitraryLoads</key>\s*<true", t):
            add("high", pl, "App Transport Security is off (NSAllowsArbitraryLoads). Apple asks for a reason; use HTTPS.")
        used = {"NSCameraUsageDescription": r"camera|AVCapture", "NSLocationWhenInUseUsageDescription": r"CLLocationManager",
                "NSPhotoLibraryUsageDescription": r"PHPhoto|UIImagePicker", "NSMicrophoneUsageDescription": r"AVAudioSession|AVAudioRecorder",
                "NSContactsUsageDescription": r"CNContact"}
        swift = "\n".join(text(s)[:200000] for s in files(os.path.dirname(pl), suffix=".swift"))
        for key, rx in used.items():
            if re.search(rx, swift, re.I) and key not in t:
                add("high", pl, f"code uses an API that needs {key}, but it is missing. The app crashes or is rejected.")
    pub = os.path.join(root, "pubspec.yaml")
    if os.path.isfile(pub):
        kinds.add("flutter")
        t = text(pub)
        m = re.search(r"^version:\s*(\S+)", t, re.M)
        if not m:
            add("medium", pub, "no `version:` (needed as version+build, e.g. 1.2.0+7).")
        elif "+" not in m.group(1):
            add("low", pub, "version has no build number (+N). Stores need an increasing build number.")
        if re.search(r"^\s+path:\s*\.\./", t, re.M):
            add("medium", pub, "dependency on a local path outside the repo: CI and other machines cannot build it.")
    pk = os.path.join(root, "package.json")
    if os.path.isfile(pk) and re.search(r"react-native|expo", text(pk)):
        kinds.add("react-native")
        ap = os.path.join(root, "app.json")
        if os.path.isfile(ap):
            try:
                j = json.load(open(ap)).get("expo", {})
                for k in ("version", "ios", "android"):
                    if k not in j:
                        add("low", ap, f"expo.{k} not set.")
            except Exception:
                pass
    secret_rx = re.compile(r"(api[_-]?key|secret|token|private[_-]?key)\s*[:=]\s*[\"'][A-Za-z0-9_\-/+]{16,}[\"']", re.I)
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in fs:
            if f.endswith((".kt", ".java", ".swift", ".dart", ".ts", ".tsx", ".js", ".plist", ".xml", ".json")) and f != "package-lock.json":
                p = os.path.join(d, f)
                if os.path.getsize(p) < 300000:
                    for m in secret_rx.finditer(text(p)):
                        add("high", p, f"possible hardcoded secret ({m.group(1)}). A mobile app can be unpacked; keep real secrets on a server.")
                        break
    for kf in files(root, suffix=".jks"):
        add("high", kf, "keystore file inside the project folder. Keep it out of git and back it up safely.")
    print(f"# Mobile release check ({', '.join(sorted(kinds)) or 'no mobile project found'})\n")
    order = {"high": 0, "medium": 1, "low": 2}
    for sev, path, msg in sorted(out, key=lambda x: order[x[0]]):
        print(f"[{sev.upper():6}] {path}  {msg}")
    print(f"\n{len(out)} findings, {sum(1 for o in out if o[0] == 'high')} high")
    return 1 if any(o[0] == "high" for o in out) else 0


if __name__ == "__main__":
    sys.exit(main())
