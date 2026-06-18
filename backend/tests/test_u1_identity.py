import json
import zipfile

from snapstudio_core.u1_identity import (
    normalize_project_identity, scrub_foreign, find_foreign, is_u1_clean,
    normalize_slice_info, U1_VERSION,
)
from snapstudio_core.config_io import load_project_settings
from snapstudio_core.convert import convert_to_u1


def _bambu_cfg():
    return {
        "version": "02.05.00.66",
        "printer_model": "Bambu Lab H2D",
        "printer_settings_id": "Bambu Lab H2D 0.4 nozzle",
        "print_settings_id": "0.20mm Standard @BBL H2D",
        "default_print_profile": "0.20mm Standard @BBL H2D",
        "default_filament_profile": ["Bambu PLA Basic @BBL H2D"],
        "filament_settings_id": ["Generic PLA @BBL H2D", "Generic PLA @BBL H2D"],
        "filament_vendor": ["Bambu Lab", "Bambu Lab"],
        "filament_colour": ["#FF0000", "#00FF00"],
        "filament_type": ["PLA", "PLA"],
        "different_settings_to_system": ["enable_support", ""],
        "time_lapse_gcode": ";======== H2D 20251104 ========",
        "ensure_vertical_shell_thickness": "enabled",
    }


# ---- unit: identity normalization + scrub ----
def test_raw_bambu_is_not_clean():
    ok, issues = is_u1_clean(_bambu_cfg())
    assert ok is False and issues


def test_normalize_then_scrub_is_clean_and_preserves_design():
    cfg = _bambu_cfg()
    normalize_project_identity(cfg, n_filaments=len(cfg["filament_colour"]))
    scrub_foreign(cfg)
    ok, issues = is_u1_clean(cfg)
    assert ok is True, issues
    assert find_foreign(cfg) == []
    assert cfg["version"] == U1_VERSION
    assert cfg["printer_model"] == "Snapmaker U1"
    assert "@Snapmaker U1" in cfg["print_settings_id"]
    assert cfg["filament_settings_id"] == ["Snapmaker PLA", "Snapmaker PLA"]
    assert cfg["filament_vendor"] == ["Snapmaker", "Snapmaker"]
    # design preserved
    assert cfg["filament_colour"] == ["#FF0000", "#00FF00"]
    assert cfg["filament_type"] == ["PLA", "PLA"]
    # leftover foreign gcode cleared
    assert cfg["time_lapse_gcode"] == ""


def test_normalize_slice_info_blanks_bbl_version():
    xml = (b'<?xml version="1.0"?>\n<config><header>'
           b'<header_item key="X-BBL-Client-Version" value="02.05.00.66"/>'
           b"</header></config>")
    out = normalize_slice_info(xml)
    assert b'value="02.05.00.66"' not in out
    assert b'key="X-BBL-Client-Version" value=""' in out


# ---- end-to-end: a minimal Bambu 3MF converts to a clean U1 3MF ----
def _bambu_3mf(tmp_path):
    p = tmp_path / "foo.3mf"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types/>')
        z.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships/>')
        z.writestr("3D/3dmodel.model", '<?xml version="1.0"?><model/>')
        z.writestr("Metadata/project_settings.config", json.dumps(_bambu_cfg()))
        z.writestr(
            "Metadata/slice_info.config",
            '<?xml version="1.0"?>\n<config><header>'
            '<header_item key="X-BBL-Client-Version" value="02.05.00.66"/>'
            "</header></config>",
        )
    return p


def test_convert_3mf_strips_all_foreign(tmp_path):
    src = _bambu_3mf(tmp_path)
    res = convert_to_u1(str(src))
    z = zipfile.ZipFile(res.output_path)
    cfg = load_project_settings(z.read("Metadata/project_settings.config"))
    # No foreign tokens survive in any VALUE (key names like `bbl_calib_mark_logo`
    # and slice_info's `X-BBL-Client-Version` are standard and exist in the
    # known-good U1 file, so we check values, not raw text).
    assert find_foreign(cfg) == []
    # H2D / Bambu never appear as legitimate key names, so they must be gone entirely.
    blob = (
        z.read("Metadata/project_settings.config").decode("utf-8").lower()
        + z.read("Metadata/slice_info.config").decode("utf-8").lower()
    )
    assert "h2d" not in blob and "bambu" not in blob
    # slice_info Bambu version stamp blanked
    assert "02.05.00.66" not in blob
    assert cfg["printer_model"] == "Snapmaker U1"
    assert cfg["version"] == U1_VERSION
    # newer-schema enum normalized so Orca does not "replace" it on load
    assert cfg["ensure_vertical_shell_thickness"] == "ensure_all"
    assert cfg["filament_colour"] == ["#FF0000", "#00FF00"]  # design preserved
    assert res.validated_ok is True
    assert src.exists()  # source untouched
