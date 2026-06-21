"""First Layer Doctor MVP — static, advisory first-layer troubleshooting.

Read-only and offline: the user picks a first-layer symptom and gets likely
causes, safe beginner-first checks, U1-specific (advanced) checks, and slicer
settings to inspect. ADVISORY ONLY — never auto-edits printer config, slicer
settings, g-code or profiles; never guarantees a fix; never says to ignore a bad
first layer or preview. Categories are informed by Snapmaker's public U1 first-
layer troubleshooting guidance (linked from docs, not copied).

Note: this is the symptom knowledge base. Geometry-based first-layer analysis
(contact area / adhesion risk on a model) lives separately in `first_layer.py`.
"""
from __future__ import annotations

DISCLAIMER = (
    "These are likely causes and safe first checks — not a guarantee. Studio does "
    "not change your printer config, slicer settings or g-code; inspect first, then "
    "change only what you understand. Never ignore a bad first layer or slice "
    "preview — fix the cause before printing the whole model."
)

# evidence_needed values: "observation", "model", "telemetry"
_SYMPTOMS: dict[str, dict] = {
    "not_stick": {
        "title": "First layer does not stick",
        "likely_causes": ["dirty build plate", "Z-offset too high", "bed not level",
                         "bed too cold", "worn PEI coating"],
        "first_checks": ["clean the build plate (grease/dust ruin adhesion)",
                         "confirm the active profile is Snapmaker U1",
                         "re-run heated bed leveling", "check Z-offset carefully",
                         "make sure the filament is dry and flowing"],
        "u1_checks": ["(advanced) re-run heated bed leveling / load-cell check",
                      "(advanced) inspect the PEI sheet for wear or damage"],
        "slicer_checks": ["raise bed temperature for the material", "add a brim",
                          "slow the first layer"],
        "avoid": ["don't force the nozzle hard into the bed to make it stick"],
        "evidence_needed": ["observation"],
    },
    "nozzle_too_high": {
        "title": "Lines are separated / round (nozzle too high)",
        "likely_causes": ["Z-offset too high", "bed not level"],
        "first_checks": ["lower the Z-offset in small steps", "re-run heated bed leveling",
                         "clean the build plate"],
        "u1_checks": ["(advanced) re-run heated bed leveling"],
        "slicer_checks": ["slightly increase first-layer flow if still gappy after Z-offset"],
        "avoid": ["don't make one big Z-offset jump — adjust gradually"],
        "evidence_needed": ["observation"],
    },
    "nozzle_too_low": {
        "title": "Lines transparent, rough, or scraped (nozzle too low)",
        "likely_causes": ["Z-offset too low", "over-squished first layer"],
        "first_checks": ["raise the Z-offset in small steps", "re-run heated bed leveling"],
        "u1_checks": ["(advanced) re-run heated bed leveling / load-cell check"],
        "slicer_checks": ["reduce first-layer flow only if raising Z-offset isn't enough"],
        "avoid": ["don't keep printing scraped layers — it can mar the PEI sheet"],
        "evidence_needed": ["observation"],
    },
    "wrinkles": {
        "title": "Wrinkles or waves in the first layer",
        "likely_causes": ["nozzle too low", "first layer too fast", "debris under the plate"],
        "first_checks": ["raise Z-offset slightly", "slow the first layer",
                         "clean the build plate"],
        "u1_checks": ["(advanced) check for debris between the build plate and heated bed",
                      "(advanced) re-run heated bed leveling"],
        "slicer_checks": ["reduce first-layer speed"],
        "avoid": ["don't ignore wrinkles — they get printed into the part"],
        "evidence_needed": ["observation"],
    },
    "gaps": {
        "title": "Gaps between first-layer lines",
        "likely_causes": ["nozzle too high", "under-extrusion", "wet filament"],
        "first_checks": ["lower Z-offset in small steps", "dry the filament",
                         "check for a partial nozzle clog"],
        "u1_checks": ["(advanced) re-run heated bed leveling"],
        "slicer_checks": ["slightly increase first-layer flow / line width"],
        "avoid": ["don't crank flow far up to mask a clog or wet filament"],
        "evidence_needed": ["observation"],
    },
    "corners_lifting": {
        "title": "Corners lifting / early warping",
        "likely_causes": ["poor adhesion", "bed too cold", "draft/uneven cooling",
                         "insufficient contact area"],
        "first_checks": ["clean and re-level the bed", "raise bed temperature",
                         "add a brim", "reduce part cooling on the first layers"],
        "u1_checks": ["(advanced) check the PEI sheet condition"],
        "slicer_checks": ["add brim/raft", "reduce first-layer cooling", "orient for more contact area"],
        "avoid": ["don't run a draft/fan over the first layers of a warp-prone part"],
        "evidence_needed": ["observation", "model"],
    },
    "blob_drag": {
        "title": "Blob on the nozzle dragging through the first layer",
        "likely_causes": ["nozzle buildup/ooze", "previous print residue", "purge too small"],
        "first_checks": ["clean the nozzle per guidance", "check the prime/purge line",
                         "clean the build plate"],
        "u1_checks": ["(advanced) inspect the toolhead/nozzle for buildup"],
        "slicer_checks": ["ensure a prime line/skirt is enabled"],
        "avoid": ["don't pick at a hot nozzle blob with bare hands"],
        "evidence_needed": ["observation"],
    },
    "area_specific": {
        "title": "Issue appears only in one area of the plate",
        "likely_causes": ["uneven bed / leveling", "debris under the plate in that spot",
                         "local PEI wear"],
        "first_checks": ["clean the build plate", "re-run heated bed leveling",
                         "check that spot of the PEI sheet for wear"],
        "u1_checks": ["(advanced) check for debris between the build plate and heated bed",
                      "(advanced) review the bed mesh range in Fluidd/Moonraker — a later/advanced check"],
        "slicer_checks": ["move the model to a flatter area of the plate if one area is worn"],
        "avoid": ["don't assume the whole bed is bad if only one spot fails"],
        "evidence_needed": ["observation", "telemetry"],
    },
    "toolhead_specific": {
        "title": "Problem appears only with one toolhead",
        "likely_causes": ["that toolhead's nozzle buildup/clog", "toolhead-specific offset",
                         "uneven wear on that toolhead"],
        "first_checks": ["check the affected toolhead's nozzle for buildup",
                         "verify the filament for that toolhead is dry and flowing"],
        "u1_checks": ["(advanced) compare against toolhead 1 as a U1-specific reference check",
                      "(advanced) check the affected toolhead's calibration/offset"],
        "slicer_checks": ["verify the filament-to-toolhead mapping is correct"],
        "avoid": ["don't re-level the whole machine before checking the single toolhead"],
        "evidence_needed": ["observation"],
    },
    "breaks_loose": {
        "title": "Tall / small-footprint model breaks loose",
        "likely_causes": ["insufficient contact area", "tall + narrow leverage", "knocks during print"],
        "first_checks": ["add a brim or raft", "re-orient for a larger flat base",
                         "ensure strong first-layer adhesion (clean / level / Z-offset)"],
        "u1_checks": ["(advanced) check PEI condition under the part"],
        "slicer_checks": ["add brim/raft", "add supports/skirt", "re-orient for more contact area"],
        "avoid": ["don't print tall narrow parts with no brim and expect them to hold"],
        "evidence_needed": ["observation", "model"],
    },
}


def symptoms() -> list[dict]:
    return [{"id": k, "title": v["title"]} for k, v in _SYMPTOMS.items()]


def lookup(symptom: str) -> dict:
    """Advisory first-layer checklist for a symptom. Returns {result, warnings}."""
    entry = _SYMPTOMS.get(symptom)
    if not entry:
        return {"result": None,
                "warnings": [f"unknown symptom '{symptom}'. Pick one of: "
                             + ", ".join(_SYMPTOMS.keys())]}
    return {
        "result": {
            "symptom": symptom,
            "title": entry["title"],
            "likely_causes": entry["likely_causes"],
            "first_checks": entry["first_checks"],
            "u1_checks": entry["u1_checks"],
            "slicer_checks": entry["slicer_checks"],
            "avoid": entry["avoid"],
            "evidence_needed": entry["evidence_needed"],
            "disclaimer": DISCLAIMER,
        },
        "warnings": [],
    }
