"""Printer Hub Phase B — control contract tests (mocked Moonraker, no hardware).

These assert that user-initiated control relays hit the correct Moonraker endpoint
with POST, validate inputs, and fail gracefully. Real-hardware verification is a
manual checklist (docs/printer-hub-control.md) — there is no physical U1 in CI.
"""
import pytest

from snapstudio_core import moonraker
from snapstudio_api import service


@pytest.fixture
def capture_post(monkeypatch):
    """Capture moonraker POSTs instead of hitting a printer."""
    calls = []

    def fake_post(host, port, path, timeout, body=None, content_type=None):
        calls.append({"host": host, "port": port, "path": path,
                      "has_body": body is not None, "content_type": content_type})
        return {"result": "ok"}

    monkeypatch.setattr(moonraker, "_post", fake_post)
    return calls


def test_pause_hits_pause_endpoint(capture_post):
    out = service.printer_pause("U1.local", 7125)
    assert out["ok"] and out["action"] == "pause"
    assert capture_post[-1]["path"] == "/printer/print/pause"


def test_resume_hits_resume_endpoint(capture_post):
    service.printer_resume("U1.local")
    assert capture_post[-1]["path"] == "/printer/print/resume"


def test_cancel_hits_cancel_endpoint(capture_post):
    out = service.printer_cancel("U1.local")
    assert out["action"] == "cancel"
    assert capture_post[-1]["path"] == "/printer/print/cancel"


def test_start_requires_filename():
    with pytest.raises(ValueError):
        service.printer_start("U1.local", "", 7125)


def test_start_passes_filename_in_query(capture_post):
    out = service.printer_start("U1.local", "cube.gcode", 7125)
    assert out["action"] == "start" and out["filename"] == "cube.gcode"
    assert "/printer/print/start?filename=cube.gcode" == capture_post[-1]["path"]


def test_emergency_stop_uses_m112_gcode(capture_post):
    # Real U1 Moonraker returns 404 for /printer/emergency_stop; use canonical M112.
    out = service.printer_emergency_stop("U1.local")
    assert out["action"] == "emergency_stop"
    assert "M112" in capture_post[-1]["path"]
    assert "/printer/gcode/script" in capture_post[-1]["path"]


def test_upload_rejects_non_gcode(tmp_path):
    bad = tmp_path / "model.stl"
    bad.write_bytes(b"solid")
    with pytest.raises(ValueError):
        service.printer_upload_gcode("U1.local", str(bad), 7125)


def test_upload_gcode_posts_multipart(capture_post, tmp_path):
    g = tmp_path / "part.gcode"
    g.write_bytes(b"G28\nG1 X0 Y0\n")
    out = service.printer_upload_gcode("U1.local", str(g), 7125, confirm=False)
    assert out["filename"] == "part.gcode"
    upload = next(p for p in capture_post if p["path"] == "/server/files/upload")
    assert upload["has_body"] and "multipart/form-data" in upload["content_type"]


def test_an_upload_is_not_ok_until_the_printer_confirms_it(capture_post, tmp_path, monkeypatch):
    """`ok` used to mean "the POST returned". It now means "the printer has the
    file and has finished reading it", because Moonraker parses metadata
    asynchronously and the difference is a job that cannot be started."""
    g = tmp_path / "part.gcode"
    g.write_bytes(b"G28")
    from snapstudio_core import moonraker

    # The printer never answers. Don't spend the polling budget in real time.
    monkeypatch.setattr(moonraker, "_get", lambda *a, **k: {})
    monkeypatch.setattr(moonraker.time, "sleep", lambda *_: None)
    out = service.printer_upload_gcode("U1.local", str(g), 7125)
    assert out["ok"] is False
    assert out["confirmation"]["ok"] is False
    assert out["confirmation"]["detail"]


def test_an_upload_the_printer_confirms_is_ok(capture_post, tmp_path, monkeypatch):
    from snapstudio_core import moonraker

    monkeypatch.setattr(moonraker, "confirm_upload",
                        lambda *a, **k: {"ok": True, "present": True,
                                         "metadata_ready": True, "detail": "confirmed"})
    g = tmp_path / "part.gcode"
    g.write_bytes(b"G28")
    out = service.printer_upload_gcode("U1.local", str(g), 7125)
    assert out["ok"] is True
    assert out["confirmation"]["metadata_ready"] is True


def test_upload_requires_path():
    with pytest.raises(ValueError):
        service.printer_upload_gcode("U1.local", "", 7125)


def test_job_queue_is_read_only(monkeypatch):
    def fake_get(host, port, path, timeout):
        assert path == "/server/job_queue/status"
        return {"result": {"queue_state": "ready",
                            "queued_jobs": [{"filename": "a.gcode", "job_id": "1"}]}}
    monkeypatch.setattr(moonraker, "_get", fake_get)
    out = service.printer_job_queue("U1.local")
    assert out["count"] == 1 and out["jobs"][0]["filename"] == "a.gcode"


def test_control_failure_propagates_as_exception(monkeypatch):
    def boom(*a, **k):
        raise OSError("connection refused")
    monkeypatch.setattr(moonraker, "_post", boom)
    with pytest.raises(OSError):
        service.printer_cancel("offline.local")
