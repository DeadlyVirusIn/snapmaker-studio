"""Loopback JSON server for the desktop app.

Binds 127.0.0.1 only. GET /health is open (for liveness probing); POST /doctor
requires the per-launch X-Auth-Token. On start, prints one JSON line
{"port": N, "token": "..."} to stdout so the Tauri shell can connect.
"""
from __future__ import annotations
import json
import os
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from . import service


def _watch_parent_then_exit() -> None:
    """When launched by the desktop shell, exit as soon as the parent process
    dies — for ANY reason (window close, crash, or force-kill). This guarantees
    no orphan sidecar survives the app. No-op if not launched with a parent PID
    or on non-Windows platforms.
    """
    ppid = os.environ.get("SNAPSTUDIO_PARENT_PID")
    if not ppid:
        return
    try:
        import ctypes
        from ctypes import wintypes

        if not hasattr(ctypes, "windll"):  # non-Windows
            return
        pid = int(ppid)

        PROCESS_SYNCHRONIZE = 0x00100000
        INFINITE = 0xFFFFFFFF

        k32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        # Declare explicit signatures — without these, ctypes defaults the
        # HANDLE return to a 32-bit int and truncates it on 64-bit Windows,
        # silently breaking the wait. wintypes.HANDLE is a full-width pointer.
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k32.WaitForSingleObject.restype = wintypes.DWORD
        k32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]

        handle = k32.OpenProcess(PROCESS_SYNCHRONIZE, False, pid)
        if not handle:
            return

        def _wait():
            k32.WaitForSingleObject(handle, INFINITE)
            os._exit(0)

        threading.Thread(target=_wait, daemon=True).start()
    except (AttributeError, OSError, ValueError):
        # Non-Windows (no windll) or bad PID — skip; not fatal.
        return


def _make_handler(token: str):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # silence default logging
            pass

        def _cors(self):
            # Loopback-only service; the Tauri webview is a different origin, so
            # responses need CORS headers or the in-app fetch is blocked.
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Auth-Token")

        def _send(self, code: int, obj: dict):
            body = json.dumps(obj).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self._cors()
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            # Preflight for POST requests carrying the X-Auth-Token header.
            self.send_response(204)
            self._cors()
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self):
            if self.path == "/health":
                self._send(200, service.health())
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            # Always drain the request body BEFORE responding. Replying (e.g. 401)
            # with an unread body resets the connection on Windows (WinError 10053).
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length else b""
            if self.headers.get("X-Auth-Token") != token:
                self._send(401, {"error": "unauthorized"})
                return
            try:
                data = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                self._send(400, {"error": "invalid JSON"})
                return
            if self.path == "/doctor":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.doctor(path))
                except Exception as e:  # adapter must not crash the server
                    self._send(500, {"error": str(e)})
            elif self.path == "/convert":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.convert(path, data.get("out_dir")))
                except Exception as e:  # adapter must not crash the server
                    self._send(500, {"error": str(e)})
            elif self.path == "/diff":
                a, b = data.get("a"), data.get("b")
                if not a or not b:
                    self._send(400, {"error": "missing 'a' or 'b'"})
                    return
                try:
                    self._send(200, service.diff(a, b))
                except Exception as e:  # adapter must not crash the server
                    self._send(500, {"error": str(e)})
            else:
                self._send(404, {"error": "not found"})

    return Handler


def build_server(host: str = "127.0.0.1", port: int = 0):
    """Return (httpd, token). Caller runs httpd.serve_forever()."""
    token = secrets.token_hex(16)
    httpd = ThreadingHTTPServer((host, port), _make_handler(token))
    return httpd, token


def serve(host: str = "127.0.0.1", port: int = 0) -> None:
    _watch_parent_then_exit()
    httpd, token = build_server(host, port)
    actual_port = httpd.server_address[1]
    print(json.dumps({"port": actual_port, "token": token}), flush=True)  # handshake line
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
