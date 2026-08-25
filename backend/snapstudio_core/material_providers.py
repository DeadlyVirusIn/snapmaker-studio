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

import ipaddress
import json
import re
import urllib.error
import urllib.parse
import urllib.request

SCHEMA_VERSION = "materials/2"


class InvalidProviderAddress(ValueError):
    """A provider address Studio will not turn into a request."""


#: Name suffixes that mean "a machine on this network". A bare single-label name
#: (`spoolman`) is a LAN name too. Anything else with a dot in it is a public DNS
#: name, and Studio does not make requests to those.
_LOCAL_SUFFIXES = (".local", ".lan", ".home", ".internal", ".home.arpa")

_HOSTNAME_RE = re.compile(
    r"\A(?!-)[A-Za-z0-9_-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9_-]{1,63}(?<!-))*\.?\Z")


def _host_is_local(host: str) -> bool:
    """Is this address on the user's own network?

    Studio is local-first, and that is a promise about where requests go rather
    than a description of its architecture. A provider address is typed by the
    user into a settings box, so without this check that box is a way to make
    Studio fetch an arbitrary URL on the public internet — which is exactly what
    it says it never does.
    """
    name = host.strip().strip("[]").rstrip(".").lower()
    if not name:
        return False
    try:
        address = ipaddress.ip_address(name)
    except ValueError:
        if name == "localhost" or "." not in name:
            return True
        return name.endswith(_LOCAL_SUFFIXES)
    # 100.64/10 is carrier-grade NAT, which is also what Tailscale hands out; a
    # tailnet is the user's own network by any reasonable reading.
    return bool(
        address.is_loopback or address.is_private or address.is_link_local
        or address in ipaddress.ip_network("100.64.0.0/10")
        or (address.version == 6 and address.is_site_local))


def validate_provider_url(value: str) -> str:
    """Return a normalised provider base URL, or raise InvalidProviderAddress.

    Accepts `http://spoolman.local:7912`, `http://192.168.1.9:7912`, a bare
    `spoolman:7912`. Refuses another scheme, credentials in the URL, a path,
    query or fragment, and any host that is not on the local network.

    The refusals are not paranoia about the user. `file://` made Studio read a
    local file, `ftp://` made it open an FTP connection, and a public hostname
    made it fetch a page from the internet — all three demonstrated against this
    function's predecessor, which passed the string straight to urllib.
    """
    text = (value or "").strip()
    if not text:
        raise InvalidProviderAddress("Enter the address of your Spoolman server.")
    if len(text) > 255:
        raise InvalidProviderAddress("That address is too long to be a server address.")
    if "://" not in text:
        text = "http://" + text
    parts = urllib.parse.urlsplit(text)
    if parts.scheme not in ("http", "https"):
        raise InvalidProviderAddress(
            "Studio only reads providers over http or https on your own network.")
    if parts.username or parts.password:
        raise InvalidProviderAddress(
            "Put the server's address here on its own — Studio does not send a "
            "username or password in a URL.")
    if parts.query or parts.fragment or parts.path.strip("/"):
        raise InvalidProviderAddress(
            "Enter just the server's address and port, without a path.")
    host = parts.hostname
    if not host:
        raise InvalidProviderAddress("That doesn't look like a server address.")
    if not _HOSTNAME_RE.match(host) and ":" not in host:
        raise InvalidProviderAddress("That doesn't look like a server address.")
    if not _host_is_local(host):
        raise InvalidProviderAddress(
            f"{host} is not an address on your own network. Studio reads material "
            "providers running on your network only — it makes no requests to the "
            "internet.")
    try:
        port = parts.port
    except ValueError as exc:
        raise InvalidProviderAddress("That port is not a number.") from exc
    authority = f"[{host}]" if ":" in host else host
    return f"{parts.scheme}://{authority}" + (f":{port}" if port else "")

STOCK = "stock-u1"
SPOOLMAN = "spoolman"

CONFIRMED = "confirmed"
LIKELY = "likely"
UNKNOWN = "unknown"

#: How a remaining weight came to be known. Nothing here is ever a measurement:
#: no spool holder on a U1 weighs filament, so the best available is a figure some
#: other tool has been keeping track of.
TRACKED = "tracked"        # the provider states a remaining weight
DERIVED = "derived"        # computed from a net weight minus what was recorded used
UNTRACKED = "unknown"      # nothing knows

#: More than this on one spool is not filament, it is a units mistake or a typo.
#: A 5 kg spool is a real product; 25 kg on one U1 slot is not.
IMPLAUSIBLE_GRAMS = 25_000


#: Who established that something is in this slot. The distinction the whole
#: multi-printer story turns on: a printer that reports its own filament state has
#: *looked*, while a provider mapping is a person writing down what they believe
#: they loaded. On a machine that reports no filament state at all — most Klipper
#: printers — a provider is the only source, and it must not be dressed up as the
#: machine having confirmed anything.
BY_PRINTER = "printer"
BY_PROVIDER = "provider"


def _slot(index: int, *, material=None, subtype=None, color=None, vendor=None,
          spool_id=None, remaining_g=None, source=STOCK, confidence=CONFIRMED,
          present=True, remaining_quality=UNTRACKED, remaining_as_of=None,
          notes=None, confirmed_by=None) -> dict:
    """One normalised slot. Absent facts stay absent."""
    return {
        "slot": index,
        "present": present,
        "confirmed_by": confirmed_by,
        "material": material,          # family, e.g. "PLA"
        "subtype": subtype,            # e.g. "Matte", when the source says so
        "color": color,
        "vendor": vendor,
        "spool_id": spool_id,
        "remaining_g": remaining_g,
        # How much to trust that number, and when it was last touched. A blocker
        # ("this print will run out") may only be built on a figure that says
        # where it came from.
        "remaining_quality": remaining_quality if remaining_g is not None else UNTRACKED,
        "remaining_as_of": remaining_as_of,
        "source": source,
        "confidence": confidence,
        "notes": list(notes or ()),
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
    except moonraker.PrinterUnavailable as exc:
        out["error"] = f"Studio could not reach the printer just now: {exc}"
        return out
    except Exception as exc:  # noqa: BLE001 — a printer that will not answer is an answer
        out["error"] = f"the printer did not answer: {type(exc).__name__}"
        return out
    if loaded is None:
        out["error"] = "this printer does not report which filaments are loaded"
        return out

    out["available"] = True
    for index, entry in enumerate(loaded):
        if not entry:
            out["slots"].append(_slot(index, present=False, confirmed_by=BY_PRINTER))
            continue
        family, subtype = _family_and_subtype(entry.get("material"))
        out["slots"].append(_slot(
            index, material=family, subtype=subtype, color=entry.get("color"),
            vendor=entry.get("vendor"), source=STOCK, confidence=CONFIRMED,
            confirmed_by=BY_PRINTER))
    # A printer knows what is loaded and nothing about how much is left on it.
    out["remaining_known"] = False
    return out


# --- Spoolman ----------------------------------------------------------------

def _get_json(url: str, timeout: float = 4.0):
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        # Bounded like every other response Studio reads from the network.
        return json.loads(response.read(4 * 1024 * 1024).decode("utf-8", "replace"))


def spoolman(base_url: str, slot_map: dict | None = None, timeout: float = 4.0,
             slot_base: int | None = None) -> dict:
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

    try:
        root = validate_provider_url(base_url)
    except InvalidProviderAddress as exc:
        out["error"] = str(exc)
        return out
    try:
        # Spoolman leaves archived spools out of this list unless asked. Studio
        # asks for them: a slot mapped to a spool somebody archived last week
        # should read as "that spool is archived", not as "there is no such
        # spool", which is what it said while this parameter was missing — and
        # which every mocked test agreed with, because a mock returns whatever
        # it was handed.
        spools = _get_json(f"{root}/api/v1/spool?allow_archived=true", timeout=timeout)
    except TimeoutError:
        out["error"] = (f"Spoolman did not answer within {timeout:g} seconds — Studio carried "
                        "on without it")
        return out
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
    for spool in spools:
        if not isinstance(spool, dict):
            continue
        filament = spool.get("filament") or {}
        vendor = (filament.get("vendor") or {}).get("name")
        family, subtype = _family_and_subtype(filament.get("material"))
        remaining, quality, notes = _remaining(spool, filament)
        out["spools"].append({
            "id": spool.get("id"),
            "material": family,
            "subtype": subtype,
            "color": _colour(filament.get("color_hex")),
            "vendor": vendor,
            "remaining_g": remaining,
            "remaining_quality": quality,
            # When this figure was last true. `last_used` is the only field a
            # real Spoolman has that means that; `registered` is when the spool
            # was added, which is not the same thing and must not stand in for
            # it. A spool nothing has printed from has no such date, and that is
            # the common case rather than the odd one.
            "remaining_as_of": spool.get("last_used") or None,
            "registered": spool.get("registered") or None,
            "notes": notes,
            "name": filament.get("name"),
            "archived": bool(spool.get("archived")),
        })
    out["remaining_known"] = any(s["remaining_g"] is not None for s in out["spools"])

    by_id = {s["id"]: s for s in out["spools"]}
    mapped, base = _mapped_slots(slot_map, slot_base)
    out["slot_base"] = base
    for slot_index, spool_id in mapped:
        spool = by_id.get(spool_id)
        if not spool:
            out["slots"].append(_slot(slot_index, present=False, source=SPOOLMAN,
                                      confidence=UNKNOWN, confirmed_by=BY_PROVIDER,
                                      notes=[f"no spool with id {spool_id} in Spoolman"]))
            continue
        notes = list(spool["notes"])
        if spool["archived"]:
            notes.append("this spool is archived in Spoolman")
        out["slots"].append(_slot(
            slot_index, material=spool["material"], subtype=spool["subtype"],
            color=spool["color"], vendor=spool["vendor"], spool_id=spool["id"],
            remaining_g=spool["remaining_g"], source=SPOOLMAN,
            remaining_quality=spool["remaining_quality"],
            remaining_as_of=spool["remaining_as_of"], notes=notes,
            # The user told Studio which spool is in which slot. That is a
            # statement of intent, not a measurement the printer confirmed.
            confidence=LIKELY, confirmed_by=BY_PROVIDER))
    return out


def _mapped_slots(slot_map: dict | None,
                  slot_base: int | None = None) -> tuple[list[tuple[int, object]], int]:
    """Read the user's slot-to-spool map, whichever way they numbered their slots.

    Spoolman does not know which slot a spool is in, so the map comes from the
    user — and a person looking at a U1 counts the slots 1, 2, 3, 4 while the
    G-code counts them 0, 1, 2, 3. Getting that wrong puts every spool one slot
    out, and would then report the wrong material for every slot with complete
    confidence, which is worse than not knowing at all.

    So: when the caller says which way it numbered them, that is used. Otherwise
    a map that cannot be zero-based — it names a slot beyond the last one — is
    read as one-based, and the interpretation is reported alongside the result so
    the user can see it rather than discover it.
    """
    pairs = []
    for key, value in (slot_map or {}).items():
        try:
            index = int(str(key).strip())
        except (TypeError, ValueError):
            continue
        if index < 0:
            continue
        pairs.append((index, value))
    if not pairs:
        return [], 0 if slot_base is None else slot_base

    indices = [index for index, _ in pairs]
    base = slot_base
    if base is None:
        base = 1 if (min(indices) >= 1 and max(indices) >= 4) else 0
    if base:
        pairs = [(index - base, value) for index, value in pairs if index - base >= 0]
    return sorted(pairs), base


def _colour(value) -> str | None:
    """A hex colour, or nothing. A malformed one is not a colour."""
    if value is None:
        return None
    text = str(value).strip().lstrip("#")
    if len(text) >= 6 and all(c in "0123456789abcdefABCDEF" for c in text[:6]):
        return "#" + text[:6].upper()
    return None


def _remaining(spool: dict, filament: dict) -> tuple[float | None, str, list[str]]:
    """How much filament is left, how that is known, and what is odd about it.

    Never invents a number: a spool with nothing recorded comes back as unknown,
    and a number that cannot be true — negative, or more than any spool holds — is
    treated as not knowing rather than as a fact worth blocking a print over.
    """
    notes: list[str] = []
    value = _number(spool.get("remaining_weight"))
    quality = _quality(spool)
    if value is None:
        # Spoolman does not always store a remaining weight; when it stores the
        # spool's net weight and what has been used, the difference is honest
        # arithmetic — but it is arithmetic, and it is labelled as such.
        net = _number(filament.get("weight")) or _number(spool.get("initial_weight"))
        used = _number(spool.get("used_weight"))
        if net is not None and used is not None:
            value = round(net - used, 1)
            quality = DERIVED
        else:
            return None, UNTRACKED, notes

    if value < 0:
        notes.append("Spoolman reports a negative weight for this spool, so Studio "
                     "cannot use it")
        return None, UNTRACKED, notes
    if value > IMPLAUSIBLE_GRAMS:
        notes.append(f"Spoolman reports {value:g} g on this spool, which is not a "
                     "weight of filament — check the units in Spoolman")
        return None, UNTRACKED, notes

    net = _number(filament.get("weight"))
    if net and value > net * 1.5:
        notes.append(f"Spoolman reports more left ({value:g} g) than the spool holds "
                     f"({net:g} g), so Studio cannot use it")
        return None, UNTRACKED, notes
    return value, quality, notes


def _quality(spool: dict) -> str:
    """Is this remaining weight bookkeeping something has kept, or arithmetic?

    Spoolman always answers with a `remaining_weight`, because it computes one
    from the spool's initial weight minus what has been recorded used. That means
    the field being present proves nothing on its own — a spool registered five
    minutes ago and never printed from reports a full kilogram, and the previous
    version of this function called that `tracked`, the highest confidence Studio
    has, which is what a blocker is built on.

    So the distinction is drawn where the evidence actually is: a figure is
    tracked when something has been recording consumption against this spool, and
    derived when it is initial weight minus a used weight nothing has updated.
    """
    used = _number(spool.get("used_weight"))
    if spool.get("last_used") and used:
        return TRACKED
    return DERIVED


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number or number in (float("inf"), float("-inf")):
        return None
    return round(number, 1)


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
                    if key == "remaining_g":
                        existing["remaining_quality"] = slot.get("remaining_quality", UNTRACKED)
                        existing["remaining_as_of"] = slot.get("remaining_as_of")
            existing["notes"] = list(existing.get("notes") or ()) + list(slot.get("notes") or ())

            # Two sources describing the same slot differently is not a detail to
            # smooth over: one of them is about to be wrong about what will come
            # out of the nozzle. The printer's answer stands, and the
            # disagreement is said out loud.
            for key, what in (("material", "material"), ("color", "colour")):
                mine, theirs = existing.get(key), slot.get(key)
                if mine and theirs and str(mine).upper() != str(theirs).upper():
                    existing.setdefault("conflicts", []).append(
                        f"the printer reports {mine} in this slot and {slot['source']} "
                        f"has {theirs} — Studio is using what the printer can see")
                    existing["confidence"] = UNKNOWN
                    existing.setdefault("disagreed", {})[what] = {
                        "printer": mine, slot["source"]: theirs}

            # A provider filling gaps never changes who saw the slot. If the
            # printer reported it, the printer confirmed it; if only a provider
            # ever spoke, nothing confirmed it.
            if existing.get("confirmed_by") != BY_PRINTER and slot.get("confirmed_by") == BY_PRINTER:
                existing["confirmed_by"] = BY_PRINTER

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
            "confirmed_by": slot.get("confirmed_by"),
            "color": slot.get("color"),
            "material": material or None,
            "vendor": slot.get("vendor"),
            "spool_id": slot.get("spool_id"),
            "remaining_g": slot.get("remaining_g"),
            # Carried through so the checks downstream can tell a figure something
            # is keeping track of from a figure nothing is.
            "remaining_quality": slot.get("remaining_quality", UNTRACKED),
            "remaining_as_of": slot.get("remaining_as_of"),
            "conflicts": list(slot.get("conflicts") or ()),
            "notes": list(slot.get("notes") or ()),
        }
    return out
