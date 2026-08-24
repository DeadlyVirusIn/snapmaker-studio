"""Where Studio learns what filament is actually loaded.

Until now there was one answer: whatever the U1 reports over Moonraker. That is
the right default and it will stay the default, but it cannot answer the question
people keep asking — *do I have enough filament for this print?* — because a
printer knows which spool is in a slot and nothing about how much is left on it.

Other tools do know. Spoolman tracks spools and their remaining weight, U1Hub
keeps a loadout, and some firmware builds expose more than stock does. So this is
a seam, not an integration: each provider is read-only, optional, and normalises
to one shape that `material_plan` consumes without caring where it came from.

Three rules, and they are the reason this is a seam rather than a feature:

* **Nothing is required.** A stock U1 with no other software is a first-class
  setup and always will be.
* **Nothing is written.** Studio does not create, update, consume or delete
  anyone else's records. Reading someone's spool database and then quietly
  decrementing it is how two tools end up disagreeing about reality.
* **Nothing is invented.** A provider that cannot say how much filament is left
  reports `None`, and everything downstream treats that as unknown rather than
  as plenty.

Every service here lives on the local network at an address the user supplies,
exactly like the printer. Studio still makes no outbound internet requests.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

SCHEMA_VERSION = "materials/1"

STOCK = "stock-u1"
SPOOLMAN = "spoolman"

CONFIRMED = "confirmed"
LIKELY = "likely"
UNKNOWN = "unknown"


def _slot(index: int, *, material=None, subtype=None, color=None, vendor=None,
          spool_id=None, remaining_g=None, source=STOCK, confidence=CONFIRMED,
          present=True) -> dict:
    """One normalised slot. Absent facts stay absent."""
    return {
        "slot": index,
        "present": present,
        "material": material,          # family, e.g. "PLA"
        "subtype": subtype,            # e.g. "Matte", when the source says so
        "color": color,
        "vendor": vendor,
        "spool_id": spool_id,
        "remaining_g": remaining_g,
        "source": source,
        "confidence": confidence,
    }


def _family_and_subtype(value: str | None) -> tuple[str | None, str | None]:
    """"PLA Matte" -> ("PLA", "Matte")."""
    if not value:
        return None, None
    parts = str(value).strip().split(None, 1)
    if not parts:
        return None, None
    return parts[0].upper(), (parts[1] if len(parts) > 1 else None)


# --- stock U1 ----------------------------------------------------------------

def stock_u1(host: str, port: int = 7125) -> dict:
    """What the printer itself reports. The default, and the only one always available."""
    from . import moonraker

    out = {"schema_version": SCHEMA_VERSION, "source": STOCK, "available": False, "slots": []}
    if not host:
        out["error"] = "no printer address configured"
        return out
    try:
        loaded = moonraker.loaded_filaments(host, port)
    except Exception as exc:  # noqa: BLE001 — a printer that will not answer is an answer
        out["error"] = f"the printer did not answer: {type(exc).__name__}"
        return out
    if loaded is None:
        out["error"] = "this printer does not report which filaments are loaded"
        return out

    out["available"] = True
    for index, entry in enumerate(loaded):
        if not entry:
            out["slots"].append(_slot(index, present=False))
            continue
        family, subtype = _family_and_subtype(entry.get("material"))
        out["slots"].append(_slot(
            index, material=family, subtype=subtype, color=entry.get("color"),
            vendor=entry.get("vendor"), source=STOCK, confidence=CONFIRMED))
    # A printer knows what is loaded and nothing about how much is left on it.
    out["remaining_known"] = False
    return out


# --- Spoolman ----------------------------------------------------------------

def _get_json(url: str, timeout: float = 4.0):
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        # Bounded like every other response Studio reads from the network.
        return json.loads(response.read(4 * 1024 * 1024).decode("utf-8", "replace"))


def spoolman(base_url: str, slot_map: dict | None = None, timeout: float = 4.0) -> dict:
    """Read spools from a Spoolman instance on the local network.

    Read-only, and deliberately so: Studio does not create spools and does not
    decrement anyone's remaining weight. Consumption tracking belongs to the tool
    that owns the data.

    ``slot_map`` maps a printer slot to a Spoolman spool id, because Spoolman
    does not know which slot a spool is in — the user does. Without it, Studio
    reports the spools it can see and does not pretend to know where they are.
    """
    out = {"schema_version": SCHEMA_VERSION, "source": SPOOLMAN, "available": False,
           "slots": [], "spools": []}
    if not base_url:
        out["error"] = "no Spoolman address configured"
        return out

    root = str(base_url).rstrip("/")
    try:
        spools = _get_json(f"{root}/api/v1/spool", timeout=timeout)
    except urllib.error.URLError as exc:
        out["error"] = f"Spoolman did not answer: {getattr(exc, 'reason', exc)}"
        return out
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"Spoolman answered with something unexpected: {type(exc).__name__}"
        return out

    if not isinstance(spools, list):
        out["error"] = "Spoolman answered with something unexpected"
        return out

    out["available"] = True
    out["remaining_known"] = True
    for spool in spools:
        filament = spool.get("filament") or {}
        vendor = (filament.get("vendor") or {}).get("name")
        family, subtype = _family_and_subtype(filament.get("material"))
        colour = filament.get("color_hex")
        out["spools"].append({
            "id": spool.get("id"),
            "material": family,
            "subtype": subtype,
            "color": ("#" + str(colour).lstrip("#")[:6].upper()) if colour else None,
            "vendor": vendor,
            "remaining_g": _number(spool.get("remaining_weight")),
            "name": filament.get("name"),
            "archived": bool(spool.get("archived")),
        })

    by_id = {s["id"]: s for s in out["spools"]}
    for slot_index, spool_id in sorted((slot_map or {}).items(), key=lambda kv: int(kv[0])):
        spool = by_id.get(spool_id)
        if not spool:
            out["slots"].append(_slot(int(slot_index), present=False, source=SPOOLMAN,
                                      confidence=UNKNOWN))
            continue
        out["slots"].append(_slot(
            int(slot_index), material=spool["material"], subtype=spool["subtype"],
            color=spool["color"], vendor=spool["vendor"], spool_id=spool["id"],
            remaining_g=spool["remaining_g"], source=SPOOLMAN,
            # The user told Studio which spool is in which slot. That is a
            # statement of intent, not a measurement the printer confirmed.
            confidence=LIKELY))
    return out


def _number(value):
    try:
        return round(float(value), 1)
    except (TypeError, ValueError):
        return None


# --- combining ---------------------------------------------------------------

def combine(*states: dict) -> dict:
    """Merge providers, best evidence first.

    The printer is authoritative about *what* is in a slot, because it is looking
    at it. Another provider may add what the printer cannot know — a spool
    identity, a remaining weight — but never overrides the material or colour the
    machine itself reported.
    """
    merged: dict[int, dict] = {}
    sources = []
    remaining_known = False

    for state in states:
        if not state or not state.get("available"):
            continue
        sources.append(state["source"])
        remaining_known = remaining_known or bool(state.get("remaining_known"))
        for slot in state.get("slots", []):
            index = slot["slot"]
            existing = merged.get(index)
            if existing is None:
                merged[index] = dict(slot)
                continue
            # Fill gaps only; never overwrite what the printer said it sees.
            for key in ("material", "subtype", "color", "vendor", "spool_id", "remaining_g"):
                if existing.get(key) in (None, "") and slot.get(key) not in (None, ""):
                    existing[key] = slot[key]
                    existing.setdefault("added_by", {})[key] = slot["source"]
            if slot.get("present") and not existing.get("present"):
                # One source says empty, another says a spool is there. That is a
                # disagreement, not a fact, and it is reported as one.
                existing["present"] = True
                existing["confidence"] = UNKNOWN
                existing.setdefault("conflicts", []).append(
                    f"{existing['source']} reports this slot empty, {slot['source']} does not")

    return {
        "schema_version": SCHEMA_VERSION,
        "available": bool(merged),
        "sources": sources,
        "remaining_known": remaining_known,
        "slots": [merged[i] for i in sorted(merged)],
    }


def as_loaded_filaments(state: dict) -> list | None:
    """Back into the shape the existing checks already understand.

    `material_plan` and the post-slice checks were written against the printer's
    own list, index-aligned with `None` for an empty slot. Keeping that shape means
    every provider works with code that predates the seam.
    """
    if not state or not state.get("available"):
        return None
    slots = state.get("slots") or []
    if not slots:
        return None
    highest = max(s["slot"] for s in slots)
    out: list = [None] * (highest + 1)
    for slot in slots:
        if not slot.get("present"):
            continue
        material = " ".join(x for x in (slot.get("material"), slot.get("subtype")) if x)
        out[slot["slot"]] = {
            "color": slot.get("color"),
            "material": material or None,
            "vendor": slot.get("vendor"),
            "spool_id": slot.get("spool_id"),
            "remaining_g": slot.get("remaining_g"),
        }
    return out
