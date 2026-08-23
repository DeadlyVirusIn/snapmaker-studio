"""Fidelity audit.

The value of this report is entirely in the categories nobody else has:
``unverified`` and ``unsupported``. A report that can only say "preserved" or
"changed" has to lie about the parts it does not understand. So most of these
tests build a prepared copy that is wrong in a specific way and assert Studio
notices, rather than checking that a good conversion looks good.
"""
from __future__ import annotations

import json
import zipfile

from snapstudio_core import fidelity

MODEL = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<model unit="millimeter" xml:lang="en-US"'
    ' xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"{extra}>'
    "<resources><object id=\"1\" type=\"model\"><mesh>"
    '<vertices><vertex x="0" y="0" z="0"/><vertex x="1" y="0" z="0"/>'
    '<vertex x="0" y="1" z="0"/></vertices>'
    '<triangles><triangle v1="0" v2="1" v3="2"/></triangles>'
    "</mesh></object></resources>"
    '<build><item objectid="1" transform="{tf}"/></build></model>'
)

SETTINGS = {
    "printer_model": "Bambu Lab X1 Carbon",
    "filament_colour": ["#FF0000", "#00FF00"],
    "filament_type": ["PLA", "PLA"],
    "layer_height": "0.2",
    "outer_wall_speed": "200",
}

MODEL_SETTINGS = (
    "<config><object id=\"1\"><metadata key=\"extruder\" value=\"1\"/></object>"
    "<plate><metadata key=\"plater_id\" value=\"1\"/></plate></config>"
)


def _write(path, parts: dict) -> str:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data if isinstance(data, bytes) else str(data).encode())
    return str(path)


def _base_parts(extra_model="", tf="1 0 0 0 1 0 0 0 1 10 10 0", settings=None) -> dict:
    return {
        "[Content_Types].xml": "<x/>",
        "3D/3dmodel.model": MODEL.format(extra=extra_model, tf=tf),
        "Metadata/project_settings.config": json.dumps(settings or SETTINGS),
        "Metadata/model_settings.config": MODEL_SETTINGS,
    }


def _pair(tmp_path, before_parts=None, after_parts=None):
    a = _write(tmp_path / "orig.3mf", before_parts or _base_parts())
    b = _write(tmp_path / "prep.3mf", after_parts or _base_parts())
    return a, b


def status_of(report, element_contains):
    for row in report["rows"]:
        if element_contains.lower() in row["element"].lower():
            return row["status"]
    return None


def row_of(report, element_contains):
    for row in report["rows"]:
        if element_contains.lower() in row["element"].lower():
            return row
    return None


# --- the good case ----------------------------------------------------------

def test_identical_copy_is_fully_accounted(tmp_path):
    a, b = _pair(tmp_path)
    report = fidelity.audit(a, b)
    assert report["available"] is True
    assert report["counts"].get(fidelity.UNVERIFIED, 0) == 0
    assert report["claims"]["may_claim_nothing_lost"] is True
    assert "accounted for" in report["summary"]


def test_every_row_has_a_status_and_a_detail(tmp_path):
    a, b = _pair(tmp_path)
    for row in fidelity.audit(a, b)["rows"]:
        assert row["status"] in _ALL_STATUSES
        assert row["detail"]


_ALL_STATUSES = {
    fidelity.PRESERVED_EXACT, fidelity.PRESERVED_SEMANTIC, fidelity.CHANGED,
    fidelity.REMOVED, fidelity.ADDED, fidelity.UNSUPPORTED, fidelity.UNVERIFIED,
}


# --- adversarial: things that must not pass silently ------------------------

def test_a_part_that_vanished_for_no_reason_is_unverified(tmp_path):
    after = _base_parts()
    del after["Metadata/model_settings.config"]
    a, b = _pair(tmp_path, after_parts=after)
    report = fidelity.audit(a, b)
    row = row_of(report, "Per-object settings")
    assert row["status"] in (fidelity.UNVERIFIED, fidelity.REMOVED)
    assert "bug" in row["reason"]
    assert report["claims"]["may_claim_nothing_lost"] is False


def test_altered_mesh_data_is_unverified_not_preserved(tmp_path):
    """Studio never rewrites mesh parts. If one differs, something is wrong and the
    report must not smooth it over."""
    before = _base_parts()
    before["3D/Objects/object_1.model"] = "<model><vertex/></model>"
    after = dict(before)
    after["3D/Objects/object_1.model"] = "<model><vertex/><vertex/></model>"
    a, b = _pair(tmp_path, before_parts=before, after_parts=after)
    report = fidelity.audit(a, b)
    assert status_of(report, "Mesh data") == fidelity.UNVERIFIED
    assert report["claims"]["fully_accounted"] is False


def test_geometry_count_change_in_the_root_model_is_unverified(tmp_path):
    after = _base_parts()
    after["3D/3dmodel.model"] = after["3D/3dmodel.model"].replace(
        '<triangles><triangle v1="0" v2="1" v3="2"/></triangles>',
        '<triangles><triangle v1="0" v2="1" v3="2"/><triangle v1="0" v2="1" v3="2"/></triangles>')
    a, b = _pair(tmp_path, after_parts=after)
    assert status_of(fidelity.audit(a, b), "Model geometry") == fidelity.UNVERIFIED


def test_an_unexpected_new_part_is_reported_as_added(tmp_path):
    after = _base_parts()
    after["Metadata/something_new.json"] = "{}"
    a, b = _pair(tmp_path, after_parts=after)
    report = fidelity.audit(a, b)
    assert any(r["status"] == fidelity.ADDED for r in report["rows"])


def test_a_dropped_layer_height_profile_is_called_out(tmp_path):
    """Variable layer height is work a creator did. Silently dropping it is the
    kind of loss this report exists to surface."""
    before = _base_parts()
    before["Metadata/layer_heights_profile.txt"] = "0 0.2\n10 0.12\n"
    a, b = _pair(tmp_path, before_parts=before, after_parts=_base_parts())
    report = fidelity.audit(a, b)
    row = row_of(report, "Variable layer height")
    assert row["status"] == fidelity.REMOVED
    assert "bug" in row["reason"]
    assert report["claims"]["nothing_removed"] is False


def test_a_preserved_layer_height_profile_is_confirmed(tmp_path):
    parts = _base_parts()
    parts["Metadata/layer_heights_profile.txt"] = "0 0.2\n"
    a, b = _pair(tmp_path, before_parts=parts, after_parts=dict(parts))
    assert status_of(fidelity.audit(a, b), "Variable layer height") == fidelity.PRESERVED_EXACT


def test_a_changed_per_layer_gcode_file_is_unverified(tmp_path):
    before = _base_parts()
    before["Metadata/custom_gcode_per_layer.xml"] = "<custom_gcodes><layer z='1'/></custom_gcodes>"
    after = dict(before)
    after["Metadata/custom_gcode_per_layer.xml"] = "<custom_gcodes/>"
    a, b = _pair(tmp_path, before_parts=before, after_parts=after)
    assert status_of(fidelity.audit(a, b), "Colour changes and pauses") == fidelity.UNVERIFIED


def test_an_unknown_required_extension_is_unsupported_and_blocks_the_claim(tmp_path):
    extra = ' xmlns:fs="http://example.invalid/fullspectrum/1" requiredextensions="fs"'
    parts = _base_parts(extra_model=extra)
    a, b = _pair(tmp_path, before_parts=parts, after_parts=dict(parts))
    report = fidelity.audit(a, b)
    row = row_of(report, "Slicer extensions Studio does not understand")
    assert row["status"] == fidelity.UNSUPPORTED
    assert "never checked" in row["reason"]
    assert report["claims"]["may_claim_nothing_lost"] is False


# --- intentional changes carry their reason ---------------------------------

def test_slice_cache_removal_is_explained_not_hidden(tmp_path):
    before = _base_parts()
    before["Metadata/plate_1.gcode"] = "G1 X0\n"
    a, b = _pair(tmp_path, before_parts=before, after_parts=_base_parts())
    report = fidelity.audit(a, b)
    row = row_of(report, "Sliced output from the original printer")
    assert row["status"] == fidelity.REMOVED
    assert "slice again" in row["reason"]
    # Removing something is still a loss, so the strongest claim is withdrawn.
    assert report["claims"]["may_claim_nothing_lost"] is False
    assert report["claims"]["fully_accounted"] is True


def test_a_placement_fix_is_reported_as_moved_not_as_damage(tmp_path):
    a = _write(tmp_path / "o.3mf", _base_parts(tf="1 0 0 0 1 0 0 0 1 10 10 0"))
    b = _write(tmp_path / "p.3mf", _base_parts(tf="1 0 0 0 1 0 0 0 1 90 90 0"))
    report = fidelity.audit(a, b)
    row = row_of(report, "Model geometry and object placement")
    assert row["status"] == fidelity.CHANGED
    assert "moved" in row["detail"]
    assert "placement fix" in row["reason"]


def test_changed_settings_are_counted_and_named(tmp_path):
    after_settings = dict(SETTINGS)
    after_settings["printer_model"] = "Snapmaker U1"
    after_settings["exclude_object"] = "1"
    a, b = _pair(tmp_path, after_parts=_base_parts(settings=after_settings))
    report = fidelity.audit(a, b)
    changed = row_of(report, "Print settings changed")
    assert changed["status"] == fidelity.CHANGED
    assert "printer_model" in changed["detail"]
    added = row_of(report, "Print settings added")
    assert added["status"] == fidelity.ADDED
    assert "exclude_object" in added["detail"]


def test_a_setting_dropped_entirely_is_not_carried_over(tmp_path):
    after_settings = {k: v for k, v in SETTINGS.items() if k != "outer_wall_speed"}
    a, b = _pair(tmp_path, after_parts=_base_parts(settings=after_settings))
    row = row_of(fidelity.audit(a, b), "Print settings not carried over")
    assert row["status"] == fidelity.REMOVED
    assert "outer_wall_speed" in row["detail"]


def test_settings_kept_are_counted(tmp_path):
    a, b = _pair(tmp_path)
    row = row_of(fidelity.audit(a, b), "Print settings kept")
    assert row["status"] == fidelity.PRESERVED_EXACT
    assert "5 setting(s)" in row["detail"]


def test_filament_colours_and_order_are_checked(tmp_path):
    swapped = dict(SETTINGS)
    swapped["filament_colour"] = ["#00FF00", "#FF0000"]
    a, b = _pair(tmp_path, after_parts=_base_parts(settings=swapped))
    assert status_of(fidelity.audit(a, b), "Filament colours") == fidelity.CHANGED


def test_tool_assignment_change_is_reported(tmp_path):
    after = _base_parts()
    after["Metadata/model_settings.config"] = MODEL_SETTINGS.replace('value="1"/></object>',
                                                                     'value="3"/></object>')
    a, b = _pair(tmp_path, after_parts=after)
    assert status_of(fidelity.audit(a, b), "Which colour each object uses") == fidelity.CHANGED


# --- claims -----------------------------------------------------------------

def test_claims_are_computed_from_the_rows_not_asserted(tmp_path):
    a, b = _pair(tmp_path)
    clean = fidelity.audit(a, b)["claims"]
    assert clean == {"geometry_unchanged": True, "nothing_removed": True,
                     "fully_accounted": True, "may_claim_nothing_lost": True}

    after = _base_parts()
    del after["Metadata/model_settings.config"]
    a2, b2 = _pair(tmp_path, after_parts=after)
    dirty = fidelity.audit(a2, b2)["claims"]
    assert dirty["may_claim_nothing_lost"] is False


def test_summary_tells_the_user_to_check_unverified_items(tmp_path):
    before = _base_parts()
    before["Metadata/mystery.bin"] = b"\x00\x01"
    after = _base_parts()
    after["Metadata/mystery.bin"] = b"\x00\x02"
    a, b = _pair(tmp_path, before_parts=before, after_parts=after)
    report = fidelity.audit(a, b)
    assert "check them yourself" in report["summary"]


# --- robustness -------------------------------------------------------------

def test_unreadable_original_is_unavailable_not_an_exception(tmp_path):
    bad = tmp_path / "bad.3mf"
    bad.write_bytes(b"not a zip")
    a, b = _pair(tmp_path)
    report = fidelity.audit(str(bad), b)
    assert report["available"] is False
    assert report["claims"]["may_claim_nothing_lost"] is False


def test_unreadable_prepared_copy_is_unavailable(tmp_path):
    bad = tmp_path / "bad2.3mf"
    bad.write_bytes(b"not a zip")
    a, _ = _pair(tmp_path)
    assert fidelity.audit(a, str(bad))["available"] is False


def test_real_conversion_is_fully_accounted(tmp_path):
    """End to end against the actual prepare pipeline, not a hand-built copy."""
    from snapstudio_core.convert import convert_to_u1

    src = tmp_path / "foreign.3mf"
    _write(src, _base_parts())
    result = convert_to_u1(str(src), out_dir=str(tmp_path / "out"))
    report = fidelity.audit(str(src), result.output_path)
    assert report["available"] is True
    assert report["counts"].get(fidelity.UNVERIFIED, 0) == 0, report["unverified"]
    assert report["claims"]["fully_accounted"] is True
