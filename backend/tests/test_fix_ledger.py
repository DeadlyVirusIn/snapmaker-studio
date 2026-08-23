"""Fix ledger.

Two things have to hold. The record must be complete enough to answer "what did
Studio do to my file and how do I get back", and it must never leak the user's
directory layout into something they might paste into a bug report. There is also
a third, quieter requirement: bookkeeping must never be able to fail the fix the
user actually asked for.
"""
from __future__ import annotations

import json
import zipfile

from snapstudio_core import fix_ledger


def entry(tmp_path, *, operation=fix_ledger.PREPARE, source="C:/Users/someone/models/a.3mf",
          output="C:/Users/someone/models/a_SnapmakerU1.3mf", **kw):
    return fix_ledger.build_entry(
        operation=operation, source=source, output=output,
        timestamp="2026-08-23T10:00:00Z", engine_version="api/1", **kw)


def test_an_entry_records_the_operation_and_both_file_names(tmp_path):
    e = entry(tmp_path)
    assert e["operation"] == fix_ledger.PREPARE
    assert e["title"] == "Prepared a U1 copy"
    assert e["source_name"] == "a.3mf"
    assert e["output_name"] == "a_SnapmakerU1.3mf"
    assert e["schema_version"] == fix_ledger.SCHEMA_VERSION


def test_changes_carry_old_new_and_reason(tmp_path):
    e = entry(tmp_path, changes=[{"key": "brim_type", "old": "auto_brim",
                                  "new": "no_brim", "reason": "Orca decides differently"}])
    change = e["changes"][0]
    assert change["old"] == "auto_brim" and change["new"] == "no_brim"
    assert change["reason"]


def test_entries_are_newest_first(tmp_path):
    fix_ledger.record(tmp_path, entry(tmp_path, output="one.3mf"))
    fix_ledger.record(tmp_path, entry(tmp_path, output="two.3mf"))
    names = [e["output_name"] for e in fix_ledger.entries(tmp_path)]
    assert names[0] == "two.3mf"


def test_rerunning_a_fix_replaces_its_entry_rather_than_stacking(tmp_path):
    fix_ledger.record(tmp_path, entry(tmp_path, output=str(tmp_path / "out.3mf")))
    fix_ledger.record(tmp_path, entry(tmp_path, output=str(tmp_path / "out.3mf"),
                                      validated=True))
    found = fix_ledger.entries(tmp_path)
    assert len(found) == 1
    assert found[0]["validated"] is True


def test_history_can_be_filtered_to_one_project(tmp_path):
    a, b = str(tmp_path / "a.3mf"), str(tmp_path / "b.3mf")
    fix_ledger.record(tmp_path, entry(tmp_path, source=a, output=str(tmp_path / "a_out.3mf")))
    fix_ledger.record(tmp_path, entry(tmp_path, source=b, output=str(tmp_path / "b_out.3mf")))
    only_a = fix_ledger.entries(tmp_path, source=a)
    assert [e["output_name"] for e in only_a] == ["a_out.3mf"]


def test_the_ledger_is_capped(tmp_path, monkeypatch):
    monkeypatch.setattr(fix_ledger, "MAX_ENTRIES", 3)
    for i in range(6):
        fix_ledger.record(tmp_path, entry(tmp_path, output=f"{i}.3mf"))
    assert len(fix_ledger.entries(tmp_path, limit=100)) == 3


# --- the way back -----------------------------------------------------------

def test_going_back_points_at_the_untouched_original(tmp_path):
    src = tmp_path / "orig.3mf"
    src.write_bytes(b"original")
    out = tmp_path / "orig_SnapmakerU1.3mf"
    out.write_bytes(b"prepared")
    fix_ledger.record(tmp_path, entry(tmp_path, source=str(src), output=str(out)))

    back = fix_ledger.original_for(tmp_path, str(out))
    assert back["available"] is True
    assert back["source_path"] == str(src)
    assert "never modified" in back["note"]
    # Nothing was written or deleted by asking.
    assert src.read_bytes() == b"original"
    assert out.read_bytes() == b"prepared"


def test_a_moved_original_is_reported_honestly(tmp_path):
    out = tmp_path / "out.3mf"
    out.write_bytes(b"prepared")
    fix_ledger.record(tmp_path, entry(tmp_path, source=str(tmp_path / "gone.3mf"),
                                      output=str(out)))
    back = fix_ledger.original_for(tmp_path, str(out))
    assert back["available"] is False
    assert "no longer where Studio last saw it" in back["reason"]
    assert "never modified" in back["reason"]


def test_an_unknown_file_says_so(tmp_path):
    back = fix_ledger.original_for(tmp_path, str(tmp_path / "mystery.3mf"))
    assert back["available"] is False
    assert "no record" in back["reason"]


# --- privacy ----------------------------------------------------------------

def test_a_shared_export_carries_no_file_locations(tmp_path):
    source = "C:/Users/someone/Documents/secret project/model.3mf"
    output = "C:/Users/someone/Documents/secret project/model_SnapmakerU1.3mf"
    fix_ledger.record(tmp_path, entry(tmp_path, source=source, output=output))

    exported = fix_ledger.export_all(tmp_path)
    blob = json.dumps(exported)
    assert "C:/Users/someone" not in blob
    assert "secret project" not in blob
    assert "local" not in exported["entries"][0]
    # The useful part still survives.
    assert exported["entries"][0]["source_name"] == "model.3mf"
    assert exported["entries"][0]["paths_removed"] is True


def test_local_paths_are_still_available_to_the_app(tmp_path):
    fix_ledger.record(tmp_path, entry(tmp_path, source="C:/x/a.3mf", output="C:/x/b.3mf"))
    assert fix_ledger.entries(tmp_path)[0]["local"]["source_path"] == "C:/x/a.3mf"


# --- robustness -------------------------------------------------------------

def test_a_corrupt_ledger_file_is_ignored_not_fatal(tmp_path):
    fix_ledger.ledger_path(tmp_path).write_text("not json", encoding="utf-8")
    assert fix_ledger.entries(tmp_path) == []
    fix_ledger.record(tmp_path, entry(tmp_path))
    assert len(fix_ledger.entries(tmp_path)) == 1


def test_an_unwritable_directory_does_not_raise(tmp_path):
    """Bookkeeping must never fail the fix the user asked for."""
    blocked = tmp_path / "file-not-a-dir"
    blocked.write_text("x", encoding="utf-8")
    fix_ledger.record(blocked / "nested", entry(tmp_path))   # must not raise
    assert fix_ledger.entries(blocked / "nested") == []


def test_titles_are_plain_language():
    assert fix_ledger.title_for(fix_ledger.PLACEMENT) == "Moved the objects onto the plate"
    assert fix_ledger.title_for("something_new") == "Something new"


# --- end to end through the real service ------------------------------------

def _foreign_project(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("3D/3dmodel.model", '<model unit="millimeter"><build/></model>')
        z.writestr("Metadata/project_settings.config",
                   json.dumps({"printer_model": "Bambu Lab X1 Carbon",
                               "filament_colour": ["#FF0000"], "filament_type": ["PLA"],
                               "brim_type": "auto_brim"}))
    return str(path)


def test_preparing_a_copy_writes_a_ledger_entry(tmp_path, monkeypatch):
    monkeypatch.setenv("SNAPSTUDIO_DATA_DIR", str(tmp_path / "data"))
    from snapstudio_api import service

    src = _foreign_project(tmp_path / "foreign.3mf")
    result = service.convert(src, out_dir=str(tmp_path / "out"))

    history = service.fix_history(source=src)
    assert history["entries"], "preparing a copy recorded nothing"
    top = history["entries"][0]
    assert top["operation"] == fix_ledger.PREPARE
    assert top["output_name"] == result["output_name"]
    assert top["validated"] is result["validated_ok"]

    back = service.fix_original(result["output_path"])
    assert back["available"] is True
    assert back["source_path"] == src


def test_a_dry_run_records_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("SNAPSTUDIO_DATA_DIR", str(tmp_path / "data"))
    from snapstudio_api import service

    src = _foreign_project(tmp_path / "dry.3mf")
    service.convert(src, out_dir=str(tmp_path / "out"), dry_run=True)
    assert service.fix_history(source=src)["entries"] == []
