"""Fidelity audit — what actually survived preparing a copy.

Every converter in this space tells a user the same thing: *converted*. None of
them tells the user what that cost. The interesting question is not "did it
work" — it is "what is different now, and what could not be carried over at all".

This module answers that by comparing the original project with the prepared copy
and classifying every element it can identify:

* ``preserved_exact``     — byte-identical
* ``preserved_semantic``  — the bytes moved but the meaning did not
* ``changed``             — deliberately different, with the reason
* ``removed``             — deliberately dropped, with the reason
* ``added``               — the prepared copy carries something new
* ``unsupported``         — data Studio does not understand well enough to judge
* ``unverified``          — Studio could not confirm either way

The last two categories are the point. A report that can only say "preserved" or
"changed" has to lie about the parts it does not understand, and those are
exactly the parts — Full Spectrum data, a slicer extension nobody has documented,
a vendor's private metadata — where a user most needs to know that nobody checked.

**Studio never claims nothing was lost unless this audit proves it for that
project.** ``claims`` at the end of the report is what public copy is allowed to
say, computed rather than asserted.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .container import ThreeMF
from .errors import UnsafeArchive

SCHEMA_VERSION = "fidelity/1"

PRESERVED_EXACT = "preserved_exact"
PRESERVED_SEMANTIC = "preserved_semantic"
CHANGED = "changed"
REMOVED = "removed"
ADDED = "added"
UNSUPPORTED = "unsupported"
UNVERIFIED = "unverified"

# Order for display: what a user needs to see first.
_ORDER = {UNVERIFIED: 0, UNSUPPORTED: 1, REMOVED: 2, CHANGED: 3,
          ADDED: 4, PRESERVED_SEMANTIC: 5, PRESERVED_EXACT: 6}

PROJECT_SETTINGS = "Metadata/project_settings.config"
MODEL_SETTINGS = "Metadata/model_settings.config"
SLICE_INFO = "Metadata/slice_info.config"
ROOT_MODEL = "3D/3dmodel.model"

_PLATE_GCODE_RE = re.compile(r"^Metadata/plate_\d+\.(gcode|json)$")
_PLATE_IMAGE_RE = re.compile(r"^Metadata/(plate|top|pick)_\d+.*\.png$")

# Parts Studio deliberately rewrites or drops, and why. Anything changed that is
# not in this table is reported as unverified rather than excused.
_INTENTIONAL = {
    PROJECT_SETTINGS: ("the U1 machine profile and Snapmaker Orca import fixes are "
                       "applied here"),
    SLICE_INFO: ("the authoring slicer's version stamp is blanked so Snapmaker Orca "
                 "does not refuse the project as newer than itself"),
    ROOT_MODEL: "object placement is rewritten only when a placement fix was applied",
}

_HUMAN = {
    "[Content_Types].xml": "Archive index",
    "_rels/.rels": "Archive relationships",
    "3D/_rels/3dmodel.model.rels": "Model relationships",
    PROJECT_SETTINGS: "Print settings",
    MODEL_SETTINGS: "Per-object settings and plate layout",
    SLICE_INFO: "Slicing summary recorded by the original slicer",
    ROOT_MODEL: "Model geometry and object placement",
}


def _row(element: str, status: str, *, detail: str, reason: str | None = None,
         part: str | None = None) -> dict:
    return {"element": element, "status": status, "detail": detail,
            "reason": reason, "part": part}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _human(part: str) -> str:
    if part in _HUMAN:
        return _HUMAN[part]
    if _PLATE_GCODE_RE.match(part):
        return "Sliced output from the original printer"
    if _PLATE_IMAGE_RE.match(part):
        return "Plate picture"
    if part.startswith("3D/Textures/"):
        return "Texture image"
    if part.startswith("3D/Objects/"):
        return "Mesh data"
    if part.startswith("Auxiliaries/"):
        return "Extra files packaged with the project"
    return part


def _json_or_none(tm: ThreeMF, part: str):
    if not tm.has_part(part):
        return None
    try:
        return json.loads(tm.read_part(part).decode("utf-8", "ignore"))
    except Exception:
        return None


def _text(tm: ThreeMF, part: str) -> str:
    if not tm.has_part(part):
        return ""
    try:
        return tm.read_part(part).decode("utf-8", "ignore")
    except Exception:
        return ""


# --- part-by-part -----------------------------------------------------------

def _classify_part(part: str, before: bytes, after: bytes | None,
                   placement_applied: bool) -> dict:
    name = _human(part)
    if after is None:
        if _PLATE_GCODE_RE.match(part):
            return _row(name, REMOVED, part=part,
                        detail="dropped from the prepared copy",
                        reason=("these toolpaths were generated for the original "
                                "printer, so Snapmaker Orca must slice again for the U1"))
        return _row(name, UNVERIFIED, part=part,
                    detail="present in the original, missing from the prepared copy",
                    reason="Studio cannot account for this — report it as a bug")
    if before == after:
        return _row(name, PRESERVED_EXACT, part=part,
                    detail="byte-for-byte identical")
    if part == ROOT_MODEL:
        return _model_part_row(part, before, after, placement_applied)
    if part in _INTENTIONAL:
        return _row(name, CHANGED, part=part, detail="rewritten by Studio",
                    reason=_INTENTIONAL[part])
    if part.startswith("3D/Objects/"):
        return _row(name, UNVERIFIED, part=part,
                    detail="mesh data differs and Studio did not intend to change it",
                    reason="Studio does not rewrite mesh parts — report this as a bug")
    return _row(name, UNVERIFIED, part=part, detail="content differs",
                reason="Studio has no rule that should have changed this part")


_VERTEX_RE = re.compile(rb"<vertex\b")
_TRIANGLE_RE = re.compile(rb"<triangle\b")
_ITEM_RE = re.compile(rb"<item\b")
_PAINT_RE = re.compile(rb"paint_color|paint_supports|mmu_segmentation|paint_seam")


def _model_part_row(part: str, before: bytes, after: bytes,
                    placement_applied: bool) -> dict:
    """The root model changes only when placement was rewritten. Geometry itself
    must be identical either way, and that is checked rather than assumed."""
    counts_before = (len(_VERTEX_RE.findall(before)), len(_TRIANGLE_RE.findall(before)),
                     len(_ITEM_RE.findall(before)), len(_PAINT_RE.findall(before)))
    counts_after = (len(_VERTEX_RE.findall(after)), len(_TRIANGLE_RE.findall(after)),
                    len(_ITEM_RE.findall(after)), len(_PAINT_RE.findall(after)))
    if counts_before != counts_after:
        return _row(_human(part), UNVERIFIED, part=part,
                    detail=(f"vertices/triangles/objects/painted markers went from "
                            f"{counts_before} to {counts_after}"),
                    reason="Studio does not add or remove geometry — report this as a bug")
    if placement_applied:
        return _row(_human(part), CHANGED, part=part,
                    detail="the same geometry, moved to different coordinates",
                    reason="a placement fix moved the objects onto the U1 plate")
    return _row(_human(part), PRESERVED_SEMANTIC, part=part,
                detail="the same geometry, re-serialised",
                reason="the mesh, object count and painted markers are unchanged")


# --- semantic elements ------------------------------------------------------

def _settings_row(before: dict | None, after: dict | None) -> list[dict]:
    if before is None or after is None:
        return [_row("Print settings", UNVERIFIED,
                     detail="one of the projects has no readable print settings")]
    changed = sorted(k for k in set(before) & set(after)
                     if before[k] != after[k])
    kept = sum(1 for k in before if k in after and after[k] == before[k])
    dropped = sorted(k for k in before if k not in after)
    added = sorted(k for k in after if k not in before)
    rows = [_row("Print settings kept", PRESERVED_EXACT,
                 detail=f"{kept} setting(s) carried over unchanged")]
    if changed:
        rows.append(_row("Print settings changed", CHANGED,
                         detail=f"{len(changed)} setting(s) differ: "
                                + ", ".join(changed[:8])
                                + (" …" if len(changed) > 8 else ""),
                         reason=("U1 machine profile, Snapmaker Orca import fixes, or "
                                 "Studio-recommended settings if you chose them")))
    if dropped:
        rows.append(_row("Print settings not carried over", REMOVED,
                         detail=f"{len(dropped)} setting(s): " + ", ".join(dropped[:8])
                                + (" …" if len(dropped) > 8 else ""),
                         reason=("these belong to the original printer and have no "
                                 "meaning on a U1")))
    if added:
        rows.append(_row("Print settings added", ADDED,
                         detail=f"{len(added)} setting(s): " + ", ".join(added[:8])
                                + (" …" if len(added) > 8 else ""),
                         reason="required by the U1 profile"))
    return rows


def _count_row(label: str, before: int, after: int, *, unchanged_reason: str,
               changed_reason: str) -> dict:
    if before == after:
        return _row(label, PRESERVED_EXACT, detail=f"{before} before and after",
                    reason=unchanged_reason)
    return _row(label, CHANGED, detail=f"{before} → {after}", reason=changed_reason)


def _semantic_rows(a: ThreeMF, b: ThreeMF) -> list[dict]:
    from .fingerprint import compute_fingerprint

    rows: list[dict] = []
    try:
        fa, fb = compute_fingerprint(a), compute_fingerprint(b)
    except Exception:
        return [_row("Objects, plates and colours", UNVERIFIED,
                     detail="Studio could not read one of the projects well enough to compare")]

    rows.append(_count_row("Objects", fa.object_count, fb.object_count,
                           unchanged_reason="every object in the original is in the copy",
                           changed_reason="Studio does not add or remove objects — "
                                          "report this as a bug"))
    painted_a = sum(fa.painted_triangles.values())
    painted_b = sum(fb.painted_triangles.values())
    rows.append(_count_row("Painted colour and support marks", painted_a, painted_b,
                           unchanged_reason="painted regions are untouched",
                           changed_reason="Studio does not repaint models — "
                                          "report this as a bug"))
    rows.append(_count_row("Filament slots", fa.filament_count, fb.filament_count,
                           unchanged_reason="every colour slot survives, in its original order",
                           changed_reason="a filament remap was applied"))
    if fa.filament_colors and fb.filament_colors:
        if tuple(fa.filament_colors) == tuple(fb.filament_colors):
            rows.append(_row("Filament colours", PRESERVED_EXACT,
                             detail=f"{len(fa.filament_colors)} colour(s), same values in "
                                    "the same order"))
        else:
            rows.append(_row("Filament colours", CHANGED,
                             detail="the colour list differs",
                             reason="a filament remap or preset normalisation was applied"))

    # Per-object records: plate assignment, tool assignment, per-object overrides.
    ms_a, ms_b = _text(a, MODEL_SETTINGS), _text(b, MODEL_SETTINGS)
    if ms_a and ms_b:
        plates_a = len(re.findall(r"<plate\b", ms_a))
        plates_b = len(re.findall(r"<plate\b", ms_b))
        rows.append(_count_row("Plates", plates_a, plates_b,
                               unchanged_reason="the plate layout is unchanged",
                               changed_reason="Studio does not add or remove plates — "
                                              "report this as a bug"))
        extruders_a = re.findall(r'key="extruder"\s+value="(\d+)"', ms_a)
        extruders_b = re.findall(r'key="extruder"\s+value="(\d+)"', ms_b)
        if extruders_a == extruders_b:
            rows.append(_row("Which colour each object uses", PRESERVED_EXACT,
                             detail=f"{len(extruders_a)} assignment(s) unchanged"))
        else:
            rows.append(_row("Which colour each object uses", CHANGED,
                             detail=f"{len(extruders_a)} → {len(extruders_b)} assignment(s) "
                                    "or different values",
                             reason="a plate colour remap was applied"))
    elif ms_a and not ms_b:
        rows.append(_row("Per-object settings and plate layout", REMOVED,
                         detail="present in the original, absent from the copy",
                         reason="Studio cannot account for this — report it as a bug"))
    return rows


# --- optional data other tools rely on --------------------------------------

_OPTIONAL = {
    "Metadata/layer_heights_profile.txt": "Variable layer height profile",
    "Metadata/custom_gcode_per_layer.xml": "Colour changes and pauses at set layers",
    "Metadata/layer_config_ranges.xml": "Per-height setting ranges",
    "Metadata/brim_ear_points.txt": "Brim ear positions",
    "Metadata/cut_information.xml": "Cut information",
    "Metadata/filament_sequence.json": "Filament sequence",
}


def _optional_rows(a: ThreeMF, b: ThreeMF) -> list[dict]:
    """Data a creator spent time on that a converter can silently drop."""
    rows = []
    for part, label in _OPTIONAL.items():
        in_a, in_b = a.has_part(part), b.has_part(part)
        if not in_a and not in_b:
            continue
        if in_a and not in_b:
            rows.append(_row(label, REMOVED, part=part,
                             detail="present in the original, absent from the copy",
                             reason="Studio did not intend to drop this — report it as a bug"))
        elif in_a and in_b:
            same = a.read_part(part) == b.read_part(part)
            rows.append(_row(label, PRESERVED_EXACT if same else UNVERIFIED, part=part,
                             detail="byte-for-byte identical" if same else "content differs",
                             reason=None if same else
                             "Studio has no rule that should have changed this"))
        else:
            rows.append(_row(label, ADDED, part=part,
                             detail="only in the prepared copy"))
    return rows


def _unsupported_rows(a: ThreeMF) -> list[dict]:
    """Anything the original declares that Studio does not understand.

    A required 3MF extension Studio has never seen means there may be data in the
    file it neither read nor checked, and saying so is the whole point of this
    report.
    """
    from . import project_traits

    rows = []
    head = _text(a, ROOT_MODEL)[:project_traits._MODEL_HEAD_BYTES]
    tag = re.search(r"<model\b[^>]*>", head, re.S)
    if tag:
        attrs = project_traits._attrs(tag.group(0))
        prefixes = [p for p in re.split(r"\s+", attrs.get("requiredextensions", "").strip()) if p]
        declared = {k.split(":", 1)[1]: v for k, v in attrs.items() if k.startswith("xmlns:")}
        unknown = [declared.get(p, p) for p in prefixes
                   if declared.get(p, p) not in project_traits._KNOWN_EXTENSIONS]
        if unknown:
            rows.append(_row("Slicer extensions Studio does not understand", UNSUPPORTED,
                             detail=", ".join(unknown),
                             reason=("this project requires a 3MF extension Studio has no "
                                     "reader for, so any data it carries was copied "
                                     "verbatim but never checked")))

    # PrusaSlicer stores several things Snapmaker Orca has no equivalent for. The
    # copy is still usable; saying which parts did not survive is the whole point
    # of this report, and it is better said here than discovered on the plate.
    rows.extend(_prusa_rows(a))
    return rows


def _prusa_rows(tm) -> list[dict]:
    from . import prusa

    try:
        parts = set(tm.list_parts())
        if prusa.SETTINGS_PART not in parts:
            return []
        settings_raw = tm.read_part(prusa.SETTINGS_PART)
        model_raw = tm.read_part(prusa.MODEL_CONFIG_PART) if prusa.MODEL_CONFIG_PART in parts else None
        summary = prusa.summarise(settings_raw, model_raw)
    except Exception:
        return []

    return [_row(item["element"], UNSUPPORTED, detail="from PrusaSlicer",
                 reason=item["reason"])
            for item in prusa.not_carried(summary)]


# --- entry point ------------------------------------------------------------

def audit(original: str, prepared: str) -> dict:
    """Compare an original project with a prepared copy. Never raises."""
    try:
        a = ThreeMF.open(original)
    except UnsafeArchive as e:
        return _unavailable(str(e))
    except Exception:
        return _unavailable("Studio could not open the original as a 3MF project.")
    try:
        b = ThreeMF.open(prepared)
    except UnsafeArchive as e:
        return _unavailable(str(e))
    except Exception:
        return _unavailable("Studio could not open the prepared copy as a 3MF project.")

    parts_a, parts_b = a.list_parts(), b.list_parts()
    set_b = set(parts_b)

    placement_applied = False
    if a.has_part(ROOT_MODEL) and b.has_part(ROOT_MODEL):
        placement_applied = _placement_moved(a.read_part(ROOT_MODEL), b.read_part(ROOT_MODEL))

    rows: list[dict] = []
    for part in parts_a:
        if part.endswith("/") or part == PROJECT_SETTINGS:
            continue
        after = b.read_part(part) if part in set_b else None
        rows.append(_classify_part(part, a.read_part(part), after, placement_applied))
    for part in parts_b:
        if part.endswith("/") or part in set(parts_a):
            continue
        rows.append(_row(_human(part), ADDED, part=part,
                         detail="only in the prepared copy",
                         reason="added while preparing the U1 copy"))

    rows += _settings_rows(a, b)
    rows += _semantic_rows(a, b)
    rows += _optional_rows(a, b)
    rows += _unsupported_rows(a)

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    ordered = sorted(rows, key=lambda r: (_ORDER[r["status"]], r["element"]))
    claims = _claims(counts)
    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "original": Path(original).name,
        "prepared": Path(prepared).name,
        "rows": ordered,
        "counts": counts,
        "kept": [r for r in ordered if r["status"] in (PRESERVED_EXACT, PRESERVED_SEMANTIC)],
        "changed": [r for r in ordered if r["status"] in (CHANGED, ADDED)],
        "not_carried": [r for r in ordered if r["status"] in (REMOVED, UNSUPPORTED)],
        "unverified": [r for r in ordered if r["status"] == UNVERIFIED],
        "claims": claims,
        "summary": _summary(counts, claims),
        "disclaimer": ("This compares what Studio can identify in both files. Anything it "
                       "could not identify is listed as unverified rather than assumed to "
                       "be fine."),
    }


def _settings_rows(a: ThreeMF, b: ThreeMF) -> list[dict]:
    return _settings_row(_json_or_none(a, PROJECT_SETTINGS), _json_or_none(b, PROJECT_SETTINGS))


def _placement_moved(before: bytes, after: bytes) -> bool:
    """True when the build-item transforms differ but nothing else about the
    geometry does — i.e. a placement fix ran."""
    grab = lambda raw: re.findall(rb'<item\b[^>]*transform="([^"]*)"', raw)
    return grab(before) != grab(after)


def _claims(counts: dict) -> dict:
    """What Studio is allowed to say about this project, computed not asserted."""
    nothing_unverified = counts.get(UNVERIFIED, 0) == 0
    nothing_removed = counts.get(REMOVED, 0) == 0
    nothing_unsupported = counts.get(UNSUPPORTED, 0) == 0
    return {
        "geometry_unchanged": nothing_unverified,
        "nothing_removed": nothing_removed and nothing_unsupported,
        "fully_accounted": nothing_unverified,
        "may_claim_nothing_lost": nothing_unverified and nothing_removed and nothing_unsupported,
    }


def _summary(counts: dict, claims: dict) -> str:
    kept = counts.get(PRESERVED_EXACT, 0) + counts.get(PRESERVED_SEMANTIC, 0)
    changed = counts.get(CHANGED, 0) + counts.get(ADDED, 0)
    removed = counts.get(REMOVED, 0)
    unsupported = counts.get(UNSUPPORTED, 0)
    unverified = counts.get(UNVERIFIED, 0)
    parts = [f"{kept} element(s) kept", f"{changed} changed"]
    if removed:
        parts.append(f"{removed} not carried over")
    if unsupported:
        parts.append(f"{unsupported} Studio does not understand")
    if unverified:
        parts.append(f"{unverified} Studio could not verify")
    text = ", ".join(parts) + "."
    if claims["may_claim_nothing_lost"]:
        return text + " Everything Studio can identify is accounted for."
    if unverified:
        return text + " Some elements could not be accounted for — check them yourself."
    return text + " The elements that were not carried over are listed with the reason."


def _unavailable(reason: str) -> dict:
    return {"schema_version": SCHEMA_VERSION, "available": False, "reason": reason,
            "rows": [], "counts": {}, "kept": [], "changed": [], "not_carried": [],
            "unverified": [],
            "claims": {"geometry_unchanged": False, "nothing_removed": False,
                       "fully_accounted": False, "may_claim_nothing_lost": False},
            "summary": reason}
