"""A settings box is not permission to fetch anything, anywhere.

Studio's first hard rule is that it is local-first: no cloud, nothing uploaded, no
outbound internet requests. A provider address is typed by the user, and before
this was written it went straight to `urllib.request.urlopen`. Three things were
demonstrated against that code, not imagined:

* `file:///…` made Studio open a local path;
* `ftp://…` made it open an FTP connection;
* `http://example.com` made it resolve and fetch a page on the public internet,
  which returned a 404 — meaning the request genuinely left the machine.

None of it was reachable from the shipped app, because nothing in the desktop ever
sent a provider address. It was about to become reachable, which is why this exists
before the settings page does rather than after it.
"""
from __future__ import annotations

import pytest

from snapstudio_core.material_providers import (InvalidProviderAddress, spoolman,
                                                validate_provider_url)

LOCAL = [
    "http://127.0.0.1:7912",
    "http://localhost:7912",
    "localhost:7912",
    "http://192.168.1.9:7912",
    "http://10.0.0.4",
    "http://172.16.5.5:7912",
    "http://169.254.10.10:7912",
    "http://100.101.102.103:7912",     # tailnet / CGNAT
    "http://spoolman.local:7912",
    "http://spoolman.lan",
    "http://spoolman",                  # a bare LAN name
    "http://nas.home.arpa:7912",
    "https://spoolman.local:7912",
    "http://[::1]:7912",
    "http://[fd00::1]:7912",
]

REFUSED = [
    "http://example.com",
    "http://spoolman.example.com:7912",
    "https://api.spoolman.io",
    "http://8.8.8.8:7912",
    "http://[2606:4700:4700::1111]",
    "file:///c:/windows/win.ini",
    "ftp://192.168.1.9",
    "gopher://192.168.1.9",
    "http://user:secret@192.168.1.9:7912",
    "http://192.168.1.9:7912/api/v1/spool",
    "http://192.168.1.9:7912/?x=1",
    "http://192.168.1.9:7912/#frag",
    "",
    "   ",
    "http://192.168.1.9:notaport",
    "x" * 300,
]


@pytest.mark.parametrize("address", LOCAL)
def test_an_address_on_your_own_network_is_accepted(address):
    assert validate_provider_url(address).startswith(("http://", "https://"))


@pytest.mark.parametrize("address", REFUSED)
def test_anything_else_is_refused(address):
    with pytest.raises(InvalidProviderAddress):
        validate_provider_url(address)


def test_the_refusal_explains_itself_without_jargon():
    with pytest.raises(InvalidProviderAddress) as raised:
        validate_provider_url("http://example.com")
    message = str(raised.value)
    assert "your own network" in message
    assert "no requests to the internet" in message


def test_a_public_address_never_reaches_the_network(monkeypatch):
    """The refusal happens before anything is opened, not after."""
    def explode(url, timeout=4.0):
        raise AssertionError(f"Studio tried to fetch {url}")

    monkeypatch.setattr("snapstudio_core.material_providers._get_json", explode)
    out = spoolman("http://example.com")
    assert out["available"] is False
    assert "your own network" in out["error"]


def test_a_file_url_never_reaches_the_filesystem(monkeypatch):
    def explode(url, timeout=4.0):
        raise AssertionError(f"Studio tried to open {url}")

    monkeypatch.setattr("snapstudio_core.material_providers._get_json", explode)
    out = spoolman("file:///c:/windows/win.ini")
    assert out["available"] is False
    assert out["error"]


def test_a_bare_address_gains_the_scheme_rather_than_being_refused():
    assert validate_provider_url("192.168.1.9:7912") == "http://192.168.1.9:7912"


def test_a_trailing_slash_and_stray_space_are_tolerated():
    assert validate_provider_url("  http://spoolman.local:7912/  ") == \
        "http://spoolman.local:7912"


def test_the_normalised_url_is_what_gets_requested(monkeypatch):
    seen = {}
    monkeypatch.setattr("snapstudio_core.material_providers._get_json",
                        lambda url, timeout=4.0: seen.setdefault("url", url) and [])
    spoolman("spoolman.local:7912/")
    assert seen["url"].startswith("http://spoolman.local:7912/api/v1/spool")


def test_a_huge_response_is_bounded():
    """The reader caps what it will take from a provider, like every other reader."""
    import inspect

    from snapstudio_core import material_providers

    source = inspect.getsource(material_providers._get_json)
    assert "1024" in source and "read(" in source


def test_a_provider_error_never_carries_the_address_into_the_result(monkeypatch):
    """A support bundle must not gain a LAN address through an error string."""
    import urllib.error

    monkeypatch.setattr(
        "snapstudio_core.material_providers._get_json",
        lambda url, timeout=4.0: (_ for _ in ()).throw(
            urllib.error.URLError("connection refused")))
    out = spoolman("http://192.168.1.44:7912")
    assert "192.168.1.44" not in json_text(out)


def json_text(value) -> str:
    import json

    return json.dumps(value)
