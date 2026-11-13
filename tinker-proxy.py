#!/usr/bin/env python3
"""Local proxy: nanocode -> Tinker Anthropic API.

nanocode sends its key as `Authorization: Bearer <token>`, but the Tinker
credential surrogate is only swapped by the runtime when it sits in the
`x-api-key` header (its registered placement). This proxy accepts nanocode's
requests on localhost, drops its Bearer token, and re-issues them to Tinker
with the surrogate in `x-api-key`, which the runtime then swaps for the real
key. Responses (including SSE streams) are passed through unchanged.

Uses `requests` so the VM egress proxy (from env) is honoured.

Usage:
    python3 tinker-proxy.py [port]        # default port 18789
    NANOCODE_ANTHROPIC_BASE_URL=http://127.0.0.1:18789/v1
    NANOCODE_ANTHROPIC_AUTH_TOKEN=dummy   # ignored by the proxy
    nc --harness claude --model thinkingmachines/Inkling-2-Small \
       --context-window 65536 --thinking none
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import dynamic_credential_entry

UPSTREAM = "https://tinker.thinkingmachines.dev/services/tinker-prod/anthropic/api"
# nanocode 0.7.0 only accepts its builtin model ids on the CLI, so we run it
# with a builtin Claude id and rewrite the model field here to Inkling.
MODEL_REWRITE = "thinkingmachines/Inkling-2-Small"


def get_surrogate() -> str:
    return dynamic_credential_entry("custom.tinker", "access_token")["surrogate"]


class ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _handle(self, method: str) -> None:
        # nanocode hits <base>/messages ; base ends in /v1, so path is /v1/...
        upstream_url = UPSTREAM + self.path
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None

        # Rewrite the model id so nanocode's builtin Claude id becomes Inkling.
        if body:
            try:
                payload = json.loads(body)
                if isinstance(payload, dict) and "model" in payload:
                    payload["model"] = MODEL_REWRITE
                    body = json.dumps(payload).encode()
            except (ValueError, UnicodeDecodeError):
                pass

        fwd = {}
        for k, v in self.headers.items():
            lk = k.lower()
            if lk in ("host", "connection", "authorization", "content-length",
                      "transfer-encoding", "accept-encoding"):
                continue
            fwd[k] = v
        fwd["x-api-key"] = get_surrogate()
        fwd["Content-Type"] = "application/json"
        fwd["User-Agent"] = "curl/8.5.0"

        try:
            resp = requests.request(
                method, upstream_url, data=body, headers=fwd,
                stream=True, timeout=300,
            )
        except Exception as exc:  # noqa: BLE001 - surface as 502
            msg = ("proxy upstream error: %s" % exc).encode()
            self.send_response(502)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
            return

        self.send_response(resp.status_code, resp.reason or "")
        for k, v in resp.headers.items():
            lk = k.lower()
            if lk in ("connection", "transfer-encoding", "content-length",
                      "content-encoding"):
                continue
            self.send_header(k, v)
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        try:
            for chunk in resp.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                self.wfile.write(b"%x\r\n%s\r\n" % (len(chunk), chunk))
            self.wfile.write(b"0\r\n\r\n")
        finally:
            resp.close()

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def log_message(self, fmt, *args):
        sys.stderr.write("proxy: %s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18789
    server = ThreadingHTTPServer(("127.0.0.1", port), ProxyHandler)
    print(f"tinker proxy listening on 127.0.0.1:{port} -> {UPSTREAM}", flush=True)
    server.serve_forever()
