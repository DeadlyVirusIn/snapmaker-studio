"""Colour planning — what a project with more colours than toolheads actually needs.

A U1 has four toolheads. Projects routinely carry more than four colours, and
every tool in this space says the same unhelpful thing: *too many colours*. That
is a count, not an answer. The useful question is **why** there are more, because
the two reasons have completely different fixes:

* **Colours that coexist within the same layers** — painted regions, or several
  objects on one plate printed layer by layer — need a toolhead each. More of
  those than toolheads means the palette has to come down.
* **Colours introduced part-way up** — a colour change recorded at a specific
  height — are already sequential. They may be handled as planned swaps instead
  of costing a toolhead.

Studio classifies each colour into one of those, or into **cannot classify**, and
refuses to guess between them.

Three honesty constraints shape the implementation:

1. **Painted colour is read, not guessed — and only as far as it goes.** Studio
   decodes the project's own per-facet paint (:mod:`painted_color`), so the
   filaments a painted region uses, how much area each covers and the heights
   each spans are facts here rather than an "unclassified". What painting still
   cannot settle is whether two colours land on the *same printed layer*:
   overlapping heights prove they *can*, and only slicing proves they do. A
   colour whose painting cannot be compared stays unclassified with the reason,
   never in the optimistic bucket — that is the bucket that would tell someone
   their project is easier than it is.

2. **Layer numbers do not exist in an unsliced project.** A colour change is
   recorded at a height. Studio reports the height, and offers a layer number only
   as an estimate, labelled as one, computed from the project's own layer height.

3. **A slot a project paints with but never lists is reported, not silently
   renumbered.** It is a defect in the project, and guessing which filament was
   meant would be inventing a colour.

Studio does not promise that a manual-swap workflow will work — that depends on
the slicer. It reports what the file contains and what that implies.
"""
from __future__ import annotations

import json
import re

from . import painted_color
from .container import ThreeMF
from .errors import UnsafeArchive

SCHEMA_VERSION = "colorplan/1"

DEFAULT_TOOLHEADS = 4

PROJECT_SETTINGS = "Metadata/project_settings.config"
MODEL_SETTINGS = "Metadata/model_settings.config"
CUSTOM_GCODE = "Metadata/custom_gcode_per_layer.xml"

# How a colour is used.
SIMULTANEOUS = "simultaneous"   # needs a toolhead: it shares layers with others
LAYER_BASED = "layer_based"     # introduced at a height; a planned swap is possible
UNCLASSIFIED = "unclassified"   # Studio cannot tell, and says so

# Overall answers.
FITS = "fits"
POSSIBLE_WITH_SWAPS = "possible_with_swaps"
NEEDS_REDUCTION = "needs_reduction"
CANNOT_CLASSIFY = "cannot_classify"

_EXTRUDER_RE = re.compile(r'key="extruder"\s+value="(\d+)"')
_LAYER_TAG_RE = re.compile(r"<layer\b[^>]*>")
_ATTR_RE = re.compile(r'([A-Za-z_:][\w.:-]*)\s*=\s*"([^"]*)"')


def _settings(tm: ThreeMF) -> dict:
    if not tm.has_part(PROJECT_SETTINGS):
        return {}
    try:
        out = json.loads(tm.read_part(PROJECT_SETTINGS).decode("utf-8", "ignore"))
        return out if isinstance(out, dict) else {}
    except Exception:
        return {}


def _text(tm: ThreeMF, part: str) -> str:
    if not tm.has_part(part):
        return ""
    try:
        return tm.read_part(part).decode("utf-8", "ignore")
    except Exception:
        return ""


def _float(value):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _layer_changes(raw: str) -> list[dict]:
    """Colour changes recorded against a height, from the project's own record.

    Attributes vary between slicer versions, so each tag is read for whatever it
    carries rather than matched against a fixed schema.
    """
    out = []
    for tag in _LAYER_TAG_RE.findall(raw):
        attrs = dict(_ATTR_RE.findall(tag))
        z = _float(attrs.get("top_z") or attrs.get("print_z") or attrs.get("z"))
        extruder = attrs.get("extruder")
        if z is None and extruder is None:
            continue
        out.append({
            "z_mm": z,
            "extruder": int(extruder) if (extruder or "").isdigit() else None,
            "color": attrs.get("color") or attrs.get("colour"),
            "kind": attrs.get("gcode") or attrs.get("type"),
        })
    return out


def _estimated_layer(z_mm: float | None, layer_height: float | None,
                     first_layer: float | None) -> int | None:
    """A layer number is not in an unsliced project. This is arithmetic on the
    project's own layer height and is labelled an estimate wherever it is shown."""
    if z_mm is None or not layer_height or layer_height <= 0:
        return None
    first = first_layer if (first_layer and first_layer > 0) else layer_height
    if z_mm <= first:
        return 1
    return int(round((z_mm - first) / layer_height)) + 1


def _colour_entry(index: int, colour: str | None, material: str | None,
                  usage: str, evidence: str, **extra) -> dict:
    entry = {"slot": index, "color": colour, "material": material,
             "usage": usage, "evidence": evidence}
    entry.update(extra)
    return entry


def analyse(path: str, toolheads: int | None = None) -> dict:
    """Classify a project's colours against the number of toolheads available.

    ``toolheads`` should be the count a printer actually reported. When it is
    None, the U1's published four are used and the result says so — the caller
    must not present a default as a reading from the machine.
    """
    measured = toolheads is not None
    try:
        tm = ThreeMF.open(path)
    except UnsafeArchive as e:
        return _unavailable(str(e))
    except Exception:
        return _unavailable("Studio could not read this file as a 3MF project.")

    cfg = _settings(tm)
    colours = cfg.get("filament_colour") or []
    materials = cfg.get("filament_type") or []
    if not isinstance(colours, list) or not colours:
        return _unavailable("This project does not list any filament colours.")

    total = len(colours)
    tools = max(1, int(toolheads or DEFAULT_TOOLHEADS))

    model_settings = _text(tm, MODEL_SETTINGS)
    # Object/part `extruder` values are 1-based, the same convention plate_remap
    # uses — that module's mapping was validated against a real nine-plate U1
    # project, so the two must agree or one of them is wrong on real files.
    assigned = {int(v) for v in _EXTRUDER_RE.findall(model_settings)}
    assigned = {i for i in assigned if 1 <= i <= total}

    paint = painted_color.read_container(tm)
    by_slot = {entry["slot"]: entry for entry in paint.get("slots", [])}
    paint_by_slot = {slot: entry for slot, entry in by_slot.items()
                     if entry.get("from_painting")}
    together = painted_color.coexistence(paint)
    overlap_by_slot: dict[int, list[dict]] = {}
    for pair in together["pairs"]:
        for slot in pair["slots"]:
            overlap_by_slot.setdefault(slot, []).append(pair)
    painted = bool(paint_by_slot) or paint.get("painted_triangle_count", 0) > 0
    painted_triangles = paint.get("painted_triangle_count", 0)

    layer_height = _float(cfg.get("layer_height"))
    first_layer = _float(cfg.get("initial_layer_print_height"))
    changes = _layer_changes(_text(tm, CUSTOM_GCODE))
    change_by_slot: dict[int, dict] = {}
    for change in changes:
        slot = change.get("extruder")
        if slot and 1 <= slot <= total and slot not in change_by_slot:
            change_by_slot[slot] = change

    # A colour whose height was never measured cannot be proven separate from
    # anything, and every colour it might be separate from has to know that.
    measured_slots = {entry["slot"] for entry in paint.get("slots", [])
                      if entry.get("z_min_mm") is not None}
    unmeasured = sorted((set(assigned) | set(paint_by_slot)) - measured_slots)

    simultaneous, layer_based, unclassified = [], [], []
    for index in range(1, total + 1):
        colour = colours[index - 1]
        material = materials[index - 1] if index - 1 < len(materials) else None
        change = change_by_slot.get(index)
        brush = by_slot.get(index)
        if index in assigned or brush:
            usage, evidence, extra = _height_usage(
                index, brush, index in assigned, overlap_by_slot.get(index, []),
                unmeasured, layer_height, first_layer)
            entry = _colour_entry(index, colour, material, usage, evidence,
                                  **{**_paint_facts(paint_by_slot.get(index)), **extra})
            {SIMULTANEOUS: simultaneous, LAYER_BASED: layer_based,
             UNCLASSIFIED: unclassified}[usage].append(entry)
        elif change:
            z = change.get("z_mm")
            estimate = _estimated_layer(z, layer_height, first_layer)
            layer_based.append(_colour_entry(
                index, colour, material, LAYER_BASED,
                f"the project records a colour change to this slot at "
                f"{z:.2f} mm" if z is not None else
                "the project records a colour change to this slot",
                from_z_mm=round(z, 2) if z is not None else None,
                estimated_layer=estimate,
                layer_is_estimated=estimate is not None))
        else:
            unclassified.append(_colour_entry(
                index, colour, material, UNCLASSIFIED,
                "Studio found no object, painted region or colour change using this "
                "slot, so it cannot say how it is used"))

    # A project can paint with a slot it never lists. That is the project's
    # defect, and it is reported rather than renumbered onto a filament that
    # happens to exist.
    unlisted = sorted(slot for slot in paint_by_slot if slot > total or slot < 1)

    verdict = _verdict(total, tools, simultaneous, layer_based, unclassified)
    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "color_count": total,
        "toolheads": tools,
        "toolheads_measured": measured,
        "toolheads_source": ("your printer reported this many toolheads" if measured
                             else "the Snapmaker U1's published four toolheads — "
                                  "Studio did not read this from a printer"),
        "painted_regions": painted,
        "painted_marker_count": painted_triangles,
        "painted": _painted_summary(paint, paint_by_slot, together, unlisted,
                                    colours, materials),
        "simultaneous": simultaneous,
        "layer_based": layer_based,
        "unclassified": unclassified,
        "verdict": verdict,
        "headline": _headline(total, tools, verdict),
        "summary": _summary(verdict, tools, simultaneous, layer_based, unclassified),
        "guidance": _guidance(verdict, bool(paint_by_slot), unlisted),
        "disclaimer": ("Studio reads what the project records — including its painting — "
                       "but it does not slice. Heights that overlap show two colours can "
                       "meet on a layer; only the slice proves that they do."),
    }


def _verdict(total: int, tools: int, simultaneous: list, layer_based: list,
             unclassified: list) -> str:
    if total <= tools:
        return FITS
    if len(simultaneous) > tools:
        return NEEDS_REDUCTION
    if len(simultaneous) + len(unclassified) <= tools:
        return FITS if not layer_based else POSSIBLE_WITH_SWAPS
    if unclassified:
        return CANNOT_CLASSIFY
    return POSSIBLE_WITH_SWAPS


def _headline(total: int, tools: int, verdict: str) -> str:
    lead = f"{total} colour{'s' if total != 1 else ''}, {tools} toolhead{'s' if tools != 1 else ''}"
    if verdict == FITS:
        return f"{lead} — every colour has a toolhead."
    if verdict == POSSIBLE_WITH_SWAPS:
        return f"{lead} — possible without repainting."
    if verdict == NEEDS_REDUCTION:
        return f"{lead} — needs colour reduction."
    return f"{lead} — Studio cannot classify this safely."


def _summary(verdict: str, tools: int, simultaneous: list, layer_based: list,
             unclassified: list) -> str:
    if verdict == FITS:
        return "Nothing to resolve: this project fits the toolheads you have."
    if verdict == POSSIBLE_WITH_SWAPS:
        heights = ", ".join(
            f"{c['from_z_mm']:.1f} mm" for c in layer_based
            if c.get("from_z_mm") is not None) or "a later height"
        return (f"{len(simultaneous)} colour(s) share layers and need a toolhead each. "
                f"{len(layer_based)} appear only from {heights}, so they may be handled "
                "as planned swaps rather than by reducing the painted palette.")
    if verdict == NEEDS_REDUCTION:
        return (f"{len(simultaneous)} colours share the same layers and each needs its own "
                f"toolhead, which is more than the {tools} available. Some of them have to "
                "be merged before this can print as one job.")
    return (f"{len(unclassified)} colour(s) could not be classified, so Studio will not "
            "tell you whether swaps would work. The reason is on each colour below; "
            "opening the project in Snapmaker Orca settles it.")


def _guidance(verdict: str, painted: bool = False,
              unlisted: list | None = None) -> list[str]:
    lines: list[str]
    if verdict == FITS:
        lines = ["Load the colours in the order the project lists them."]
    elif verdict == POSSIBLE_WITH_SWAPS:
        lines = [
            "Assign the colours that share layers to your toolheads.",
            "Plan the remaining colour(s) as a swap at the height shown.",
            "Confirm in Snapmaker Orca before printing — Studio does not slice.",
        ]
    elif verdict == NEEDS_REDUCTION:
        lines = [
            "Merge the closest colours in the project, or split it across plates.",
            "Reducing painted colours is a change to the model, so make it on a copy.",
        ]
    else:
        lines = [
            "Open the project in Snapmaker Orca and look at the colour assignment.",
            "Studio reads the painting itself; what needs the slicer is whether two "
            "colours end up on the same layer.",
        ]
    for slot in (unlisted or []):
        lines.append(f"This project paints with slot {slot} but does not list a "
                     f"filament for it — check the colour assignment in Orca.")
    return lines


def _unavailable(reason: str) -> dict:
    return {"schema_version": SCHEMA_VERSION, "available": False, "reason": reason,
            "color_count": 0, "toolheads": DEFAULT_TOOLHEADS,
            "simultaneous": [], "layer_based": [], "unclassified": [],
            "verdict": CANNOT_CLASSIFY, "headline": reason, "summary": reason,
            "guidance": [], "painted_regions": False, "painted_marker_count": 0,
            "painted": {"available": False, "reason": reason, "slots": [],
                        "headline": None}}


# ---------------------------------------------------------------------------
# Painted colour.
#
# The paint is decoded facet by facet in painted_color; what happens here is the
# step after: turning "slot 4 is painted between 38.2 and 61.0 mm" into an answer
# about whether slot 4 needs a toolhead of its own. The rule is that a colour
# only leaves the "needs a toolhead" bucket when its separation from every other
# colour is *proven*, and that an unproven separation is stated as unproven.
# ---------------------------------------------------------------------------
def _paint_facts(brush: dict | None) -> dict:
    """The measured painting facts a UI can show beside a colour."""
    if not brush:
        return {"painted": False}
    return {
        "painted": True,
        "painted_facets": brush.get("triangles_touching"),
        "painted_area_mm2": round(brush.get("area_mm2") or 0.0, 2),
        "painted_z_min_mm": brush.get("painted_z_min_mm"),
        "painted_z_max_mm": brush.get("painted_z_max_mm"),
        # Where the slot prints at all, which is what a shared layer depends on
        # and is wider than the painting whenever the object itself uses it.
        "used_z_min_mm": brush.get("z_min_mm"),
        "used_z_max_mm": brush.get("z_max_mm"),
    }


def _height_usage(slot: int, bucket: dict | None, assigned: bool, pairs: list,
                  unmeasured: list, layer_height, first_layer):
    """How a colour is used, decided from measured heights wherever there are any.

    This is the same question for a painted colour and for a colour assigned to a
    whole object: does it ever have to be on the plate at the same time as
    another? Proven overlap costs a toolhead. Proven separation from everything
    else leaves the colour available as a planned swap. Anything else is
    unclassified with the reason — never the optimistic answer.

    Studio used to answer "needs a toolhead" for every assigned colour, because it
    had not measured where those objects were. It has now, so the answer is
    evidence rather than a safe assumption; where the measurement is missing, the
    safe assumption is what remains.
    """
    low = (bucket or {}).get("z_min_mm")
    high = (bucket or {}).get("z_max_mm")
    painted = bool((bucket or {}).get("from_painting"))
    overlapping = sorted({other for pair in pairs if pair["verdict"] == "overlaps"
                          for other in pair["slots"] if other != slot})
    if low is None or high is None:
        if assigned:
            return SIMULTANEOUS, (
                "an object on the plate is assigned this colour and Studio could "
                "not measure where that object sits, so it must be assumed to "
                "share layers with the others"), {}
        return UNCLASSIFIED, (
            "this project paints with this colour, but the painted facets carry "
            "no readable height, so Studio cannot say whether it shares layers "
            "with the others"), {}
    if overlapping:
        names = ", ".join(str(other) for other in overlapping)
        return SIMULTANEOUS, (
            f"used between {low:.2f} mm and {high:.2f} mm, where "
            f"slot{'s' if len(overlapping) > 1 else ''} {names} "
            f"{'are' if len(overlapping) > 1 else 'is'} used too, so the two can "
            "meet on a layer and each needs a toolhead"), {}
    others = [other for other in unmeasured if other != slot]
    if others:
        names = ", ".join(str(other) for other in others)
        return UNCLASSIFIED, (
            f"used between {low:.2f} mm and {high:.2f} mm, but slot{'s' if len(others) > 1 else ''} "
            f"{names} {'have' if len(others) > 1 else 'has'} no measured height, "
            "so a separation cannot be proven"), {}
    estimate = _estimated_layer(low, layer_height, first_layer)
    lead = "painted only" if painted else "used only"
    return LAYER_BASED, (
        f"{lead} between {low:.2f} mm and {high:.2f} mm, and every other colour "
        "ends below that or starts above it, so this one never has to share a "
        "layer"), {
        "from_z_mm": round(low, 2),
        "estimated_layer": estimate,
        "layer_is_estimated": estimate is not None,
    }


def _painted_summary(paint: dict, paint_by_slot: dict, together: dict,
                     unlisted: list, colours: list, materials: list) -> dict:
    """What the painting is, in one place, for the UI and the disclosure panel."""
    if not paint.get("available"):
        return {"available": False, "reason": paint.get("reason"),
                "slots": [], "headline": None}
    slots = sorted(paint_by_slot)
    if not slots:
        return {"available": True, "painted": False, "slots": [],
                "headline": None, "reason": paint.get("reason")}
    count = len(slots)
    return {
        "available": True,
        "painted": True,
        "dialect": paint.get("dialect"),
        "format_version": paint.get("format_version"),
        "format_version_known": paint.get("format_version_known"),
        "slots": slots,
        "unlisted_slots": unlisted,
        "painted_facets": paint.get("painted_triangle_count"),
        "malformed_facets": paint.get("malformed_triangle_count"),
        "facets_outside_mesh": paint.get("facets_outside_mesh"),
        "truncated": paint.get("truncated"),
        "confidence": paint.get("confidence"),
        "objects": paint.get("objects"),
        "coexistence": together,
        "headline": (f"Parts of this model are painted with {count} filament "
                     f"colour{'s' if count != 1 else ''}."),
        "evidence": paint.get("evidence"),
    }
