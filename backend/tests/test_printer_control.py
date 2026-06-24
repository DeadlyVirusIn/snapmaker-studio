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


def test_emergency_stop_hits_estop_endpoint(capture_post):
    out = service.printer_emergency_stop("U1.local")
    assert out["action"] == "emergency_stop"
    assert capture_post[-1]["path"] == "/printer/emergency_stop"


def test_upload_rejects_non_gcode(tmp_path):
    bad = tmp_path / "model.stl"
    bad.write_bytes(b"solid")
    with pytest.raises(ValueError):
        service.printer_upload_gcode("U1.local", str(bad), 7125)


def test_upload_gcode_posts_multipart(capture_post, tmp_path):
    g = tmp_path / "part.gcode"
    g.write_bytes(b"G28\nG1 X0 Y0\n")
    out = service.printer_upload_gcode("U1.local", str(g), 7125)
    assert out["ok"] and out["filename"] == "part.gcode"
    last = capture_post[-1]
    assert last["path"] == "/server/files/upload"
    assert last["has_body"] and "multipart/form-data" in last["content_type"]


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
