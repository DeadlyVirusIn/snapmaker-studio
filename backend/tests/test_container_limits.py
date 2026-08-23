"""Untrusted-3MF reader limits.

Studio opens files people downloaded from model sites, so the 3MF reader has to
survive a hostile archive: one that claims to be small and decompresses to
gigabytes, or that carries an absurd number of entries. These tests build those
archives for real and assert the reader refuses them instead of exhausting memory.
"""
from __future__ import annotations

import zipfile

import pytest

from snapstudio_core import container
from snapstudio_core.container import ThreeMF
from snapstudio_core.errors import UnsafeArchive


def _write_zip(path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in entries.items():
            z.writestr(name, data)


def test_normal_archive_still_opens(tmp_path):
    p = tmp_path / "ok.3mf"
    _write_zip(p, {"[Content_Types].xml": b"<x/>", "3D/3dmodel.model": b"<model/>"})
    tm = ThreeMF.open(p)
    assert tm.read_part("3D/3dmodel.model") == b"<model/>"
    assert tm.list_parts() == ["[Content_Types].xml", "3D/3dmodel.model"]


def test_directory_entries_are_preserved(tmp_path):
    """Round-tripping must not drop directory entries from the archive layout."""
    p = tmp_path / "dirs.3mf"
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Metadata/", b"")
        z.writestr("Metadata/a.txt", b"hello")
    tm = ThreeMF.open(p)
    assert "Metadata/" in tm.list_parts()
    out = tmp_path / "out.3mf"
    tm.save(out)
    with zipfile.ZipFile(out) as z:
        assert "Metadata/" in z.namelist()


def test_highly_compressible_bomb_is_refused(tmp_path, monkeypatch):
    """A single entry that expands past the budget is refused, not buffered."""
    monkeypatch.setattr(container, "MAX_TOTAL_UNCOMPRESSED", 4 * 1024 * 1024)
    monkeypatch.setattr(container, "MAX_PART_UNCOMPRESSED", 4 * 1024 * 1024)
    p = tmp_path / "bomb.3mf"
    _write_zip(p, {"3D/3dmodel.model": b"\0" * (16 * 1024 * 1024)})
    # The compressed file is tiny; only metering the decompressed stream catches it.
    assert p.stat().st_size < 200_000
    with pytest.raises(UnsafeArchive):
        ThreeMF.open(p)


def test_total_budget_across_many_parts_is_enforced(tmp_path, monkeypatch):
    """No single part exceeds the per-part cap, but together they blow the total."""
    monkeypatch.setattr(container, "MAX_TOTAL_UNCOMPRESSED", 2 * 1024 * 1024)
    monkeypatch.setattr(container, "MAX_PART_UNCOMPRESSED", 2 * 1024 * 1024)
    p = tmp_path / "many.3mf"
    _write_zip(p, {f"part{i}.bin": b"\0" * (512 * 1024) for i in range(8)})
    with pytest.raises(UnsafeArchive):
        ThreeMF.open(p)


def test_entry_count_is_capped(tmp_path, monkeypatch):
    monkeypatch.setattr(container, "MAX_PARTS", 5)
    p = tmp_path / "lots.3mf"
    _write_zip(p, {f"f{i}.txt": b"x" for i in range(20)})
    with pytest.raises(UnsafeArchive) as e:
        ThreeMF.open(p)
    assert "entries" in str(e.value)


def test_limit_env_override_ignores_garbage(monkeypatch):
    monkeypatch.setenv("SNAPSTUDIO_TEST_LIMIT", "not-a-number")
    assert container._limit("SNAPSTUDIO_TEST_LIMIT", 123) == 123
    monkeypatch.setenv("SNAPSTUDIO_TEST_LIMIT", "-5")
    assert container._limit("SNAPSTUDIO_TEST_LIMIT", 123) == 123
    monkeypatch.setenv("SNAPSTUDIO_TEST_LIMIT", "999")
    assert container._limit("SNAPSTUDIO_TEST_LIMIT", 123) == 999


def test_unsafe_archive_message_is_user_safe(tmp_path, monkeypatch):
    """The message a user could see must not carry a path or a stack trace."""
    monkeypatch.setattr(container, "MAX_TOTAL_UNCOMPRESSED", 1024)
    monkeypatch.setattr(container, "MAX_PART_UNCOMPRESSED", 1024)
    p = tmp_path / "bomb2.3mf"
    _write_zip(p, {"big.bin": b"\0" * 100_000})
    with pytest.raises(UnsafeArchive) as e:
        ThreeMF.open(p)
    assert str(p) not in str(e.value)
