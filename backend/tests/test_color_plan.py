"""Colour planning beyond four toolheads.

The dangerous answer here is the optimistic one. Telling someone their seven-colour
project can be printed with planned swaps, when in fact the colours share layers,
costs them a whole print. So most of these tests check that Studio refuses to
classify a colour it cannot account for, and that painted projects — where the
painted colour is read but cannot be proven separate — never come back as easy.
"""
from __future__ import annotations

import json
import zipfile

from snapstudio_core import color_plan as cp


def _project(tmp_path, name="p.3mf", *, colours, materials=None, objects=(),
             layer_changes=(), painted=False, layer_height="0.2",
             first_layer="0.2"):
    """objects: iterable of 1-based slot numbers assigned to objects on the plate.

    The file records these 1-based, matching plate_remap's convention.
    """
    settings = {
        "printer_model": "Snapmaker U1",
        "filament_colour": list(colours),
        "filament_type": list(materials or ["PLA"] * len(colours)),
        "layer_height": layer_height,
        "initial_layer_print_height": first_layer,
    }
    object_xml = "".join(
        f'<object id="{i + 1}"><metadata key="extruder" value="{slot}"/></object>'
        for i, slot in enumerate(objects))
    model = ('<model unit="millimeter"><resources/><build><item objectid="1"/></build></model>')
    if painted:
        # `painted` may be True (a painted facet with no readable geometry, which
        # is what a mesh Studio cannot place looks like) or a list of
        # (attribute, (z_low, z_high)) for facets whose heights are real.
        if painted is True:
            facets = '<triangle v1="0" v2="1" v3="2" paint_color="8"/>'
            vertices = ""
        else:
            vertices, facets, index = [], [], 0
            for attribute, (low, high) in painted:
                vertices += [f'<vertex x="0" y="0" z="{low}"/>',
                             f'<vertex x="10" y="0" z="{low}"/>',
                             f'<vertex x="0" y="10" z="{high}"/>']
                facets.append(f'<triangle v1="{index}" v2="{index + 1}" '
                              f'v3="{index + 2}" paint_color="{attribute}"/>')
                index += 3
            vertices = f"<vertices>{''.join(vertices)}</vertices>"
            facets = "".join(facets)
        model = model.replace("<resources/>",
                              '<resources><object id="1"><mesh>'
                              f'{vertices}<triangles>{facets}'
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


def test_painted_facets_with_no_readable_height_are_still_not_swappable(tmp_path):
    """The slot is read; the height is not. Without a height there is no proof of
    separation, so the colour must not land in the easy bucket."""
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5", "#6"],
                 objects=(1, 2), painted=True)
    out = cp.analyse(p, toolheads=4)
    assert out["painted_regions"] is True
    assert slots(out["layer_based"]) == []
    assert out["verdict"] == cp.CANNOT_CLASSIFY


def test_the_painted_explanation_names_what_is_missing_not_slicing_in_general(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5"],
                 objects=(1,), painted=True)
    out = cp.analyse(p, toolheads=4)
    entry = [e for e in out["unclassified"] if e.get("painted")][0]
    assert "no readable height" in entry["evidence"]
    assert entry["slot"] == 2  # the slot the painting actually names


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


# --- painted colour, now that it is read rather than guessed at --------------
#
# Every one of these was "cannot classify" before Studio decoded the project's
# own paint. What has to stay true is that the new answers are *proven* ones:
# a colour leaves the "needs a toolhead" bucket only when its separation from
# every other colour is demonstrated, and an unproven separation still says so.

from snapstudio_core import paint_codec as _codec  # noqa: E402


def _paint(state):
    return _codec.encode_tree(state)


def test_a_painted_colour_that_never_shares_a_height_is_offered_as_a_swap(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5"],
                 painted=[(_paint(2), (0.0, 10.0)), (_paint(5), (38.2, 61.0))])
    out = cp.analyse(p, toolheads=4)
    swap = [e for e in out["layer_based"] if e["slot"] == 5]
    assert swap, out["layer_based"]
    assert swap[0]["from_z_mm"] == 38.2
    assert "38.20 mm" in swap[0]["evidence"]
    assert swap[0]["painted_area_mm2"] > 0


def test_two_painted_colours_sharing_a_height_each_need_a_toolhead(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4"],
                 painted=[(_paint(2), (0.0, 20.0)), (_paint(3), (10.0, 30.0))])
    out = cp.analyse(p, toolheads=4)
    assert slots(out["simultaneous"]) == [2, 3]
    assert "can meet on a layer" in out["simultaneous"][0]["evidence"]


def test_a_painted_colour_cannot_be_proven_separate_from_an_unmeasured_object(tmp_path):
    # An object-assigned colour's height is not read from geometry, so Studio
    # cannot prove the painted one avoids it — and says exactly that instead of
    # quietly assuming either answer.
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4", "#5"], objects=(1,),
                 painted=[(_paint(5), (38.2, 61.0))])
    out = cp.analyse(p, toolheads=4)
    entry = [e for e in out["unclassified"] if e["slot"] == 5][0]
    assert "no measured height" in entry["evidence"]
    assert "38.20 mm" in entry["evidence"]


def test_the_painted_summary_is_a_sentence_a_beginner_can_read(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4"],
                 painted=[(_paint(2), (0.0, 5.0)), (_paint(3), (0.0, 5.0)),
                          (_paint(4), (0.0, 5.0))])
    painted = cp.analyse(p, toolheads=4)["painted"]
    assert painted["headline"] == "Parts of this model are painted with 3 filament colours."
    assert painted["slots"] == [2, 3, 4]
    assert painted["painted_facets"] == 3
    assert painted["dialect"] == "bambu"


def test_painting_with_a_slot_the_project_never_lists_is_reported(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2"],
                 painted=[(_paint(6), (0.0, 5.0))])
    out = cp.analyse(p, toolheads=4)
    assert out["painted"]["unlisted_slots"] == [6]
    assert any("slot 6" in line for line in out["guidance"])


def test_a_painted_project_reports_how_much_of_it_each_colour_covers(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4"],
                 painted=[(_paint((0, [2, 3])), (0.0, 0.0))])
    out = cp.analyse(p, toolheads=4)
    areas = {e["slot"]: e["painted_area_mm2"] for e in
             out["simultaneous"] + out["layer_based"] + out["unclassified"]
             if e.get("painted")}
    # One triangle of 50 mm², split in half by the paint itself.
    assert areas[2] == 25.0 and areas[3] == 25.0


def test_the_disclaimer_no_longer_claims_painting_cannot_be_read(tmp_path):
    p = _project(tmp_path, colours=["#1", "#2"], painted=[(_paint(2), (0.0, 5.0))])
    out = cp.analyse(p, toolheads=4)
    assert "does not slice" in out["disclaimer"]
    assert "cannot" not in out["disclaimer"].lower()


def test_an_assigned_colour_is_offered_as_a_swap_when_its_object_cannot_share_a_layer(tmp_path):
    """Studio used to answer "needs a toolhead" for every colour assigned to an
    object, because it had not measured where those objects sit. It has now, so
    two objects at heights that cannot meet are two colours that can be swapped."""
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4"],
                 painted=[(_paint(2), (0.0, 10.0)), (_paint(3), (30.0, 40.0))])
    out = cp.analyse(p, toolheads=4)
    assert slots(out["layer_based"]) == [2, 3]
    assert out["layer_based"][1]["from_z_mm"] == 30.0
    assert "never has to share a layer" in out["layer_based"][0]["evidence"]


def test_an_object_whose_height_cannot_be_measured_still_takes_a_toolhead(tmp_path):
    """The old conservative answer is what remains where the measurement does
    not: an unmeasurable object must be assumed to share layers."""
    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4"], objects=(1,),
                 painted=True)
    out = cp.analyse(p, toolheads=4)
    entry = [e for e in out["simultaneous"] if e["slot"] == 1][0]
    assert "could not measure" in entry["evidence"]


def test_the_plan_is_json_the_way_the_service_sends_it(tmp_path):
    """The colour plan crosses a JSON boundary to reach the app. A value that
    cannot be serialised is not a formatting problem — it is a 500 where a card
    should be, and the installed-build harness is where it was found."""
    import json

    p = _project(tmp_path, colours=["#1", "#2", "#3", "#4"], objects=(1,),
                 painted=[(_paint(2), (0.0, 10.0)), (_paint(3), (30.0, 40.0))],
                 layer_changes=((4, 12.0),))
    out = cp.analyse(p, toolheads=4)
    json.dumps(out)
    assert out["toolheads_measured"] is True
