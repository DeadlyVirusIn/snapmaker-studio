"""library.py schema-version / migration scaffold."""
import sqlite3

import pytest

from snapstudio_core import library


def test_new_db_initialized_to_version_1(tmp_path):
    conn = library.connect(str(tmp_path / "new.db"))
    try:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 1
    finally:
        conn.close()


def test_existing_unversioned_db_migrated_without_data_loss(tmp_path):
    db = str(tmp_path / "old.db")
    # simulate a pre-versioning DB: schema present, user_version 0, one real row
    raw = sqlite3.connect(db)
    raw.executescript(library._SCHEMA)
    raw.execute("PRAGMA user_version = 0")
    raw.execute("INSERT INTO projects (name, source_path, updated_at) VALUES (?,?,?)",
                ("cube", "/x/cube.3mf", "2026-06-22T00:00:00Z"))
    raw.commit(); raw.close()

    conn = library.connect(db)
    try:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 1
        rows = conn.execute("SELECT name, source_path FROM projects").fetchall()
        assert len(rows) == 1 and rows[0][0] == "cube"   # data preserved
    finally:
        conn.close()


def test_future_version_fails_safely(tmp_path):
    db = str(tmp_path / "future.db")
    raw = sqlite3.connect(db)
    raw.executescript(library._SCHEMA)
    raw.execute(f"PRAGMA user_version = {library.SCHEMA_VERSION + 5}")
    raw.commit(); raw.close()

    with pytest.raises(library.LibraryVersionError):
        library.connect(db)
