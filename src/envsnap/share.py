"""Temp sender-hosted share: stdlib HTTP, unguessable token, close=dead."""
from __future__ import annotations

import functools
import http.server
import os
import secrets


class _Handler(http.server.BaseHTTPRequestHandler):
    path_to_serve = ""
    token = ""

    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.strip("/") != self.token:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"not found")
            return
        try:
            size = os.path.getsize(self.path_to_serve)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(size))
            self.send_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(self.path_to_serve)}"',
            )
            self.end_headers()
            with open(self.path_to_serve, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except Exception:
            self.send_response(500)
            self.end_headers()


def serve_file(path: str, port: int = 8765):
    """Return (server, actual_port, token). Caller runs serve_forever in fg."""
    token = secrets.token_urlsafe(16)
    handler = functools.partial(_Handler)
    # bind token/path via class attrs (simple, single-file server)
    _Handler.path_to_serve = os.path.abspath(path)
    _Handler.token = token
    srv = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    actual = srv.server_address[1]
    return srv, actual, token


def lan_ip() -> str:
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()
