"""A guard against the abstraction quietly growing a per-printer branch.

The failure this sprint set out to prevent is not a big rewrite that goes wrong.
It is one small, reasonable-looking line — `if model == "U1": ...` — added under
deadline in a module that is supposed to reason from capabilities, after which the
architecture claim is no longer true and nothing says so.

So this reads the generic printer-intelligence modules with `ast` and fails on a
**conditional** that turns on a printer's model name. It deliberately does not
police the whole repository, and it deliberately does not police strings: Studio
prepares U1 copies and hands them to Snapmaker Orca, so those names appear
throughout the prepare path and in user-facing sentences, correctly. Naming a
printer is fine. *Branching* on which printer it is, inside the layer whose whole
job is to read what a machine reports, is not.

The escape hatch is the profile. Something genuinely specific to one machine
belongs in `data/printer_profiles/*.json` as a fact, where it carries a source and
a verification level, and the generic code reads it without knowing whose it is.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

CORE = Path(__file__).parent.parent / "snapstudio_core"

#: The layer that must reason from what a printer reports. `printer_profiles`
#: itself is excluded: matching a model name is precisely its job, and it is the
#: one place where doing so is honest.
GENERIC_MODULES = [
    "moonraker.py",
    "firmware_caps.py",
    "preflight.py",
    "post_slice.py",
    "send_check.py",
    "material_plan.py",
    "toolhead_fit.py",
    "bed_fit.py",
]

#: Lowercased fragments that name a machine rather than describe a capability.
MODEL_TOKENS = ("u1", "snapmaker", "voron", "bambu", "prusa", "creality", "sovol")


def _names_a_model(value: str) -> bool:
    text = value.strip().lower()
    if not text or len(text) > 40:
        # A long string is a sentence, and sentences are allowed to name printers.
        return False
    return any(token in text for token in MODEL_TOKENS)


class _Branches(ast.NodeVisitor):
    """Collect comparisons against a model name that steer control flow."""

    def __init__(self) -> None:
        self.hits: list[tuple[int, str]] = []

    def visit_Compare(self, node: ast.Compare) -> None:
        parts = [node.left, *node.comparators]
        for part in parts:
            if isinstance(part, ast.Constant) and isinstance(part.value, str) \
                    and _names_a_model(part.value):
                self.hits.append((node.lineno, ast.unparse(node)))
                break
        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        for case in node.cases:
            pattern = case.pattern
            if isinstance(pattern, ast.MatchValue) and isinstance(pattern.value, ast.Constant) \
                    and isinstance(pattern.value.value, str) and _names_a_model(pattern.value.value):
                self.hits.append((case.pattern.lineno, ast.unparse(pattern)))
        self.generic_visit(node)


@pytest.mark.parametrize("filename", GENERIC_MODULES)
def test_no_model_name_branching_in_the_generic_printer_layer(filename):
    path = CORE / filename
    tree = ast.parse(path.read_text("utf-8"), filename=str(path))
    finder = _Branches()
    finder.visit(tree)
    if finder.hits:
        detail = "\n".join(f"  {filename}:{line}  {src}" for line, src in finder.hits)
        pytest.fail(
            "printer-model branching in a module that must reason from what the "
            f"printer reports:\n{detail}\n"
            "Put the machine-specific fact in data/printer_profiles/ and read it "
            "generically instead.")


def test_the_guard_would_actually_catch_one():
    """A guard nobody has seen fail is not known to work."""
    finder = _Branches()
    finder.visit(ast.parse('if printer_model == "Snapmaker U1":\n    pass\n'))
    assert finder.hits

    finder = _Branches()
    finder.visit(ast.parse('if "u1" in sliced_for.lower():\n    pass\n'))
    assert finder.hits, "the exact shape post_slice used to carry must be caught"

    # And that it does not fire on an ordinary sentence mentioning a printer.
    finder = _Branches()
    finder.visit(ast.parse(
        'msg = "Re-slice this model in Snapmaker Orca with a U1 profile."\n'))
    assert not finder.hits


def test_capability_names_are_not_vendor_names():
    """Capabilities are named for what they do, not for who ships them."""
    from snapstudio_core import printer_profiles

    for name in printer_profiles.CAPABILITY_OBJECTS:
        assert not _names_a_model(name), name


def test_every_shipped_profile_declares_a_known_verification_level():
    from snapstudio_core import printer_profiles

    for profile in printer_profiles.load_all():
        assert profile["verification_level"] in printer_profiles.LEVEL_ORDER


def test_only_a_printer_with_hardware_evidence_is_hardware_verified():
    """Adding a profile must not quietly add a hardware claim.

    The U1 is the only machine this project has connected to. If a second profile
    ever declares itself hardware verified, that is a claim about a session that
    has to exist, and this test is where someone is made to notice.
    """
    from snapstudio_core import printer_profiles

    verified = [p["printer_id"] for p in printer_profiles.load_all()
                if p["verification_level"] == printer_profiles.HARDWARE_VERIFIED]
    assert verified == ["snapmaker_u1"], (
        "a profile claims hardware verification. Physical hardware must have been "
        "connected and the session recorded in docs/internal/evidence/ before this "
        "list changes.")
