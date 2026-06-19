"""Mesh diagnostics + geometry loader tests (Design Intelligence, read-only).

Builds synthetic STL meshes with known properties (a closed box, a box missing a
face, a tall-narrow box) and pins integrity / volume / overhang / stability output.
No real-file mutation; pure geometry."""
import struct
from snapstudio_core.geometry import load_mesh
from snapstudio_core import mesh_diagnostics as MD


def _box_faces(x, y, z):
    """8 corners + 12 triangles of an axis-aligned box from (0,0,0) to (x,y,z),
    outward-facing (CCW). Returns list of triangles, each 3 (x,y,z) points."""
    v = [(0, 0, 0), (x, 0, 0), (x, y, 0), (0, y, 0),
         (0, 0, z), (x, 0, z), (x, y, z), (0, y, z)]
    quads = [
        (0, 3, 2, 1),  # bottom (-Z)
        (4, 5, 6, 7),  # top (+Z)
        (0, 1, 5, 4),  # -Y
        (2, 3, 7, 6),  # +Y
        (1, 2, 6, 5),  # +X
        (3, 0, 4, 7),  # -X
    ]
    tris = []
    for a, b, c, d in quads:
        tris.append((v[a], v[b], v[c]))
        tris.append((v[a], v[c], v[d]))
    return tris


def _write_binary_stl(path, tris):
    out = b"\x00" * 80 + struct.pack("<I", len(tris))
    for (p1, p2, p3) in tris:
        out += struct.pack("<12fH", 0, 0, 0, *p1, *p2, *p3, 0)
    path.write_bytes(out)


def _closed_box_stl(tmp_path, x=20, y=20, z=20, name="box.stl"):
    p = tmp_path / name
    _write_binary_stl(p, _box_faces(x, y, z))
    return p


def test_loader_reads_stl_indexed_mesh(tmp_path):
    m = load_mesh(str(_closed_box_stl(tmp_path)))
    assert m is not None
    assert m.triangle_count == 12
    assert len(m.verts) == 8  # deduped corners


def test_closed_box_is_watertight_manifold_and_volume(tmp_path):
    r = MD.analyze(str(_closed_box_stl(tmp_path, 20, 20, 20)))
    assert r["available"] is True
    assert r["integrity"]["watertight"] is True
    assert r["integrity"]["manifold"] is True
    assert r["integrity"]["holes"] == 0
    assert r["integrity"]["winding_consistent"] is True
    # 20*20*20 = 8000 mm^3
    assert abs(r["volume_mm3"] - 8000.0) < 1.0
    assert r["material_estimate_g"] is not None  # watertight -> estimate allowed


def test_box_bottom_not_counted_as_overhang(tmp_path):
    # a plain box rests on the bed: no steep overhangs, no supports needed
    r = MD.analyze(str(_closed_box_stl(tmp_path, 20, 20, 20)))
    assert r["overhang"]["supports_likely"] is False
    assert r["overhang"]["overhang_pct"] == 0.0


def test_box_with_missing_face_has_hole_and_no_estimate(tmp_path):
    tris = _box_faces(20, 20, 20)[:-2]  # drop the two -X triangles -> open hole
    p = tmp_path / "holed.stl"
    _write_binary_stl(p, tris)
    r = MD.analyze(str(p))
    assert r["integrity"]["watertight"] is False
    assert r["integrity"]["holes"] >= 1
    assert r["integrity"]["open_edges"] > 0
    # not watertight -> material estimate withheld (no fabricated number)
    assert r["material_estimate_g"] is None
    assert any(f["level"] == "risk" and "hole" in f["text"].lower() for f in r["findings"])


def test_tall_narrow_box_flags_tip_risk(tmp_path):
    # 5 x 5 x 120 mm -> aspect 24, extreme tall/narrow
    r = MD.analyze(str(_closed_box_stl(tmp_path, 5, 5, 120, name="tall.stl")))
    assert r["stability"]["aspect"] > 4.0
    assert r["stability"]["tip_risk"] is True


def test_squat_box_no_tip_risk(tmp_path):
    r = MD.analyze(str(_closed_box_stl(tmp_path, 60, 60, 20, name="squat.stl")))
    assert r["stability"]["tip_risk"] is False
    assert r["stability"]["com_over_base"] is True


def test_findings_are_plain_language_objects(tmp_path):
    r = MD.analyze(str(_closed_box_stl(tmp_path)))
    assert r["findings"] and all(set(f) == {"level", "text"} for f in r["findings"])
    assert all(f["level"] in ("ok", "warn", "risk") for f in r["findings"])


def test_unreadable_path_degrades_gracefully(tmp_path):
    p = tmp_path / "bad.stl"
    p.write_bytes(b"not an stl")
    r = MD.analyze(str(p))
    assert r["available"] is False and "reason" in r
