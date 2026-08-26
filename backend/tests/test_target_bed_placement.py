"""Where a prepared object lands on the U1 plate, and moving it there on request.

Studio carries a source project's placement exactly. A placement that is legal on
the bed it came from need not be legal on the U1's: a PrusaSlicer object at build
transform `10 10 10` whose mesh runs from −10 to +10 occupies 0 to 20 mm, and the
U1's printable polygon starts at x = 0.5 and y = 1. Snapmaker Orca files the whole
object under *Outside* and refuses to slice the plate.

Two facts, kept apart throughout:

    the placement was preserved     — Studio did not move anything
    the placement does not fit      — the target cannot print it there

The second is not a fidelity loss, and fixing it is never automatic. What
Snapmaker Orca does with each state was measured rather than assumed: it refuses
to slice a plate holding something off it, and — with a control — it ignores
helper geometry when deciding, which is why the footprint here is printable parts
only. A modifier cube 400 mm off the plate sliced fine; the same cube as a normal
part stopped the slice.
"""
from __future__ import annotations

import json
import re
import tempfile
import zipfile
from pathlib import Path

import pytest

from snapstudio_core import (multipart as MP, placement as P,
                             plate_placement as PP)
from snapstudio_core.convert import convert_to_u1
from snapstudio_core.fidelity import audit

FIXTURES = Path(__file__).parent / "fixtures"
OUTSIDE_SOURCE = FIXTURES / "painted" / "prusaslicer-2.9.6-painted-cube.3mf"
THREE_OBJECTS = FIXTURES / "prusa-multi-object" / "prusa_three_objects.3mf"
DONOR = FIXTURES / "prusa-semantics" / "H_two_volumes_different_slots_out.3mf"
ROOT = "3D/3dmodel.model"
CARRIED = ["[Content_Types].xml", "_rels/.rels",
           "Metadata/project_settings.config", "Metadata/slice_info.config"]


@pytest.fixture(scope="module")
def outside() -> str:
    return convert_to_u1(str(OUTSIDE_SOURCE), out_dir=tempfile.mkdtemp()).output_path


@pytest.fixture(scope="module")
def three() -> str:
    return convert_to_u1(str(THREE_OBJECTS), out_dir=tempfile.mkdtemp()).output_path


def transforms(path: str) -> dict:
    with zipfile.ZipFile(path) as archive:
        root = archive.read(ROOT).decode("utf-8")
    return dict(P._BUILD_ITEM.findall(root))


def shifted(prepared: str, dx: float, dy: float, out: Path) -> str:
    """The same project with the whole arrangement moved by (dx, dy)."""
    def move(match: re.Match) -> str:
        item = match.group(0)
        found = re.search(r'transform="([^"]*)"', item)
        transform = P.parse_transform(found.group(1)) if found else None
        if transform is None:
            return item
        moved = P.format_transform(P.translated(transform, dx, dy))
        return item.replace(f'transform="{found.group(1)}"', f'transform="{moved}"')

    with zipfile.ZipFile(prepared) as src, zipfile.ZipFile(out, "w") as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == ROOT:
                data = re.sub(r"<item[^>]*/>", move,
                              data.decode("utf-8")).encode("utf-8")
            dst.writestr(item, data)
    return str(out)


def _probe_with_second_cube(role: str, tmp_path: Path) -> str:
    """A cube on the plate and a second cube 400 mm away, in the given role."""
    parts = [dict(_cube(0, 0, 0, 20), index=0), dict(_cube(400, 0, 0, 20), index=1)]
    roles = ["part", role]
    donor = convert_to_u1(str(DONOR), out_dir=str(tmp_path / f"donor_{role}")).output_path
    target = tmp_path / f"probe_{role}.3mf"
    with zipfile.ZipFile(donor) as source, zipfile.ZipFile(
            target, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in CARRIED:
            archive.writestr(name, source.read(name))
        archive.writestr(ROOT, MP.root_model_multi_xml([{
            "root_id": 3, "part_ids": [1, 2],
            "path": "/3D/Objects/object_1.model",
            "transform": "1 0 0 0 1 0 0 0 1 120 120 0"}]))
        archive.writestr("3D/Objects/object_1.model",
                         MP.objects_model_xml(parts, roles=roles))
        archive.writestr("3D/_rels/3dmodel.model.rels", MP.object_rels_xml())
        archive.writestr("Metadata/model_settings.config", (
            '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'
            '  <object id="3">\n'
            '    <metadata key="name" value="probe"/>\n'
            '    <metadata key="extruder" value="0"/>\n'
            + MP.part_records(parts, "probe", [1, 1], roles, [1, 2])
            + "  </object>\n</config>\n").encode("utf-8"))
    return str(target)


# --- transforms ---------------------------------------------------------------

def test_a_twelve_number_transform_and_a_sixteen_number_matrix_agree():
    """A build item writes twelve numbers, a part matrix sixteen, same meaning.

    Reading the wrong twelve out of the sixteen is how a rotation becomes a
    translation, so both shapes are parsed and checked against each other.
    """
    item = P.parse_transform("1 0 0 0 1 0 0 0 1 10 20 30")
    matrix = P.parse_transform("1 0 0 10 0 1 0 20 0 0 1 30 0 0 0 1")
    assert item == matrix
    assert P.apply(item, (1.0, 2.0, 3.0)) == (11.0, 22.0, 33.0)


def test_composing_is_not_the_same_as_applying_twice():
    outer = P.parse_transform("1 0 0 0 1 0 0 0 1 100 0 0")
    inner = P.parse_transform("1 0 0 0 1 0 0 0 1 5 0 0")
    once = P.apply(P.compose(outer, inner), (0.0, 0.0, 0.0))
    assert once == (105.0, 0.0, 0.0)


def test_a_move_touches_x_and_y_and_nothing_else():
    before = P.parse_transform("0 -1 0 1 0 0 0 0 1 10 20 30")
    after = P.translated(before, 1.5, -2.0)
    assert after[0] == before[0] and after[1] == before[1] and after[2] == before[2]
    assert after[3] == (11.5, 18.0, 30.0)


# --- the polygon --------------------------------------------------------------

def test_the_polygon_comes_from_the_project_not_from_a_remembered_number(outside):
    report = P.assess(outside)
    assert report["polygon_source"] == "Metadata/project_settings.config"
    assert report["polygon"] == [(0.5, 1.0), (270.5, 1.0), (270.5, 271.0), (0.5, 271.0)]


def test_containment_uses_the_polygon_and_not_its_bounding_box():
    """An L-shaped bed proves the difference. Nothing in the U1's own outline can.

    A point in the notch of an L is inside the bounding box and outside the bed,
    and a width-by-depth rectangle would print into thin air.
    """
    ell = [(0.0, 0.0), (100.0, 0.0), (100.0, 40.0), (40.0, 40.0),
           (40.0, 100.0), (0.0, 100.0)]
    assert P._inside_polygon((20.0, 20.0), ell)
    assert not P._inside_polygon((80.0, 80.0), ell), "that corner is not bed"
    footprint = {"min_x": 70.0, "min_y": 70.0, "max_x": 90.0, "max_y": 90.0,
                 "width": 20.0, "depth": 20.0}
    verdict = P.classify(footprint, ell,
                         [(70.0, 70.0), (90.0, 70.0), (90.0, 90.0), (70.0, 90.0)])
    assert verdict["status"] == P.FULLY_OUTSIDE


def test_a_synthetic_printer_is_answered_with_its_own_polygon(tmp_path):
    """No U1 dimension is written into the geometry: swap the polygon, swap the answer."""
    prepared = convert_to_u1(str(OUTSIDE_SOURCE), out_dir=str(tmp_path)).output_path
    tiny = tmp_path / "tiny_bed.3mf"
    with zipfile.ZipFile(prepared) as src, zipfile.ZipFile(tiny, "w") as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "Metadata/project_settings.config":
                settings = json.loads(data.decode("utf-8"))
                settings["printable_area"] = ["0x0", "15x0", "15x15", "0x15"]
                data = json.dumps(settings).encode("utf-8")
            dst.writestr(item, data)
    report = P.assess(str(tiny), printer="a 15 mm printer")
    assert report["objects"][0]["status"] == P.TOO_LARGE_TO_FIT
    assert "larger than" in report["objects"][0]["message"]


# --- the object that has always been outside ----------------------------------

def test_the_known_outside_fixture_is_diagnosed_exactly(outside):
    report = P.assess(outside)
    entry = report["objects"][0]
    assert entry["status"] == P.PARTLY_OUTSIDE
    assert entry["footprint_mm"]["min_x"] == 0.0 and entry["footprint_mm"]["min_y"] == 0.0
    assert entry["excess_mm"] == {"left": 0.5, "front": 1.0}
    assert entry["fits_by_translation"] is True


def test_one_side_over_is_named_and_two_sides_are_not_invented():
    """Beginner wording: name the side when there is one, do not list four."""
    polygon = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    one = P.classify({"min_x": -2.0, "min_y": 10.0, "max_x": 20.0, "max_y": 30.0,
                      "width": 22.0, "depth": 20.0}, polygon)
    assert P.describe("Object 1", one, "U1") == (
        "Object 1 is 2 mm outside the U1 printable area on the left.")
    two = P.classify({"min_x": -2.0, "min_y": -1.0, "max_x": 20.0, "max_y": 30.0,
                      "width": 22.0, "depth": 31.0}, polygon)
    assert P.describe("Object 1", two, "U1") == (
        "Object 1 extends outside the U1 printable area.")


def test_every_failure_is_not_called_outside():
    polygon = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    inside = P.classify({"min_x": 10, "min_y": 10, "max_x": 20, "max_y": 20,
                         "width": 10, "depth": 10}, polygon)
    touching = P.classify({"min_x": 0, "min_y": 0, "max_x": 20, "max_y": 20,
                           "width": 20, "depth": 20}, polygon)
    partly = P.classify({"min_x": -5, "min_y": 10, "max_x": 20, "max_y": 20,
                         "width": 25, "depth": 10}, polygon)
    fully = P.classify({"min_x": 200, "min_y": 200, "max_x": 210, "max_y": 210,
                        "width": 10, "depth": 10}, polygon)
    huge = P.classify({"min_x": 0, "min_y": 0, "max_x": 500, "max_y": 20,
                       "width": 500, "depth": 20}, polygon)
    assert [inside["status"], touching["status"], partly["status"],
            fully["status"], huge["status"]] == [
        P.INSIDE, P.TOUCHING_BOUNDARY, P.PARTLY_OUTSIDE, P.FULLY_OUTSIDE,
        P.TOO_LARGE_TO_FIT]
    assert P.classify(None, polygon)["status"] == P.UNKNOWN


def test_a_helper_volume_off_the_plate_does_not_make_the_object_outside(tmp_path):
    """Measured against Orca 2.3.5, with a control.

    A modifier cube 400 mm off the plate sliced without complaint; the same cube
    written as a normal part stopped the slice. So the footprint is printable
    parts only, and this holds Studio to the behaviour that was measured.
    """
    assert P.assess(_probe_with_second_cube("modifier", tmp_path))["all_inside"] is True
    assert P.assess(_probe_with_second_cube("part", tmp_path))["all_inside"] is False


def _cube(x0: float, y0: float, z0: float, size: float) -> dict:
    x1, y1, z1 = x0 + size, y0 + size, z0 + size
    corners = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
               (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
             (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return {"vertices": [f'<vertex x="{x}" y="{y}" z="{z}"/>' for x, y, z in corners],
            "triangles": [f'<triangle v1="{a}" v2="{b}" v3="{c}"/>'
                          for a, b, c in faces]}


# --- the project as a whole ---------------------------------------------------
#
# Moving is `plate_placement`, which ships the check and the fix the app calls.
# It keeps half a millimetre of margin off every edge on purpose — a skirt, a brim
# and the prime tower all need room, and "just touching the edge" should not read
# as safe — so its move is that much larger than the bare geometry needs.

def test_a_project_already_on_the_plate_says_so_and_offers_nothing(three):
    report = P.assess(three)
    assert report["all_inside"] and report["objects_outside"] == 0
    assert report["summary"] == "Every object is on the Snapmaker U1 plate."
    result = PP.prepare_placed_copy(three, out_dir=tempfile.mkdtemp())
    assert result["ok"] is False
    assert "already on the plate" in result["reason"]


def test_a_project_already_on_the_plate_writes_no_file(three, tmp_path):
    PP.prepare_placed_copy(three, out_dir=str(tmp_path))
    assert not list(tmp_path.glob("*.3mf")), "no file for a move that moves nothing"


def test_the_whole_arrangement_is_answered_not_only_one_object(three, tmp_path):
    pushed = shifted(three, -60.0, -50.0, tmp_path / "pushed.3mf")
    report = P.assess(pushed)
    assert report["objects_total"] == 3 and report["objects_outside"] == 2
    assert report["rigid_move"] == {"possible": True, "dx": 30.5, "dy": 21.0,
                                    "moves": True}


def test_an_arrangement_too_wide_for_the_plate_is_not_offered_a_move(tmp_path):
    prepared = convert_to_u1(str(THREE_OBJECTS), out_dir=str(tmp_path)).output_path
    with zipfile.ZipFile(prepared) as src:
        root = src.read(ROOT).decode("utf-8")
    ids = re.findall(r'<item objectid="([0-9]+)"', root)
    root = root.replace(
        f'<item objectid="{ids[-1]}" transform="1 0 0 0 1 0 0 0 1 140 90 10"',
        f'<item objectid="{ids[-1]}" transform="1 0 0 0 1 0 0 0 1 900 90 10"')
    far = tmp_path / "far.3mf"
    with zipfile.ZipFile(prepared) as src, zipfile.ZipFile(far, "w") as dst:
        for item in src.infolist():
            data = root.encode("utf-8") if item.filename == ROOT else src.read(
                item.filename)
            dst.writestr(item, data)
    report = P.assess(str(far))
    assert report["rigid_move"]["possible"] is False
    assert "spacing" in report["rigid_move"]["reason"]
    result = PP.prepare_placed_copy(str(far), out_dir=str(tmp_path / "out"))
    assert result["ok"] is False


def test_an_object_larger_than_the_plate_is_never_offered_a_move(tmp_path):
    prepared = convert_to_u1(str(OUTSIDE_SOURCE), out_dir=str(tmp_path)).output_path
    tiny = tmp_path / "tiny.3mf"
    with zipfile.ZipFile(prepared) as src, zipfile.ZipFile(tiny, "w") as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "Metadata/project_settings.config":
                settings = json.loads(data.decode("utf-8"))
                settings["printable_area"] = ["0x0", "15x0", "15x15", "0x15"]
                data = json.dumps(settings).encode("utf-8")
            dst.writestr(item, data)
    report = P.assess(str(tiny), printer="a 15 mm printer")
    assert report["objects"][0]["status"] == P.TOO_LARGE_TO_FIT
    assert "larger than" in report["objects"][0]["message"]
    assert report["rigid_move"]["possible"] is False


# --- the move -----------------------------------------------------------------

def test_the_move_is_the_smallest_one_that_works_and_the_same_every_time(outside):
    """Not the middle of the plate: the least that gets it on.

    Half a millimetre of edge margin is deliberate, so a cube whose bare geometry
    needs +0.5 and +1.0 is moved +1.0 and +1.5.
    """
    first = PP.assess(outside)["suggested_offset"]
    second = PP.assess(outside)["suggested_offset"]
    assert first == second == {"x": 1.0, "y": 1.5}


def test_the_move_says_how_far_not_that_it_fixed_something(outside, tmp_path):
    result = PP.prepare_placed_copy(outside, out_dir=str(tmp_path))
    assert result["ok"] is True
    assert result["offset_mm"] == {"x": 1.0, "y": 1.5}
    assert "X +1.0 mm" in result["changes"][0]["detail"]
    assert transforms(result["output_path"]) == {"2": "1 0 0 0 1 0 0 0 1 11 11.5 10"}


def test_the_original_is_untouched_and_the_copy_is_new(outside, tmp_path):
    before = Path(outside).read_bytes()
    result = PP.prepare_placed_copy(outside, out_dir=str(tmp_path))
    assert Path(outside).read_bytes() == before
    assert Path(result["output_path"]).resolve() != Path(outside).resolve()


def test_only_the_placement_differs(outside, tmp_path):
    result = PP.prepare_placed_copy(outside, out_dir=str(tmp_path))
    assert result["verification"]["passed"]
    with zipfile.ZipFile(outside) as before, zipfile.ZipFile(
            result["output_path"]) as after:
        differing = [name for name in before.namelist()
                     if before.read(name) != after.read(name)]
    assert differing == [ROOT]


def test_the_moved_copy_is_on_the_plate(outside, tmp_path):
    result = PP.prepare_placed_copy(outside, out_dir=str(tmp_path))
    assert not result["after"]["off_plate"]
    assert P.assess(result["output_path"])["all_inside"] is True


def test_every_object_moves_by_the_same_amount(three, tmp_path):
    pushed = shifted(three, -60.0, -50.0, tmp_path / "pushed.3mf")
    result = PP.prepare_placed_copy(pushed, out_dir=str(tmp_path / "out"))
    assert result["ok"] is True
    deltas = set()
    before, after = transforms(pushed), transforms(result["output_path"])
    for object_id, text in before.items():
        one = P.parse_transform(text)
        two = P.parse_transform(after[object_id])
        deltas.add((round(two[3][0] - one[3][0], 4), round(two[3][1] - one[3][1], 4),
                    round(two[3][2] - one[3][2], 4)))
    assert len(deltas) == 1, "one rigid move"
    assert next(iter(deltas))[2] == 0.0, "in X and Y only"
    assert P.assess(result["output_path"])["all_inside"] is True


def test_the_spacing_between_objects_is_unchanged(three, tmp_path):
    pushed = shifted(three, -60.0, -50.0, tmp_path / "pushed.3mf")
    result = PP.prepare_placed_copy(pushed, out_dir=str(tmp_path / "out"))

    def gaps(path: str) -> list:
        centres = []
        for entry in P.read_objects(path)["objects"]:
            box = entry["footprint"]
            centres.append(((box["min_x"] + box["max_x"]) / 2,
                            (box["min_y"] + box["max_y"]) / 2))
        return [(round(b[0] - a[0], 6), round(b[1] - a[1], 6))
                for a, b in zip(centres, centres[1:])]

    assert gaps(pushed) == gaps(result["output_path"])


# --- corruptions the verification must refuse ---------------------------------

def refuse(project: str, tmp_path: Path, change) -> None:
    """Damage the rewrite the way a bug would, and require the copy to be refused."""
    original = PP._rewrite_items

    def broken(raw: bytes, offset_for):
        rewritten, moved = original(raw, offset_for)
        return change(rewritten.decode("utf-8")).encode("utf-8"), moved

    PP._rewrite_items = broken
    try:
        result = PP.prepare_placed_copy(project, out_dir=str(tmp_path))
        assert result["ok"] is False, result
        assert "changed something other than where the objects sit" in result["reason"]
        assert not list(tmp_path.glob("*.3mf")), "no file survives a refusal"
    finally:
        PP._rewrite_items = original


def test_a_rotation_that_creeps_in_is_refused(outside, tmp_path):
    refuse(outside, tmp_path, lambda t: t.replace(
        'transform="1 0 0 0 1 0 0 0 1 11 11.5 10"',
        'transform="0 -1 0 1 0 0 0 0 1 11 11.5 10"'))


def test_a_height_change_is_refused(outside, tmp_path):
    refuse(outside, tmp_path, lambda t: t.replace(
        'transform="1 0 0 0 1 0 0 0 1 11 11.5 10"',
        'transform="1 0 0 0 1 0 0 0 1 11 11.5 25"'))


def test_geometry_that_changes_is_refused(outside, tmp_path):
    refuse(outside, tmp_path,
           lambda t: t.replace("</resources>", "<!-- x --></resources>"))


def test_an_object_left_behind_is_refused(three, tmp_path):
    """One object moves, another does not: not a rigid move, and not accepted."""
    pushed = shifted(three, -60.0, -50.0, tmp_path / "pushed.3mf")
    original = PP._rewrite_items

    def only_some(raw: bytes, offset_for):
        rewritten, moved = original(raw, offset_for)
        text = rewritten.decode("utf-8")
        items = re.findall(r"<item[^>]*/>", text)
        return text.replace(items[-1], re.sub(
            r'transform="[^"]*"', 'transform="1 0 0 0 1 0 0 0 1 80 40 10"',
            items[-1])).encode("utf-8"), moved

    PP._rewrite_items = only_some
    try:
        result = PP.prepare_placed_copy(pushed, out_dir=str(tmp_path / "out"))
        assert result["ok"] is False
    finally:
        PP._rewrite_items = original


def test_a_modifier_off_the_plate_no_longer_reports_the_object_off_it(tmp_path):
    """The defect this sprint found in the shipped check.

    A modifier cube 400 mm from the plate made Studio report the object 270 mm off
    it, and offer to move an arrangement Snapmaker Orca slices without complaint.
    """
    project = _probe_with_second_cube("modifier", tmp_path)
    assert PP.assess(project)["off_plate"] == []
    assert P.assess(project)["all_inside"] is True
    printable = _probe_with_second_cube("part", tmp_path)
    assert PP.assess(printable)["off_plate"], "a printable part off the plate still counts"


# --- the audit ----------------------------------------------------------------

def test_the_audit_reports_a_rigid_move_as_the_arrangement_kept(outside, tmp_path):
    """Moving the plate is not the same as one object drifting."""
    result = PP.prepare_placed_copy(outside, out_dir=str(tmp_path))
    rows = [r for r in audit(str(OUTSIDE_SOURCE), result["output_path"])["rows"]
            if r["element"].startswith("Where ")]
    assert rows and rows[0]["status"] == "preserved_semantic"
    assert "+1 mm X" in rows[0]["detail"]


def test_the_audit_keeps_placement_preserved_and_target_fit_apart(outside):
    report = audit(str(OUTSIDE_SOURCE), outside)
    rows = [r for r in report["rows"] if r["element"].startswith("Where ")]
    assert rows and rows[0]["status"] == "preserved_exact", (
        "Studio moved nothing, so nothing was lost")
    assert report["placement"]["objects_outside"] == 1, (
        "and the target still cannot print it there")
