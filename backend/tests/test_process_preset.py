"""Choosing the U1 process preset that describes a project.

Preserve mode keeps the creator's layer height, so stamping one fixed preset name
onto every project produced a 0.12 mm project labelled "0.20 Standard" — correct
settings under a wrong label, which Snapmaker Orca then reports as a customised
preset with no explanation. These tests pin both halves: the name is corrected
when one genuinely fits, and no name is invented when none does.
"""
from __future__ import annotations

import json
import zipfile

import pytest

from snapstudio_core import process_preset as pp


@pytest.mark.parametrize("height,expected", [
    ("0.08", "0.08 Standard @Snapmaker U1 (0.4 nozzle)"),
    ("0.12", "0.12 Standard @Snapmaker U1 (0.4 nozzle)"),
    (0.2, "0.20 Standard @Snapmaker U1 (0.4 nozzle)"),
    ("0.28", "0.28 Standard @Snapmaker U1 (0.4 nozzle)"),
])
def test_a_system_layer_height_gets_its_own_preset_name(height, expected):
    out = pp.choose({"layer_height": height, "nozzle_diameter": ["0.4"]})
    assert out["matched"] is True
    assert out["print_settings_id"] == expected


def test_the_nozzle_variant_follows_the_project():
    out = pp.choose({"layer_height": "0.16", "nozzle_diameter": ["0.6", "0.6"]})
    assert out["print_settings_id"] == "0.16 Standard @Snapmaker U1 (0.6 nozzle)"
    assert out["printer_settings_id"] == "Snapmaker U1 (0.6 nozzle)"
    assert out["printer_variant"] == "0.6"


def test_a_layer_height_with_no_system_preset_is_not_given_an_invented_name():
    out = pp.choose({"layer_height": "0.13", "nozzle_diameter": ["0.4"]})
    assert out["matched"] is False
    assert "print_settings_id" not in out
    assert "customised preset" in out["reason"]
    assert "layer height is unchanged" in out["reason"]


def test_mixed_nozzle_sizes_have_no_honest_preset_name():
    out = pp.choose({"layer_height": "0.12", "nozzle_diameter": ["0.2", "0.4"]})
    assert out["matched"] is False
    assert "single standard U1 nozzle" in out["reason"]


def test_an_unknown_nozzle_size_is_not_matched():
    assert pp.choose({"layer_height": "0.12", "nozzle_diameter": ["1.0"]})["matched"] is False


def test_a_missing_layer_height_keeps_the_default_and_says_why():
    out = pp.choose({"nozzle_diameter": ["0.4"]})
    assert out["matched"] is False
    assert "does not record a layer height" in out["reason"]


def test_a_hair_of_floating_point_noise_still_matches():
    assert pp.choose({"layer_height": "0.2000001", "nozzle_diameter": ["0.4"]})["matched"] is True


def test_a_genuinely_different_height_does_not_match():
    assert pp.choose({"layer_height": "0.205", "nozzle_diameter": ["0.4"]})["matched"] is False


def test_garbage_values_do_not_raise():
    for bad in ("", "abc", None, [], {}):
        assert pp.choose({"layer_height": bad, "nozzle_diameter": ["0.4"]})["matched"] is False


# --- through the real prepare pipeline --------------------------------------

def _project(tmp_path, name, layer_height):
    src = tmp_path / name
    with zipfile.ZipFile(src, "w") as z:
        z.writestr("3D/3dmodel.model", '<model unit="millimeter"><build/></model>')
        z.writestr("Metadata/project_settings.config", json.dumps({
            "printer_model": "Bambu Lab X1 Carbon",
            "filament_colour": ["#FF0000"], "filament_type": ["PLA"],
            "layer_height": layer_height, "nozzle_diameter": ["0.4"]}))
    return str(src)


def _prepared_settings(tmp_path, src, out_name):
    from snapstudio_core.convert import convert_to_u1

    result = convert_to_u1(src, out_dir=str(tmp_path / out_name))
    with zipfile.ZipFile(result.output_path) as z:
        return json.loads(z.read("Metadata/project_settings.config")), result


def test_a_fine_project_is_no_longer_labelled_as_standard(tmp_path):
    cfg, _ = _prepared_settings(tmp_path, _project(tmp_path, "fine.3mf", "0.12"), "a")
    assert cfg["print_settings_id"] == "0.12 Standard @Snapmaker U1 (0.4 nozzle)"
    assert cfg["default_print_profile"] == cfg["print_settings_id"]
    # The creator's actual layer height is still untouched — this changes a label.
    assert cfg["layer_height"] == "0.12"


def test_a_standard_project_keeps_the_standard_label(tmp_path):
    cfg, _ = _prepared_settings(tmp_path, _project(tmp_path, "std.3mf", "0.20"), "b")
    assert cfg["print_settings_id"] == "0.20 Standard @Snapmaker U1 (0.4 nozzle)"


def test_a_custom_layer_height_keeps_the_default_label_and_warns(tmp_path):
    cfg, result = _prepared_settings(tmp_path, _project(tmp_path, "odd.3mf", "0.13"), "c")
    assert cfg["print_settings_id"] == "0.20 Standard @Snapmaker U1 (0.4 nozzle)"
    assert cfg["layer_height"] == "0.13"


def test_the_preset_name_is_reported_as_a_change(tmp_path):
    """A label change is still a change, and the summary has to account for it."""
    _, result = _prepared_settings(tmp_path, _project(tmp_path, "rep.3mf", "0.12"), "d")
    reported = {c["key"] for c in result.settings_summary["compat_changed"]}
    reported |= {c["key"] for c in result.settings_summary.get("mapped_to_u1", [])}
    assert "print_settings_id" in reported
