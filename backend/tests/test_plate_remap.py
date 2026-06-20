"""Per-Plate Filament Remapper — inspection tests (Commit A).

Correctness-critical: UI Plate N must map to the <plate> with plater_id == N, not
object order. Validated here on a synthetic 3MF that reproduces the real Freedom
Torch ambiguity (Plate 4 and Plate 6 both carry extruder-6 objects) plus a painted
object, so the parser can't conflate them.
"""
import glob
import os
import zipfile

from snapstudio_core import plate_remap as pr

# Synthetic Bambu/Orca-style 3MF: plates 4 & 6 share filament 6; plate 4 has a
# painted object; palette comes from project_settings (slice_info empty).
_MODEL_SETTINGS = """<?xml version="1.0"?>
<config>
  <object id="12"><metadata key="name" value="Torch_Base"/><metadata key="extruder" value="6"/>
    <part id="1" subtype="normal_part"><metadata key="name" value="base"/></part></object>
  <object id="14"><metadata key="name" value="Frame"/><metadata key="extruder" value="6"/></object>
  <object id="18"><metadata key="name" value="Torch_Base"/><metadata key="extruder" value="6"/></object>
  <object id="99"><metadata key="name" value="GoldStar"/><metadata key="extruder" value="4"/></object>
  <plate><metadata key="plater_id" value="4"/><metadata key="plater_name" value=""/>
    <model_instance><metadata key="object_id" value="12"/></model_instance>
    <model_instance><metadata key="object_id" value="14"/></model_instance></plate>
  <plate><metadata key="plater_id" value="6"/><metadata key="plater_name" value=""/>
    <model_instance><metadata key="object_id" value="18"/></model_instance>
    <model_instance><metadata key="object_id" value="99"/></model_instance></plate>
</config>"""

_ROOT = """<?xml version="1.0"?><model xmlns:p="x"><resources>
  <object id="12"><components><component p:path="/3D/Objects/o12.model" objectid="1"/></components></object>
  <object id="99"><components><component p:path="/3D/Objects/o99.model" objectid="2"/></components></object>
</resources></model>"""

_PAINTED = '<?xml version="1.0"?><model><triangles>' + \
    '<triangle v1="0" v2="1" v3="2" paint_color="4"/>' * 3 + '</triangles></model>'
_PLAIN = '<?xml version="1.0"?><model><triangles><triangle v1="0" v2="1" v3="2"/></triangles></model>'

_PROJECT = '{"filament_colour":["#FFFFFF","#000000","#008000","#F7D959","#DE4343","#A3D8E1"],' \
           '"filament_type":["PLA","PLA","PLA","PLA","PLA","PLA"]}'


def _make_3mf(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("Metadata/model_settings.config", _MODEL_SETTINGS)
        z.writestr("Metadata/project_settings.config", _PROJECT)
        z.writestr("3D/3dmodel.model", _ROOT)
        z.writestr("3D/Objects/o12.model", _PAINTED)   # plate 4 object: painted (accents)
        z.writestr("3D/Objects/o99.model", _PLAIN)


def test_inspect_real_repo_sample():
    sample = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "*U1*.3mf")))
    if not sample:
        return
    out = pr.inspect(sample[0])
    assert out["available"] is True
    assert out["plate_count"] >= 1
    assert out["plates"][0]["ui_number"] is not None


def test_ui_plate_maps_by_plater_id_not_object_order(tmp_path):
    f = str(tmp_path / "synth.3mf"); _make_3mf(f)
    out = pr.inspect(f)
    assert out["available"] is True and out["plate_count"] == 2
    p4 = next(p for p in out["plates"] if p["ui_number"] == 4)
    p6 = next(p for p in out["plates"] if p["ui_number"] == 6)
    assert sorted(o["object_id"] for o in p4["objects"]) == [12, 14]
    assert sorted(o["object_id"] for o in p6["objects"]) == [18, 99]


def test_plate4_and_plate6_share_filament6_but_are_distinct(tmp_path):
    f = str(tmp_path / "synth.3mf"); _make_3mf(f)
    out = pr.inspect(f)
    p4 = next(p for p in out["plates"] if p["ui_number"] == 4)
    p6 = next(p for p in out["plates"] if p["ui_number"] == 6)
    assert 6 in [x["id"] for x in p4["filaments_used"]]
    assert 6 in [x["id"] for x in p6["filaments_used"]]
    # Plate 6 also uses filament 4 (the gold object) — proves they're not merged.
    assert 4 in [x["id"] for x in p6["filaments_used"]]
    assert 4 not in [x["id"] for x in p4["filaments_used"]]


def test_painted_accents_detected_per_plate(tmp_path):
    f = str(tmp_path / "synth.3mf"); _make_3mf(f)
    out = pr.inspect(f)
    p4 = next(p for p in out["plates"] if p["ui_number"] == 4)
    assert p4["painted_accents_present"] is True
    o12 = next(o for o in p4["objects"] if o["object_id"] == 12)
    assert o12["painted_facets"] == 3


def test_palette_from_project_settings_colours(tmp_path):
    f = str(tmp_path / "synth.3mf"); _make_3mf(f)
    out = pr.inspect(f)
    assert out["filament_palette"]["3"]["color"] == "#008000"   # green
    assert out["filament_palette"]["6"]["color"] == "#A3D8E1"


def test_not_a_3mf_is_unavailable(tmp_path):
    bad = tmp_path / "x.txt"; bad.write_text("nope")
    assert pr.inspect(str(bad))["available"] is False


# ---- Commit B: dry-run diff ----

def test_dry_run_plate4_changes_only_plate4(tmp_path):
    f = str(tmp_path / "s.3mf"); _make_3mf(f)
    d = pr.dry_run(f, ui_plate=4, from_filament=6, to_filament=3)
    assert d["available"] and d["change_count"] == 2
    assert sorted(c["object_id"] for c in d["changes"]) == [12, 14]
    assert 6 in d["untouched_plates"]            # Plate 6 NOT touched
    assert d["painted_accents_preserved"] is True


def test_dry_run_plate6_only_blue_object_not_gold(tmp_path):
    f = str(tmp_path / "s.3mf"); _make_3mf(f)
    d = pr.dry_run(f, ui_plate=6, from_filament=6, to_filament=3)
    # obj 18 (filament 6) changes; obj 99 (gold filament 4) untouched
    assert [c["object_id"] for c in d["changes"]] == [18]
    assert 99 in [u["object_id"] for u in d["unchanged_objects_on_plate"]]


def test_dry_run_gold_filament_not_present_on_plate4_is_noop(tmp_path):
    f = str(tmp_path / "s.3mf"); _make_3mf(f)
    d = pr.dry_run(f, ui_plate=4, from_filament=4, to_filament=3)
    assert d["change_count"] == 0
    assert any("filament 4" in w for w in d["warnings"])


def test_dry_run_unknown_plate(tmp_path):
    f = str(tmp_path / "s.3mf"); _make_3mf(f)
    d = pr.dry_run(f, ui_plate=99, from_filament=6, to_filament=3)
    assert d["available"] is False and "not found" in d["reason"]


def test_dry_run_same_source_target_warns(tmp_path):
    f = str(tmp_path / "s.3mf"); _make_3mf(f)
    d = pr.dry_run(f, ui_plate=4, from_filament=6, to_filament=6)
    assert any("same" in w for w in d["warnings"])


# ---- Commit C: verified writer/export ----

import hashlib
import zipfile


def _entry_hashes(path):
    out = {}
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            out[n] = hashlib.sha256(z.read(n)).hexdigest()
    return out


def test_export_plate4_changes_only_6_to_3(tmp_path):
    src = str(tmp_path / "s.3mf"); _make_3mf(src)
    out = str(tmp_path / "out.3mf")
    r = pr.export_remap(src, 4, 6, 3, out)
    assert r["passed"] is True
    assert sorted(c["object_id"] for c in r["changed_objects"]) == [12, 14]
    re_out = pr.inspect(out)
    p4 = next(p for p in re_out["plates"] if p["ui_number"] == 4)
    assert all(o["base_filament"] == 3 for o in p4["objects"])   # both now filament 3


def test_export_plate6_unchanged(tmp_path):
    src = str(tmp_path / "s.3mf"); _make_3mf(src)
    out = str(tmp_path / "out.3mf")
    pr.export_remap(src, 4, 6, 3, out)
    s6 = next(p for p in pr.inspect(src)["plates"] if p["ui_number"] == 6)
    o6 = next(p for p in pr.inspect(out)["plates"] if p["ui_number"] == 6)
    sig = lambda p: [(o["object_id"], o["base_filament"]) for o in p["objects"]]
    assert sig(s6) == sig(o6)            # Plate 6 objects' filaments identical
    assert sig(o6) == [(18, 6), (99, 4)]  # incl. obj 18 still filament 6


def test_export_gold_accents_unchanged(tmp_path):
    src = str(tmp_path / "s.3mf"); _make_3mf(src)
    out = str(tmp_path / "out.3mf")
    pr.export_remap(src, 4, 6, 3, out)
    # gold object 99 (filament 4) untouched; painted facet counts preserved
    o99 = next(o for p in pr.inspect(out)["plates"] for o in p["objects"] if o["object_id"] == 99)
    assert o99["base_filament"] == 4
    s12 = next(o for p in pr.inspect(src)["plates"] for o in p["objects"] if o["object_id"] == 12)
    o12 = next(o for p in pr.inspect(out)["plates"] for o in p["objects"] if o["object_id"] == 12)
    assert s12["painted_facets"] == o12["painted_facets"]   # paint count unchanged


def test_export_nontarget_zip_entries_byte_identical(tmp_path):
    src = str(tmp_path / "s.3mf"); _make_3mf(src)
    out = str(tmp_path / "out.3mf")
    pr.export_remap(src, 4, 6, 3, out)
    hs, ho = _entry_hashes(src), _entry_hashes(out)
    assert set(hs) == set(ho)
    differing = [n for n in hs if hs[n] != ho[n]]
    assert differing == ["Metadata/model_settings.config"]   # ONLY this changed


def test_export_output_reopens_and_validates(tmp_path):
    src = str(tmp_path / "s.3mf"); _make_3mf(src)
    out = str(tmp_path / "out.3mf")
    r = pr.export_remap(src, 4, 6, 3, out)
    assert r["verification"]["passed"] is True
    assert pr.inspect(out)["available"] is True


def test_export_refuses_invalid_mapping(tmp_path):
    src = str(tmp_path / "s.3mf"); _make_3mf(src)
    # filament 1 is not used on plate 4 -> no changes -> refuse
    r = pr.export_remap(src, 4, 1, 3, str(tmp_path / "bad.3mf"))
    assert r["passed"] is False
    assert not (tmp_path / "bad.3mf").exists()   # nothing written
    # target not in palette -> refuse
    r2 = pr.export_remap(src, 4, 6, 99, str(tmp_path / "bad2.3mf"))
    assert r2["passed"] is False


def test_export_never_mutates_source(tmp_path):
    src = str(tmp_path / "s.3mf"); _make_3mf(src)
    before = _entry_hashes(src)
    pr.export_remap(src, 4, 6, 3, str(tmp_path / "out.3mf"))
    after = _entry_hashes(src)
    assert before == after            # source byte-identical after export
    # and refusing to write to the source path itself
    r = pr.export_remap(src, 4, 6, 3, src)
    assert r["passed"] is False
