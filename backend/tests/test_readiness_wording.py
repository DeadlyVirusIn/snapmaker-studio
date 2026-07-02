"""beta.21.1 copy-truth: fit/profile checks must never read as print-readiness.

Banned in any Validation Center / Design Health output: "Ready as-is",
"Ready after preparation", "Prints on Snapmaker U1", "clean to slice".
"""
import json
import os
import re
import zipfile
from pathlib import Path

from snapstudio_core.validation_report import readiness_report
from snapstudio_core.mesh_diagnostics import analyze as mesh_report

_ROOT = Path(__file__).resolve().parents[2]

BANNED = ["ready as-is", "ready after preparation", "prints on snapmaker u1", "clean to slice"]


def _all_text(report) -> str:
    return json.dumps(report).lower()


def _make_3mf(tmp, colors=4, printer="Snapmaker U1"):
    base = str(_ROOT / "examples" / "sample_cube_U1.3mf")
    dst = os.path.join(tmp, f"c{colors}.3mf")
    zin = zipfile.ZipFile(base)
    cfg = json.loads(zin.read("Metadata/project_settings.config"))
    cfg["filament_colour"] = [f"#{i:06X}" for i in range(colors)]
    cfg["printer_model"] = printer
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zin.infolist():
            data = json.dumps(cfg).encode() if it.filename == "Metadata/project_settings.config" else zin.read(it.filename)
            zo.writestr(it, data)
    return dst


def _make_multi_object_3mf(tmp):
    """Duplicate the build <item> so object spacing becomes unknown."""
    base = str(_ROOT / "examples" / "sample_cube_U1.3mf")
    dst = os.path.join(tmp, "multi.3mf")
    zin = zipfile.ZipFile(base)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename.endswith("3dmodel.model"):
                xml = data.decode("utf-8")
                m = re.search(r"<item\s+[^>]*/>", xml)
                assert m, "sample must contain a build item"
                item2 = m.group(0)
                tm = re.search(r'transform="([^"]+)"', item2)
                if tm:
                    vals = [float(v) for v in tm.group(1).split()]
                    vals[9] += 60.0
                    item2 = item2.replace(tm.group(1), " ".join(f"{v:g}" for v in vals))
                xml = xml.replace(m.group(0), m.group(0) + item2, 1)
                data = xml.encode("utf-8")
            zo.writestr(it, data)
    return dst


def test_validation_center_never_renders_banned_readiness_wording(tmp_path):
    r = readiness_report(_make_3mf(str(tmp_path)))
    text = _all_text(r)
    for phrase in BANNED:
        assert phrase not in text, f"banned wording rendered: {phrase!r}"


def test_multi_object_unknown_spacing_shows_no_ready_wording(tmp_path):
    r = readiness_report(_make_multi_object_3mf(str(tmp_path)))
    text = _all_text(r)
    for phrase in BANNED:
        assert phrase not in text
    # unknown spacing must block a green readiness story outright
    assert r["ready"] is False
    assert not re.search(r"\bready\b(?![^.]*\b(orca|review|not|advisory)\b)", text), \
        "unqualified 'ready' wording with unverified spacing"


def test_stl_geometry_health_positive_without_print_success(tmp_path):
    stl = str(_ROOT / "examples" / "sample_cube.stl")
    rep = mesh_report(stl)
    text = _all_text(rep)
    assert "clean to slice" not in text
    # positive health is still expressible — just not as a print promise
    assert "readable by the slicer" in text or "watertight" in text
    assert "print-ready" not in text and "guaranteed" not in text


def test_source_has_no_banned_strings():
    """Belt-and-braces: the report modules must not contain the banned strings."""
    for mod in ("validation_report.py", "mesh_diagnostics.py"):
        src = (_ROOT / "backend" / "snapstudio_core" / mod).read_text(encoding="utf-8").lower()
        for phrase in BANNED:
            assert phrase not in src, f"{mod} contains banned wording {phrase!r}"
