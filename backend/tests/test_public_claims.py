"""Guard: public-facing copy must not make print-success guarantees.

Keeps the README + release notes free of absolute "will print" / "100% U1-ready"
/ "guaranteed print" claims. Advisory hedges like "not a guarantee" are allowed.
"""
import os

import pytest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
_PUBLIC_DOCS = [
    "README.md",
    os.path.join("docs", "RELEASE_NOTES.md"),
]

_BANNED = [
    "tells you whether it will print",
    "tells you if it will print",
    "tells you whether a design will print",
    "100% u1-ready",
    "guaranteed print",
    "guaranteed to print",
    "guarantees it will print",
]


@pytest.mark.parametrize("rel", _PUBLIC_DOCS)
def test_no_print_success_guarantees(rel):
    path = os.path.join(_ROOT, rel)
    if not os.path.exists(path):
        pytest.skip(f"{rel} not present")
    text = open(path, encoding="utf-8").read().lower()
    for phrase in _BANNED:
        assert phrase not in text, f"banned claim '{phrase}' found in {rel}"
