"""U1 Printer Hub — read-only Moonraker client (spike).

The Snapmaker U1 runs stock Moonraker on :7125, LAN-trusted (no auth), mDNS
`U1.local` (see docs/design/PRINTER_HUB.md). This module talks to it **read-only**:
discover, connect, and read status / temperatures / toolheads / print state.

HARD CONSTRAINT: GET requests only. No uploads, no print start/stop, no config
or printer modification of any kind. Every function here is non-destructive.
"""
from __future__ import annotations
import json
import urllib.request

DEFAULT_PORT = 7125
SCHEMA_VERSION = "printer/1"
# 4 toolheads on the U1 (klipper extruder objects).
_TOOLHEAD_OBJECTS = ["extruder", "extruder1", "extruder2", "extruder3"]


def _get(host: str, port: int, path: str, timeout: float) -> dict:
    """Read-only HTTP GET against Moonraker. Raises on failure."""
    url = f"http://{host}:{port}{path}"
    req = urllib.request.Request(url, method="GET")  # explicit: never anything but GET
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def probe(host: str, port: int = DEFAULT_PORT, timeout: float = 2.0) -> dict:
    """Connect check via GET /server/info. Never raises — reports reachability."""
    try:
        res = _get(host, port, "/server/info", timeout).get("result", {})
        return {
            "reachable": True, "host": host, "port": port,
            "klippy_state": res.get("klippy_state"),
            "moonraker_version": res.get("moonraker_version"),
            "api_version": res.get("api_version_string"),
        }
    except Exception as e:
        return {"reachable": False, "host": host, "port": port, "error": str(e)}


def discover(hosts: list[str] | None = None, port: int = DEFAULT_PORT, timeout: float = 1.5) -> list[dict]:
    """Probe candidate hosts (default the U1 mDNS name). Read-only."""
    candidates = hosts or ["U1.local", "snapmaker-u1.local"]
    return [probe(h, port, timeout) for h in candidates]


def status(host: str, port: int = DEFAULT_PORT, timeout: float = 3.0) -> dict:
    """Read-only live status: print state, bed + per-toolhead temperatures.
    GET /printer/objects/query only — no subscriptions are persisted, nothing written."""
    objs = "&".join(["print_stats", "heater_bed", "toolhead", "virtual_sdcard", *_TOOLHEAD_OBJECTS])
    st = _get(host, port, "/printer/objects/query?" + objs, timeout).get("result", {}).get("status", {})
    ps = st.get("print_stats", {}) or {}
    bed = st.get("heater_bed", {}) or {}
    toolheads = []
    for i, key in enumerate(_TOOLHEAD_OBJECTS):
        e = st.get(key)
        if isinstance(e, dict):
            toolheads.append({"index": i, "temperature": e.get("temperature"), "target": e.get("target")})
    return {
        "schema_version": SCHEMA_VERSION,
        "host": host, "port": port,
        "print_state": ps.get("state"),
        "filename": ps.get("filename") or None,
        "progress": (st.get("virtual_sdcard", {}) or {}).get("progress"),
        "bed": {"temperature": bed.get("temperature"), "target": bed.get("target")},
        "toolheads": toolheads,
    }
