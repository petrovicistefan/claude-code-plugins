#!/usr/bin/env python3
"""Screenshot a URL at several viewport sizes and report horizontal overflow.

Uses a Chrome, Chromium, Edge or Brave browser already installed on the machine,
driven through the Chrome DevTools Protocol. Needs only the Python standard library.
Pass --browser to use a specific browser executable.
"""
import argparse
import base64
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
LINUX_NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
               "microsoft-edge", "brave-browser"]

OVERFLOW_JS = """
(() => {
  const vw = document.documentElement.clientWidth;
  const wide = [];
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.width > 0 && (r.right > vw + 1 || r.left < -1)) {
      const id = el.id ? '#' + el.id : '';
      const cls = typeof el.className === 'string' && el.className.trim()
        ? '.' + el.className.trim().split(/\\s+/).slice(0, 2).join('.') : '';
      wide.push(`${el.tagName.toLowerCase()}${id}${cls} (right ${Math.round(r.right)}px)`);
      if (wide.length >= 10) break;
    }
  }
  return {scrollWidth: document.documentElement.scrollWidth,
          height: document.documentElement.scrollHeight, viewport: vw, wide};
})()
"""


def find_browser(explicit=None):
    if explicit:
        return explicit if os.path.exists(explicit) else None
    for path in CANDIDATES:
        if os.path.exists(path):
            return path
    for name in LINUX_NAMES:
        path = shutil.which(name)
        if path:
            return path
    return None


class WebSocket:
    """Minimal client for the text frames used by the DevTools Protocol."""

    def __init__(self, url):
        u = urllib.parse.urlparse(url)
        self.sock = socket.create_connection((u.hostname, u.port), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\n"
                           "Upgrade: websocket\r\nConnection: Upgrade\r\n"
                           f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("browser closed the connection")
            response += chunk
        if b" 101 " not in response.split(b"\r\n", 1)[0]:
            raise ConnectionError("websocket handshake failed")
        self.buffer = response.split(b"\r\n\r\n", 1)[1]
        self.next_id = 0

    def _read(self, n):
        while len(self.buffer) < n:
            chunk = self.sock.recv(1 << 16)
            if not chunk:
                raise ConnectionError("browser closed the connection")
            self.buffer += chunk
        data, self.buffer = self.buffer[:n], self.buffer[n:]
        return data

    def send(self, text):
        payload = text.encode()
        header = bytes([0x81])
        n = len(payload)
        if n < 126:
            header += bytes([0x80 | n])
        elif n < 1 << 16:
            header += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            header += bytes([0x80 | 127]) + struct.pack(">Q", n)
        mask = os.urandom(4)
        self.sock.sendall(header + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

    def recv(self):
        message = b""
        while True:
            b1, b2 = self._read(2)
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read(8))[0]
            data = self._read(n)
            opcode = b1 & 0x0F
            if opcode == 8:
                raise ConnectionError("browser closed the connection")
            if opcode in (0, 1, 2):
                message += data
                if b1 & 0x80:
                    return json.loads(message)

    def call(self, method, **params):
        self.next_id += 1
        self.send(json.dumps({"id": self.next_id, "method": method, "params": params}))
        while True:
            msg = self.recv()
            if msg.get("id") == self.next_id:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error'].get('message')}")
                return msg.get("result", {})

    def wait_for(self, event, timeout):
        end = time.time() + timeout
        while time.time() < end:
            if self.recv().get("method") == event:
                return True
        return False


def start_browser(path):
    profile = tempfile.mkdtemp(prefix="responsive-check-")
    proc = subprocess.Popen(
        [path, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
         "--hide-scrollbars", "--remote-debugging-port=0", f"--user-data-dir={profile}", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    port_file = os.path.join(profile, "DevToolsActivePort")
    for _ in range(100):
        if os.path.exists(port_file) and open(port_file).read().strip():
            port = int(open(port_file).read().split()[0])
            return proc, profile, port
        if proc.poll() is not None:
            break
        time.sleep(0.1)
    proc.kill()
    shutil.rmtree(profile, ignore_errors=True)
    sys.exit(f"Could not start the browser at {path}.")


def page_socket(port):
    targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list"))
    page = next(t for t in targets if t.get("type") == "page")
    return WebSocket(page["webSocketDebuggerUrl"])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--out", default="screenshots")
    p.add_argument("--sizes", default="375x812,768x1024,1280x800,1920x1080")
    p.add_argument("--wait", type=float, default=1.0, help="seconds to wait after load")
    p.add_argument("--browser", help="path to a Chrome, Chromium, Edge or Brave executable")
    a = p.parse_args()

    browser = find_browser(a.browser)
    if not browser:
        sys.exit("No Chrome, Chromium, Edge or Brave browser found. Install one, "
                 "or pass --browser with the browser executable.")

    os.makedirs(a.out, exist_ok=True)
    proc, profile, port = start_browser(browser)
    problems = 0
    try:
        ws = page_socket(port)
        ws.call("Page.enable")
        for size in a.sizes.split(","):
            w, h = (int(x) for x in size.lower().split("x"))
            ws.call("Emulation.setDeviceMetricsOverride", width=w, height=h,
                    deviceScaleFactor=1, mobile=w < 768)
            ws.call("Page.navigate", url=a.url)
            if not ws.wait_for("Page.loadEventFired", timeout=30):
                print(f"{w}x{h}: page did not finish loading in 30 s")
            time.sleep(a.wait)
            info = ws.call("Runtime.evaluate", expression=OVERFLOW_JS, returnByValue=True)["result"]["value"]
            full_h = max(h, min(info["height"], 16000))
            shot = ws.call("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                           clip={"x": 0, "y": 0, "width": max(w, info["scrollWidth"]),
                                 "height": full_h, "scale": 1})
            path = os.path.join(a.out, f"{w}x{h}.png")
            with open(path, "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            overflow = info["scrollWidth"] > info["viewport"]
            problems += overflow
            status = f"OVERFLOW: page is {info['scrollWidth']}px wide" if overflow else "OK"
            print(f"{w}x{h}: {path} - {status}")
            for item in info["wide"]:
                print(f"    wider than viewport: {item}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)
    print(f"Browser: {browser}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
