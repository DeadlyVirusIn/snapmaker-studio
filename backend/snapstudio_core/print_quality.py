"""Print Quality Doctor MVP — static, advisory symptom knowledge base.

Read-only and offline: the user picks a symptom seen in a bad print/preview and
gets likely causes + safe first checks. ADVISORY ONLY — never auto-edits settings
or g-code, never guarantees a fix, never tells the user to ignore a bad preview.
Design: docs/design/PRINT_QUALITY_DOCTOR.md.
"""
from __future__ import annotations

DISCLAIMER = (
    "These are likely causes and safe first checks — not a guarantee. Studio does "
    "not change your settings or g-code; inspect first, then change only what you "
    "understand. Never ignore a bad slice preview — fix the cause first."
)

# evidence_needed values: "observation", "model", "telemetry"
_SYMPTOMS: dict[str, dict] = {
    "stringing": {
        "title": "Stringing / wisps",
        "likely_causes": ["wet filament", "retraction too low", "nozzle temperature too high"],
        "first_checks": ["dry the filament", "lower the nozzle temperature a little",
                         "check retraction distance and speed"],
        "orca_paths": ["Filament → temperature", "Quality → retraction"],
        "hardware_checks": ["store filament dry; check for a partial nozzle clog"],
        "avoid": ["don't crank retraction very high in one step — change gradually"],
        "evidence_needed": ["observation", "telemetry"],
    },
    "ringing": {
        "title": "Ringing / ghosting",
        "likely_causes": ["speed/acceleration too high", "loose belts", "frame vibration/resonance"],
        "first_checks": ["reduce speed and acceleration/jerk", "check belt tension",
                         "confirm input shaping is configured"],
        "orca_paths": ["Speed → acceleration / jerk"],
        "hardware_checks": ["check belt tension; ensure the printer sits on a stable surface"],
        "avoid": ["don't disable input shaping to 'fix' it"],
        "evidence_needed": ["observation", "telemetry"],
    },
    "layer_shift": {
        "title": "Layer shift",
        "likely_causes": ["belt/pulley slip", "stepper skipping", "collisions with the print",
                         "acceleration too high"],
        "first_checks": ["inspect belts and pulley grub screws", "clear any obstructions",
                         "lower acceleration"],
        "orca_paths": ["Speed → acceleration"],
        "hardware_checks": ["check motor current and belt tension; look for binding on the axes"],
        "avoid": ["don't keep reprinting at the same settings hoping it resolves"],
        "evidence_needed": ["observation", "telemetry"],
    },
    "warping": {
        "title": "Warping / lifting corners",
        "likely_causes": ["poor bed adhesion", "bed too cold", "uneven cooling/draft", "no brim"],
        "first_checks": ["clean and level the bed, set Z-offset", "raise bed temperature",
                         "add a brim or raft", "reduce part cooling on the first layers"],
        "orca_paths": ["Plate → adhesion (brim/raft)", "Filament → bed temperature"],
        "hardware_checks": ["use an enclosure / avoid drafts; clean the build plate"],
        "avoid": ["don't over-tighten the nozzle into the bed to force adhesion"],
        "evidence_needed": ["observation", "telemetry"],
    },
    "bed_adhesion": {
        "title": "Won't stick / lets go of the bed",
        "likely_causes": ["dirty or greasy plate", "Z-offset too high (nozzle too far)",
                          "bed too cold for the material", "first layer too fast", "no brim"],
        "first_checks": ["clean the plate (soap/water or IPA)", "re-level and lower the Z-offset a little",
                         "raise the bed temperature for your material", "slow the first layer",
                         "add a brim"],
        "orca_paths": ["Plate → adhesion (brim/raft)", "Filament → bed temperature",
                       "Quality → first layer speed", "Printer → Z-offset"],
        "hardware_checks": ["clean the build plate; check the plate isn't worn; avoid drafts"],
        "avoid": ["don't drive the nozzle hard into the bed to force it to stick"],
        "evidence_needed": ["observation", "telemetry"],
    },
    "support_failure": {
        "title": "Supports fail or won't separate",
        "likely_causes": ["support Z-distance too large (no contact) or too small (fused)",
                          "supports under-supported / toppling", "overhang too steep for the angle",
                          "first layer of supports not adhering", "too fast over supports"],
        "first_checks": ["adjust the support Z-distance one step at a time",
                         "increase support density / interface layers under steep overhangs",
                         "lower the support and overhang speed", "check first-layer adhesion under supports"],
        "orca_paths": ["Support → Z-distance", "Support → density / interface", "Support → speed"],
        "hardware_checks": ["confirm part cooling is working; check first-layer calibration"],
        "avoid": ["don't assume turning supports on is enough — contact and Z-distance still decide the result"],
        "evidence_needed": ["observation", "model"],
    },
    "first_layer": {
        "title": "Missing / poor first layer",
        "likely_causes": ["Z-offset too high", "bed not level", "dirty plate", "flow too low"],
        "first_checks": ["re-level and adjust Z-offset", "clean the plate", "slow the first layer"],
        "orca_paths": ["Quality → first layer", "Printer → Z-offset"],
        "hardware_checks": ["clean the build plate; check the nozzle isn't partially clogged"],
        "avoid": ["don't print the whole model to 'see if it fixes itself'"],
        "evidence_needed": ["observation", "model"],
    },
    "blobs": {
        "title": "Blobs / zits",
        "likely_causes": ["pressure mismatch", "retraction/coasting", "Z-seam placement",
                         "over-extrusion"],
        "first_checks": ["calibrate flow", "adjust seam alignment", "tune retraction"],
        "orca_paths": ["Quality → seam", "Quality → retraction"],
        "hardware_checks": ["check the nozzle for buildup"],
        "avoid": ["don't raise flow to 'fill gaps' if blobs are the problem"],
        "evidence_needed": ["observation"],
    },
    "under_extrusion": {
        "title": "Under-extrusion",
        "likely_causes": ["partial clog", "wet or too-cold filament", "extruder slipping",
                         "nozzle wear"],
        "first_checks": ["check/clean the nozzle", "dry the filament", "raise temperature slightly",
                         "verify flow"],
        "orca_paths": ["Filament → flow", "Filament → temperature"],
        "hardware_checks": ["inspect for a clog; check extruder gear and idler tension; nozzle wear"],
        "avoid": ["don't push flow far above 100% to mask a clog"],
        "evidence_needed": ["observation", "telemetry"],
    },
    "rough_surface": {
        "title": "Rough / inconsistent surface (incl. coarse layer lines)",
        "likely_causes": ["wet filament", "temperature instability", "layer height too large",
                         "mechanical play"],
        "first_checks": ["dry the filament", "stabilize temperature", "reduce layer height",
                         "check frame and belts"],
        "orca_paths": ["Quality → layer height", "Filament → flow"],
        "hardware_checks": ["check for axis play; consider adaptive/variable layer height"],
        "avoid": ["don't assume it's the model before checking material and temperature"],
        "evidence_needed": ["observation"],
    },
    "bridging": {
        "title": "Poor bridging / overhangs",
        "likely_causes": ["insufficient cooling", "overhang too steep", "speed too high"],
        "first_checks": ["set part cooling fan to 100%", "reduce overhang/bridge speed",
                         "add supports for steep overhangs"],
        "orca_paths": ["Cooling → fan", "Support"],
        "hardware_checks": ["confirm the part cooling fan actually spins"],
        "avoid": ["don't remove supports from steep overhangs and expect a clean result"],
        "evidence_needed": ["observation", "model"],
    },
    "color_bleed": {
        "title": "Color bleeding / waste (multi-material)",
        "likely_causes": ["purge/flush volumes too low", "wrong filament mapping", "ooze between tools"],
        "first_checks": ["raise flush volumes", "verify the slot mapping", "check the prime tower"],
        "orca_paths": ["Multi-material → flush volumes", "prime tower"],
        "hardware_checks": ["check nozzle/toolhead for ooze and residue"],
        "avoid": ["don't disable the prime tower to save filament if colors bleed"],
        "evidence_needed": ["observation", "model"],
    },
}


def symptoms() -> list[dict]:
    """The pickable symptom list (id + title)."""
    return [{"id": k, "title": v["title"]} for k, v in _SYMPTOMS.items()]


def lookup(symptom: str) -> dict:
    """Advisory checklist for a symptom. Returns {result, warnings}."""
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
            "orca_paths": entry["orca_paths"],
            "hardware_checks": entry["hardware_checks"],
            "avoid": entry["avoid"],
            "evidence_needed": entry["evidence_needed"],
            "disclaimer": DISCLAIMER,
        },
        "warnings": [],
    }
