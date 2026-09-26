#!/usr/bin/env python3
"""Minimal Termux / phone companion (Companion protocol v1).

Stdlib only — copy to Termux and run:
  python termux-companion.py --port 18767

Supports health / ping / notify stubs so dsh-device-bridge can smoke-test.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    token = ""
    kind = "termux"
    allow = ["health", "ping", "notify"]

    def _auth(self) -> bool:
        if not self.token:
            return True
        return self.headers.get("Authorization") == f"Bearer {self.token}"

    def _json(self, code: int, obj: dict) -> None:
        raw = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if not self._auth():
            return self._json(401, {"ok": False, "error": "unauthorized"})
        if self.path.split("?")[0] != "/v1/health":
            return self._json(404, {"ok": False, "error": "not found"})
        self._json(
            200,
            {
                "ok": True,
                "kind": self.kind,
                "version": "0.1.1",
                "capabilities": list(self.allow),
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        if not self._auth():
            return self._json(401, {"ok": False, "error": "unauthorized"})
        if self.path.split("?")[0] != "/v1/invoke":
            return self._json(404, {"ok": False, "error": "not found"})
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n) or b"{}")
        action = str(body.get("action") or "")
        args = body.get("args") if isinstance(body.get("args"), dict) else {}
        if action not in self.allow:
            return self._json(400, {"ok": False, "error": f"action not allowlisted: {action}"})
        if action in ("ping", "health"):
            return self._json(200, {"ok": True, "result": {"action": action, "pong": True}})
        if action == "notify":
            title = str(args.get("title") or "dsh")
            text = str(args.get("body") or args.get("text") or "")
            # Stub: log only. On a real Termux box you could call termux-notification.
            sys.stderr.write(f"[notify] {title}: {text}\n")
            return self._json(200, {"ok": True, "result": {"notified": True, "title": title}})
        return self._json(400, {"ok": False, "error": f"unhandled action: {action}"})

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    ap = argparse.ArgumentParser(description="Termux companion stub for dsh-device-bridge")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=18767)
    ap.add_argument("--token", default=os.environ.get("DSH_COMPANION_TOKEN", ""))
    ap.add_argument("--kind", default="termux")
    args = ap.parse_args()
    Handler.token = args.token
    Handler.kind = args.kind
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(
        f"termux-companion on http://{args.host}:{args.port} kind={args.kind} caps={Handler.allow}",
        flush=True,
    )
    httpd.serve_forever()


if __name__ == "__main__":
    main()
