"""Colour planning beyond four toolheads.

The dangerous answer here is the optimistic one. Telling someone their seven-colour
project can be printed with planned swaps, when in fact the colours share layers,
costs them a whole print. So most of these tests check that Studio refuses to
classify a colour it cannot account for, and that painted projects — where the
colour data genuinely cannot be read without slicing — never come back as easy.
"""
from __future__ import annotations

import json
import zipfile

from snapstudio_core import color_plan as cp


def _project(tmp_path, name="p.3mf", *, colours, materials=None, objects=(),
             layer_changes=(), painted=False, layer_height="0.2",
             first_layer="0.2"):
    """objects: iterable of 1-based slot numbers assigned to objects on the plate."""
    settings = {
        "printer_model": "Snapmaker U1",
        "filament_colour": list(colours),
        "filament_type": list(materials or ["PLA"] * len(colours)),
        "layer_height": layer_height,
        "initial_layer_print_height": first_layer,
    }
    object_xml = "".join(
        f'<object id="{i + 1}"><metadata key="extruder" value="{slot - 1}"/></object>'
        for i, slot in enumerate(objects))
    model = ('<model unit="millimeter"><resources/><build><item objectid="1"/></build></model>')
    if painted:
        model = model.replace("<resources/>",
                              '<resources><object id="1"><mesh><triangles>'
                              '<triangle v1="0" v2="1" v3="2" paint_color="8"/>'
                              "</triangles></mesh></object></resources>")
    parts = {
        "3D/3dmodel.model": model,
        "Metadata/project_settings.config": json.dumps(settings),
        "Metadata/model_settings.config": f"<config>{object_xml}<plate/></config>",
    }
    if layer_changes:
        entries = "".join(
            f'<layer top_z="{z}" type="2" extruder="{slot}" color="#000000"/>'
            for slot, z in layer_changes)
        parts["Metadata/custom_gcode_per_layer.xml"] = (
            f"<custom_gcodes_per_layer><plate>{entries}</plate></custom_gcodes_per_layer>")
    p = tmp_path / name
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
        for part, data in parts.items():
            z.writestr(part, data)
    return str(p)


def slots(entries):
    return sorted(e["slot"] for e in entries)


# --- the easy cases ---------------------------------------------------------

def test_four_colours_on_four_toolheads_just_fits(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4"], objects=(1, 2, 3, 4))
    out = cp.analyse(p, toolheads=4)
    assert out["verdict"] == cp.FITS
    assert "every colour has a toolhead" in out["headline"]


def test_headline_states_both_numbers(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2"], objects=(1, 2))
    assert cp.analyse(p, toolheads=4)["headline"].startswith("2 colours, 4 toolheads")


# --- the interesting case: extra colours arrive later -----------------------

def test_extra_colours_introduced_at_a_height_are_layer_based(tmp_path):
    p = _project(tmp_path,
                 colours=["#1", "#2", "#3", "#4", "#5", "#6"],
                 objects=(1, 2, 3, 4),
                 layer_changes=((5, 8.2), (6, 19.4)))
    out = cp.analyse(p, toolheads=4)
    assert out["verdict"] == cp.POSSIBLE_WITH_SWAPS
    assert slots(out["simultaneous"]) == [1, 2, 3, 4]
    assert slots(out["layer_based"]) == [5, 6]
    assert "possible without repainting" in out["headline"]


def test_layer_based_entries_report_the_height_from_the_file(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5"],
                 objects=(1, 2, 3, 4), layer_changes=((5, 12.5),))
    entry = cp.analyse(p, toolheads=4)["layer_based"][0]
    assert entry["from_z_mm"] == 12.5
    assert "12.50 mm" in entry["evidence"]


def test_a_layer_number_is_only_ever_offered_as_an_estimate(tmp_path):
    """An unsliced project has no layer numbers. Studio may compute one from the
    project's layer height, but must never present it as fact."""
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5"],
                 objects=(1, 2, 3, 4), layer_changes=((5, 8.2),),
                 layer_height="0.2", first_layer="0.2")
    entry = cp.analyse(p, toolheads=4)["layer_based"][0]
    assert entry["layer_is_estimated"] is True
    assert entry["estimated_layer"] == 41      # (8.2 - 0.2) / 0.2 + 1
    # The evidence quotes the height, not the estimate.
    assert "mm" in entry["evidence"]


def test_no_layer_estimate_without_a_layer_height(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5"],
                 objects=(1, 2, 3, 4), layer_changes=((5, 8.2),),
                 layer_height="", first_layer="")
    entry = cp.analyse(p, toolheads=4)["layer_based"][0]
    assert entry["estimated_layer"] is None
    assert entry["layer_is_estimated"] is False


def test_summary_names_the_heights_a_user_would_swap_at(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5", "#6"],
                 objects=(1, 2, 3, 4), layer_changes=((5, 8.2), (6, 19.4)))
    summary = cp.analyse(p, toolheads=4)["summary"]
    assert "8.2 mm" in summary and "19.4 mm" in summary


# --- the case that must not be sugar-coated ---------------------------------

def test_more_shared_layer_colours_than_toolheads_needs_reduction(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5", "#6"],
                 objects=(1, 2, 3, 4, 5, 6))
    out = cp.analyse(p, toolheads=4)
    assert out["verdict"] == cp.NEEDS_REDUCTION
    assert "needs colour reduction" in out["headline"]
    assert "merged" in out["summary"] or "merge" in " ".join(out["guidance"]).lower()


def test_painted_colours_are_never_classified_as_swappable(tmp_path):
    """Painted colour is stored encoded. Studio can prove painting exists but not
    which colours it uses, so those colours must not land in the easy bucket."""
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5", "#6"],
                 objects=(1, 2), painted=True)
    out = cp.analyse(p, toolheads=4)
    assert out["painted_regions"] is True
    assert slots(out["layer_based"]) == []
    assert slots(out["unclassified"]) == [3, 4, 5, 6]
    assert out["verdict"] == cp.CANNOT_CLASSIFY
    assert "cannot classify" in out["headline"].lower()


def test_the_painted_explanation_says_why_studio_cannot_read_it(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5"],
                 objects=(1,), painted=True)
    entry = cp.analyse(p, toolheads=4)["unclassified"][0]
    assert "without slicing" in entry["evidence"]
    assert "will not guess" in entry["evidence"]


def test_painted_project_can_still_be_proven_to_need_reduction(tmp_path):
    """When the object assignments alone already exceed the toolheads, the answer
    is provable regardless of what the painted data holds."""
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5", "#6"],
                 objects=(1, 2, 3, 4, 5), painted=True)
    assert cp.analyse(p, toolheads=4)["verdict"] == cp.NEEDS_REDUCTION


def test_an_unused_colour_slot_is_unclassified_not_assumed_free(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5"], objects=(1, 2))
    out = cp.analyse(p, toolheads=4)
    assert slots(out["unclassified"]) == [3, 4, 5]
    assert "no object, painted region or colour change" in out["unclassified"][0]["evidence"]


# --- shape, wording and robustness ------------------------------------------

def test_every_entry_carries_its_evidence(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5", "#6"],
                 objects=(1, 2, 3, 4), layer_changes=((5, 4.0),))
    out = cp.analyse(p, toolheads=4)
    for bucket in ("simultaneous", "layer_based", "unclassified"):
        for entry in out[bucket]:
            assert entry["evidence"], f"{bucket} entry {entry['slot']} has no evidence"
            assert entry["usage"] in (cp.SIMULTANEOUS, cp.LAYER_BASED, cp.UNCLASSIFIED)


def test_the_disclaimer_says_studio_does_not_slice(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2"], objects=(1, 2))
    assert "does not slice" in cp.analyse(p)["disclaimer"]


def test_guidance_never_promises_a_swap_workflow_will_work(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5"],
                 objects=(1, 2, 3, 4), layer_changes=((5, 6.0),))
    text = " ".join(cp.analyse(p, toolheads=4)["guidance"]).lower()
    assert "confirm in snapmaker orca" in text
    assert "will work" not in text
    assert "guaranteed" not in text


def test_toolhead_count_is_respected(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3"], objects=(1, 2, 3))
    assert cp.analyse(p, toolheads=2)["verdict"] == cp.NEEDS_REDUCTION
    assert cp.analyse(p, toolheads=4)["verdict"] == cp.FITS


def test_a_project_with_no_colours_is_unavailable(tmp_path):
    p = tmp_path / "empty.3mf"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("3D/3dmodel.model", "<model/>")
        z.writestr("Metadata/project_settings.config", json.dumps({"printer_model": "x"}))
    out = cp.analyse(str(p))
    assert out["available"] is False
    assert "filament colours" in out["reason"]


def test_an_unreadable_file_does_not_raise(tmp_path):
    bad = tmp_path / "bad.3mf"
    bad.write_bytes(b"not a zip")
    assert cp.analyse(str(bad))["available"] is False


def test_malformed_layer_records_are_skipped_not_fatal(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5"], objects=(1, 2, 3, 4))
    # Rewrite the archive with a junk custom-gcode part.
    import shutil
    with zipfile.ZipFile(p) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    parts["Metadata/custom_gcode_per_layer.xml"] = b"<custom_gcodes_per_layer><layer/></"
    p2 = tmp_path / "junk.3mf"
    with zipfile.ZipFile(p2, "w") as z:
        for n, d in parts.items():
            z.writestr(n, d)
    out = cp.analyse(str(p2), toolheads=4)
    assert out["available"] is True
