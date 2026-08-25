"""Printer profiles — facts about a machine, and how sure Studio is of them.

Studio grew up around one printer. Everything it knows about a machine it learned
from a Snapmaker U1, and until now there was nothing in the code that could tell
the difference between "this is how printers work" and "this is how the U1
works". The bed fallback was a module constant called ``U1_BED``; the toolhead
fallback was ``U1_TOOLHEADS = 4``; a sliced job was checked against the string
``"u1"`` rather than against the printer on the other end of the wire.

This module is where that knowledge becomes data. A profile carries **facts**:
build volume, tool count, what the machine reports about its own materials, what
it is known not to report. It carries no behaviour — there is deliberately no
per-printer function anywhere in this package, and a test fails the build if
model-name branching appears in the generic printer modules.

Two rules govern everything here.

**Live evidence beats the profile, always.** A profile says what a machine of this
kind is expected to be. The machine says what it is. If a profile claims four
tools and the printer reports three, Studio says three — the profile is never
allowed to correct the hardware. :func:`resolve` implements exactly that
precedence and records which source won.

**How a fact was established travels with it.** A profile states its verification
level, and that level is not a synonym for quality — it is a statement about
evidence. The U1 is ``hardware_verified`` because a physical U1 answered these
questions. A profile built from a published configuration is ``profile_verified``,
and Studio must never round that up to "supported", "tested" or "verified" on its
own.
"""
from __future__ import annotations

import json
from importlib.resources import files

SCHEMA_VERSION = "printerprofile/1"

# --- verification levels ----------------------------------------------------
#
# Ordered strongest evidence first. The ordering exists so the UI can sort and so
# a test can assert that nothing ever presents a weaker level as a stronger one.

HARDWARE_VERIFIED = "hardware_verified"
PROFILE_VERIFIED = "profile_verified"
SIMULATED = "simulated"
UNKNOWN = "unknown"

LEVEL_ORDER = {HARDWARE_VERIFIED: 0, PROFILE_VERIFIED: 1, SIMULATED: 2, UNKNOWN: 3}

#: The exact words each level is allowed to be shown as. They are here rather
#: than in the UI so that one place decides, and so the public-claim guard has
#: something to check against. Nothing may shorten ``profile_verified`` to
#: "verified": the qualifier is the whole point of the label.
LEVEL_LABEL = {
    HARDWARE_VERIFIED: "Hardware verified",
    PROFILE_VERIFIED: "Profile verified — hardware not tested by this project",
    SIMULATED: "Simulated — exercised only against generated responses",
    UNKNOWN: "Not established",
}

LEVEL_MEANING = {
    HARDWARE_VERIFIED: ("A physical machine of this kind answered these questions, "
                        "read-only, and the answers were recorded."),
    PROFILE_VERIFIED: ("These facts come from the machine's published configuration and "
                       "have been run through Studio's real printer logic. No machine of "
                       "this kind has been connected to Studio."),
    SIMULATED: ("Behaviour exercised only through responses Studio generated for itself. "
                "Nothing outside Studio has confirmed any of it."),
    UNKNOWN: "Studio has not established this.",
}


def level_label(level: str | None) -> str:
    return LEVEL_LABEL.get(level or UNKNOWN, LEVEL_LABEL[UNKNOWN])


def level_meaning(level: str | None) -> str:
    return LEVEL_MEANING.get(level or UNKNOWN, LEVEL_MEANING[UNKNOWN])


# --- loading ----------------------------------------------------------------

#: The printer Studio prepares copies for. Preparing a project is a U1-specific
#: operation by design — Studio writes a U1 profile copy for Snapmaker Orca — so
#: this is legitimate product scope, not an assumption about printers in general.
#: It is named here so that the *printer intelligence* layer can stop assuming it.
PREPARE_TARGET_ID = "snapmaker_u1"

_CACHE: dict[str, dict] = {}


def available() -> list[str]:
    """Profile ids Studio ships, sorted."""
    root = files("snapstudio_core.data.printer_profiles")
    return sorted(p.name[:-5] for p in root.iterdir()
                  if p.name.endswith(".json"))


def load(printer_id: str) -> dict:
    """Load one profile by id. Raises KeyError when there is no such profile."""
    if printer_id in _CACHE:
        return _CACHE[printer_id]
    if printer_id not in available():
        raise KeyError(printer_id)
    root = files("snapstudio_core.data.printer_profiles")
    data = json.loads((root / f"{printer_id}.json").read_text("utf-8"))
    _CACHE[printer_id] = data
    return data


def load_all() -> list[dict]:
    return [load(pid) for pid in available()]


def prepare_target() -> dict:
    """The profile Studio prepares copies for — the fallback for offline advice.

    Design intelligence that runs with no printer connected has to compare the
    model against *something*. The honest something is the machine Studio is
    about to prepare the file for, and saying which one that was is part of the
    answer rather than a footnote.
    """
    return load(PREPARE_TARGET_ID)


def display_name(profile: dict | None) -> str:
    """What to call this printer in a sentence, without inventing a model."""
    if not profile:
        return "your printer"
    return profile.get("display_name") or profile.get("model") or "your printer"


def summarise(profile: dict | None) -> dict | None:
    """The small, UI-facing shape: who it is and how well established that is."""
    if not profile:
        return None
    level = profile.get("verification_level") or UNKNOWN
    return {
        "printer_id": profile.get("printer_id"),
        "display_name": display_name(profile),
        "manufacturer": profile.get("manufacturer"),
        "model": profile.get("model"),
        "verification_level": level,
        "verification_label": level_label(level),
        "verification_meaning": level_meaning(level),
        "verification_note": profile.get("verification_note"),
        "tool_count": profile.get("tool_count"),
        "build_volume_mm": profile.get("build_volume_mm"),
        "known_unknowns": list(profile.get("known_unknowns") or ()),
        "not_verified": list(profile.get("not_verified") or ()),
        "source_refs": list(profile.get("source_refs") or ()),
    }


# --- identification ---------------------------------------------------------

def _tokens(profile: dict) -> list[str]:
    return [str(t).lower() for t in (profile.get("identity") or {}).get("model_tokens") or ()]


def identify_model_string(text: str | None, profiles: list[dict] | None = None) -> dict:
    """Which shipped profile does a stated model name belong to?

    Used for the name a *sliced file* states it was made for, and for anything
    else that hands Studio a model string. Longest token wins, so "voron 2.4"
    beats the bare "voron" and the U1's "u1" cannot swallow a name that merely
    contains those two characters.

    Returns ``matched: False`` rather than guessing. A name Studio does not
    recognise is not evidence of anything, least of all of a mismatch.
    """
    out = {"matched": False, "printer_id": None, "token": None, "stated": text}
    if not text:
        return out
    haystack = str(text).lower()
    best: tuple[int, str, str] | None = None
    for profile in (profiles if profiles is not None else load_all()):
        for token in _tokens(profile):
            if token and token in haystack:
                if best is None or len(token) > best[0]:
                    best = (len(token), profile["printer_id"], token)
    if best:
        out.update(matched=True, printer_id=best[1], token=best[2])
    return out


def identify(facts: dict | None, profiles: list[dict] | None = None) -> dict:
    """Which printer is on the other end, judged only on what it said.

    Moonraker does not publish a model name, so identification is inference from
    shape: how many tools it reports, how big its axes are, which of its objects
    are Snapmaker-specific. That is worth doing — it is what lets Studio stop
    saying "U1" about a machine that is not one — but it is never certain, and
    this returns a confidence rather than a verdict.

    ``confirmed`` is reserved for a match nothing else could produce. Everything
    softer is ``likely`` or no match at all, and no match is a perfectly good
    answer: Studio can check a printer thoroughly without knowing its name.
    """
    facts = facts or {}
    out: dict = {"matched": False, "printer_id": None, "confidence": None,
                 "evidence": None, "matched_on": []}
    if not facts.get("reachable"):
        out["evidence"] = "no printer answered"
        return out

    objects = [str(o).split(" ", 1)[0].strip().lower()
               for o in (facts.get("klipper_objects") or [])]
    tools = facts.get("toolhead_count")

    for profile in (profiles if profiles is not None else load_all()):
        material = profile.get("material_state") or {}
        marker = material.get("object")
        # A vendor-specific Klipper object is the one piece of identification a
        # Moonraker printer really does hand over. `print_task_config` is not in
        # mainline Klipper; a machine carrying it is a Snapmaker.
        if marker and material.get("source") == "klipper_object" and marker.lower() in objects:
            matched_on = [f"the printer exposes the {marker} object, which mainline Klipper does not have"]
            if tools and tools == profile.get("tool_count"):
                matched_on.append(f"it reports {tools} toolheads, as this profile records")
            out.update(matched=True, printer_id=profile["printer_id"],
                       confidence="confirmed", matched_on=matched_on,
                       evidence="; ".join(matched_on))
            return out

    out["evidence"] = ("nothing this printer reported identifies which model it is — "
                       "Moonraker does not publish a model name, and none of the "
                       "vendor-specific objects Studio knows about are present")
    return out


# --- capability resolution --------------------------------------------------
#
# The capabilities Studio reasons about, and the Klipper object kinds that prove
# each one. This is the generic half: a capability is present because an object
# is present, on any Klipper machine, with no reference to who made it.

CAPABILITY_OBJECTS = {
    "bed_mesh": ("bed_mesh",),
    "exclude_object": ("exclude_object",),
    "input_shaper": ("input_shaper",),
    "pause_resume": ("pause_resume",),
    "eddy_probe": ("probe_eddy_current",),
    "filament_runout": ("filament_switch_sensor", "filament_motion_sensor"),
    "quad_gantry_level": ("quad_gantry_level",),
    "z_tilt": ("z_tilt",),
    "virtual_sdcard": ("virtual_sdcard",),
}

PRESENT = "present"
ABSENT = "absent"
EXPECTED = "expected"          # the profile expects it; the machine has not been asked
NOT_EXPECTED = "not_expected"  # the profile does not expect it; the machine has not been asked
CAP_UNKNOWN = "unknown"


def capability(name: str, klipper_objects, profile: dict | None = None) -> dict:
    """Does this printer have this capability, and how does Studio know?

    Live first. An object list from the machine settles the question in both
    directions: the object is there, or it is not there and this firmware does
    not offer the feature.

    Without a live list, the profile can only say what is *expected*, and this
    says so in those words. An expectation is not a capability, and a profile
    that does not expect something is not evidence the machine lacks it — the
    published configuration a profile is built from is a starting point owners
    edit.
    """
    objects = klipper_objects
    kinds = None
    if objects is not None:
        kinds = {str(o).split(" ", 1)[0].strip().lower() for o in objects}
    names = CAPABILITY_OBJECTS.get(name, (name,))

    if kinds:
        if any(n in kinds for n in names):
            return {"name": name, "state": PRESENT, "source": "live",
                    "evidence": f"the printer's firmware lists {names[0]}"}
        return {"name": name, "state": ABSENT, "source": "live",
                "evidence": f"the printer's firmware does not list {names[0]}"}

    expectation = ((profile or {}).get("expected_capabilities") or {}).get(name)
    if expectation is None:
        return {"name": name, "state": CAP_UNKNOWN, "source": "none",
                "evidence": "the printer was not asked and no profile records an expectation"}
    expected = bool(expectation.get("expected"))
    return {
        "name": name,
        "state": EXPECTED if expected else NOT_EXPECTED,
        "source": "profile",
        "confidence": expectation.get("confidence"),
        "evidence": (f"{display_name(profile)} is {'expected to have' if expected else 'not recorded as having'} "
                     f"this, from {expectation.get('confidence') or 'an unstated source'}; "
                     "the printer itself has not been asked"),
    }


def resolve(facts: dict | None, profile: dict | None = None) -> dict:
    """Join live printer facts to a profile, live winning every contest.

    Returns the values the rest of Studio should reason with, each carrying where
    it came from. When the two disagree the live value is used and the
    disagreement is reported — never smoothed over, and never resolved the other
    way. A profile that claims four tools against a printer reporting three is
    the profile being wrong about that machine.
    """
    facts = facts or {}
    reachable = bool(facts.get("reachable"))
    out: dict = {
        "schema_version": SCHEMA_VERSION,
        "printer_reachable": reachable,
        "profile": summarise(profile),
        "conflicts": [],
        "sources": {},
    }

    def settle(key: str, live, profile_value, unit: str = ""):
        if live is not None:
            out[key] = live
            out["sources"][key] = "live"
            if profile_value is not None and profile_value != live:
                out["conflicts"].append({
                    "field": key,
                    "live": live,
                    "profile": profile_value,
                    "detail": (f"This printer reports {live}{unit}; the "
                               f"{display_name(profile)} profile records {profile_value}{unit}. "
                               "Studio uses what the printer reports."),
                })
            return
        out[key] = profile_value
        out["sources"][key] = "profile" if profile_value is not None else "none"

    settle("tool_count", facts.get("toolhead_count"),
           (profile or {}).get("tool_count"))

    # Build volume is the one field where the live number and the profile number
    # are answers to different questions: Klipper reports how far the toolhead
    # travels, and a machine profile records how much of the plate can be printed
    # on. The U1 travels 335 mm in Y over a 270 mm plate. So a difference here is
    # not a conflict to report at the user, and calling it one would be noise.
    live_bed = facts.get("bed_mm")
    out["build_volume_mm"] = live_bed or (profile or {}).get("build_volume_mm")
    out["sources"]["build_volume_mm"] = ("live" if live_bed else
                                         "profile" if (profile or {}).get("build_volume_mm") else "none")
    if live_bed:
        out["build_volume_note"] = ("measured from the printer's own axis limits, which "
                                    "include travel beyond the printable plate")

    objects = facts.get("klipper_objects") if reachable else None
    out["capabilities"] = {name: capability(name, objects, profile)
                           for name in CAPABILITY_OBJECTS}

    # What is loaded is the check most easily faked, so it is spelled out here
    # rather than inferred at each call site. A machine with no filament-state
    # object has told Studio nothing about its spools, and the number of
    # extruders it has is not an answer to that question.
    out["material_state"] = _material_state(facts, profile)
    return out


def _material_state(facts: dict, profile: dict | None) -> dict:
    loaded = facts.get("loaded_filaments")
    if loaded is not None:
        return {
            "known": True,
            "source": "live",
            "slots": len(loaded),
            "evidence": "the printer reports which filaments are loaded",
        }
    material = (profile or {}).get("material_state") or {}
    if facts.get("loaded_filaments_error"):
        return {
            "known": False,
            "source": "unreachable",
            "slots": None,
            "evidence": facts["loaded_filaments_error"],
            "detail": ("Studio could not ask this printer what is loaded. That is not the "
                       "printer saying it has nothing."),
        }
    if material.get("source") == "none":
        return {
            "known": False,
            "source": "profile",
            "slots": None,
            "evidence": material.get("note") or "this machine reports no filament state",
            "detail": ("Nothing on this printer says what is loaded, so Studio does not "
                       "know. A tool count is not a spool count, and Studio will not "
                       "invent slots from one."),
        }
    return {
        "known": False,
        "source": "live" if facts.get("reachable") else "none",
        "slots": None,
        "evidence": "this printer did not report which filaments are loaded",
        "detail": ("Studio does not know what is loaded. It will not guess from how many "
                   "toolheads there are."),
    }
