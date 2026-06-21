from snapstudio_core import library


def _db(tmp_path):
    return library.connect(str(tmp_path / "library.db"))


def test_upsert_list_and_update(tmp_path):
    conn = _db(tmp_path)
    pid = library.upsert_project(
        conn, name="Sample Project", source_path="C:/x/Sample Project.3mf",
        source_family="bambu", verdict="REPAIRABLE", score=90, filament_count=5,
        last_action="doctor", updated_at="2026-06-18T20:00:00Z")
    rows = library.list_projects(conn)
    assert len(rows) == 1 and rows[0]["name"] == "Sample Project" and rows[0]["score"] == 90

    # upsert by same source_path updates in place (no duplicate row)
    pid2 = library.upsert_project(
        conn, name="Sample Project", source_path="C:/x/Sample Project.3mf",
        source_family="bambu", output_path="C:/x/Sample Project_SnapmakerU1.3mf",
        verdict="READY", score=100, filament_count=5, last_action="convert",
        updated_at="2026-06-18T20:05:00Z")
    assert pid2 == pid
    rows = library.list_projects(conn)
    assert len(rows) == 1
    assert rows[0]["verdict"] == "READY" and rows[0]["score"] == 100
    assert rows[0]["output_path"].endswith("_SnapmakerU1.3mf")


def test_search_and_tags(tmp_path):
    conn = _db(tmp_path)
    a = library.upsert_project(conn, name="Liberty Eagle", source_path="C:/a.3mf",
                               updated_at="2026-06-18T10:00:00Z")
    library.upsert_project(conn, name="Calibration Cube", source_path="C:/b.stl",
                           updated_at="2026-06-18T11:00:00Z")
    assert [r["name"] for r in library.search_projects(conn, "eagle")] == ["Liberty Eagle"]
    library.add_tag(conn, a, "flags")
    tagged = library.search_projects(conn, tag="flags")
    assert len(tagged) == 1 and tagged[0]["name"] == "Liberty Eagle"
    assert library.search_projects(conn, tag="missing") == []


def test_history_and_delete(tmp_path):
    conn = _db(tmp_path)
    pid = library.upsert_project(conn, name="X", source_path="C:/x.3mf",
                                 updated_at="2026-06-18T09:00:00Z")
    library.add_history(conn, pid, "doctor", "REPAIRABLE 90", "2026-06-18T09:00:00Z")
    library.add_history(conn, pid, "convert", "READY 100", "2026-06-18T09:01:00Z")
    h = library.get_history(conn, pid)
    assert [e["action"] for e in h] == ["convert", "doctor"]  # newest first
    library.delete_project(conn, pid)
    assert library.list_projects(conn) == []
    assert library.get_history(conn, pid) == []
