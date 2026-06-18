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


def record_diagnosis(path: str, result: dict) -> None:
    """Best-effort: index a file the user just diagnosed. Never raises."""
    try:
        conn = _conn()
        try:
            library.upsert_project(
                conn, name=os.path.basename(path), source_path=path,
                source_family=result.get("family"), output_path=None,
                verdict=result.get("verdict"), score=result.get("score"),
                filament_count=result.get("filament_count"),
                last_action="doctor", updated_at=_now())
        finally:
            conn.close()
    except Exception:
        pass  # the library is an index; failing to record must not break /doctor


def record_conversion(path: str, result: dict) -> None:
    """Best-effort: index a successful conversion (verdict/family from a fresh
    read-only diagnosis of the source). Never raises."""
    try:
        try:
            diag = diagnose_path(path).to_dict()
        except Exception:
            diag = {}
        conn = _conn()
        try:
            library.upsert_project(
                conn, name=os.path.basename(path), source_path=path,
                source_family=diag.get("family"),
                output_path=result.get("output_path"),
                verdict=diag.get("verdict"), score=diag.get("score"),
                filament_count=diag.get("filament_count"),
                last_action="convert", updated_at=_now())
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
