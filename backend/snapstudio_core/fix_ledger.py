"""Fix ledger — a record of everything Studio changed, and the way back.

Studio's promise is Diagnose → Explain → Fix → Validate → Undo. The first four
existed; the last one did not, because "undo" was scattered across three
different places and mostly meant "find the original file yourself".

This module holds one record per Studio-generated file: what was done, what
triggered it, every change with its old and new value and reason, whether the
result validated, and the original the work came from.

Undo is deliberately not a version-control system. The original is immutable —
Studio never writes to it — so returning to it means pointing the workflow back
at a file that has been sitting there untouched the whole time. That is safer
than trying to reverse a prepared file's edits, and a user can understand it.

**Paths.** The full source and output paths are needed locally to reopen a file,
and are exactly what must not travel in a shared diagnostic. Every entry
therefore carries a `local` block with the real paths and a shareable body with
only file names, so `export_entry()` can hand out the record without leaking
someone's directory layout, user name or drive.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

SCHEMA_VERSION = "fixledger/1"

# Keep the ledger small and predictable: this is a record of recent work, not an
# archive. Older entries fall off the end.
MAX_ENTRIES = 200

LEDGER_FILE = "fix-ledger.json"

# Operations Studio records. Anything writing a file should name itself here so
# the ledger reads as a list of actions rather than a list of file paths.
PREPARE = "prepare_u1_copy"
PLACEMENT = "move_onto_plate"
SCALE = "prepare_scaled_copy"
PLATE_REMAP = "plate_colour_remap"

_TITLES = {
    PREPARE: "Prepared a U1 copy",
    PLACEMENT: "Moved the objects onto the plate",
    SCALE: "Made a resized copy",
    PLATE_REMAP: "Changed a plate's colours",
}


def title_for(operation: str) -> str:
    return _TITLES.get(operation, operation.replace("_", " ").capitalize())


def ledger_path(data_dir: str | os.PathLike) -> Path:
    return Path(data_dir) / LEDGER_FILE


def _load(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    entries = data.get("entries") if isinstance(data, dict) else data
    return entries if isinstance(entries, list) else []


def _save(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": SCHEMA_VERSION, "entries": entries[:MAX_ENTRIES]}
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def build_entry(*, operation: str, source: str, output: str, timestamp: str,
                changes: list[dict] | None = None, findings: list[dict] | None = None,
                validated: bool | None = None, engine_version: str | None = None,
                notes: list[str] | None = None) -> dict:
    """One ledger entry. Full paths live only in `local`."""
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": operation,
        "title": title_for(operation),
        "timestamp": timestamp,
        "source_name": Path(source).name if source else None,
        "output_name": Path(output).name if output else None,
        "changes": list(changes or []),
        "findings": list(findings or []),
        "validated": validated,
        "engine_version": engine_version,
        "notes": list(notes or []),
        # Not shareable: these are the user's own directory layout.
        "local": {"source_path": source, "output_path": output},
    }


def record(data_dir: str | os.PathLike, entry: dict) -> dict:
    """Add an entry, newest first. Never raises — a ledger failure must not fail
    the fix the user actually asked for."""
    try:
        path = ledger_path(data_dir)
        entries = _load(path)
        out = (entry.get("local") or {}).get("output_path")
        if out:
            # One record per produced file: re-running a fix replaces its entry
            # rather than stacking duplicates.
            entries = [e for e in entries if (e.get("local") or {}).get("output_path") != out]
        entries.insert(0, entry)
        _save(path, entries)
    except Exception:
        pass
    return entry


def entries(data_dir: str | os.PathLike, source: str | None = None,
            limit: int = 50) -> list[dict]:
    """Recent entries, newest first. With `source`, only what came from that file."""
    found = _load(ledger_path(data_dir))
    if source:
        target = os.path.normcase(os.path.abspath(source))
        found = [e for e in found
                 if os.path.normcase(os.path.abspath(
                     (e.get("local") or {}).get("source_path") or "")) == target]
    return found[:max(0, limit)]


def latest_for_output(data_dir: str | os.PathLike, output: str) -> dict | None:
    target = os.path.normcase(os.path.abspath(output))
    for entry in _load(ledger_path(data_dir)):
        if os.path.normcase(os.path.abspath(
                (entry.get("local") or {}).get("output_path") or "")) == target:
            return entry
    return None


def export_entry(entry: dict) -> dict:
    """The same record with the local paths removed, for sharing in a bug report."""
    shareable = {k: v for k, v in entry.items() if k != "local"}
    shareable["paths_removed"] = True
    return shareable


def export_all(data_dir: str | os.PathLike, limit: int = 50) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "entries": [export_entry(e) for e in entries(data_dir, limit=limit)],
        "note": ("File locations are deliberately omitted so this can be shared in a "
                 "bug report."),
    }


def original_for(data_dir: str | os.PathLike, output: str) -> dict:
    """Where to go back to, and whether it is still there.

    Returning to the original never touches a file: the original was never
    written to, so this is a matter of pointing the workflow back at it.
    """
    entry = latest_for_output(data_dir, output)
    if not entry:
        return {"available": False,
                "reason": "Studio has no record of how this file was made."}
    source = (entry.get("local") or {}).get("source_path")
    if not source:
        return {"available": False,
                "reason": "Studio's record for this file does not name an original."}
    exists = os.path.exists(source)
    return {
        "available": exists,
        "source_path": source if exists else None,
        "source_name": entry.get("source_name"),
        "operation": entry.get("operation"),
        "title": entry.get("title"),
        "reason": None if exists else
        (f"The original ({entry.get('source_name')}) is no longer where Studio "
         "last saw it. It was never modified, so it is safe to open again from "
         "wherever you moved it."),
        "note": ("Your original was never modified. Going back to it just points "
                 "Studio at the untouched file — the copy stays on disk."),
    }
