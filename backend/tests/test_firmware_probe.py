"""Detecting a community firmware without inventing a marker.

The first version of this probe asked the printer for a path only a community
firmware serves, and treated any 200 as detection. On a real U1 that reported a
stock machine as running Extended Firmware, because the printer's web server
hands the *same* single-page app to every URL it is asked for — `/firmware-config/`,
`/metrics` and `/definitely-not-real-9f3b/` all come back as the identical
2,863-byte page.

So detection now means the firmware answered *for itself*: a page that differs
from what the server says to a path nobody claims, and that identifies itself in
its content. Everything else is "Studio does not know", which is not the same as
"this printer is stock" and must never be reported as though it were.
"""
from __future__ import annotations

import io
import urllib.error

import pytest

from snapstudio_core import moonraker

CATCH_ALL = b"<!DOCTYPE html><html><head><title>Fluidd</title></head><body>app</body></html>"
REAL_PAGE = b"<!DOCTYPE html><html><head><title>firmware-config</title></head><body>ok</body></html>"


class FakeResponse(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
        return False


def serving(pages: dict):
    """A printer that answers each path with the bytes given, or 404."""
    def open_url(request, timeout=None):
        url = request.full_url if hasattr(request, "full_url") else str(request)
        for path, body in pages.items():
            if url.endswith(path):
                return FakeResponse(body)
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)
    return open_url


def test_a_server_that_answers_everything_the_same_way_proves_nothing(monkeypatch):
    """The case that made the first version wrong on a real printer."""
    monkeypatch.setattr(moonraker.urllib.request, "urlopen",
                        serving({"/firmware-config/": CATCH_ALL,
                                 moonraker.CONTROL_PATH: CATCH_ALL}))
    result = moonraker.extended_firmware("printer.local")
    assert result["detected"] is False
    assert "not the same as" in result["evidence"]


def test_a_firmware_that_answers_for_itself_is_detected(monkeypatch):
    monkeypatch.setattr(moonraker.urllib.request, "urlopen",
                        serving({"/firmware-config/": REAL_PAGE}))
    result = moonraker.extended_firmware("printer.local")
    assert result["detected"] is True
    assert result["source"] == "/firmware-config/"


def test_a_different_page_that_does_not_identify_itself_is_not_detection(monkeypatch):
    """Distinct from the catch-all, but nothing in it says what it is."""
    monkeypatch.setattr(moonraker.urllib.request, "urlopen",
                        serving({"/firmware-config/": b"<html>hello</html>",
                                 moonraker.CONTROL_PATH: CATCH_ALL}))
    assert moonraker.extended_firmware("printer.local")["detected"] is False


def test_a_printer_that_does_not_answer_is_unknown_not_stock(monkeypatch):
    monkeypatch.setattr(moonraker.urllib.request, "urlopen", serving({}))
    result = moonraker.extended_firmware("printer.local")
    assert result["detected"] is False
    assert result["known"] is False


def test_no_printer_address_is_answered_not_probed():
    assert moonraker.extended_firmware("")["detected"] is False


@pytest.mark.parametrize("value", [None, {}, {"detected": False}])
def test_the_capability_report_never_claims_firmware_without_a_probe(value):
    from snapstudio_core import firmware_caps

    out = firmware_caps.interpret(["bed_mesh", "extruder"]
                                  + [f"gcode_macro M{i}" for i in range(120)],
                                  1, None, extended_probe=value)
    assert out["extended_firmware"] is False
    assert out["many_custom_macros"] is True
