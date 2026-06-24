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
    """Read-only live status: print state, progress, layers, bed + per-toolhead
    temperatures, live message and motion factors.
    GET /printer/objects/query only — no subscriptions are persisted, nothing written."""
    objs = "&".join(["print_stats", "heater_bed", "toolhead", "virtual_sdcard",
                     "display_status", "gcode_move", *_TOOLHEAD_OBJECTS])
    st = _get(host, port, "/printer/objects/query?" + objs, timeout).get("result", {}).get("status", {})
    ps = st.get("print_stats", {}) or {}
    bed = st.get("heater_bed", {}) or {}
    vsd = st.get("virtual_sdcard", {}) or {}
    disp = st.get("display_status", {}) or {}
    gmove = st.get("gcode_move", {}) or {}
    info = ps.get("info", {}) or {}
    toolheads = []
    for i, key in enumerate(_TOOLHEAD_OBJECTS):
        e = st.get(key)
        if isinstance(e, dict):
            toolheads.append({
                "index": i,
                "temperature": e.get("temperature"),
                "target": e.get("target"),
                "active": bool(e.get("target")),  # heating/holding => in use this job
            })
    return {
        "schema_version": SCHEMA_VERSION,
        "host": host, "port": port,
        "print_state": ps.get("state"),
        "filename": ps.get("filename") or None,
        "message": disp.get("message") or None,
        "progress": vsd.get("progress") if vsd.get("progress") is not None else disp.get("progress"),
        "print_duration_s": ps.get("print_duration"),
        "total_duration_s": ps.get("total_duration"),
        "filament_used_mm": ps.get("filament_used"),
        "current_layer": info.get("current_layer"),
        "total_layer": info.get("total_layer"),
        "speed_factor": gmove.get("speed_factor"),
        "extrude_factor": gmove.get("extrude_factor"),
        "bed": {"temperature": bed.get("temperature"), "target": bed.get("target")},
        "toolheads": toolheads,
    }


def _job_brief(j: dict) -> dict:
    return {
        "filename": j.get("filename"),
        "status": j.get("status"),
        "start_time": j.get("start_time"),
        "end_time": j.get("end_time"),
        "print_duration_s": j.get("print_duration"),
        "total_duration_s": j.get("total_duration"),
        "filament_used_mm": j.get("filament_used"),
    }


# Moonraker [history] job statuses that mean the print did not finish cleanly.
_FAILURE_STATES = {"error", "cancelled", "klippy_shutdown", "klippy_disconnect", "interrupted"}


def history(host: str, port: int = DEFAULT_PORT, limit: int = 20, timeout: float = 4.0) -> dict:
    """Read-only print history + failure observation via Moonraker [history].
    GET /server/history/list + /server/history/totals only."""
    listing = _get(host, port, f"/server/history/list?limit={int(limit)}&order=desc",
                   timeout).get("result", {})
    jobs = [_job_brief(j) for j in (listing.get("jobs") or [])]
    totals = _get(host, port, "/server/history/totals", timeout).get("result", {}).get("job_totals", {}) or {}
    failures = [j for j in jobs if (j.get("status") in _FAILURE_STATES)]
    return {
        "schema_version": SCHEMA_VERSION,
        "host": host, "port": port,
        "jobs": jobs,
        "failures": failures,
        "totals": {
            "total_jobs": totals.get("total_jobs"),
            "total_print_time_s": totals.get("total_print_time"),
            "total_time_s": totals.get("total_time"),
            "total_filament_used_mm": totals.get("total_filament_used"),
            "longest_print_s": totals.get("longest_print"),
        },
    }


def file_metadata(host: str, filename: str, port: int = DEFAULT_PORT, timeout: float = 4.0) -> dict:
    """Read-only gcode metadata the printer already extracted for a file — the slicer's
    OWN estimate (print time, filament grams/mm, layers, slicer, first-layer temps).
    GET /server/files/metadata only. This is data Studio otherwise can't have without
    slicing; here it's read straight from the open Moonraker stack.

    `available: False` (never raises) when the file isn't on the printer / has no metadata."""
    try:
        from urllib.parse import quote
        res = _get(host, port, "/server/files/metadata?filename=" + quote(filename), timeout).get("result", {}) or {}
    except Exception as e:
        return {"schema_version": SCHEMA_VERSION, "available": False, "filename": filename, "reason": str(e)}
    if not res:
        return {"schema_version": SCHEMA_VERSION, "available": False, "filename": filename}
    thumbs = res.get("thumbnails") or []
    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "filename": res.get("filename") or filename,
        "estimated_time_s": res.get("estimated_time"),
        "filament_total_mm": res.get("filament_total"),
        "filament_weight_g": res.get("filament_weight_total"),
        "filament_name": res.get("filament_name"),
        "filament_type": res.get("filament_type"),
        "layer_count": res.get("layer_count"),
        "layer_height": res.get("layer_height"),
        "first_layer_height": res.get("first_layer_height"),
        "object_height": res.get("object_height"),
        "first_layer_bed_temp": res.get("first_layer_bed_temp"),
        "first_layer_extr_temp": res.get("first_layer_extr_temp"),
        "nozzle_diameter": res.get("nozzle_diameter"),
        "slicer": res.get("slicer"),
        "slicer_version": res.get("slicer_version"),
        "thumbnail_count": len(thumbs),
    }


def diagnostics(host: str, port: int = DEFAULT_PORT, timeout: float = 3.0) -> dict:
    """Read-only health diagnostics: klippy state + message + Moonraker warnings.
    GET /printer/info + /server/info only. Never raises — reports what it can."""
    out: dict = {"schema_version": SCHEMA_VERSION, "host": host, "port": port}
    try:
        pi = _get(host, port, "/printer/info", timeout).get("result", {}) or {}
        out["klippy_state"] = pi.get("state")
        out["state_message"] = (pi.get("state_message") or "").strip() or None
        out["hostname"] = pi.get("hostname")
    except Exception as e:
        out["state_message"] = f"printer info unavailable: {e}"
    try:
        si = _get(host, port, "/server/info", timeout).get("result", {}) or {}
        out["warnings"] = si.get("warnings") or []
        out["failed_components"] = si.get("failed_components") or []
        out.setdefault("klippy_state", si.get("klippy_state"))
    except Exception:
        out.setdefault("warnings", [])
        out.setdefault("failed_components", [])
    out["healthy"] = (out.get("klippy_state") == "ready"
                      and not out.get("warnings") and not out.get("failed_components"))
    return out


def _matrix_stats(matrix: list) -> dict | None:
    """Reduce a probed Z matrix to insight stats (NOT a raw dump): overall range/std,
    central vs edge flatness, worst corner. All in mm."""
    rows = [r for r in matrix if isinstance(r, (list, tuple)) and r]
    if len(rows) < 2 or len(rows[0]) < 2:
        return None
    flat = [float(z) for r in rows for z in r]
    n = len(flat)
    lo, hi = min(flat), max(flat)
    mean = sum(flat) / n
    std = (sum((z - mean) ** 2 for z in flat) / n) ** 0.5
    nr, nc = len(rows), len(rows[0])
    # central block (inner half) vs the rest (edges).
    r0, r1 = nr // 4, nr - nr // 4
    c0, c1 = nc // 4, nc - nc // 4
    center = [float(rows[i][j]) for i in range(r0, max(r1, r0 + 1)) for j in range(c0, max(c1, c0 + 1))]
    center_range = (max(center) - min(center)) if center else (hi - lo)
    corners = [float(rows[0][0]), float(rows[0][-1]), float(rows[-1][0]), float(rows[-1][-1])]
    corner_spread = max(corners) - min(corners)
    return {
        "range_mm": round(hi - lo, 3),
        "std_mm": round(std, 3),
        "max_dip_mm": round(lo - mean, 3),
        "max_peak_mm": round(hi - mean, 3),
        "center_range_mm": round(center_range, 3),
        "corner_spread_mm": round(corner_spread, 3),
        "rows": nr, "cols": nc,
    }


def bed_mesh(host: str, port: int = DEFAULT_PORT, timeout: float = 3.0) -> dict:
    """Read-only: the printer's REAL measured bed surface, reduced to flatness insight
    stats (not a raw matrix). GET /printer/objects/query?bed_mesh only. Never raises."""
    out: dict = {"schema_version": SCHEMA_VERSION, "host": host, "port": port, "available": False}
    try:
        bm = _get(host, port, "/printer/objects/query?bed_mesh", timeout) \
            .get("result", {}).get("status", {}).get("bed_mesh", {}) or {}
    except Exception as e:
        out["reason"] = str(e)
        return out
    matrix = bm.get("probed_matrix") or bm.get("mesh_matrix")
    stats = _matrix_stats(matrix) if matrix else None
    if not stats:
        out["reason"] = "no probed bed mesh on the printer (run a bed mesh calibration first)"
        out["profile_name"] = bm.get("profile_name") or None
        return out
    out.update({
        "available": True,
        "profile_name": bm.get("profile_name") or None,
        "mesh_min": bm.get("mesh_min"),
        "mesh_max": bm.get("mesh_max"),
        **stats,
    })
    return out


def capabilities(host: str, port: int = DEFAULT_PORT, timeout: float = 3.0) -> dict:
    """Read-only printer capabilities — the U1's REAL bed volume + toolhead count, so
    Design Intelligence can use the actual printer instead of assumed values.
    GET /printer/objects/list + /printer/objects/query?toolhead only."""
    objects = _get(host, port, "/printer/objects/list", timeout).get("result", {}).get("objects", []) or []
    toolhead_count = sum(1 for o in objects if o == "extruder" or (o.startswith("extruder") and o[8:].isdigit()))
    th = _get(host, port, "/printer/objects/query?toolhead", timeout).get("result", {}).get("status", {}).get("toolhead", {}) or {}
    amax = th.get("axis_maximum")   # klipper: [x, y, z, e]
    amin = th.get("axis_minimum")
    bed = None
    if isinstance(amax, (list, tuple)) and len(amax) >= 3:
        lo = amin if isinstance(amin, (list, tuple)) and len(amin) >= 3 else [0, 0, 0]
        bed = {"x": round(amax[0] - lo[0], 1), "y": round(amax[1] - lo[1], 1), "z": round(amax[2] - lo[2], 1)}
    return {
        "schema_version": SCHEMA_VERSION,
        "host": host, "port": port,
        "toolhead_count": toolhead_count or None,
        "bed_mm": bed,
        "klipper_objects": objects,   # raw object list — capability manifest for firmware_caps
    }


# ---------------------------------------------------------------------------
# Printer Hub Phase B — CONTROL (user-initiated only).
#
# These functions issue Moonraker POSTs that move the machine. They are ONLY ever
# called from an explicit, user-confirmed action in the Studio UI (start/pause/
# resume/cancel/upload/emergency-stop). Nothing here runs automatically, on a
# timer, or as a side effect of monitoring. The UI is the safety gate: it must
# confirm start/cancel/emergency-stop before the corresponding function is called.
# LAN-trusted Moonraker (no auth) — same trust boundary as the read-only client.
# ---------------------------------------------------------------------------

def _post(host: str, port: int, path: str, timeout: float, body: bytes | None = None,
          content_type: str | None = None) -> dict:
    """User-initiated HTTP POST against Moonraker. Raises on failure."""
    url = f"http://{host}:{port}{path}"
    headers = {"Content-Type": content_type} if content_type else {}
    req = urllib.request.Request(url, data=body or b"", method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        try:
            return json.loads(raw) if raw else {"result": "ok"}
        except Exception:
            return {"result": "ok"}


def pause(host: str, port: int = DEFAULT_PORT, timeout: float = 60.0) -> dict:
    """Pause the running print (safe, reversible). POST /printer/print/pause."""
    return {"ok": True, "action": "pause", "result": _post(host, port, "/printer/print/pause", timeout).get("result")}


def resume(host: str, port: int = DEFAULT_PORT, timeout: float = 60.0) -> dict:
    """Resume a paused print. POST /printer/print/resume."""
    return {"ok": True, "action": "resume", "result": _post(host, port, "/printer/print/resume", timeout).get("result")}


def cancel(host: str, port: int = DEFAULT_PORT, timeout: float = 60.0) -> dict:
    """Cancel the running print (NOT reversible — UI must confirm). POST /printer/print/cancel."""
    return {"ok": True, "action": "cancel", "result": _post(host, port, "/printer/print/cancel", timeout).get("result")}


def start(host: str, filename: str, port: int = DEFAULT_PORT, timeout: float = 60.0) -> dict:
    """Start printing a gcode file ALREADY on the printer (UI must confirm + show the
    filename and a 'printer clear/loaded/ready' warning). POST /printer/print/start?filename=."""
    from urllib.parse import quote
    path = "/printer/print/start?filename=" + quote(filename.lstrip("/"))
    return {"ok": True, "action": "start", "filename": filename,
            "result": _post(host, port, path, timeout).get("result")}


def emergency_stop(host: str, port: int = DEFAULT_PORT, timeout: float = 60.0) -> dict:
    """Emergency stop — cut heaters + halt motion immediately (UI must confirm on a
    dedicated screen). Klipper then needs FIRMWARE_RESTART to recover.

    Uses the canonical Klipper ``M112`` via ``/printer/gcode/script`` rather than
    Moonraker's ``POST /printer/emergency_stop`` — hardware testing on a real Snapmaker
    U1 (firmware 1.4.1.6) showed the U1's Moonraker build returns 404 for
    ``/printer/emergency_stop``, while ``/printer/gcode/script`` is available. M112 is
    the underlying emergency-shutdown gcode and works across Klipper builds."""
    return {"ok": True, "action": "emergency_stop",
            "result": _post(host, port, "/printer/gcode/script?script=M112", timeout).get("result")}


def job_queue(host: str, port: int = DEFAULT_PORT, timeout: float = 3.0) -> dict:
    """Read-only: the Moonraker job queue (list + state). GET /server/job_queue/status."""
    res = _get(host, port, "/server/job_queue/status", timeout).get("result", {}) or {}
    jobs = res.get("queued_jobs", []) or []
    return {"queue_state": res.get("queue_state"),
            "jobs": [{"filename": j.get("filename"), "id": j.get("job_id")} for j in jobs],
            "count": len(jobs)}


def upload_gcode(host: str, file_path: str, port: int = DEFAULT_PORT, timeout: float = 60.0) -> dict:
    """Upload a sliced .gcode to the printer (user-initiated). POST multipart /server/files/upload.
    Only .gcode/.g files; the file is read from a local path the user chose."""
    import os
    name = os.path.basename(file_path)
    ext = os.path.splitext(name)[1].lower()
    if ext not in (".gcode", ".g", ".gco"):
        raise ValueError("only sliced gcode (.gcode/.g) can be uploaded to the printer")
    with open(file_path, "rb") as f:
        content = f.read()
    boundary = "----snapstudioupload"
    pre = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
           f"filename=\"{name}\"\r\nContent-Type: application/octet-stream\r\n\r\n").encode()
    post = f"\r\n--{boundary}--\r\n".encode()
    body = pre + content + post
    res = _post(host, port, "/server/files/upload", timeout, body=body,
                content_type=f"multipart/form-data; boundary={boundary}")
    item = res.get("item", {}) if isinstance(res, dict) else {}
    return {"ok": True, "action": "upload", "filename": name,
            "path": item.get("path", name), "size": len(content)}
