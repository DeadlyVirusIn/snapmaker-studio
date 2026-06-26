"""File/source ecosystem detection (item 7) — synthetic 3MF fixtures, no real files."""
import json
import zipfile

from snapstudio_core.source_compatibility import detect_detailed


def _make_3mf(tmp_path, parts: dict, name="x.3mf"):
    p = tmp_path / name
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("3D/3dmodel.model", b"<model/>")
        for k, v in parts.items():
            z.writestr(k, v)
    return str(p)


def test_stl_is_detected_as_bare_mesh(tmp_path):
    p = tmp_path / "thing.stl"
    p.write_bytes(b"solid x\nendsolid x\n")
    r = detect_detailed(str(p))
    assert r["ecosystem"] == "stl"
    assert "geometry" in " ".join(r["can_read"]).lower()
    assert r["cannot_convert"]  # honest about what's missing


def test_generic_3mf(tmp_path):
    r = detect_detailed(_make_3mf(tmp_path, {}))
    assert r["ecosystem"] == "generic"
    assert "Orca" in r["recommended_next_step"]


def test_bambu_u1_project(tmp_path):
    cfg = json.dumps({"printer_model": "Snapmaker U1", "filament_type": ["PLA", "PETG"]})
    r = detect_detailed(_make_3mf(tmp_path, {"Metadata/project_settings.config": cfg}))
    assert r["ecosystem"] == "bambu-family"
    assert r["is_u1"] is True
    assert r["readable_settings"]["filament_types"] == ["PETG", "PLA"]
    assert r["cannot_convert"] == []   # already a U1 project
    assert "U1-family" in r["recommended_next_step"]


def test_bambu_non_u1_flags_risk(tmp_path):
    cfg = json.dumps({"printer_model": "Bambu Lab X1C", "filament_type": ["PLA"]})
    r = detect_detailed(_make_3mf(tmp_path, {"Metadata/project_settings.config": cfg}))
    assert r["ecosystem"] == "bambu-family"
    assert r["is_u1"] is False
    assert r["risks"] and "U1" in r["risks"][0]
    assert r["cannot_convert"]          # source profile won't carry over


def test_prusa_project(tmp_path):
    ini = b"; PrusaSlicer config\nprinter_model = MK4\nfilament_colour = #FF0000;#00FF00\nfilament_type = PLA;PETG\n"
    r = detect_detailed(_make_3mf(tmp_path, {"Metadata/Slic3r_PE.config": ini}))
    assert r["ecosystem"] == "prusa"
    assert r["source_app"] == "PrusaSlicer"
    assert r["readable_settings"]["filament_count"] == 2
    assert r["cannot_convert"]          # prusa settings don't transfer
    assert "Orca" in r["recommended_next_step"]


def test_cura_project(tmp_path):
    r = detect_detailed(_make_3mf(tmp_path, {"Metadata/Cura.metadata": b"{}"}))
    assert r["ecosystem"] == "cura"
    assert r["cannot_convert"]          # cura settings not read yet (honest)


def test_unknown_non_3mf_is_honest(tmp_path):
    p = tmp_path / "notes.txt"
    p.write_text("hello")
    r = detect_detailed(str(p))
    assert r["ecosystem"] == "unknown"
    assert r["risks"]


def test_no_false_full_conversion_claim(tmp_path):
    """No ecosystem report may claim a full conversion Studio doesn't do."""
    for parts, eco in [
        ({"Metadata/Slic3r_PE.config": b"printer_model = MK4\n"}, "prusa"),
        ({"Metadata/Cura.x": b"{}"}, "cura"),
        ({}, "generic"),
    ]:
        r = detect_detailed(_make_3mf(tmp_path, parts))
        blob = (" ".join(r["can_read"]) + " " + r["recommended_next_step"]).lower()
        assert "fully convert" not in blob and "full conversion" not in blob
        assert "100%" not in blob
