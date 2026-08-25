"""Which filament each object is assigned to, in whichever dialect says so.

A project's per-object filament assignment is the quietest thing a converter can
destroy. The mesh survives, the file opens, the colours are all still listed —
and every object prints in filament 1. Studio did exactly that to every
PrusaSlicer project it prepared: an object assigned filament 3 arrived assigned
filament 1, with nothing anywhere saying so.

So the assignment is read as a fact in its own right, from both dialects, in a
shape that can be compared across the crossing:

* **PrusaSlicer** — `Metadata/Slic3r_PE_model.config`, objects carrying
  `<metadata type="object" key="extruder">`, with volumes able to carry their own.
* **Bambu / Orca / Snapmaker Orca** — `Metadata/model_settings.config`, objects
  and their parts carrying `<metadata key="extruder">`.

Two distinctions are kept rather than flattened. An object with no assignment is
*default*, which is not the same claim as an object explicitly assigned slot 1.
And an object whose volumes disagree cannot be represented as a single U1 part,
which is a real limit of the crossing and is reported as one — never resolved by
picking a volume and hoping.
"""
from __future__ import annotations

import re

from .container import ThreeMF

PRUSA_CONFIG = "Metadata/Slic3r_PE_model.config"
BAMBU_CONFIG = "Metadata/model_settings.config"

DIALECT_PRUSA = "prusa"
DIALECT_BAMBU = "bambu"

# How an object's slot came to be what it is.
EXPLICIT = "explicit"      # the object says so itself
FROM_VOLUME = "from_volume"  # its volumes agree and the object is silent
DEFAULT = "default"        # nothing says, so the project's first filament

_OBJECT = re.compile(r"<object\b")
_VOLUME = re.compile(r"<volume\b")
_PART = re.compile(r"<part\b")
_ID = re.compile(r'id="([^"]+)"')
_PRUSA_META = re.compile(
    r'<metadata\s+type="(object|volume|part)"\s+key="([^"]+)"\s+value="([^"]*)"')
_BAMBU_META = re.compile(r'<metadata\s+key="([^"]+)"\s+value="([^"]*)"')


def _int(value: str):
    value = (value or "").strip()
    return int(value) if value.isdigit() else None


def _read(tm: ThreeMF, part: str) -> str | None:
    if not tm.has_part(part):
        return None
    try:
        return tm.read_part(part).decode("utf-8", "ignore")
    except Exception:
        return None


def _prusa(text: str) -> list[dict]:
    out = []
    chunks = re.split(_OBJECT, text)[1:]
    for position, chunk in enumerate(chunks):
        head = chunk.split(">", 1)[0]
        found = _ID.search(head)
        entry = {"object_id": found.group(1) if found else str(position + 1),
                 "index": position, "name": None, "slot": None,
                 "source": DEFAULT, "volume_slots": []}
        for kind, key, value in _PRUSA_META.findall(chunk.split("<volume", 1)[0]):
            if key == "extruder":
                slot = _int(value)
                if slot:
                    entry["slot"], entry["source"] = slot, EXPLICIT
            elif key == "name" and entry["name"] is None:
                entry["name"] = value
        for volume in re.split(_VOLUME, chunk)[1:]:
            slot = None
            for _kind, key, value in _PRUSA_META.findall(volume):
                if key == "extruder":
                    slot = _int(value) or slot
            entry["volume_slots"].append(slot)
        if entry["slot"] is None:
            stated = {slot for slot in entry["volume_slots"] if slot}
            if len(stated) == 1:
                entry["slot"], entry["source"] = stated.pop(), FROM_VOLUME
        out.append(entry)
    return out


def _bambu(text: str) -> list[dict]:
    out = []
    for position, chunk in enumerate(re.split(_OBJECT, text)[1:]):
        head = chunk.split(">", 1)[0]
        found = _ID.search(head)
        entry = {"object_id": found.group(1) if found else str(position + 1),
                 "index": position, "name": None, "slot": None,
                 "source": DEFAULT, "volume_slots": []}
        for key, value in _BAMBU_META.findall(chunk.split("<part", 1)[0]):
            if key == "extruder":
                slot = _int(value)
                if slot:
                    entry["slot"], entry["source"] = slot, EXPLICIT
            elif key == "name" and entry["name"] is None:
                entry["name"] = value
        for part in re.split(_PART, chunk)[1:]:
            slot = None
            for key, value in _BAMBU_META.findall(part):
                if key == "extruder":
                    slot = _int(value) or slot
            entry["volume_slots"].append(slot)
        out.append(entry)
    return out


def read(tm: ThreeMF) -> dict:
    """Every object's filament assignment, from whichever dialect the file speaks."""
    prusa = _read(tm, PRUSA_CONFIG)
    if prusa is not None:
        return {"available": True, "dialect": DIALECT_PRUSA, "objects": _prusa(prusa)}
    bambu = _read(tm, BAMBU_CONFIG)
    if bambu is not None:
        return {"available": True, "dialect": DIALECT_BAMBU, "objects": _bambu(bambu)}
    return {"available": False, "dialect": None, "objects": [],
            "reason": "this project records no per-object filament assignment"}


# --- comparing one side with the other ---------------------------------------

PRESERVED = "preserved"
CHANGED = "changed"
LOST = "lost"
NOT_REPRESENTABLE = "not_representable"
UNKNOWN = "unknown"


def compare(before: dict, after: dict) -> dict:
    """Object by object, what happened to the assignment.

    Objects are matched by position, because the two dialects number objects
    differently and preparing a copy renames them: a Prusa object id and a U1
    object id that happen to share a number are not the same claim. Position is
    the one thing the crossing preserves, and where the counts differ the extra
    objects are reported as unknown rather than paired up hopefully.
    """
    if not before.get("available") or not after.get("available"):
        return {"available": False, "rows": [],
                "reason": "one side records no assignments to compare"}

    rows = []
    source_objects = before["objects"]
    prepared_objects = after["objects"]
    for index, source in enumerate(source_objects):
        prepared = prepared_objects[index] if index < len(prepared_objects) else None
        name = source.get("name") or f"object {index + 1}"
        if prepared is None:
            rows.append({"object": name, "index": index, "from": source["slot"],
                         "to": None, "status": UNKNOWN,
                         "detail": "this object is not in the prepared copy"})
            continue
        wanted = source["slot"]
        got = prepared["slot"]
        if wanted is None and source["source"] == DEFAULT:
            status = PRESERVED if got in (None, 1) else CHANGED
            detail = ("left on the project's default filament" if status == PRESERVED
                      else f"the source stated no filament; the copy assigns slot {got}")
        elif wanted == got:
            status = PRESERVED
            detail = (f"slot {wanted} carried over"
                      + (" (stated by the object's volume)"
                         if source["source"] == FROM_VOLUME else ""))
        elif got is None:
            status = LOST
            detail = f"the source assigns slot {wanted}; the copy assigns none"
        else:
            status = CHANGED
            detail = f"slot {wanted} → slot {got}"
        row = {"object": name, "index": index, "from": wanted, "to": got,
               "status": status, "detail": detail,
               "from_source": source["source"]}
        stated = {slot for slot in source.get("volume_slots") or [] if slot}
        if len(stated) > 1:
            # A U1 object is one part. Volumes that disagree cannot all be
            # represented, and that is a fact about the crossing, not a defect.
            row["status"] = NOT_REPRESENTABLE
            row["detail"] = (
                f"this object's volumes use filaments {sorted(stated)}, and a "
                "prepared U1 object is a single part — the object's own slot "
                f"({wanted}) is carried and the rest cannot be represented")
        rows.append(row)

    for index in range(len(source_objects), len(prepared_objects)):
        prepared = prepared_objects[index]
        rows.append({"object": prepared.get("name") or f"object {index + 1}",
                     "index": index, "from": None, "to": prepared["slot"],
                     "status": UNKNOWN,
                     "detail": "this object is only in the prepared copy"})

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {"available": True, "rows": rows, "counts": counts,
            "all_preserved": all(row["status"] == PRESERVED for row in rows),
            "source_dialect": before.get("dialect"),
            "prepared_dialect": after.get("dialect")}
