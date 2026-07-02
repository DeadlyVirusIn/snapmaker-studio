"""3MF zip handling must never turn archive entry names into filesystem paths.

Context: OrcaSlicer fixed a 3MF path-traversal bug (crafted entry names like
``../x`` escaping during import). Studio's ThreeMF container is in-memory by
design — these tests pin that behaviour so a future change can't regress it.
"""
from __future__ import annotations

import zipfile

from snapstudio_core.container import ThreeMF


def _hostile_3mf(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("../evil.txt", b"escape attempt")
        z.writestr("..\\evil_win.txt", b"escape attempt")
        z.writestr("/abs/evil.txt", b"escape attempt")
        z.writestr("3D/3dmodel.model", b"<model/>")


def test_open_hostile_entry_names_stays_in_memory(tmp_path):
    src = tmp_path / "hostile.3mf"
    _hostile_3mf(src)

    before = {p for p in tmp_path.rglob("*")}
    tmf = ThreeMF.open(src)

    # Entries are in-memory parts keyed by their raw names — nothing extracted.
    assert tmf.has_part("../evil.txt")
    assert tmf.read_part("3D/3dmodel.model") == b"<model/>"
    assert {p for p in tmp_path.rglob("*")} == before
    assert not (tmp_path / "evil.txt").exists()
    assert not (tmp_path.parent / "evil.txt").exists()


def test_save_writes_single_zip_only(tmp_path):
    src = tmp_path / "hostile.3mf"
    _hostile_3mf(src)
    out = tmp_path / "out"
    out.mkdir()
    dst = out / "copy.3mf"

    ThreeMF.open(src).save(dst)

    # Save produces exactly one zip; hostile names stay inside it.
    assert [p.name for p in out.rglob("*")] == ["copy.3mf"]
    with zipfile.ZipFile(dst) as z:
        assert "../evil.txt" in z.namelist()
