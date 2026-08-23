"""Printer discovery across the ports a U1 actually listens on.

A stock U1 serves Moonraker through its on-device nginx on :80 (the same address
the built-in Fluidd page uses) as well as on Klipper's standard :7125. Probing
only one of those makes a reachable printer look offline. And when nothing
answers at all, the usual cause is a setting on the printer's touchscreen, not a
broken network — so discovery has to say that.
"""
from __future__ import annotations

from snapstudio_core import moonraker


def test_falls_back_to_the_nginx_port(monkeypatch):
    seen: list[tuple[str, int]] = []

    def fake_probe(host, port=moonraker.DEFAULT_PORT, timeout=1.5):
        seen.append((host, port))
        return {"reachable": port == 80, "host": host, "port": port}

    monkeypatch.setattr(moonraker, "probe", fake_probe)
    out = moonraker.discover(["u1.local"])
    assert seen == [("u1.local", 7125), ("u1.local", 80)]
    assert out[0]["reachable"] is True
    assert out[0]["port"] == 80


def test_stops_at_the_first_port_that_answers(monkeypatch):
    seen: list[int] = []

    def fake_probe(host, port=moonraker.DEFAULT_PORT, timeout=1.5):
        seen.append(port)
        return {"reachable": True, "host": host, "port": port}

    monkeypatch.setattr(moonraker, "probe", fake_probe)
    moonraker.discover(["u1.local"])
    assert seen == [7125]


def test_explicit_port_is_not_second_guessed(monkeypatch):
    seen: list[int] = []

    def fake_probe(host, port=moonraker.DEFAULT_PORT, timeout=1.5):
        seen.append(port)
        return {"reachable": False, "host": host, "port": port}

    monkeypatch.setattr(moonraker, "probe", fake_probe)
    moonraker.discover(["u1.local"], port=7125)
    assert seen == [7125]


def test_unreachable_result_explains_advanced_mode(monkeypatch):
    monkeypatch.setattr(moonraker, "probe",
                        lambda host, port=0, timeout=1.5: {"reachable": False, "host": host, "port": port})
    out = moonraker.discover(["u1.local"])
    assert out[0]["reachable"] is False
    assert "Advanced Mode" in out[0]["hint"]


def test_reachable_result_carries_no_hint(monkeypatch):
    monkeypatch.setattr(moonraker, "probe",
                        lambda host, port=0, timeout=1.5: {"reachable": True, "host": host, "port": port})
    assert "hint" not in moonraker.discover(["u1.local"])[0]
