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


# --- not being able to ask is not an answer ------------------------------------

def test_a_dropped_connection_is_not_the_printer_saying_it_has_no_filament(monkeypatch):
    """Both used to come back as None, so a socket that failed for a moment was
    reported to the user as "this printer does not report which filaments are
    loaded" — a statement about their machine, made on no evidence."""
    def refuse(host, port, path, timeout):
        raise OSError("[WinError 10048] no source port available")

    monkeypatch.setattr(moonraker, "_get", refuse)
    with pytest.raises(moonraker.PrinterUnavailable):
        moonraker.loaded_filaments("printer.local")


def test_a_printer_without_the_object_still_answers_none(monkeypatch):
    monkeypatch.setattr(moonraker, "_get",
                        lambda *a, **k: {"result": {"status": {}}})
    assert moonraker.loaded_filaments("printer.local") is None


def test_the_material_provider_says_which_of_the_two_happened(monkeypatch):
    from snapstudio_core import material_providers as providers

    def refuse(host, port=7125, timeout=3.0):
        raise moonraker.PrinterUnavailable("Studio could not read what is loaded: OSError")

    monkeypatch.setattr(moonraker, "loaded_filaments", refuse)
    state = providers.stock_u1("printer.local")
    assert state["available"] is False
    assert "could not reach" in state["error"]

    monkeypatch.setattr(moonraker, "loaded_filaments", lambda *a, **k: None)
    state = providers.stock_u1("printer.local")
    assert "does not report" in state["error"]


def test_the_firmware_route_degrades_instead_of_erroring(monkeypatch):
    from snapstudio_api import service

    def refuse(host, port=7125, timeout=3.0):
        raise OSError("no route to host")

    monkeypatch.setattr(moonraker, "capabilities", refuse)
    out = service.printer_firmware("printer.local")
    assert out["available"] is False
    assert "could not ask" in out["summary"]
    assert out["extended_firmware"] is False
