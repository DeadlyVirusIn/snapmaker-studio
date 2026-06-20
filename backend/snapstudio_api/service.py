"""Adapter functions — delegate to the pure engine, return JSON-ready dicts.

The adapter (not the pure engine) is where side effects live: wall-clock
timestamps and the on-disk library index. The engine stays pure and testable.
"""
from __future__ import annotations
import datetime
import os
import threading
import uuid
from snapstudio_core.doctor import diagnose_path
from snapstudio_core.convert import convert_to_u1
from snapstudio_core.diff import diff_projects
from snapstudio_core.container import ThreeMF
from snapstudio_core import library
from snapstudio_core.batch import run_batch

API_VERSION = "api/1"


# --- library index (local-first SQLite of what the user has opened) ----------

def _data_dir() -> str:
    base = os.environ.get("SNAPSTUDIO_DATA_DIR") or os.path.join(
        os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "SnapmakerStudio")
    os.makedirs(base, exist_ok=True)
    return base


def _db_path() -> str:
    return os.path.join(_data_dir(), "library.db")


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _conn():
    # One connection per request: ThreadingHTTPServer hands each request its own
    # thread, and SQLite connections must not be shared across threads.
    return library.connect(_db_path())


def health() -> dict:
    return {"status": "ok", "api_version": API_VERSION}


def doctor(path: str) -> dict:
    """Read-only U1 compatibility diagnosis for a file path. Never modifies the file."""
    return diagnose_path(path).to_dict()


def convert(path: str, out_dir: str | None = None) -> dict:
    """Make a file U1-ready and save it next to the source. Returns the result."""
    return convert_to_u1(path, out_dir).to_dict()


def diff(a: str, b: str) -> dict:
    """Compare two projects (read-only): what changed between A and B."""
    return diff_projects(ThreeMF.open(a), ThreeMF.open(b)).to_dict()


def insights(path: str) -> dict:
    """Rich read-only Project Intelligence (geometry, materials, readiness)."""
    from snapstudio_core.intelligence import project_info
    return project_info(path)


def report(path: str) -> dict:
    """Read-only Validation Center report: checks + preserved/changes/at-risk."""
    from snapstudio_core.validation_report import readiness_report
    return readiness_report(path)


def canonical(path: str) -> dict:
    """Read-only source-neutral view of a design (multi-ecosystem foundation)."""
    from snapstudio_core.canonical import to_canonical
    return to_canonical(path).to_dict()


def mesh(path: str) -> dict:
    """Read-only mesh diagnostics: integrity, overhang/supports, stability, volume."""
    from snapstudio_core.mesh_diagnostics import analyze
    return analyze(path)


def strategies() -> dict:
    """List the intent-based print strategies (read-only). Orca still slices."""
    from snapstudio_core.strategies import list_strategies
    return list_strategies()


def strategy_recommend(path: str) -> dict:
    """Recommend a print strategy from REAL design signals (read-only). Never fabricates
    duration, tool-change count, or purge volume."""
    from snapstudio_core import strategies as strat
    from snapstudio_core.intelligence import project_info
    info = project_info(path)
    signals = {
        "colors": info.get("colors"),
        "source_family": info.get("source_family"),
        "dimensions_mm": info.get("dimensions_mm"),
        "triangles": info.get("triangles"),
        "complexity": info.get("complexity"),
        "issues": info.get("issues"),
    }
    # Enrich with real mesh diagnostics when available (best-effort, read-only).
    try:
        from snapstudio_core.mesh_diagnostics import analyze as _mesh
        md = _mesh(path)
        if md.get("available"):
            signals["tip_risk"] = md["stability"]["tip_risk"]
            signals["supports_likely"] = md["overhang"]["supports_likely"]
    except Exception:
        pass
    rec = strat.recommend(signals)
    rec["signals"] = {k: signals[k] for k in ("colors", "source_family", "dimensions_mm", "complexity")}
    return rec


def printer_discover(hosts: list[str] | None = None) -> dict:
    """Read-only: probe candidate U1 hosts over Moonraker."""
    from snapstudio_core import moonraker
    return {"printers": moonraker.discover(hosts or None), "schema_version": "printer/1"}


def printer_status(host: str, port: int = 7125) -> dict:
    """Read-only: live U1 status (print state, bed + toolhead temps)."""
    from snapstudio_core import moonraker
    return moonraker.status(host, port)


def printer_history(host: str, port: int = 7125, limit: int = 20) -> dict:
    """Read-only: recent prints + failures + totals (Moonraker history)."""
    from snapstudio_core import moonraker
    return moonraker.history(host, port, limit)


def printer_file_metadata(host: str, filename: str, port: int = 7125) -> dict:
    """Read-only: the slicer's own estimates for a file on the printer (time, filament,
    layers, slicer) — extracted by Moonraker, no slicing done here."""
    from snapstudio_core import moonraker
    return moonraker.file_metadata(host, filename, port)


def printer_diagnostics(host: str, port: int = 7125) -> dict:
    """Read-only: klippy health + Moonraker warnings."""
    from snapstudio_core import moonraker
    return moonraker.diagnostics(host, port)


def printer_capabilities(host: str, port: int = 7125) -> dict:
    """Read-only: the U1's real bed volume + toolhead count."""
    from snapstudio_core import moonraker
    return moonraker.capabilities(host, port)


def printer_bed_mesh(host: str, port: int = 7125) -> dict:
    """Read-only: the printer's measured bed surface reduced to flatness insight stats."""
    from snapstudio_core import moonraker
    return moonraker.bed_mesh(host, port)


def first_layer(path: str, host: str | None = None, port: int = 7125) -> dict:
    """First-Layer Intelligence: fuse the design's footprint/stability with the printer's
    REAL measured bed (when a host is reachable) into plain-language first-layer findings.
    Read-only end to end. Works design-only when no printer is connected."""
    from snapstudio_core.mesh_diagnostics import analyze
    from snapstudio_core import first_layer as fl
    md = analyze(path)
    if not md.get("available"):
        return {"schema_version": fl.SCHEMA_VERSION, "available": False,
                "reason": "geometry unavailable", "bed_aware": False}
    bed = None
    bed_dim = 270.0
    if host:
        from snapstudio_core import moonraker
        bed = moonraker.bed_mesh(host, port)            # never raises
        try:
            caps = moonraker.capabilities(host, port)   # can raise when unreachable
            if caps.get("bed_mm") and caps["bed_mm"].get("x"):
                bed_dim = caps["bed_mm"]["x"]
        except Exception:
            pass
    out = fl.assess(md.get("footprint"), md.get("stability"), bed, bed_dim)
    out["available"] = True
    return out


def cost_estimate(path: str, price_per_kg: float = 20.0, currency: str = "$") -> dict:
    """Material Cost Estimation: real material weight (from mesh geometry) x the user's
    filament price. Read-only; returns unavailable when geometry has no weight."""
    from snapstudio_core.mesh_diagnostics import analyze
    from snapstudio_core import cost_estimate as ce
    md = analyze(path)
    grams = md.get("material_estimate_g") if md.get("available") else None
    return ce.estimate(grams, price_per_kg, currency, basis="design estimate (PLA)")


def cost_to_price(path: str, host: str | None = None, filename: str | None = None,
                  port: int = 7125, currency: str = "$", **factors) -> dict:
    """Cost-to-Price Intelligence: true cost (material + power + machine wear +
    labour + failed-print buffer) and a suggested selling price with margin.

    Weight + print time come from the slicer's OWN metadata already on the U1 when
    a host + filename are given (most accurate); otherwise the design's geometry
    estimate is used for weight and time is left unknown. Read-only; never raises."""
    from snapstudio_core import pricing
    grams = None
    print_hours = None
    basis = "design estimate (PLA)"
    if host and filename:
        from snapstudio_core import moonraker
        try:
            md = moonraker.file_metadata(host, filename, port)
            if md.get("available"):
                grams = md.get("filament_weight_g")
                secs = md.get("estimated_time_s")
                print_hours = (secs / 3600.0) if secs else None
                basis = "printer slicer metadata"
        except Exception:
            pass
    if grams is None:
        from snapstudio_core.mesh_diagnostics import analyze
        mdg = analyze(path)
        grams = mdg.get("material_estimate_g") if mdg.get("available") else None
    # Only forward known pricing factors; ignore unrelated keys defensively.
    allowed = {"price_per_kg", "power_w", "electricity_per_kwh", "machine_price",
               "machine_life_hours", "labor_hours", "labor_rate",
               "failure_rate_pct", "markup_pct", "marketplace_fee_pct"}
    kw = {k: float(v) for k, v in factors.items() if k in allowed and v is not None}
    return pricing.price(grams, print_hours, currency=currency, basis=basis, **kw)


def printer_failure_insights(host: str, port: int = 7125, limit: int = 50) -> dict:
    """Failure-Pattern Learning: read the printer's OWN Moonraker history and surface
    failure patterns (rate, repeat-offender files, dominant cause, recent streak) as
    plain-language insight. Read-only; never raises on an empty/unreachable history."""
    from snapstudio_core import moonraker
    from snapstudio_core import failure_patterns as fp
    hist = moonraker.history(host, port, limit)
    return fp.assess(hist.get("jobs"), hist.get("totals"))


def batch_pricing(paths: list[str], currency: str = "$", **factors) -> dict:
    """Business Mode: price every part in a batch and roll them into one P&L —
    total cost, total suggested price, total profit across the whole job. Reuses
    cost_to_price per part (geometry weight); read-only; never raises on one part."""
    from snapstudio_core import pricing
    priced = []
    for p in (paths or []):
        try:
            priced.append(cost_to_price(p, currency=currency, **factors))
        except Exception:
            priced.append({"available": False})
    return pricing.aggregate(priced)


def mm_doctor(path: str, host: str | None = None, port: int = 7125) -> dict:
    """Multi-Material Doctor: one verdict for a multicolour U1 print — colours vs
    toolheads, filament-settings consistency, painted-region mapping. Uses the
    connected U1's real toolhead count when reachable, else the U1's 4. Read-only."""
    from snapstudio_core.intelligence import project_info
    from snapstudio_core import mm_doctor as mmd
    info = project_info(path)
    issues = info.get("issues") or []
    metadata_issues = [i for i in issues if "filament metadata inconsistent" in str(i)]
    heads = None
    heads_known = False
    if host:
        from snapstudio_core import moonraker
        try:
            caps = moonraker.capabilities(host, port)
            if caps.get("toolhead_count"):
                heads, heads_known = caps["toolhead_count"], True
        except Exception:
            pass
    return mmd.assess(info.get("colors"), heads=heads, heads_known=heads_known,
                      painted=bool(info.get("painted")), metadata_issues=metadata_issues,
                      object_count=info.get("objects") or 1)


def bed_fit(path: str, host: str | None = None, port: int = 7125) -> dict:
    """Bed-Fit / Out-of-Bounds Doctor: does the model fit the U1 bed, and if not,
    WHY (the cryptic 'out of bounds' error) and HOW to fix it. Uses the connected
    U1's real bed when reachable, else the known U1 bed. Read-only; works offline."""
    from snapstudio_core.intelligence import project_info
    from snapstudio_core import bed_fit as bf
    info = project_info(path)
    dims = info.get("dimensions_mm")
    object_count = info.get("objects") or 1
    multi = (info.get("colors") or 0) > 1
    bed = None
    bed_known = False
    if host:
        from snapstudio_core import moonraker
        try:
            caps = moonraker.capabilities(host, port)
            bm = caps.get("bed_mm")
            if bm and bm.get("x"):
                bed, bed_known = bm, True
        except Exception:
            pass
    return bf.assess(dims, bed=bed, bed_known=bed_known,
                     object_count=object_count, multi_material=multi)


def predict_success(path: str, host: str | None = None, port: int = 7125) -> dict:
    """Print Success Prediction: synthesise design readiness + toolhead fit +
    first-layer risk + (when a printer is reachable) its health score and this
    file's prior-failure count into one pre-print likelihood. Read-only; the
    printer-side signals are simply skipped when no host is given."""
    from snapstudio_core import success_predict as sp
    from snapstudio_core.validation_report import readiness_report
    import os
    readiness = toolfit = fl = health = None
    prior = 0
    try:
        readiness = readiness_report(path)
    except Exception:
        pass
    try:
        toolfit = toolhead_fit(path, host, port)
    except Exception:
        pass
    try:
        fl = first_layer(path, host, port)
    except Exception:
        pass
    if host:
        try:
            health = printer_health(host, port)
        except Exception:
            pass
        try:
            from snapstudio_core import moonraker
            base = os.path.basename(path).lower()
            hist = moonraker.history(host, port, 50)
            from snapstudio_core import failure_patterns as fp
            fa = fp.assess(hist.get("jobs"), hist.get("totals"))
            for ro in (fa.get("repeat_offenders") or []):
                if (ro.get("filename") or "").lower() == base:
                    prior = int(ro.get("failures") or 0)
        except Exception:
            pass
    return sp.predict(readiness=readiness, toolfit=toolfit, first_layer=fl,
                      health=health, prior_failures=prior)


def pricing_doctor(path: str, host: str | None = None, filename: str | None = None,
                   port: int = 7125, currency: str = "$", **factors) -> dict:
    """Pricing Doctor: hobby / marketplace / premium selling prices for a print,
    built on the Cost Doctor's true cost. Read-only."""
    from snapstudio_core import pricing
    cost = cost_to_price(path, host, filename, port, currency, **factors)
    if not cost.get("available"):
        return {"schema_version": "pricing/1", "available": False,
                "reason": cost.get("reason", "no cost available")}
    fee = float(factors.get("marketplace_fee_pct") or 0.0)
    out = pricing.tiers(cost.get("true_cost"), currency=currency, marketplace_fee_pct=fee)
    out["true_cost_basis"] = cost.get("basis")
    return out


def profit_doctor(path: str, host: str | None = None, filename: str | None = None,
                  port: int = 7125, currency: str = "$", prints_per_month: int = 20,
                  fixed_cost: float | None = None, batch_count: int = 10,
                  **factors) -> dict:
    """Profit Doctor: profit per print, margin, batch, monthly projection and
    break-even — built on the Cost Doctor's cost and suggested price. Read-only."""
    from snapstudio_core import pricing
    cost = cost_to_price(path, host, filename, port, currency, **factors)
    if not cost.get("available"):
        return {"schema_version": "pricing/1", "available": False,
                "reason": cost.get("reason", "no cost available")}
    fc = fixed_cost if fixed_cost is not None else float(factors.get("machine_price") or 0) or None
    return pricing.profit_analysis(
        cost.get("true_cost"), cost.get("suggested_price"), currency=currency,
        prints_per_month=prints_per_month, fixed_cost=fc, batch_count=batch_count)


def printer_firmware(host: str, port: int = 7125) -> dict:
    """Firmware Capability Intelligence: interpret the U1's OWN klipper object list
    into a plain-language capability set (mesh, input shaping, runout, exclusion,
    custom macros, multi-toolhead) and flag extended firmware. Read-only."""
    from snapstudio_core import moonraker, firmware_caps as fwc
    caps = moonraker.capabilities(host, port)
    return fwc.interpret(caps.get("klipper_objects"), caps.get("toolhead_count"),
                         caps.get("bed_mm"))


def intelligence_report(path: str, host: str | None = None, filename: str | None = None,
                        port: int = 7125, currency: str = "$", **factors) -> dict:
    """Studio Intelligence Report: run every Doctor and synthesise one verdict —
    Studio score, will-it-print, cost, price, profit, biggest risk, next action,
    with each Doctor as supporting evidence. Read-only; one failing Doctor never
    sinks the report."""
    from snapstudio_core import intelligence_report as ir

    def _safe(fn, *a, **kw):
        try:
            return fn(*a, **kw)
        except Exception:
            return None

    predict = _safe(predict_success, path, host, port)
    bed = _safe(bed_fit, path, host, port)
    mm = _safe(mm_doctor, path, host, port)
    fl = _safe(first_layer, path, host, port)
    health = _safe(printer_health, host, port) if host else None
    cost = _safe(cost_to_price, path, host, filename, port, currency, **factors)
    pricing = _safe(pricing_doctor, path, host, filename, port, currency, **factors)
    profit = _safe(profit_doctor, path, host, filename, port, currency=currency, **factors)
    return ir.build(predict=predict, bed_fit=bed, mm=mm, first_layer=fl,
                    health=health, cost=cost, pricing=pricing, profit=profit)


def printer_health(host: str, port: int = 7125, limit: int = 50) -> dict:
    """Printer Health Score: fold the U1's OWN read-only signals — firmware/
    connectivity diagnostics + print-history failure patterns — into one 0–100
    score, a grade, and plain-language drivers. Read-only; never raises."""
    from snapstudio_core import moonraker, failure_patterns as fp, health_score as hs
    diag = None
    fail = None
    try:
        diag = moonraker.diagnostics(host, port)
    except Exception:
        pass
    try:
        hist = moonraker.history(host, port, limit)
        fail = fp.assess(hist.get("jobs"), hist.get("totals"))
    except Exception:
        pass
    return hs.score(diagnostics=diag, failures=fail)


def toolhead_fit(path: str, host: str | None = None, port: int = 7125) -> dict:
    """Toolhead-Fit Intelligence: does the design's colour count fit the U1's toolheads?
    Uses the printer's REAL toolhead count when a host is reachable, else the U1's known 4.
    Read-only end to end; works offline (printer-unaware) when no host is given."""
    from snapstudio_core.intelligence import project_info
    from snapstudio_core import toolhead_fit as tf
    info = project_info(path)
    colors = info.get("colors")
    heads = None
    known = False
    if host:
        from snapstudio_core import moonraker
        try:
            caps = moonraker.capabilities(host, port)   # can raise when unreachable
            if caps.get("toolhead_count"):
                heads = caps["toolhead_count"]
                known = True
        except Exception:
            pass
    return tf.assess(colors, heads, known)


def library_list(query: str = "", tag: str | None = None) -> dict:
    """List indexed projects, newest first. Optional name search / tag filter."""
    conn = _conn()
    try:
        rows = (library.search_projects(conn, query, tag)
                if (query or tag) else library.list_projects(conn))
        return {"projects": rows, "count": len(rows), "schema_version": "library/1"}
    finally:
        conn.close()


def library_delete(project_id: int) -> dict:
    """Remove a project from the index. Does NOT touch the user's files."""
    conn = _conn()
    try:
        library.delete_project(conn, int(project_id))
        return {"deleted": int(project_id)}
    finally:
        conn.close()


def library_history(project_id: int) -> dict:
    """Workflow timeline for one project, newest first (read-only)."""
    conn = _conn()
    try:
        events = library.get_history(conn, int(project_id))
        return {"project_id": int(project_id), "events": events, "schema_version": "history/1"}
    finally:
        conn.close()


def record_diagnosis(path: str, result: dict) -> None:
    """Best-effort: index a file the user just diagnosed + log a history event. Never raises."""
    try:
        conn = _conn()
        try:
            pid = library.upsert_project(
                conn, name=os.path.basename(path), source_path=path,
                source_family=result.get("family"), output_path=None,
                verdict=result.get("verdict"), score=result.get("score"),
                filament_count=result.get("filament_count"),
                last_action="doctor", updated_at=_now())
            library.add_history(conn, pid, "doctor",
                                f"Checked — {result.get('verdict', '')}".strip(" —"), _now())
        finally:
            conn.close()
    except Exception:
        pass  # the library is an index; failing to record must not break /doctor


def record_conversion(path: str, result: dict) -> None:
    """Best-effort: index a successful conversion + log a history event. Never raises."""
    try:
        try:
            diag = diagnose_path(path).to_dict()
        except Exception:
            diag = {}
        conn = _conn()
        try:
            pid = library.upsert_project(
                conn, name=os.path.basename(path), source_path=path,
                source_family=diag.get("family"),
                output_path=result.get("output_path"),
                verdict=diag.get("verdict"), score=diag.get("score"),
                filament_count=diag.get("filament_count"),
                last_action="convert", updated_at=_now())
            library.add_history(conn, pid, "convert",
                                f"Made U1-ready — {result.get('output_name', '')}".strip(" —"), _now())
        finally:
            conn.close()
    except Exception:
        pass


def _convert_and_record(path: str, out_dir: str | None = None) -> dict:
    """Convert one file and index it. Used by the batch worker so batched
    conversions land in the library exactly like single ones."""
    result = convert(path, out_dir)
    record_conversion(path, result)
    return result


# --- batch jobs (background queue) -------------------------------------------
# A job runs in a daemon thread and publishes progress snapshots into _jobs.
# Clients start a job, then poll batch_status(job_id) until finished.

_jobs: dict[str, dict] = {}
_jobs_lock = threading.Lock()
_JOBS_MAX = 32  # cap retained jobs; the sidecar can run for days


def _prune_jobs_locked() -> None:
    """Evict oldest *finished* jobs so _jobs can't grow without bound. Running
    jobs are always kept. Caller must hold _jobs_lock."""
    if len(_jobs) <= _JOBS_MAX:
        return
    finished = [k for k, v in _jobs.items() if v["status"] in ("done", "error")]
    for k in finished[: len(_jobs) - _JOBS_MAX]:  # dict preserves insertion order
        _jobs.pop(k, None)


def batch_start(paths: list[str], out_dir: str | None = None) -> dict:
    """Kick off a batch conversion in the background. Returns a job handle."""
    if not paths:
        raise ValueError("no paths to convert")
    job_id = uuid.uuid4().hex
    with _jobs_lock:
        _prune_jobs_locked()
        _jobs[job_id] = {"id": job_id, "status": "running", "error": None, "result": None}

    def on_item(res) -> None:
        with _jobs_lock:
            _jobs[job_id]["result"] = res.to_dict()

    def worker() -> None:
        try:
            run_batch(paths, _convert_and_record, out_dir, on_item)
            with _jobs_lock:
                _jobs[job_id]["status"] = "done"
        except Exception as e:  # the orchestrator shouldn't raise, but be safe
            with _jobs_lock:
                _jobs[job_id]["status"] = "error"
                _jobs[job_id]["error"] = str(e)

    threading.Thread(target=worker, daemon=True).start()
    return {"job_id": job_id, "total": len(paths), "schema_version": "batch/1"}


def batch_status(job_id: str) -> dict | None:
    """Current snapshot of a job, or None if the id is unknown."""
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        # shallow copy; result dict is already rebuilt fresh on each on_item
        return {"id": job["id"], "status": job["status"],
                "error": job["error"], "result": job["result"]}
