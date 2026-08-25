"""Studio does upload one thing, and the documents have to say so.

Printer Hub transfers a sliced job to the user's own printer over their own
network, after they press the button and confirm it. That is a real feature with a
real route (`/printer/upload_gcode`), a real engine function
(`moonraker.upload_gcode`), and a whole confirmation flow around it.

For several releases the public copy also said "nothing uploaded" and "never
uploads anything anywhere", flatly and without qualification. Both statements were
false, and they were the kind of false that matters most: a privacy claim, in the
documents someone reads *because* they care about privacy.

The intended truth was never in doubt — no cloud, no account, no telemetry, and
nothing off the user's own network. What was missing was the qualifier. So this
guard does not ban the claim; it bans the *absolute* form of it, in the documents
and user-facing strings that describe the product as it is now.

Historical text is left alone on purpose. A changelog entry describing a release
whose Printer Hub really was read-only is correct, and rewriting it would be its
own kind of dishonesty.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

#: Documents and strings that describe the product as it is now. A promise here is
#: read as a promise about today's build.
CURRENT_SURFACES = [
    ROOT / "README.md",
    ROOT / "CLAUDE.md",
    ROOT / "docs" / "SECURITY.md",
    ROOT / "docs" / "INNOVATION_FUND.md",
    ROOT / "docs" / "JUDGE_DEMO.md",
    ROOT / "docs" / "PRODUCT_VISION.md",
    ROOT / "docs" / "RELEASE_NOTES.md",
    ROOT / "docs" / "MATERIAL_PROVIDERS.md",
    ROOT / "docs" / "PRINTER_COMPATIBILITY.md",
    ROOT / "docs" / "windows-install.md",
    ROOT / "docs" / "CODE_SIGNING_POLICY.md",
    ROOT / "docs" / "innovation-fund" / "JUDGE_OVERVIEW.md",
    ROOT / "docs" / "innovation-fund" / "COMMUNITY_POST.md",
    ROOT / "docs" / "internal" / "HANDOFF_v0.8.0.md",
]

UI_DIR = ROOT / "desktop" / "src"

#: The absolute forms. Each of these, standing on its own, says Studio uploads
#: nothing at all — which is not true while Printer Hub exists.
ABSOLUTE = (
    r"nothing uploaded(?![a-z ])",
    r"nothing uploaded\s+(?!off)",
    r"\bno upload(?![a-z])",
    r"never uploads? anything anywhere",
    r"nothing (?:is )?uploaded anywhere",
    r"does not upload anything(?![a-z])",
    r"nothing leaves (?:your|the) (?:computer|machine)(?![a-z])",
    r"(?:files|nothing) never leaves? the machine",
    r"there is no account, cloud, or upload",
)

#: Wording that qualifies the claim correctly. A line carrying one of these is
#: making the true statement, not the absolute one.
QUALIFIERS = (
    "local network", "your network", "off the local network", "off your own",
    "your file stays", "your files stay", "printer hub", "user-confirmed",
    "sliced job", "on the lan",
)


def _offending_lines(text: str) -> list[tuple[int, str]]:
    """Find absolute claims, reading a window rather than a single line.

    A sentence wraps. "…nothing Studio does leaves your local / network." puts the
    qualifier on the next line, and a line-at-a-time reader calls that a false
    claim — which is precisely the mistake the v0.7.1 public-claim guard was
    rebuilt to stop making. So the qualifier is looked for across the line and its
    neighbours, the unit a claim actually lives in.
    """
    lines = text.splitlines()
    out = []
    for index, line in enumerate(lines):
        lowered = line.lower()
        # Collapse whitespace before looking. A wrapped line puts the qualifier
        # across a newline and an indent, so the phrase "local network" arrives
        # with several spaces in the middle of it and a plain substring test
        # misses it.
        window = re.sub(r"\s+", " ", " ".join(lines[max(0, index - 1):index + 2])).lower()
        if any(q in window for q in QUALIFIERS):
            continue
        for pattern in ABSOLUTE:
            if re.search(pattern, lowered):
                out.append((index + 1, line.strip()))
                break
    return out


@pytest.mark.parametrize("doc", CURRENT_SURFACES, ids=lambda p: p.name)
def test_no_current_document_claims_studio_uploads_nothing(doc):
    assert doc.exists(), f"missing document: {doc}"
    offenders = _offending_lines(doc.read_text(encoding="utf-8"))
    assert not offenders, (
        f"{doc.name} makes an absolute no-upload claim while Printer Hub uploads "
        "a sliced job to the user's printer:\n"
        + "\n".join(f"  line {n}: {line}" for n, line in offenders)
        + "\nSay what is true instead — no cloud, no account, no telemetry, and "
          "nothing off the user's own local network.")


def test_no_user_facing_string_claims_studio_uploads_nothing():
    """The app's own copy, which more people read than any document."""
    offenders = []
    for path in sorted(UI_DIR.rglob("*.tsx")) + sorted(UI_DIR.rglob("*.ts")):
        if path.name.endswith((".test.ts", ".test.tsx")):
            continue
        for number, line in _offending_lines(path.read_text(encoding="utf-8")):
            offenders.append(f"  {path.relative_to(ROOT)}:{number}: {line}")
    assert not offenders, (
        "user-facing copy makes an absolute no-upload claim:\n" + "\n".join(offenders))


def test_the_upload_feature_this_guard_is_about_actually_exists():
    """A guard for a feature that has been removed would silently pass forever."""
    from snapstudio_core import moonraker

    assert hasattr(moonraker, "upload_gcode")
    server = (ROOT / "backend" / "snapstudio_api" / "server.py").read_text(encoding="utf-8")
    assert "/printer/upload_gcode" in server


def test_the_guard_catches_the_wording_that_shipped():
    """The exact sentences that were live, so the guard is known to work."""
    for claim in (
        "MIT licensed. Local-first: no cloud, no account, no telemetry, nothing uploaded.",
        "Everything runs on your machine. No cloud, no account, no upload.",
        "Studio never uploads anything anywhere.",
        "Nothing leaves the machine; there is no account, cloud, or upload.",
        "Local-only - nothing leaves your computer",
    ):
        assert _offending_lines(claim), f"guard missed: {claim}"


def test_the_guard_accepts_the_wording_that_replaced_it():
    for claim in (
        "No cloud, no account, nothing uploaded off your local network.",
        "Local-only - nothing leaves your network",
        "Drag in a .stl or .3mf - your file stays on your computer",
        "Printer Hub sends a sliced job to your own printer only when you confirm it.",
    ):
        assert not _offending_lines(claim), f"guard false-positive: {claim}"


def test_historical_records_are_deliberately_not_policed():
    """A changelog entry about a read-only Printer Hub is correct as written."""
    changelog = ROOT / "CHANGELOG.md"
    assert changelog.exists()
    assert changelog not in CURRENT_SURFACES
    for old in ("HANDOFF_v0.6.2.md", "HANDOFF_v0.7.2.md"):
        assert (ROOT / "docs" / "internal" / old) not in CURRENT_SURFACES
