"""Notice the sliced job coming back, without watching the whole machine.

The workflow had one manual step left in it: after Snapmaker Orca sliced the
prepared copy, the user had to find the `.gcode` and hand it back to Studio. That
step is where the loop stopped feeling like one thing.

This closes it, deliberately narrowly:

* **One folder, chosen by the user.** Their slicer's export folder, picked once.
  Not the whole disk, not the home directory, and nothing is watched until they
  say so.
* **Polled, not daemonised.** The engine answers requests; it does not run
  background threads that touch the filesystem while nobody is looking. The app
  asks "anything new?" while the user is on the page that cares.
* **Only complete files.** A G-code file being written grows for as long as the
  slicer is exporting it. A candidate is offered only once its size has stopped
  changing and it ends the way a finished job ends.
* **Nothing leaves the machine**, and nothing is modified: this reads sizes,
  timestamps and file ends.

Which project a job belongs to is not decided here — `provenance.py` weighs that,
and an ambiguous answer is shown to the user rather than resolved by guessing.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

SCHEMA_VERSION = "watch/1"


def _limit(name: str, default: int) -> int:
    try:
        value = int(os.environ.get(name, ""))
    except ValueError:
        return default
    return value if value > 0 else default


#: How many files to consider. A slicer's output folder can hold hundreds of old
#: jobs; the interesting ones are always the newest.
MAX_CANDIDATES = _limit("SNAPSTUDIO_WATCH_MAX", 12)

#: Ignore anything older than this. A job sliced last week is not the one that
#: just came out of Orca.
MAX_AGE_SECONDS = _limit("SNAPSTUDIO_WATCH_MAX_AGE", 24 * 60 * 60)

#: A file whose size changed within this window is still being written.
SETTLE_SECONDS = _limit("SNAPSTUDIO_WATCH_SETTLE", 2)

SUFFIXES = (".gcode", ".gco", ".g")


def _looks_finished(path: Path) -> tuple[bool, str]:
    """Has the slicer finished writing this?

    Two independent signals, because either alone is wrong. A file can stop
    growing because the slicer stalled, and a file can contain an end marker in
    the middle if a previous export was overwritten in place.
    """
    try:
        first = path.stat().st_size
    except OSError as exc:
        return False, f"could not read it: {exc.strerror or exc}"
    if first == 0:
        return False, "the file is empty"

    time.sleep(min(SETTLE_SECONDS, 3))
    try:
        second = path.stat().st_size
    except OSError:
        return False, "the file disappeared while Studio looked at it"
    if second != first:
        return False, "still being written"

    try:
        with path.open("rb") as handle:
            handle.seek(max(0, second - 4096))
            tail = handle.read().decode("utf-8", errors="replace")
    except OSError as exc:
        return False, f"could not read the end of it: {exc.strerror or exc}"

    finished = any(marker in tail for marker in
                   ("CONFIG_BLOCK_END", "PRINT_END", "End of Gcode", "total filament used",
                    "estimated printing time"))
    return (True, "complete") if finished else (False, "the end of the file is missing — "
                                                       "the slicer may still be writing it")


def scan(folder: str | Path, *, since: float | None = None,
         limit: int | None = None) -> dict:
    """List complete, recent sliced jobs in one folder. Never raises."""
    target = Path(folder) if folder else None
    out: dict = {
        "schema_version": SCHEMA_VERSION,
        "available": False,
        "folder": str(target) if target else None,
        "candidates": [],
    }
    if not target:
        out["error"] = "no folder chosen"
        return out
    if not target.exists() or not target.is_dir():
        out["error"] = "that folder does not exist"
        return out

    cutoff = since if since is not None else time.time() - MAX_AGE_SECONDS
    try:
        entries = [p for p in target.iterdir()
                   if p.is_file() and p.suffix.lower() in SUFFIXES]
    except OSError as exc:
        out["error"] = f"Studio could not read that folder: {exc.strerror or exc}"
        return out

    recent = []
    for path in entries:
        try:
            stat = path.stat()
        except OSError:
            continue
        if stat.st_mtime < cutoff:
            continue
        recent.append((stat.st_mtime, stat.st_size, path))
    recent.sort(reverse=True)

    out["available"] = True
    out["seen"] = len(entries)
    for modified, size, path in recent[:(limit or MAX_CANDIDATES)]:
        complete, why = _looks_finished(path)
        out["candidates"].append({
            "path": str(path),
            "name": path.name,
            "size_bytes": size,
            "modified": modified,
            "age_seconds": int(max(0, time.time() - modified)),
            "complete": complete,
            "state": why,
        })
    out["summary"] = _summary(out)
    return out


def match_project(folder: str | Path, project_path: str | None, *,
                  since: float | None = None, limit: int | None = None) -> dict:
    """Scan a folder and weigh each complete job against an open project."""
    from . import gcode, project_traits, provenance

    found = scan(folder, since=since, limit=limit)
    if not found.get("available"):
        return found

    traits = {}
    if project_path:
        try:
            traits = project_traits.extract(project_path)
        except Exception:
            traits = {}

    for candidate in found["candidates"]:
        if not candidate["complete"]:
            continue
        facts = gcode.read_facts(candidate["path"])
        candidate["job"] = {
            "slicer": facts.get("slicer"),
            "printer_model": facts.get("printer_model"),
            "layer_count": facts.get("layer_count"),
            "tools_used": facts.get("tools_used"),
            "total_g": (facts.get("filament") or {}).get("total_g"),
            "readable": facts.get("available", False),
        }
        if traits and facts.get("available"):
            candidate["provenance"] = provenance.compare(
                traits, facts,
                project_name=Path(project_path).name if project_path else None,
                gcode_name=candidate["name"])

    best = provenance.best_of(found["candidates"])
    found["best"] = best["path"] if best else None
    found["best_verdict"] = best["provenance"]["verdict"] if best else None
    found["summary"] = _summary(found)
    return found


def _summary(found: dict) -> str:
    candidates = found.get("candidates") or []
    if not candidates:
        return "Nothing new in that folder yet. Slice in Snapmaker Orca and it will appear here."
    complete = [c for c in candidates if c["complete"]]
    writing = [c for c in candidates if not c["complete"]]
    if found.get("best"):
        name = next((c["name"] for c in candidates if c["path"] == found["best"]), "")
        verdict = found.get("best_verdict")
        word = "is" if verdict == "confirmed" else "looks like"
        return f"{name} {word} the sliced version of your project."
    bits = []
    if complete:
        bits.append(f"{len(complete)} finished job(s)")
    if writing:
        bits.append(f"{len(writing)} still being written")
    text = " and ".join(bits)
    return (text[:1].upper() + text[1:] +
            ". None of them could be tied to your project, so pick the right one yourself.")
