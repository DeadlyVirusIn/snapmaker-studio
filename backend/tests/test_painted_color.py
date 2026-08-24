"""Reading painted colour out of a project, and refusing to over-read it.

The public claim this makes possible is a strong one — "Studio can tell you which
filaments a painted project uses before you slice it" — so most of what is tested
here is the edge of that claim: the slot that cannot be resolved, the height that
cannot be placed, the pair of colours whose overlap does not prove they share a
layer, and the file that is trying to make the reader allocate.
"""
from __future__ import annotations

import zipfile

import pytest

from snapstudio_core import paint_codec as codec
from snapstudio_core import painted_color as painted

from painted_fixtures import (TRIANGLE_AREA, bambu_project, paint,
                              prusa_project)


def slots(result):
    return result["slots_referenced"]


def assignment(result, slot):
    for entry in result["slots"]:
        if entry["slot"] == slot:
            return entry
    raise AssertionError(f"slot {slot} not in {slots(result)}")


# --- what it reads -----------------------------------------------------------

def test_an_unpainted_project_says_so_without_inventing_a_dialect(tmp_path):
    path = bambu_project(tmp_path, meshes=[{"painted": {}, "extruder": 1}])
    result = painted.read(path)
    assert result["available"] is True
    assert result["dialect"] is None
    assert result["slots_referenced"] == []
    assert "no painted colour" in result["reason"]


def test_one_painted_colour_is_read_with_its_slot_and_its_area(tmp_path):
    path = bambu_project(tmp_path, meshes=[{"painted": {0: paint(2)}, "extruder": 1}])
    result = painted.read(path)
    assert result["dialect"] == painted.DIALECT_BAMBU
    assert slots(result) == [2]
    entry = assignment(result, 2)
    assert entry["triangles_touching"] == 1
    assert entry["facet_equivalent"] == 1.0
    assert entry["area_mm2"] == pytest.approx(TRIANGLE_AREA)
    assert result["confidence"] == painted.CONFIRMED


def test_several_painted_colours_in_one_triangle_are_each_measured(tmp_path):
    # A two-way split leaves a quarter, a quarter and a half — the shares the
    # format fixes, not shares Studio chose.
    tree = (0, [1, 3, 4])
    path = bambu_project(tmp_path, meshes=[{"painted": {0: paint(tree)}, "extruder": 2}])
    result = painted.read(path)
    assert slots(result) == [1, 3, 4]
    assert assignment(result, 1)["area_mm2"] == pytest.approx(TRIANGLE_AREA * 0.25)
    assert assignment(result, 3)["area_mm2"] == pytest.approx(TRIANGLE_AREA * 0.25)
    assert assignment(result, 4)["area_mm2"] == pytest.approx(TRIANGLE_AREA * 0.5)
    assert sum(a["area_mm2"] for a in result["slots"]) == pytest.approx(TRIANGLE_AREA)


def test_facet_counts_and_area_are_reported_as_different_facts(tmp_path):
    # One big triangle painted, one small one left alone: half the facets, but
    # far from half the area. Reporting one as the other would be a lie about
    # how much filament a colour needs.
    vertices = [(0.0, 0.0, 0.0), (100.0, 0.0, 0.0), (0.0, 100.0, 0.0),
                (0.0, 0.0, 5.0), (1.0, 0.0, 5.0), (0.0, 1.0, 5.0)]
    path = bambu_project(tmp_path, meshes=[
        {"painted": {0: paint(2)}, "extruder": 1, "vertices": vertices}])
    result = painted.read(path)
    obj = result["objects"][0]
    assert obj["triangle_count"] == 2
    assert obj["painted_triangle_count"] == 1
    entry = assignment(result, 2)
    assert entry["area_mm2"] == pytest.approx(5000.0)
    assert obj["assignments"][0]["area_share"] == pytest.approx(5000.0 / 5000.5, rel=1e-3)


def test_an_unpainted_region_inside_a_painted_triangle_takes_the_parts_own_slot(tmp_path):
    path = bambu_project(tmp_path, meshes=[
        {"painted": {0: paint((0, [0, 3]))}, "extruder": 2}])
    result = painted.read(path)
    obj = result["objects"][0]
    assert obj["default_slot"] == 2
    unpainted = [a for a in obj["assignments"] if a["state"] == 0][0]
    assert unpainted["slot"] == 2
    assert unpainted["painted"] is False
    assert "slot 2" in unpainted["evidence"]


def test_an_unresolvable_default_slot_stays_unknown(tmp_path):
    path = bambu_project(tmp_path, meshes=[
        {"painted": {0: paint((0, [0, 3]))}, "extruder": None}])
    result = painted.read(path)
    obj = result["objects"][0]
    assert obj["default_slot"] is None
    assert result["default_slot_resolved"] is False
    unpainted = [a for a in obj["assignments"] if a["state"] == 0][0]
    assert unpainted["slot"] is None
    assert "cannot say" in unpainted["evidence"]


def test_more_than_four_painted_colours_are_all_enumerated(tmp_path):
    tree = (0, [1, (1, [2, (2, [3, 4, 5])]), 6, 7])
    path = bambu_project(tmp_path, colours=["#1"] * 8,
                         meshes=[{"painted": {0: paint(tree)}, "extruder": 1}])
    assert slots(painted.read(path)) == [1, 2, 3, 4, 5, 6, 7]


def test_several_painted_volumes_are_kept_apart_and_then_added_up(tmp_path):
    path = bambu_project(tmp_path, meshes=[
        {"painted": {0: paint(1)}, "extruder": 1},
        {"painted": {0: paint(2), 1: paint(3)}, "extruder": 2},
    ])
    result = painted.read(path)
    assert len(result["objects"]) == 2
    assert slots(result) == [1, 2, 3]
    assert assignment(result, 2)["triangles_touching"] == 1
    assert result["painted_triangle_count"] == 3


def test_a_modifier_volume_is_read_but_named_as_what_it_is(tmp_path):
    path = bambu_project(tmp_path, meshes=[
        {"painted": {0: paint(2)}, "extruder": 1, "subtype": "modifier_part"}])
    result = painted.read(path)
    assert slots(result) == [2]


def test_the_prusa_dialect_reads_the_same_way(tmp_path):
    path = prusa_project(tmp_path, painted={0: paint(2), 1: paint(3)})
    result = painted.read(path)
    assert result["dialect"] == painted.DIALECT_PRUSA
    assert result["attribute"] == "slic3rpe:mmu_segmentation"
    assert slots(result) == [2, 3]
    assert result["objects"][0]["default_slot"] == 1


def test_the_declared_format_version_is_reported_not_assumed(tmp_path):
    path = bambu_project(tmp_path, version=3)
    result = painted.read(path)
    assert result["format_version"] == 3
    assert result["format_version_known"] is True


def test_a_project_with_no_declared_version_says_the_version_is_unknown(tmp_path):
    path = prusa_project(tmp_path)
    with zipfile.ZipFile(path) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    parts["3D/3dmodel.model"] = parts["3D/3dmodel.model"].replace(
        b'<metadata name="slic3rpe:MmPaintingVersion">1</metadata>', b"")
    stripped = tmp_path / "noversion.3mf"
    with zipfile.ZipFile(stripped, "w") as archive:
        for name, data in parts.items():
            archive.writestr(name, data)
    result = painted.read(str(stripped))
    assert result["format_version"] is None
    assert result["format_version_known"] is False
    assert slots(result) == [2]


# --- heights, and what they do and do not prove ------------------------------

def test_painted_heights_come_from_the_painted_geometry(tmp_path):
    path = bambu_project(tmp_path, meshes=[{"painted": {0: paint(1), 1: paint(2)},
                                            "extruder": 1}])
    result = painted.read(path)
    assert assignment(result, 1)["z_max_mm"] == pytest.approx(0.0)
    assert assignment(result, 2)["z_min_mm"] == pytest.approx(10.0)


def test_a_placement_transform_moves_the_heights_onto_the_plate(tmp_path):
    path = bambu_project(tmp_path, meshes=[{"painted": {1: paint(2)}, "extruder": 1}],
                         item_transform="1 0 0 0 1 0 0 0 1 0 0 5")
    result = painted.read(path)
    assert assignment(result, 2)["z_min_mm"] == pytest.approx(15.0)
    assert result["objects"][0]["transform_known"] is True


def test_a_scaled_instance_scales_the_heights(tmp_path):
    path = bambu_project(tmp_path, meshes=[{"painted": {1: paint(2)}, "extruder": 1}],
                         item_transform="2 0 0 0 2 0 0 0 2 0 0 0")
    assert assignment(painted.read(path), 2)["z_min_mm"] == pytest.approx(20.0)


def test_a_mirrored_instance_still_reports_a_low_and_a_high(tmp_path):
    path = bambu_project(tmp_path, meshes=[{"painted": {1: paint(2)}, "extruder": 1}],
                         item_transform="1 0 0 0 1 0 0 0 -1 0 0 30")
    entry = assignment(painted.read(path), 2)
    assert entry["z_min_mm"] == pytest.approx(20.0)
    assert entry["z_max_mm"] == pytest.approx(20.0)


def test_a_tilting_transform_leaves_the_heights_unplaced_rather_than_wrong(tmp_path):
    # A rotation about X makes a facet's height depend on its Y as well as its Z.
    # Studio reports the mesh's own heights and says they are not placed, rather
    # than transforming two numbers that no longer describe a box.
    path = bambu_project(tmp_path, meshes=[{"painted": {1: paint(2)}, "extruder": 1}],
                         item_transform="1 0 0 0 0 1 0 -1 0 0 0 0")
    entry = painted.read(path)["objects"][0]["assignments"][0]
    assert entry["z_is_placed"] is False


def test_two_colours_at_different_heights_are_proven_separate(tmp_path):
    path = bambu_project(tmp_path, meshes=[{"painted": {0: paint(1), 1: paint(2)},
                                            "extruder": 1}])
    verdict = painted.coexistence(painted.read(path))
    pair = verdict["pairs"][0]
    assert pair["verdict"] == "separate"
    assert verdict["slots_separate"] == [1, 2]


def test_two_colours_sharing_height_are_reported_as_overlapping_not_as_sharing_a_layer(tmp_path):
    path = bambu_project(tmp_path, meshes=[{"painted": {0: paint((0, [1, 2]))},
                                            "extruder": 1}])
    verdict = painted.coexistence(painted.read(path))
    assert verdict["pairs"][0]["verdict"] == "overlaps"
    assert "does not slice" in verdict["note"]


def test_a_colour_with_no_readable_height_makes_the_pair_unknown(tmp_path):
    path = bambu_project(tmp_path, meshes=[{"painted": {0: paint(1), 1: paint(2)},
                                            "extruder": 1}])
    result = painted.read(path)
    for entry in result["slots"]:
        if entry["slot"] == 2:
            entry["z_min_mm"] = entry["z_max_mm"] = None
    verdict = painted.coexistence(result)
    assert verdict["pairs"][0]["verdict"] == "unknown"
    assert verdict["unknown_pairs"]


# --- files that are trying to break it ---------------------------------------

def test_a_malformed_attribute_costs_one_triangle_not_the_file(tmp_path):
    path = bambu_project(tmp_path, meshes=[
        {"painted": {0: "ZZZZ", 1: paint(2)}, "extruder": 1}])
    result = painted.read(path)
    assert slots(result) == [2]
    obj = result["objects"][0]
    assert obj["malformed_triangle_count"] == 1
    assert obj["malformed_examples"]
    assert result["confidence"] == painted.LIKELY


def test_a_painted_facet_pointing_past_the_mesh_keeps_its_slot_and_loses_its_place(tmp_path):
    # The filament it names is still a fact about the file. Its area and height
    # are not, and are not invented.
    path = bambu_project(
        tmp_path,
        meshes=[{"painted": {0: paint(2)}, "extruder": 1,
                 "triangles": [(0, 1, 99), (3, 4, 5)]}])
    result = painted.read(path)
    obj = result["objects"][0]
    assert obj["facets_outside_mesh"] == 1
    assert slots(result) == [2]
    assert assignment(result, 2)["area_mm2"] == 0.0
    assert assignment(result, 2)["z_min_mm"] is None
    assert result["confidence"] == painted.LIKELY


def test_an_empty_paint_attribute_is_treated_as_unpainted(tmp_path):
    path = bambu_project(tmp_path, meshes=[{"painted": {0: "", 1: ""}, "extruder": 1}])
    result = painted.read(path)
    assert result["slots_referenced"] == []
    assert result["painted_triangle_count"] == 0


def test_a_truncated_attribute_is_refused_per_triangle(tmp_path):
    path = bambu_project(tmp_path, meshes=[{"painted": {0: "3"}, "extruder": 1}])
    result = painted.read(path)
    assert result["objects"][0]["malformed_triangle_count"] == 1


def test_a_state_beyond_any_filament_is_still_read_and_left_to_the_caller(tmp_path):
    # The reader's job is what the file says. Whether slot 40 exists in this
    # project is colour planning's question, and it is answered there.
    path = bambu_project(tmp_path, colours=["#1", "#2"],
                         meshes=[{"painted": {0: paint(40)}, "extruder": 1}])
    assert slots(painted.read(path)) == [40]


def test_the_painted_triangle_budget_bounds_the_work_and_is_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(painted, "MAX_PAINTED_TRIANGLES", 1)
    path = bambu_project(tmp_path, meshes=[{"painted": {0: paint(1), 1: paint(2)},
                                            "extruder": 1}])
    result = painted.read(path)
    assert result["truncated"] is True
    assert result["limits"]["budget_exhausted"] is True
    assert result["confidence"] == painted.LIKELY


def test_a_file_that_is_not_a_project_is_unavailable_rather_than_an_exception(tmp_path):
    path = tmp_path / "not.3mf"
    path.write_bytes(b"this is not a zip")
    result = painted.read(str(path))
    assert result["available"] is False
    assert result["confidence"] == painted.UNKNOWN


def test_a_project_with_no_mesh_part_is_unavailable(tmp_path):
    path = tmp_path / "empty.3mf"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("Metadata/project_settings.config", "{}")
    result = painted.read(str(path))
    assert result["available"] is False
    assert "no model geometry" in result["reason"]


def test_a_deeply_nested_attribute_is_refused_without_taking_the_project_with_it(tmp_path):
    node = 1
    for _ in range(codec.MAX_DEPTH + 2):
        node = (0, [node, 0])
    path = bambu_project(tmp_path, meshes=[
        {"painted": {0: paint(node), 1: paint(2)}, "extruder": 1}])
    result = painted.read(path)
    assert slots(result) == [2]
    assert result["objects"][0]["malformed_triangle_count"] == 1
