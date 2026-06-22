"""write_fix_report path-safety tests."""
import json

import pytest

from snapstudio_core.report import write_fix_report, ReportPathError


def test_normal_report_path_works(tmp_path):
    out = tmp_path / "FIX_REPORT.json"
    written = write_fix_report(out, [{"ok": True}], base_dir=tmp_path)
    assert written.exists()
    assert json.loads(written.read_text())[0]["ok"] is True


def test_traversal_path_rejected(tmp_path):
    base = tmp_path / "out"
    base.mkdir()
    evil = base / ".." / "escape.json"
    with pytest.raises(ReportPathError):
        write_fix_report(evil, [{}], base_dir=base)
    assert not (tmp_path / "escape.json").exists()   # no file created


def test_source_overwrite_rejected(tmp_path):
    model = tmp_path / "model.3mf"
    model.write_bytes(b"original")
    with pytest.raises(ReportPathError):
        write_fix_report(model, [{}])
    assert model.read_bytes() == b"original"          # source untouched


def test_non_json_suffix_rejected(tmp_path):
    target = tmp_path / "report.txt"
    with pytest.raises(ReportPathError):
        write_fix_report(target, [{}])
    assert not target.exists()
