#!/usr/bin/env python3
"""Small HTTP load test with latency percentiles, plus a k6 script generator.

  loadtest.py URL [--method GET] [--header "Name: value"] [--body '{"a":1}']
              [--concurrency 10] [--duration 20] [--ramp 5] [--max-rps N]
              [--allow-remote] [--k6]

Targets on localhost, private networks and *.local / *.test / *.localhost run freely.
Any other host needs --allow-remote, which means you own or have written permission
to load test that system. Request volume is capped by --max-rps (default 200).
--k6 prints a k6 script for the same scenario instead of running anything.
"""
import argparse
import ipaddress
import json
import socket
import statistics
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request


def is_local(host):
    if host in ("localhost", "::1") or host.endswith((".local", ".test", ".localhost", ".internal")):
        return True
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(host))
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except Exception:
        return False


def k6_script(a):
    headers = dict(h.split(":", 1) for h in a.header)
    headers = {k.strip(): v.strip() for k, v in headers.items()}
    body = json.dumps(a.body) if a.body else "null"
    return f"""import http from 'k6/http';
import {{ check, sleep }} from 'k6';

export const options = {{
  stages: [
    {{ duration: '{a.ramp}s', target: {a.concurrency} }},
    {{ duration: '{a.duration}s', target: {a.concurrency} }},
    {{ duration: '5s', target: 0 }},
  ],
  thresholds: {{
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
  }},
}};

export default function () {{
  const res = http.request('{a.method}', '{a.url}', {body}, {{ headers: {json.dumps(headers)} }});
  check(res, {{ 'status is 2xx': (r) => r.status >= 200 && r.status < 300 }});
  sleep(1);
}}
"""


def worker(a, stop, results, lock, t0, gap):
    headers = {k.strip(): v.strip() for k, v in (h.split(":", 1) for h in a.header)}
    data = a.body.encode() if a.body else None
    next_at = time.time()
    while not stop.is_set():
        if gap:
            next_at += gap
            wait = next_at - time.time()
            if wait > 0:
                time.sleep(wait)
        req = urllib.request.Request(a.url, data=data, method=a.method, headers=headers)
        s = time.time()
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                r.read()
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception:
            code = 0
        d = (time.time() - s) * 1000
        with lock:
            results.append((s - t0, d, code))


def pct(vals, p):
    vals = sorted(vals)
    return vals[min(len(vals) - 1, int(len(vals) * p / 100))] if vals else 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--method", default="GET")
    p.add_argument("--header", action="append", default=[])
    p.add_argument("--body")
    p.add_argument("--concurrency", type=int, default=10)
    p.add_argument("--duration", type=int, default=20)
    p.add_argument("--ramp", type=int, default=5)
    p.add_argument("--max-rps", type=int, default=200)
    p.add_argument("--allow-remote", action="store_true")
    p.add_argument("--k6", action="store_true")
    a = p.parse_args()

    if a.k6:
        print(k6_script(a))
        return 0
    host = urllib.parse.urlparse(a.url).hostname or ""
    if not is_local(host) and not a.allow_remote:
        print(f"Refusing to load test {host}: it is not a local or private address.\n"
              "Pass --allow-remote only if you own this system or have written permission to test it.")
        return 2
    gap = a.concurrency / a.max_rps if a.max_rps else 0
    results, lock, stop, t0 = [], threading.Lock(), threading.Event(), time.time()
    threads = []
    print(f"Load test {a.method} {a.url}: {a.concurrency} workers, ramp {a.ramp}s, run {a.duration}s, cap {a.max_rps} req/s")
    for i in range(a.concurrency):
        t = threading.Thread(target=worker, args=(a, stop, results, lock, t0, gap), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(a.ramp / max(1, a.concurrency))
    time.sleep(a.duration)
    stop.set()
    for t in threads:
        t.join(timeout=35)
    if not results:
        print("No responses.")
        return 1
    lat = [r[1] for r in results]
    ok = [r for r in results if 200 <= r[2] < 400]
    errs = {}
    for r in results:
        if not 200 <= r[2] < 400:
            errs[r[2]] = errs.get(r[2], 0) + 1
    span = max(r[0] for r in results) - min(r[0] for r in results) or 1
    print(f"\nRequests: {len(results)}   throughput: {len(results) / span:.1f} req/s   success: {len(ok) / len(results) * 100:.1f}%")
    print(f"Latency ms: min {min(lat):.0f}  mean {statistics.mean(lat):.0f}  p50 {pct(lat, 50):.0f}  p90 {pct(lat, 90):.0f}  p95 {pct(lat, 95):.0f}  p99 {pct(lat, 99):.0f}  max {max(lat):.0f}")
    if errs:
        print("Errors by status (0 = connection error/timeout):", errs)
    half = len(results) // 2
    first, second = [r[1] for r in results[:half]], [r[1] for r in results[half:]]
    if first and second and statistics.mean(second) > statistics.mean(first) * 1.5:
        print("Latency grew by more than 50% during the run: the system is saturating or leaking resources.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
