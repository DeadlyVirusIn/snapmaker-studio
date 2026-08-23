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

Two honesty constraints shape the implementation:

1. **Painted colour cannot be enumerated without slicing.** Per-triangle paint
   data is stored in an encoded form, so Studio can prove a project *has* painted
   regions but not which colours they use. Those colours go to "cannot classify"
   with that reason — never silently into the sequential bucket, which is the
   bucket that would tell someone their project is easier than it is.

2. **Layer numbers do not exist in an unsliced project.** A colour change is
   recorded at a height. Studio reports the height, and offers a layer number only
   as an estimate, labelled as one, computed from the project's own layer height.

Studio does not promise that a manual-swap workflow will work — that depends on
the slicer. It reports what the file contains and what that implies.
"""
from __future__ import annotations

import json
import re

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

_PAINT_TOKENS = (b"paint_color", b"mmu_segmentation")
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

    painted_triangles = 0
    for part in tm.list_parts():
        if part.endswith(".model"):
            try:
                blob = tm.read_part(part)
            except Exception:
                continue
            painted_triangles += sum(blob.count(tok) for tok in _PAINT_TOKENS)
    painted = painted_triangles > 0

    layer_height = _float(cfg.get("layer_height"))
    first_layer = _float(cfg.get("initial_layer_print_height"))
    changes = _layer_changes(_text(tm, CUSTOM_GCODE))
    change_by_slot: dict[int, dict] = {}
    for change in changes:
        slot = change.get("extruder")
        if slot and 1 <= slot <= total and slot not in change_by_slot:
            change_by_slot[slot] = change

    simultaneous, layer_based, unclassified = [], [], []
    for index in range(1, total + 1):
        colour = colours[index - 1]
        material = materials[index - 1] if index - 1 < len(materials) else None
        change = change_by_slot.get(index)
        if index in assigned:
            simultaneous.append(_colour_entry(
                index, colour, material, SIMULTANEOUS,
                "an object on the plate is assigned this colour, and a plate prints "
                "layer by layer"))
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
        elif painted:
            unclassified.append(_colour_entry(
                index, colour, material, UNCLASSIFIED,
                "this project has painted regions, and painted colour is stored in a "
                "form Studio cannot read without slicing — so it will not guess "
                "whether this colour shares layers with the others"))
        else:
            unclassified.append(_colour_entry(
                index, colour, material, UNCLASSIFIED,
                "Studio found no object, painted region or colour change using this "
                "slot, so it cannot say how it is used"))

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
        "simultaneous": simultaneous,
        "layer_based": layer_based,
        "unclassified": unclassified,
        "verdict": verdict,
        "headline": _headline(total, tools, verdict),
        "summary": _summary(verdict, tools, simultaneous, layer_based, unclassified),
        "guidance": _guidance(verdict),
        "disclaimer": ("Studio reads what the project records; it does not slice. Whether "
                       "a colour change can be handled as a swap depends on your slicer."),
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
            "tell you whether swaps would work. Open the project in Snapmaker Orca to see "
            "how the colours are used.")


def _guidance(verdict: str) -> list[str]:
    if verdict == FITS:
        return ["Load the colours in the order the project lists them."]
    if verdict == POSSIBLE_WITH_SWAPS:
        return [
            "Assign the colours that share layers to your toolheads.",
            "Plan the remaining colour(s) as a swap at the height shown.",
            "Confirm in Snapmaker Orca before printing — Studio does not slice.",
        ]
    if verdict == NEEDS_REDUCTION:
        return [
            "Merge the closest colours in the project, or split it across plates.",
            "Reducing painted colours is a change to the model, so make it on a copy.",
        ]
    return [
        "Open the project in Snapmaker Orca and look at the colour assignment.",
        "Studio only reports what the file records; painted colour needs slicing to read.",
    ]


def _unavailable(reason: str) -> dict:
    return {"schema_version": SCHEMA_VERSION, "available": False, "reason": reason,
            "color_count": 0, "toolheads": DEFAULT_TOOLHEADS,
            "simultaneous": [], "layer_based": [], "unclassified": [],
            "verdict": CANNOT_CLASSIFY, "headline": reason, "summary": reason,
            "guidance": [], "painted_regions": False}
