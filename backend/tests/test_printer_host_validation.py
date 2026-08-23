"""Printer address validation.

The saved printer host is interpolated straight into a request URL. If a value
carrying a scheme, credentials or a path were accepted, a saved setting could
quietly aim Studio's "read-only Moonraker" calls at a completely different
server. Every request builder must go through validate_host().
"""
from __future__ import annotations

import pytest

from snapstudio_core import moonraker
from snapstudio_core.moonraker import InvalidHost, validate_host


@pytest.mark.parametrize("host", [
    "u1.local",
    "snapmaker-u1.local",
    "192.168.1.50",
    "10.0.0.7",
    "localhost",
    "[fe80::1]",
    "printer.lan.",
])
def test_accepts_real_printer_addresses(host):
    assert validate_host(host) == host


@pytest.mark.parametrize("host", [
    "",
    "   ",
    "http://evil.example",
    "evil.example/redirect",
    "user@evil.example",
    "u1.local:7125/../..",
    "u1.local ",  # trailing space is stripped, so this one must still pass
])
def test_rejects_or_normalizes(host):
    if host.strip() == "u1.local":
        assert validate_host(host) == "u1.local"
        return
    with pytest.raises(InvalidHost):
        validate_host(host)


def test_rejects_query_and_fragment():
    for bad in ["u1.local?x=1", "u1.local#frag", "a b.local", "u1\nlocal",
                "u1.local\nHost: evil.example"]:
        with pytest.raises(InvalidHost):
            validate_host(bad)


def test_rejects_overlong_host():
    with pytest.raises(InvalidHost):
        validate_host("a" * 300)


def test_url_builder_uses_validation():
    assert moonraker._url("u1.local", 7125, "/server/info") == "http://u1.local:7125/server/info"
    with pytest.raises(InvalidHost):
        moonraker._url("http://evil.example", 7125, "/server/info")


def test_probe_reports_bad_host_without_making_a_request():
    """probe() never raises; a bad address must come back as unreachable with a
    plain-language reason rather than a traceback."""
    out = moonraker.probe("http://evil.example")
    assert out["reachable"] is False
    assert "printer address" in out["error"]


def test_control_calls_refuse_a_bad_host():
    """The POST path is validated too — control actions must not be a bypass."""
    for fn in (moonraker.pause, moonraker.resume, moonraker.cancel, moonraker.emergency_stop):
        with pytest.raises(InvalidHost):
            fn("evil.example/x")
