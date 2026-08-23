"""Plate placement — is each object actually *on* the U1's bed, and can that be fixed?

A project authored for another printer carries its objects at that printer's
coordinates. A 40 mm part sitting at X=300 on a 350 mm bed is small enough for the
U1 by every size check, and still lands completely off a 270 mm plate. Size checks
never catch it, because nothing is too big — it is in the wrong place.

Snapmaker Orca's answer to this is a bare "out of bounds", and the community's
answer is "hit Arrange and hope". This module gives the specific answer instead:
which object is off the plate, by how much and on which edge, whether one
translation would bring the whole arrangement back on, and — when it would —
writes a new copy with exactly that translation applied.

Discipline, in order of importance:

* **The original is never modified.** A fix writes a new file.
* **Only the placement changes.** The rewrite touches the translation component of
  build-item transforms and nothing else: no meshes, no painted colour, no
  settings, no other archive entry. Rotation and scale are carried through
  untouched, so the creator's arrangement survives.
* **It refuses rather than guesses.** If one translation cannot bring everything
  on-plate, or the project has several plates laid out on a grid this module
  cannot read, it says so and stops. A half-moved plate is worse than an honest
  "open this in Orca and use Arrange".
"""
from __future__ import annotations

import json
import re
from importlib.resources import files
from pathlib import Path

from .container import ThreeMF

SCHEMA_VERSION = "placement/1"

ROOT_MODEL = "3D/3dmodel.model"

# Objects are not placed at the extreme edge in practice: skirt, brim and the
# prime tower all need room. A hair of margin keeps a "just touching the edge"
# result from reading as safe.
EDGE_MARGIN_MM = 0.5

_ITEM_TAG_RE = re.compile(r"<item\b[^>]*/?>")
_TRANSFORM_ATTR_RE = re.compile(r'(\btransform\s*=\s*")([^"]*)(")')


def _u1_printable_area() -> list[str]:
    template = json.loads(
        (files("snapstudio_core.data") / "templates" / "u1_base_project_settings.json")
        .read_text("utf-8"))
    return template.get("printable_area") or []


def parse_printable_area(area) -> dict | None:
    """Turn a slicer's printable_area polygon into an axis-aligned rectangle.

    The value is a list of ``"XxY"`` corner strings. Only rectangular beds are
    handled; anything else returns None so the caller reports "unknown" instead
    of pretending a delta bed is a box.
    """
    if not isinstance(area, (list, tuple)) or len(area) < 3:
        return None
    xs, ys = [], []
    for corner in area:
        parts = str(corner).lower().split("x")
        if len(parts) != 2:
            return None
        try:
            xs.append(float(parts[0]))
            ys.append(float(parts[1]))
        except ValueError:
            return None
    return {"min_x": min(xs), "min_y": min(ys), "max_x": max(xs), "max_y": max(ys)}


def u1_bed_rect() -> dict:
    """The U1's printable rectangle, from Studio's own U1 profile template."""
    rect = parse_printable_area(_u1_printable_area())
    # The template is shipped with the package and is rectangular; the fallback
    # exists only so a corrupted install degrades to the published volume.
    return rect or {"min_x": 0.0, "min_y": 0.0, "max_x": 270.0, "max_y": 270.0}


def _source_bed(tm: ThreeMF) -> dict | None:
    part = "Metadata/project_settings.config"
    if not tm.has_part(part):
        return None
    try:
        cfg = json.loads(tm.read_part(part).decode("utf-8", "ignore"))
    except Exception:
        return None
    return parse_printable_area(cfg.get("printable_area"))


def _overhang(bounds: dict, bed: dict) -> dict:
    """How far an item pokes past each edge, in mm. Zero means inside."""
    lo, hi = bounds["min"], bounds["max"]
    return {
        "left": round(max(0.0, (bed["min_x"] + EDGE_MARGIN_MM) - lo[0]), 2),
        "right": round(max(0.0, hi[0] - (bed["max_x"] - EDGE_MARGIN_MM)), 2),
        "front": round(max(0.0, (bed["min_y"] + EDGE_MARGIN_MM) - lo[1]), 2),
        "back": round(max(0.0, hi[1] - (bed["max_y"] - EDGE_MARGIN_MM)), 2),
    }


def _edges_text(over: dict) -> str:
    named = [name for name, mm in over.items() if mm > 0]
    return ", ".join(named)


def _cluster_bounds(items: list[dict]) -> dict:
    xs_lo = min(i["bounds"]["min"][0] for i in items)
    ys_lo = min(i["bounds"]["min"][1] for i in items)
    xs_hi = max(i["bounds"]["max"][0] for i in items)
    ys_hi = max(i["bounds"]["max"][1] for i in items)
    return {"min_x": xs_lo, "min_y": ys_lo, "max_x": xs_hi, "max_y": ys_hi}


def _centering_offset(cluster: dict, bed: dict) -> dict:
    """The translation that centres the whole arrangement on the bed."""
    return {
        "x": round(((bed["min_x"] + bed["max_x"]) / 2.0)
                   - ((cluster["min_x"] + cluster["max_x"]) / 2.0), 3),
        "y": round(((bed["min_y"] + bed["max_y"]) / 2.0)
                   - ((cluster["min_y"] + cluster["max_y"]) / 2.0), 3),
    }


def _fits_after(cluster: dict, bed: dict, offset: dict) -> bool:
    return (cluster["min_x"] + offset["x"] >= bed["min_x"] + EDGE_MARGIN_MM - 1e-6
            and cluster["max_x"] + offset["x"] <= bed["max_x"] - EDGE_MARGIN_MM + 1e-6
            and cluster["min_y"] + offset["y"] >= bed["min_y"] + EDGE_MARGIN_MM - 1e-6
            and cluster["max_y"] + offset["y"] <= bed["max_y"] - EDGE_MARGIN_MM + 1e-6)


def _unavailable(reason: str) -> dict:
    return {"schema_version": SCHEMA_VERSION, "available": False, "reason": reason,
            "items": [], "off_plate": [], "fixable": False}


# --- multi-plate grids ------------------------------------------------------
#
# A slicer lays several build plates out on one coordinate grid: plate 1 around
# the bed centre, plate 2 a fixed stride further along X, and so on. The stride
# is the source printer's bed width plus a gap the slicer chose. Move a project
# to a printer with a different bed and every plate past the first lands in the
# wrong place — which is why objects from multi-plate projects turn up on the
# wrong plate after a naive conversion.
#
# Studio does not assume a stride. It measures the spacing the file actually
# uses, checks that the measurement explains every plate's position, and refuses
# if it does not. Guessing here puts an object on the wrong plate silently.

# How far a plate's measured centre may sit from the fitted grid before the grid
# is judged not to describe this project.
GRID_TOLERANCE_MM = 5.0


def _plates_from_model_settings(tm: ThreeMF) -> list[dict]:
    """UI plate number -> the object ids on it, from the project's own records."""
    part = "Metadata/model_settings.config"
    if not tm.has_part(part):
        return []
    try:
        from .plate_remap import _parse_plates

        return _parse_plates(tm.read_part(part).decode("utf-8", "ignore"))
    except Exception:
        return []


def _group_items_by_plate(items: list[dict], plates: list[dict]):
    """Split build items across plates. Returns (grouped, unresolved).

    An item whose object is on no plate record is 'unresolved': Studio cannot
    know which plate it belongs to, so it must not be moved.
    """
    owner: dict[str, int] = {}
    for plate in plates:
        for oid in plate.get("object_ids") or []:
            owner[str(oid)] = plate["ui_number"]
    grouped: dict[int, list[dict]] = {}
    unresolved: list[dict] = []
    for item in items:
        plate_no = owner.get(str(item["object_id"]))
        if plate_no is None:
            unresolved.append(item)
        else:
            grouped.setdefault(plate_no, []).append(item)
    return grouped, unresolved


def _derive_grid(grouped: dict[int, list[dict]], source_bed: dict | None) -> dict:
    """Measure the plate grid this project actually uses.

    Returns ``{"ok": bool, "stride": float, "gap": float, "reason": str}``. The
    gap is what the source slicer left between plates; it is carried over so the
    converted project keeps the same separation.
    """
    numbers = sorted(grouped)
    if len(numbers) < 2:
        return {"ok": False, "reason": "only one plate has objects on it"}

    centres = {n: (_cluster_bounds(grouped[n])["min_x"]
                   + _cluster_bounds(grouped[n])["max_x"]) / 2.0 for n in numbers}
    steps = []
    for a, b in zip(numbers, numbers[1:]):
        span = b - a
        if span <= 0:
            continue
        steps.append((centres[b] - centres[a]) / span)
    if not steps:
        return {"ok": False, "reason": "plate positions do not form a sequence"}
    stride = sorted(steps)[len(steps) // 2]
    if stride <= 1.0:
        return {"ok": False,
                "reason": "the plates are not laid out on a grid Studio can read"}

    # The measured stride has to explain every plate, not just the pair it came
    # from. A project that fails this check is one Studio must not touch.
    base = centres[numbers[0]]
    for n in numbers:
        expected = base + (n - numbers[0]) * stride
        if abs(centres[n] - expected) > GRID_TOLERANCE_MM:
            return {"ok": False,
                    "reason": ("the plates are not evenly spaced, so Studio cannot "
                               "work out the layout safely")}

    gap = None
    if source_bed:
        gap = stride - (source_bed["max_x"] - source_bed["min_x"])
    return {"ok": True, "stride": round(stride, 2),
            "gap": round(gap, 2) if gap is not None else None,
            "first_plate": numbers[0], "reason": ""}


def _multi_plate_plan(grouped: dict[int, list[dict]], grid: dict, bed: dict) -> dict:
    """Per-plate translations onto the U1's own grid, and which plates cannot go.

    The U1 grid keeps the source project's plate-to-plate gap and swaps in the
    U1's bed width, so the plates stay as far apart as the creator had them while
    each one lands centred on a U1 plate.
    """
    bed_w = bed["max_x"] - bed["min_x"]
    gap = grid.get("gap")
    u1_stride = bed_w + gap if gap is not None else grid["stride"]
    first = grid["first_plate"]

    offsets: dict[int, dict] = {}
    skipped: list[dict] = []
    for number in sorted(grouped):
        cluster = _cluster_bounds(grouped[number])
        shift = (number - first) * u1_stride
        target = {"min_x": bed["min_x"] + shift, "max_x": bed["max_x"] + shift,
                  "min_y": bed["min_y"], "max_y": bed["max_y"]}
        offset = _centering_offset(cluster, target)
        if _fits_after(cluster, target, offset):
            offsets[number] = offset
        else:
            skipped.append({
                "plate": number,
                "reason": ("the objects on this plate do not fit the U1 plate, so "
                           "Studio left the whole plate where it was"),
            })
    return {"offsets": offsets, "skipped": skipped, "u1_stride": round(u1_stride, 2)}


def assess(path: str, bed: dict | None = None) -> dict:
    """Where every object sits relative to the U1 bed. Read-only, never raises."""
    from . import geometry, project_traits

    target = bed or u1_bed_rect()

    try:
        tm = ThreeMF.open(path)
    except Exception:
        return _unavailable("Studio could not open this file as a 3MF project.")

    traits = project_traits.extract(path)
    plate_count = (traits.get("plate_count") or {}).get("value") or 1

    items = geometry.build_item_dims(path)
    if not items:
        return _unavailable(
            "Studio could not read where the objects sit in this project, so it "
            "cannot check their placement. Open it in Snapmaker Orca to see the plate.")

    source_bed = _source_bed(tm)

    multi_plate = bool(plate_count and plate_count > 1)
    grid: dict = {}
    plan: dict = {}
    unresolved: list[dict] = []
    grouped: dict[int, list[dict]] = {}
    # Each item is judged against the plate it is actually on. On a multi-plate
    # grid, plate 2 legitimately sits a whole bed-width along X, so measuring it
    # against plate 1's rectangle would call every project broken.
    rect_for: dict[str, dict] = {}
    if multi_plate:
        plates = _plates_from_model_settings(tm)
        grouped, unresolved_items = _group_items_by_plate(items, plates)
        unresolved = [{"object_id": i["object_id"]} for i in unresolved_items]
        grid = _derive_grid(grouped, source_bed)
        if grid.get("ok") and not unresolved:
            first = grid["first_plate"]
            for number, plate_items in grouped.items():
                shift = (number - first) * grid["stride"]
                slot = {"min_x": target["min_x"] + shift, "max_x": target["max_x"] + shift,
                        "min_y": target["min_y"], "max_y": target["max_y"]}
                for item in plate_items:
                    rect_for[str(item["object_id"])] = slot
            plan = _multi_plate_plan(grouped, grid, target)

    reported = []
    for item in items:
        over = _overhang(item["bounds"], rect_for.get(str(item["object_id"]), target))
        off = any(mm > 0 for mm in over.values())
        lo, hi = item["bounds"]["min"], item["bounds"]["max"]
        reported.append({
            "object_id": item["object_id"],
            "dimensions": item["dimensions"],
            "position": {"x": round((lo[0] + hi[0]) / 2.0, 2),
                         "y": round((lo[1] + hi[1]) / 2.0, 2)},
            "off_plate": off,
            "overhang_mm": over,
            "edges": _edges_text(over) or None,
        })

    off_plate = [r for r in reported if r["off_plate"]]
    cluster = _cluster_bounds(items)
    offset = _centering_offset(cluster, target)
    span_x = cluster["max_x"] - cluster["min_x"]
    span_y = cluster["max_y"] - cluster["min_y"]
    bed_x = target["max_x"] - target["min_x"] - 2 * EDGE_MARGIN_MM
    bed_y = target["max_y"] - target["min_y"] - 2 * EDGE_MARGIN_MM
    too_wide = span_x > bed_x or span_y > bed_y
    would_fit = (not too_wide) and _fits_after(cluster, target, offset)

    if multi_plate:
        # All-or-nothing per plate: a plate is either moved as a whole or left
        # exactly where it was. A half-moved plate is worse than an unmoved one.
        fixable = bool(off_plate) and bool(plan.get("offsets")) and not plan.get("skipped")
    else:
        fixable = bool(off_plate) and would_fit

    if not off_plate:
        summary = ("Every object sits inside the U1's printable area."
                   if len(reported) > 1 else
                   "The object sits inside the U1's printable area.")
    elif multi_plate and unresolved:
        summary = (f"{len(off_plate)} object(s) fall outside the U1's plates, and "
                   f"{len(unresolved)} object(s) are not listed on any plate, so Studio "
                   "cannot tell where they belong. It will not move anything — open the "
                   "project in Snapmaker Orca and use Arrange.")
    elif multi_plate and not grid.get("ok"):
        summary = (f"{len(off_plate)} object(s) fall outside the U1's plates. Studio "
                   f"could not read this project's plate layout ({grid.get('reason')}), "
                   "so it will not move them for you — open it in Snapmaker Orca and use "
                   "Arrange.")
    elif multi_plate and plan.get("skipped"):
        moved = len(plan.get("offsets") or {})
        summary = (f"{len(off_plate)} object(s) fall outside the U1's plates. Studio can "
                   f"reposition {moved} plate(s), but "
                   f"{len(plan['skipped'])} will not fit a U1 plate — it moves all plates "
                   "or none, so nothing is changed. Open it in Snapmaker Orca and use "
                   "Arrange.")
    elif multi_plate:
        summary = (f"{len(off_plate)} object(s) fall outside the U1's plates. Studio can "
                   f"move all {len(plan['offsets'])} plates onto the U1's own plate grid, "
                   "keeping each plate's layout, rotation, scale and the spacing between "
                   "plates.")
    elif too_wide:
        summary = (f"{len(off_plate)} object(s) fall outside the U1's plate, and the "
                   "whole arrangement is wider than the plate — moving it cannot fix "
                   "this. Scale it down or split it across plates.")
    elif would_fit:
        summary = (f"{len(off_plate)} object(s) fall outside the U1's plate, but the "
                   "whole arrangement fits — moving it as one piece brings everything "
                   "back on, keeping the creator's layout, rotation and scale.")
    else:
        summary = (f"{len(off_plate)} object(s) fall outside the U1's plate and one "
                   "move will not fix it. Open it in Snapmaker Orca and use Arrange.")

    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "bed": target,
        "source_bed": source_bed,
        "source_printer": (traits.get("target_printer") or {}).get("value"),
        "plate_count": plate_count,
        "item_count": len(reported),
        "items": reported,
        "off_plate": off_plate,
        "arrangement": {"width": round(span_x, 2), "depth": round(span_y, 2)},
        "suggested_offset": offset if (would_fit and not multi_plate) else None,
        "plate_grid": grid or None,
        "plate_offsets": ({str(k): v for k, v in plan["offsets"].items()}
                          if plan.get("offsets") else None),
        "skipped_plates": plan.get("skipped") or [],
        "unresolved_objects": unresolved,
        "fixable": fixable,
        "summary": summary,
    }


# --- the fix ---------------------------------------------------------------

def _shift_transform(value: str, dx: float, dy: float) -> str | None:
    """Add (dx, dy) to a 3MF transform's translation. None if not a 3x4 matrix.

    3MF stores the matrix row-major with the translation as the final row, so
    only entries 10 and 11 (1-indexed 12-value form) move. Everything else —
    rotation, scale, shear — is copied through unchanged.
    """
    parts = value.split()
    if len(parts) != 12:
        return None
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        return None
    nums[9] += dx
    nums[10] += dy
    return " ".join(f"{n:.6g}" for n in nums)


def _identity_shifted(dx: float, dy: float) -> str:
    return _shift_transform("1 0 0 0 1 0 0 0 1 0 0 0", dx, dy) or ""


_OBJECTID_RE = re.compile(r'\bobjectid\s*=\s*"([^"]*)"')


def _rewrite_items(raw: bytes, offset_for) -> tuple[bytes, int]:
    """Translate build items in the root model part.

    ``offset_for`` maps an item's object id to an ``(dx, dy)`` pair, or None to
    leave that item exactly where it is — which is how a skipped plate and an
    object Studio could not place stay untouched.

    Byte-surgical: only the transform attribute inside <item> tags is rewritten.
    Meshes, painted colour, settings and every other archive entry are unchanged.
    """
    text = raw.decode("utf-8")
    moved = 0

    def fix_item(match: re.Match) -> str:
        nonlocal moved
        tag = match.group(0)
        oid_match = _OBJECTID_RE.search(tag)
        offset = offset_for(oid_match.group(1) if oid_match else None)
        if offset is None:
            return tag
        dx, dy = offset
        attr = _TRANSFORM_ATTR_RE.search(tag)
        if attr is None:
            # An item with no transform is at the identity; give it the shift so
            # it moves with the rest of the plate instead of staying behind.
            moved += 1
            insert = f' transform="{_identity_shifted(dx, dy)}"'
            return tag[:-2] + insert + "/>" if tag.endswith("/>") else tag[:-1] + insert + ">"
        shifted = _shift_transform(attr.group(2), dx, dy)
        if shifted is None:
            return tag
        moved += 1
        return tag[:attr.start()] + attr.group(1) + shifted + attr.group(3) + tag[attr.end():]

    out = _ITEM_TAG_RE.sub(fix_item, text)
    return out.encode("utf-8"), moved


def _uniform_offset(dx: float, dy: float):
    return lambda _oid: (dx, dy)


def _per_plate_offset(tm: ThreeMF, plate_offsets: dict):
    """An offset lookup that moves each object by its own plate's translation."""
    owner: dict[str, int] = {}
    for plate in _plates_from_model_settings(tm):
        for oid in plate.get("object_ids") or []:
            owner[str(oid)] = plate["ui_number"]

    def lookup(object_id):
        plate_no = owner.get(str(object_id))
        if plate_no is None:
            return None
        offset = plate_offsets.get(str(plate_no))
        return (offset["x"], offset["y"]) if offset else None

    return lookup


def _unique_output(src: Path, out_dir: Path | None) -> Path:
    target = out_dir if out_dir else src.parent
    out = target / f"{src.stem}_placed_U1.3mf"
    n = 2
    while out.resolve() == src.resolve() or out.exists():
        out = target / f"{src.stem}_placed_U1_{n}.3mf"
        n += 1
    return out


def prepare_placed_copy(path: str, out_dir: str | None = None,
                        bed: dict | None = None) -> dict:
    """Write a new copy with the whole arrangement moved onto the U1 plate.

    Returns a result describing what moved and what the check said afterwards.
    Refuses — without writing anything — when the assessment says a single move
    cannot fix the project.
    """
    before = assess(path, bed=bed)
    if not before.get("available"):
        return {"schema_version": SCHEMA_VERSION, "ok": False,
                "reason": before.get("reason"), "before": before}
    if not before.get("off_plate"):
        return {"schema_version": SCHEMA_VERSION, "ok": False,
                "reason": "Nothing to move — every object is already on the plate.",
                "before": before}
    if not before.get("fixable"):
        return {"schema_version": SCHEMA_VERSION, "ok": False,
                "reason": before["summary"], "before": before}

    src = Path(path)
    try:
        tm = ThreeMF.open(src)
    except Exception:
        return {"schema_version": SCHEMA_VERSION, "ok": False,
                "reason": "Studio could not open this file as a 3MF project.",
                "before": before}
    if not tm.has_part(ROOT_MODEL):
        return {"schema_version": SCHEMA_VERSION, "ok": False,
                "reason": "This project has no 3D model part Studio can reposition.",
                "before": before}

    plate_offsets = before.get("plate_offsets")
    if plate_offsets:
        offset_for = _per_plate_offset(tm, plate_offsets)
        offset = None
    else:
        offset = before["suggested_offset"]
        offset_for = _uniform_offset(offset["x"], offset["y"])

    rewritten, moved = _rewrite_items(tm.read_part(ROOT_MODEL), offset_for)
    if not moved:
        return {"schema_version": SCHEMA_VERSION, "ok": False,
                "reason": "Studio found no placed objects to move in this project.",
                "before": before}
    tm.replace_part(ROOT_MODEL, rewritten)

    out_parent = Path(out_dir) if out_dir else None
    if out_parent:
        out_parent.mkdir(parents=True, exist_ok=True)
    out = _unique_output(src, out_parent)
    tm.save(out)

    # Validate the fix by re-running the same check against the file that was
    # actually written — not against what the code intended to write.
    after = assess(str(out), bed=bed)
    ok = bool(after.get("available")) and not after.get("off_plate")
    if not ok:
        # The copy is left in place so a user can inspect it, but the result says
        # plainly that the move did not achieve what it was supposed to.
        return {
            "schema_version": SCHEMA_VERSION, "ok": False,
            "reason": ("Studio moved the arrangement but the copy still has objects "
                       "off the plate, so it is not safe to rely on. Open the original "
                       "in Snapmaker Orca and use Arrange."),
            "output_path": str(out), "output_name": out.name,
            "before": before, "after": after,
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "ok": True,
        "output_path": str(out),
        "output_name": out.name,
        "objects_moved": moved,
        "offset_mm": offset,
        "plate_offsets": plate_offsets,
        "before": before,
        "after": after,
        "changes": [{
            "what": ("Moved every plate onto the U1's plate grid" if plate_offsets
                     else "Moved the whole arrangement onto the U1 plate"),
            "detail": (
                f"{len(plate_offsets)} plate(s) repositioned, keeping the spacing "
                f"between them." if plate_offsets else
                f"Every object shifted by X {offset['x']:+.1f} mm, "
                f"Y {offset['y']:+.1f} mm."),
            "kept": "Layout, rotation, scale and height are unchanged.",
        }],
        "summary": (f"{moved} object(s) moved onto the U1 plate in a new copy — "
                    f"{out.name}. Your original file was not changed."),
    }
