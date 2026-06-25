"""Loopback JSON server for the desktop app.

Binds 127.0.0.1 only. GET /health is open (for liveness probing); POST /doctor
requires the per-launch X-Auth-Token. On start, prints one JSON line
{"port": N, "token": "..."} to stdout so the Tauri shell can connect.
"""
from __future__ import annotations
import hmac
import json
import os
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from . import service
from . import request_validation as rv
from .request_validation import ValidationError


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


def cors_allow_origin(origin: str | None) -> str | None:
    """Return the Origin to echo in Access-Control-Allow-Origin, or None to omit it.

    Loopback-only service: allow only local app/dev origins (the Tauri webview and
    Vite dev server) instead of a wildcard, so an arbitrary remote web page can no
    longer read even unauthenticated responses. POSTs remain token-gated regardless.
    Covers Windows/Linux/macOS Tauri webview origins and localhost dev ports.
    """
    if not origin:
        return None
    o = origin.strip()
    if o == "tauri://localhost":
        return o
    try:
        host = (urlparse(o).hostname or "").lower()
    except ValueError:
        return None
    if host in ("localhost", "127.0.0.1", "tauri.localhost", "::1") or host.endswith(".localhost"):
        return o
    return None


def _make_handler(token: str):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # silence default logging
            pass

        def _cors(self):
            # Loopback-only service; the Tauri webview is a different origin, so
            # responses need CORS headers or the in-app fetch is blocked. Echo only
            # allowed local origins (not '*'); requests with no Origin (non-browser)
            # need no header.
            allowed = cors_allow_origin(self.headers.get("Origin"))
            if allowed:
                self.send_header("Access-Control-Allow-Origin", allowed)
                self.send_header("Vary", "Origin")
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
            # Guard the parse (a non-numeric Content-Length must not crash the
            # handler), but still drain any valid body before responding — an
            # unread body resets the connection on Windows (WinError 10053).
            try:
                length = int(self.headers.get("Content-Length", 0) or 0)
            except (TypeError, ValueError):
                self._send(400, {"error": "invalid Content-Length"})
                return
            raw = self.rfile.read(length) if length > 0 else b""
            if not hmac.compare_digest(self.headers.get("X-Auth-Token") or "", token):
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
                except Exception:  # adapter must not crash the server
                    self._send(500, {"error": "internal error"})
            elif self.path == "/first_layer_check":
                try:
                    self._send(200, service.first_layer_check(data.get("symptom", "")))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/quality_check":
                try:
                    self._send(200, service.quality_check(data.get("symptom", ""), data.get("path")))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/source_compatibility":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.source_compatibility(path))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/scale_preview":
                try:
                    path = rv.require_path_string(data)
                    scale = rv.require_finite_float(data, "scale_percent")
                    self._send(200, service.scale_preview(path, scale))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/scale_options":
                try:
                    path = rv.require_path_string(data)
                    printer = rv.optional_str(data, "printer", "snapmaker_u1")
                    margin = rv.optional_float(data, "margin_mm", 5.0)
                    self._send(200, service.scale_options(path, printer, margin))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/print_failure_troubleshoot":
                try:
                    path = rv.require_path_string(data)
                    kg = data.get("known_good_print")
                    if isinstance(kg, str):
                        kg = kg.strip().lower() in ("true", "1", "yes")
                    elif kg is not None:
                        kg = bool(kg)
                    self._send(200, service.print_failure_troubleshoot(
                        path,
                        rv.optional_str(data, "symptom", "fails_even_with_supports"),
                        kg,
                        rv.optional_str(data, "known_good_material", "") or None,
                        rv.optional_str(data, "failed_material", "") or None,
                        rv.optional_str(data, "failure_stage", "unknown")))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/model_search":
                try:
                    self._send(200, service.model_search_query(
                        data.get("query", ""), data.get("filters") or {}))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/compatibility_check":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.compatibility_check(path))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/convert":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    result = service.convert(path, data.get("out_dir"))
                    service.record_conversion(path, result)  # best-effort index
                    self._send(200, result)
                except Exception:  # adapter must not crash the server
                    self._send(500, {"error": "internal error"})
            elif self.path == "/prepare_scaled":
                path = data.get("path")
                scale = data.get("scale_percent")
                if not path or scale is None:
                    self._send(400, {"error": "missing 'path' or 'scale_percent'"})
                    return
                try:
                    result = service.prepare_scaled(path, float(scale), data.get("out_dir"))
                    if not result.get("blocked"):
                        service.record_conversion(path, result)  # best-effort index
                    self._send(200, result)
                except ValueError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/diff":
                a, b = data.get("a"), data.get("b")
                if not a or not b:
                    self._send(400, {"error": "missing 'a' or 'b'"})
                    return
                try:
                    self._send(200, service.diff(a, b))
                except Exception:  # adapter must not crash the server
                    self._send(500, {"error": "internal error"})
            elif self.path == "/insights":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.insights(path))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/report":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.report(path))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/canonical":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.canonical(path))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/mesh":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.mesh(path))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/strategies":
                try:
                    self._send(200, service.strategies())
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/strategy/recommend":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.strategy_recommend(path))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/printer/discover":
                try:
                    self._send(200, service.printer_discover(data.get("hosts")))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/printer/status":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_status(host, rv.require_port(data)))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/printer/history":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_history(host, rv.require_port(data), rv.optional_int(data, "limit", 20)))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/printer/file_metadata":
                host = data.get("host"); fn = data.get("filename")
                if not host or not fn:
                    self._send(400, {"error": "missing 'host' or 'filename'"})
                    return
                try:
                    self._send(200, service.printer_file_metadata(host, fn, rv.require_port(data)))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/printer/diagnostics":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_diagnostics(host, rv.require_port(data)))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/printer/bed_mesh":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_bed_mesh(host, rv.require_port(data)))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path in ("/printer/control/pause", "/printer/control/resume",
                               "/printer/control/cancel", "/printer/control/start",
                               "/printer/control/emergency_stop", "/printer/job_queue",
                               "/printer/upload_gcode"):
                # Printer Hub Phase B control. The Studio UI is the safety gate: it
                # confirms start/cancel/emergency-stop before calling these. The backend
                # only relays the user-confirmed action to Moonraker.
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                port = rv.require_port(data)
                try:
                    if self.path == "/printer/control/pause":
                        out = service.printer_pause(host, port)
                    elif self.path == "/printer/control/resume":
                        out = service.printer_resume(host, port)
                    elif self.path == "/printer/control/cancel":
                        out = service.printer_cancel(host, port)
                    elif self.path == "/printer/control/start":
                        out = service.printer_start(host, data.get("filename"), port)
                    elif self.path == "/printer/control/emergency_stop":
                        out = service.printer_emergency_stop(host, port)
                    elif self.path == "/printer/job_queue":
                        out = service.printer_job_queue(host, port)
                    else:  # /printer/upload_gcode
                        out = service.printer_upload_gcode(host, data.get("path"), port)
                    self._send(200, out)
                except (ValidationError, ValueError) as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(502, {"error": "could not reach the printer or it refused the command"})
            elif self.path == "/first_layer":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.first_layer(path, data.get("host"), rv.require_port(data)))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/toolhead_fit":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.toolhead_fit(path, data.get("host"), rv.require_port(data)))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/cost_estimate":
                try:
                    path = rv.require_path_string(data)
                    price = rv.optional_positive_float(data, "price_per_kg", 20.0)
                    currency = rv.optional_str(data, "currency", "$")
                    self._send(200, service.cost_estimate(path, price, currency))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/batch_pricing":
                paths = data.get("paths")
                if not paths or not isinstance(paths, list):
                    self._send(400, {"error": "missing 'paths' (non-empty list)"})
                    return
                try:
                    factor_keys = ("price_per_kg", "power_w", "electricity_per_kwh",
                                   "machine_price", "machine_life_hours", "labor_hours",
                                   "labor_rate", "failure_rate_pct", "markup_pct",
                                   "marketplace_fee_pct", "grams_override", "print_hours",
                                   "packaging", "shipping_cost", "shipping_charged",
                                   "material_density")
                    factors = {k: rv.optional_float(data, k, 0.0) for k in factor_keys if data.get(k) is not None}
                    self._send(200, service.batch_pricing(
                        paths, str(data.get("currency", "$")), **factors))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/mm_doctor":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.mm_doctor(
                        path, data.get("host"), rv.require_port(data)))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/bed_fit":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.bed_fit(
                        path, data.get("host"), rv.require_port(data)))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/predict_success":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.predict_success(
                        path, data.get("host"), rv.require_port(data)))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/community_knowledge":
                try:
                    self._send(200, service.community_knowledge(
                        str(data.get("query", "")), data.get("risks")))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/plate_export":
                try:
                    path = rv.require_path_string(data)
                    ui_plate = rv.require_int(data, "ui_plate")
                    from_f = rv.require_int(data, "from_filament")
                    to_f = rv.require_int(data, "to_filament")
                    out_path = rv.optional_str(data, "out_path", "") or None
                    self._send(200, service.plate_export(path, ui_plate, from_f, to_f, out_path))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/plate_dry_run":
                try:
                    path = rv.require_path_string(data)
                    ui_plate = rv.require_int(data, "ui_plate")
                    from_f = rv.require_int(data, "from_filament")
                    to_f = rv.require_int(data, "to_filament")
                    self._send(200, service.plate_dry_run(path, ui_plate, from_f, to_f))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/plate_inspect":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    self._send(200, service.plate_inspect(path))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/demo_report":
                try:
                    self._send(200, service.demo_report())
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/intelligence_report":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    factor_keys = ("price_per_kg", "power_w", "electricity_per_kwh",
                                   "machine_price", "machine_life_hours", "labor_hours",
                                   "labor_rate", "failure_rate_pct", "markup_pct",
                                   "marketplace_fee_pct", "grams_override", "print_hours",
                                   "packaging", "shipping_cost", "shipping_charged",
                                   "material_density")
                    factors = {k: rv.optional_float(data, k, 0.0) for k in factor_keys if data.get(k) is not None}
                    self._send(200, service.intelligence_report(
                        path, data.get("host"), data.get("filename"),
                        rv.require_port(data), str(data.get("currency", "$")),
                        **factors))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path in ("/pricing_doctor", "/profit_doctor"):
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    factor_keys = ("price_per_kg", "power_w", "electricity_per_kwh",
                                   "machine_price", "machine_life_hours", "labor_hours",
                                   "labor_rate", "failure_rate_pct", "markup_pct",
                                   "marketplace_fee_pct", "grams_override", "print_hours",
                                   "packaging", "shipping_cost", "shipping_charged",
                                   "material_density")
                    factors = {k: rv.optional_float(data, k, 0.0) for k in factor_keys if data.get(k) is not None}
                    common = dict(host=data.get("host"), filename=data.get("filename"),
                                  port=rv.require_port(data),
                                  currency=rv.optional_str(data, "currency", "$"))
                    if self.path == "/pricing_doctor":
                        self._send(200, service.pricing_doctor(path, **common, **factors))
                    else:
                        self._send(200, service.profit_doctor(
                            path, **common,
                            prints_per_month=rv.optional_int(data, "prints_per_month", 20),
                            fixed_cost=data.get("fixed_cost"),
                            batch_count=rv.optional_int(data, "batch_count", 10), **factors))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/cost_to_price":
                path = data.get("path")
                if not path:
                    self._send(400, {"error": "missing 'path'"})
                    return
                try:
                    factor_keys = ("price_per_kg", "power_w", "electricity_per_kwh",
                                   "machine_price", "machine_life_hours", "labor_hours",
                                   "labor_rate", "failure_rate_pct", "markup_pct",
                                   "marketplace_fee_pct", "grams_override", "print_hours",
                                   "packaging", "shipping_cost", "shipping_charged",
                                   "material_density")
                    factors = {k: rv.optional_float(data, k, 0.0) for k in factor_keys if data.get(k) is not None}
                    self._send(200, service.cost_to_price(
                        path, data.get("host"), data.get("filename"),
                        rv.require_port(data), rv.optional_str(data, "currency", "$"),
                        **factors))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/printer/capabilities":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_capabilities(host, rv.require_port(data)))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/printer/firmware":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_firmware(host, rv.require_port(data)))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/printer/health":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_health(host, rv.require_port(data), int(data.get("limit", 50))))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/printer/failure_insights":
                host = data.get("host")
                if not host:
                    self._send(400, {"error": "missing 'host'"})
                    return
                try:
                    self._send(200, service.printer_failure_insights(host, rv.require_port(data), int(data.get("limit", 50))))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/library":
                try:
                    self._send(200, service.library_list(
                        data.get("query", ""), data.get("tag")))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/library/delete":
                pid = data.get("id")
                if pid is None:
                    self._send(400, {"error": "missing 'id'"})
                    return
                try:
                    self._send(200, service.library_delete(pid))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/history":
                pid = data.get("project_id")
                if pid is None:
                    self._send(400, {"error": "missing 'project_id'"})
                    return
                try:
                    self._send(200, service.library_history(pid))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
            elif self.path == "/batch":
                paths = data.get("paths")
                if not paths or not isinstance(paths, list):
                    self._send(400, {"error": "missing 'paths' (non-empty list)"})
                    return
                try:
                    self._send(200, service.batch_start(paths, data.get("out_dir")))
                except ValidationError as e:
                    self._send(400, {"error": str(e)})
                except Exception:
                    self._send(500, {"error": "internal error"})
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
