"""Local-first, enforced rather than promised.

Studio's headline claim is that everything happens on the user's machine: no
cloud, no account, no telemetry, nothing uploaded. v0.5.0 introduces exactly one
outbound request — an explicit "check GitHub for a newer release" button — and
that is precisely the moment a claim like this starts eroding.

So the rule is written down and checked. The shell may request one host. The
engine may request none: its only network calls go to a printer address the user
typed in, which is why they are built from a variable rather than a literal.

The test looks at what is actually *requested*. A namespace URI in a 3MF, a
project link in a comment, or another tool's homepage in the ecosystem registry
are text, not traffic, and must not be confused for it.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SHELL = ROOT / "desktop" / "src-tauri" / "src" / "main.rs"
ENGINE = ROOT / "backend" / "snapstudio_core"

#: The one host the desktop shell is allowed to reach, and only on a button press.
ALLOWED_SHELL_HOSTS = {"api.github.com"}

_SHELL_REQUEST = re.compile(r"ureq::\w+\(\s*\n?\s*\"https://([a-z0-9.\-]+)")
_ENGINE_REQUEST = re.compile(r"(?:urlopen|Request)\(\s*[\"']https?://([a-z0-9.\-]+)")


def test_the_shell_requests_exactly_one_host():
    requested = set(_SHELL_REQUEST.findall(SHELL.read_text(encoding="utf-8")))
    assert requested <= ALLOWED_SHELL_HOSTS, (
        f"the shell requests hosts it should not: {sorted(requested - ALLOWED_SHELL_HOSTS)}")


def test_the_update_check_is_never_automatic():
    """It runs when a person presses a button. Nothing may call it on startup."""
    shell = SHELL.read_text(encoding="utf-8")
    assert "fn check_for_update" in shell
    # The command is registered for the frontend to invoke; the shell itself must
    # not call it during setup.
    setup = shell[shell.index(".setup("):] if ".setup(" in shell else ""
    assert "check_for_update(" not in setup, (
        "the shell calls the update check during startup — it must be user-initiated")

    app = (ROOT / "desktop" / "src" / "App.tsx").read_text(encoding="utf-8")
    assert "checkForUpdate" not in app, (
        "App.tsx calls the update check on mount — it must be user-initiated")


def test_the_engine_never_requests_a_remote_host():
    offenders = []
    for module in ENGINE.glob("*.py"):
        for match in _ENGINE_REQUEST.finditer(module.read_text(encoding="utf-8")):
            offenders.append(f"{module.name} -> {match.group(1)}")
    assert not offenders, "engine modules requesting a remote host: " + ", ".join(offenders)


def test_the_printer_address_is_always_supplied_not_baked_in():
    """The engine talks to a printer, and only to the one it was given."""
    moonraker = (ENGINE / "moonraker.py").read_text(encoding="utf-8")
    literals = re.findall(r"\"https?://(?!\{)([a-z0-9.\-]+)", moonraker)
    assert not literals, f"moonraker.py contains a hard-coded host: {literals}"


def test_the_update_check_sends_nothing_about_the_user():
    """One GET, a User-Agent, and no body. No identifier, no usage, no file names."""
    shell = SHELL.read_text(encoding="utf-8")
    block = shell[shell.index("fn check_for_update"):]
    block = block[:block.index("\n}\n")]
    for leak in ("hostname", "username", "machine_id", "uuid", "send_json",
                 ".send(", "os_info", "telemetry"):
        assert leak not in block, f"the update check sends {leak}"
