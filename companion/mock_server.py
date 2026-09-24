#!/usr/bin/env python3
"""Generic mock companion for phones/IoT (Companion protocol v1)."""
from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    token = ""
    kind = "generic"
    allow = ["health", "ping", "status"]

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
        self._json(200, {"ok": True, "kind": self.kind, "version": "0.1.0", "capabilities": self.allow})

    def do_POST(self) -> None:  # noqa: N802
        if not self._auth():
            return self._json(401, {"ok": False, "error": "unauthorized"})
        if self.path.split("?")[0] != "/v1/invoke":
            return self._json(404, {"ok": False, "error": "not found"})
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n) or b"{}")
        action = str(body.get("action") or "")
        if action not in self.allow:
            return self._json(400, {"ok": False, "error": f"action not allowlisted: {action}"})
        if action in ("ping", "health", "status"):
            return self._json(200, {"ok": True, "result": {"action": action, "pong": True}})
        return self._json(400, {"ok": False, "error": f"unhandled action: {action}"})

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=18766)
    ap.add_argument("--token", default=os.environ.get("DSH_DEVICE_TOKEN", ""))
    ap.add_argument("--kind", default="phone")
    args = ap.parse_args()
    Handler.token = args.token
    Handler.kind = args.kind
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"dsh-device-bridge mock on http://{args.host}:{args.port} kind={args.kind}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
