"""Print Failure Troubleshooter — known-good-aware advisory for U1 prints that
fail even with supports.

Read-only and advisory ONLY. Never edits slicer settings, printer profiles, or
g-code; never writes files. Core principle: a file/profile that has printed
successfully before is NOT automatically wrong — the troubleshooter compares what
*changed* (filament, condition, active temperature, first layer, support contact,
cooling, toolhead calibration) and treats speed as a later troubleshooting knob,
never an error. No guarantees of print success.
"""
from __future__ import annotations
import json

from .container import ThreeMF

SCHEMA_VERSION = "printfailure/1"
_PROJECT_SETTINGS = "Metadata/project_settings.config"

_NOT_A_GUARANTEE = "This is troubleshooting guidance, not a guarantee of print success."
_NO_AUTO_EDIT = "Studio does not auto-edit your slicer settings, printer profile, or g-code."


def _first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _num(v):
    try:
        return float(_first(v))
    except (TypeError, ValueError):
        return None


def _read_settings(path: str) -> dict:
    """Best-effort, read-only extraction of supports/speeds/filament from the
    Orca/Bambu project settings. Returns {} on any problem (never raises)."""
    try:
        tm = ThreeMF.open(path)
        if not tm.has_part(_PROJECT_SETTINGS):
            return {}
        ps = json.loads(tm.read_part(_PROJECT_SETTINGS).decode("utf-8", "replace"))
    except Exception:
        return {}
    if not isinstance(ps, dict):
        return {}
    ftypes = ps.get("filament_type") or []
    if not isinstance(ftypes, list):
        ftypes = [ftypes]
    return {
        "supports_enabled": str(_first(ps.get("enable_support")) or "0") not in ("0", "false", "False", "", "None"),
        "outer_wall_speed": _num(ps.get("outer_wall_speed")),
        "inner_wall_speed": _num(ps.get("inner_wall_speed")),
        "support_speed": _num(ps.get("support_speed")),
        "filament_types": [str(t) for t in ftypes],
    }


def _is_silk(settings: dict, *materials: str) -> bool:
    for m in materials:
        if m and "silk" in m.lower():
            return True
    return any("silk" in t.lower() for t in settings.get("filament_types", []))


def troubleshoot(path: str, symptom: str = "fails_even_with_supports",
                 known_good_print: bool | None = None, known_good_material: str | None = None,
                 failed_material: str | None = None, failure_stage: str = "unknown") -> dict:
    s = _read_settings(path)
    silk = _is_silk(s, known_good_material or "", failed_material or "")
    findings: list[dict] = []

    _STAGE_FOCUS = {
        "first_layer": ("Focus first on the first layer", "first-layer adhesion, bed leveling/mesh, and nozzle height",
                        "Check first-layer adhesion and bed leveling before anything else."),
        "supports": ("Focus first on support contact", "support contact, support Z distance, and where supports meet the model",
                     "Check support contact and Z distance before changing speeds or temperature."),
        "small_details": ("Focus first on cooling and speed on small features", "part cooling and wall/support speed on fine details",
                          "On small details, check part cooling first, then try a slower troubleshooting pass."),
        "mid_print": ("Focus first on adhesion drift and material flow", "layer adhesion over height, material flow/dryness, and cooling",
                      "For mid-print failures, check material dryness/flow and adhesion over height."),
    }
    if failure_stage in _STAGE_FOCUS:
        t, area, act = _STAGE_FOCUS[failure_stage]
        findings.append({
            "id": "failure_stage",
            "severity": "info",
            "title": t,
            "evidence": f"You said it fails at: {failure_stage.replace('_', ' ')}.",
            "explanation": f"Failures at this stage most often relate to {area}.",
            "suggested_action": act,
        })

    if known_good_print:
        known_good_context = (
            "This file/profile has printed successfully before, so the settings are "
            "not automatically wrong. Compare what changed — filament, filament "
            "condition, active print temperature, first layer, support contact, "
            "cooling, and toolhead calibration — and treat speed as a later "
            "troubleshooting knob."
        )
        findings.append({
            "id": "known_good",
            "severity": "info",
            "title": "This file may already be printable",
            "evidence": "You marked this exact file/profile as having printed successfully before.",
            "explanation": "A known-good outcome means the profile may work; a repeat failure is "
                           "more likely a difference in conditions than a wrong setting.",
            "suggested_action": "Compare against the known-good print and change one thing at a time.",
        })
    else:
        known_good_context = (
            "No known-good print was recorded. Supports help but do not guarantee success; "
            "check support contact and first layer, and make conservative changes one at a time."
        )

    if silk:
        findings.append({
            "id": "silk_variability",
            "severity": "info",
            "title": "Silk PLA can vary by brand and batch",
            "evidence": "A silk PLA filament is involved.",
            "explanation": "Different silk PLA brands and batches can behave differently; the same "
                           "file can print with one and struggle with another.",
            "suggested_action": "Check the filament manufacturer's temperature range and try a small "
                                "temperature change only within that range — never a single universal value.",
        })

    if s.get("supports_enabled") or symptom == "fails_even_with_supports":
        findings.append({
            "id": "supports_no_guarantee",
            "severity": "info",
            "title": "Supports being enabled does not guarantee success",
            "evidence": "Supports are part of this troubleshooting path.",
            "explanation": "Failures can still come from support contact, support Z distance, first-layer "
                           "adhesion, material behavior, cooling, or speed.",
            "suggested_action": "Check support contact and Z distance, and first-layer adhesion, before changing speeds.",
        })

    ow = s.get("outer_wall_speed"); sp = s.get("support_speed")
    if (ow and ow > 150) or (sp and sp > 120):
        findings.append({
            "id": "speed_knob",
            "severity": "info",
            "title": "Speed is a possible troubleshooting knob",
            "evidence": f"Outer wall ~{ow:.0f} mm/s, support ~{sp:.0f} mm/s." if (ow and sp)
                        else "Wall/support speeds are set for normal printing.",
            "explanation": "Wall/support speeds are a possible troubleshooting knob for difficult silk or "
                           "support-heavy prints. The current speed is not necessarily wrong.",
            "suggested_action": "If the same file keeps failing, try a slower troubleshooting pass and compare one change at a time.",
            "safe_starting_point": "Outer walls around 100–150 mm/s and supports around 80–120 mm/s, as a troubleshooting pass.",
        })

    findings.append({
        "id": "cooldown_temp",
        "severity": "info",
        "title": "A low temperature after a failure may be cooldown",
        "evidence": "Failure-stage troubleshooting.",
        "explanation": "A low nozzle temperature shown after a failure may be cooldown, not the active print temperature.",
        "suggested_action": "Check the slicer temperature and the printer's live temperature while it is actually printing.",
    })

    findings.append({
        "id": "multi_printer",
        "severity": "info",
        "title": "Same file failing on more than one printer",
        "evidence": "General guidance.",
        "explanation": "If the same file fails similarly on more than one printer, that points toward material, "
                       "filament condition, first layer, support contact, or profile differences — not one bad printer.",
        "suggested_action": "Compare material and conditions before replacing hardware.",
    })

    if known_good_material:
        findings.append({
            "id": "known_good_material",
            "severity": "info",
            "title": "Compare against your known-good filament",
            "evidence": f"Known-good filament: {known_good_material}."
                        + (f" Failing filament: {failed_material}." if failed_material else ""),
            "explanation": "This project has a known-good print with that filament. If another filament fails, "
                           "start by comparing filament condition, temperature range, flow, and support contact.",
            "suggested_action": "Match the known-good filament's conditions first, then change one thing at a time.",
        })

    troubleshooting_steps = [
        "Change one thing at a time so you can tell what helped.",
        "Start with material and filament condition (dryness), then active print temperature.",
        "Check first-layer adhesion and support contact / Z distance.",
        "Check part cooling and toolhead calibration.",
        "Only then try a slower troubleshooting pass on walls and supports.",
    ]
    compare_against_known_good = [
        "Filament brand / type / batch", "Filament dryness", "Active nozzle temperature during print",
        "First-layer adhesion", "Support contact / Z distance", "Cooling", "Toolhead calibration",
        "Speed (as a later troubleshooting knob)",
    ]
    disclaimers = [_NOT_A_GUARANTEE, _NO_AUTO_EDIT,
                   "Different silk PLA brands and batches can behave differently."]

    summary = ("This file may already be printable — compare what changed and adjust one thing at a time."
               if known_good_print else
               "Troubleshoot supports, material, first layer, and speed carefully — one change at a time.")

    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "symptom": symptom,
        "failure_stage": failure_stage,
        "known_good_print": bool(known_good_print),
        "summary": summary,
        "confidence": "advisory",
        "known_good_context": known_good_context,
        "findings": findings,
        "troubleshooting_steps": troubleshooting_steps,
        "compare_against_known_good": compare_against_known_good,
        "disclaimers": disclaimers,
    }
