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
                    result = service.doctor(path)
                    service.record_diagnosis(path, result)  # best-effort index
                    self._send(200, result)
                except Exception as e:  # adapter must not crash the server
                    self._send(500, {"error": str(e)})
            elif self.path == "/convert":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    result = service.convert(path, data.get("out_dir"))
                    service.record_conversion(path, result)  # best-effort index
                    self._send(200, result)
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
            elif self.path == "/insights":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.insights(path))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/report":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.report(path))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/canonical":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.canonical(path))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/mesh":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.mesh(path))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/strategies":
                try:
                    self._send(200, service.strategies())
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/strategy/recommend":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.strategy_recommend(path))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/printer/discover":
                try:
                    self._send(200, service.printer_discover(data.get("hosts")))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/printer/status":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_status(host, int(data.get("port", 7125))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/printer/history":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_history(host, int(data.get("port", 7125)), int(data.get("limit", 20))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/printer/file_metadata":
                host = data.get("host"); fn = data.get("filename")
                if not host or not fn:
                    self._send(400, {"error": "missing 'host' or 'filename'"})
                    return
                try:
                    self._send(200, service.printer_file_metadata(host, fn, int(data.get("port", 7125))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/printer/diagnostics":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_diagnostics(host, int(data.get("port", 7125))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/printer/bed_mesh":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_bed_mesh(host, int(data.get("port", 7125))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/first_layer":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.first_layer(path, data.get("host"), int(data.get("port", 7125))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/toolhead_fit":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.toolhead_fit(path, data.get("host"), int(data.get("port", 7125))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/cost_estimate":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.cost_estimate(path, float(data.get("price_per_kg", 20.0)), str(data.get("currency", "$"))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/batch_pricing":
                paths = data.get("paths")
                if not paths or not isinstance(paths, list):
                    self._send(400, {"error": "missing 'paths' (non-empty list)"})
                    return
                try:
                    factor_keys = ("price_per_kg", "power_w", "electricity_per_kwh",
                                   "machine_price", "machine_life_hours", "labor_hours",
                                   "labor_rate", "failure_rate_pct", "markup_pct",
                                   "marketplace_fee_pct")
                    factors = {k: data[k] for k in factor_keys if data.get(k) is not None}
                    self._send(200, service.batch_pricing(
                        paths, str(data.get("currency", "$")), **factors))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/predict_success":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.predict_success(
                        path, data.get("host"), int(data.get("port", 7125))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/cost_to_price":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    factor_keys = ("price_per_kg", "power_w", "electricity_per_kwh",
                                   "machine_price", "machine_life_hours", "labor_hours",
                                   "labor_rate", "failure_rate_pct", "markup_pct",
                                   "marketplace_fee_pct")
                    factors = {k: data[k] for k in factor_keys if data.get(k) is not None}
                    self._send(200, service.cost_to_price(
                        path, data.get("host"), data.get("filename"),
                        int(data.get("port", 7125)), str(data.get("currency", "$")),
                        **factors))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/printer/capabilities":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_capabilities(host, int(data.get("port", 7125))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/printer/firmware":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_firmware(host, int(data.get("port", 7125))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/printer/health":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_health(host, int(data.get("port", 7125)), int(data.get("limit", 50))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/printer/failure_insights":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_failure_insights(host, int(data.get("port", 7125)), int(data.get("limit", 50))))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/library":
                try:
                    self._send(200, service.library_list(
                        data.get("query", ""), data.get("tag")))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/library/delete":
                pid = data.get("id")
                if pid is None:
                    self._send(400, {"error": "missing 'id'"})
                    return
                try:
                    self._send(200, service.library_delete(pid))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/history":
                pid = data.get("project_id")
                if pid is None:
                    self._send(400, {"error": "missing 'project_id'"})
                    return
                try:
                    self._send(200, service.library_history(pid))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/batch":
                paths = data.get("paths")
                if not paths or not isinstance(paths, list):
                    self._send(400, {"error": "missing 'paths' (non-empty list)"})
                    return
                try:
                    self._send(200, service.batch_start(paths, data.get("out_dir")))
                except Exception as e:
                    self._send(500, {"error": str(e)})
            elif self.path == "/batch/status":
                job_id = data.get("job_id")
                if not job_id:
                    self._send(400, {"error": "missing 'job_id'"})
                    return
                status = service.batch_status(job_id)
                if status is None:
                    self._send(404, {"error": "unknown job"})
                else:
                    self._send(200, status)
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
