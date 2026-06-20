"""Commit E — real Freedom Torch fixture validation (conditional).

Proves the full A->B->C path on the real 9-plate file when it's available. The
fixture is ~90 MB so it is NOT committed; the test locates it via the
SNAPSTUDIO_FT_FIXTURE env var or the known Downloads path, and SKIPS cleanly if
absent (synthetic-fixture coverage in test_plate_remap.py still runs).

Fixture safety rules enforced here:
- the original real file is NEVER opened for writing,
- the test copies it to a temp path before any export,
- the source sha256 is checked before and after.
"""
import hashlib
import os
import shutil
import zipfile

import pytest

from snapstudio_core import plate_remap as pr

_CANDIDATES = [
    os.environ.get("SNAPSTUDIO_FT_FIXTURE"),
    r"C:/Users/kunal/Downloads/Freedom Torch_U1_UpdatedB.3mf",
    os.path.join(os.path.dirname(__file__), "..", "..", "examples", "Freedom Torch_U1_UpdatedB.3mf"),
]


def _fixture():
    for c in _CANDIDATES:
        if c and os.path.exists(c):
            return c
    return None


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _entry_hashes(path):
    out = {}
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            out[n] = hashlib.sha256(z.read(n)).hexdigest()
    return out


pytestmark = pytest.mark.skipif(_fixture() is None,
                                reason="Freedom Torch fixture not available (set SNAPSTUDIO_FT_FIXTURE)")


def test_freedom_torch_full_path(tmp_path):
    real = _fixture()
    # copy the fixture; NEVER touch the original
    src = str(tmp_path / "ft.3mf")
    shutil.copyfile(real, src)
    real_sha_before = _sha(real)

    # A: inspect
    rep = pr.inspect(src)
    assert rep["available"] and rep["plate_count"] == 9
    nums = {p["ui_number"] for p in rep["plates"]}
    assert {4, 6} <= nums

    # B: dry-run Plate 4, 6 -> 3 hits exactly objects 12 and 14
    dr = pr.dry_run(src, 4, 6, 3)
    assert dr["available"] and dr["change_count"] == 2
    assert sorted(c["object_id"] for c in dr["changes"]) == [12, 14]
    assert 6 in dr["untouched_plates"]

    # C: export to a NEW file; verification gate must pass
    out = str(tmp_path / "ft_plate4_6to3.3mf")
    res = pr.export_remap(src, 4, 6, 3, out)
    assert res["passed"] is True, res.get("reason")
    assert os.path.exists(out)
    assert sorted(c["object_id"] for c in res["changed_objects"]) == [12, 14]

    # ORIGINAL real file untouched (byte-identical)
    assert _sha(real) == real_sha_before

    # only model_settings.config differs between input-copy and output
    hi, ho = _entry_hashes(src), _entry_hashes(out)
    assert set(hi) == set(ho)
    differing = [n for n in hi if hi[n] != ho[n]]
    assert differing == ["Metadata/model_settings.config"]

    # meshes + paint byte-identical (every 3D/ entry)
    for n in hi:
        if n.startswith("3D/"):
            assert hi[n] == ho[n], f"mesh/paint changed: {n}"

    # Plate 6 + gold (filament 4) unchanged in the reinspected output
    out_rep = pr.inspect(out)
    s6 = next(p for p in rep["plates"] if p["ui_number"] == 6)
    o6 = next(p for p in out_rep["plates"] if p["ui_number"] == 6)
    sig = lambda p: sorted((o["object_id"], o.get("base_filament"), o.get("painted_facets")) for o in p["objects"])
    assert sig(s6) == sig(o6)                                 # Plate 6 identical
    gold_before = [o for p in rep["plates"] for o in p["objects"] if o.get("base_filament") == 4]
    gold_after = [o for p in out_rep["plates"] for o in p["objects"] if o.get("base_filament") == 4]
    assert len(gold_before) == len(gold_after) and gold_before  # gold accents preserved


def test_fixture_source_copy_only(tmp_path):
    """The export never mutates the (copied) source file."""
    real = _fixture()
    src = str(tmp_path / "ft2.3mf")
    shutil.copyfile(real, src)
    before = _sha(src)
    pr.export_remap(src, 4, 6, 3, str(tmp_path / "out2.3mf"))
    assert _sha(src) == before                                 # copied source untouched
