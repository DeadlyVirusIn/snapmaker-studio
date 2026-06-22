"""Guard: public-facing copy must not make print-success guarantees, and the
public release notes must not leak internal review/tooling or implementation
mechanics.

- README + release notes: no absolute "will print" / "100% U1-ready" /
  "guaranteed print" claims (advisory hedges like "not a guarantee" are allowed).
- Release notes (the file that becomes the GitHub release body) + the install doc:
  no internal review tools, AI model names, or exploit-style mechanics. Describe
  user-facing features and fixes only. This enforces the public-release protocol
  for every future release, not just one.
"""
import os
import re

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


# AI-tool / process / mechanics names that must never appear in ANY public doc.
_BANNED_TOOLS = [
    ("octo", r"\bocto\b"),
    ("/octo", r"/octo"),
    ("codex", r"\bcodex\b"),
    ("claude", r"\bclaude\b"),
    ("sonnet", r"\bsonnet\b"),
    ("gemini", r"\bgemini\b"),
    ("antigravity", r"\bantigravity\b"),
    ("multi-provider", r"multi-?provider"),
    ("body-drain", r"body-?drain"),
    ("request-hardening", r"request-?hardening"),
    ("security surface", r"security surface"),
    ("exploit", r"\bexploit"),
]


@pytest.mark.parametrize("rel", [
    os.path.join("docs", "RELEASE_NOTES.md"),
    os.path.join("docs", "windows-install.md"),
])
def test_public_docs_have_no_tooling_names(rel):
    path = os.path.join(_ROOT, rel)
    if not os.path.exists(path):
        pytest.skip(f"{rel} not present")
    text = open(path, encoding="utf-8").read().lower()
    for label, pattern in _BANNED_TOOLS:
        assert not re.search(pattern, text), f"tooling term '{label}' found in {rel}"


# The marketing release body additionally must not carry low-level mechanics terms
# (token/CSP/NaN/Infinity). Scoped to RELEASE_NOTES.md only — an install guide may
# legitimately use words like "token", so it is exempt from this stricter set.
_RELEASE_SURFACES = [
    os.path.join("docs", "RELEASE_NOTES.md"),
]

# (label, regex) — word-boundaries where a short token would false-match (e.g.
# "octo" inside "Doctor", "nan" inside a longer word).
_BANNED_INTERNAL = [
    ("octo", r"\bocto\b"),
    ("/octo", r"/octo"),
    ("codex", r"\bcodex\b"),
    ("claude", r"\bclaude\b"),
    ("sonnet", r"\bsonnet\b"),
    ("gemini", r"\bgemini\b"),
    ("antigravity", r"\bantigravity\b"),
    ("multi-provider", r"multi-?provider"),
    ("body-drain", r"body-?drain"),
    ("request-hardening", r"request-?hardening"),
    ("security surface", r"security surface"),
    ("nan", r"\bnan\b"),
    ("infinity", r"\binfinity\b"),
    ("csp", r"\bcsp\b"),
    ("token", r"\btoken\b"),
    ("exploit", r"\bexploit"),
]


@pytest.mark.parametrize("rel", _RELEASE_SURFACES)
def test_release_notes_have_no_internal_tooling_terms(rel):
    path = os.path.join(_ROOT, rel)
    if not os.path.exists(path):
        pytest.skip(f"{rel} not present")
    text = open(path, encoding="utf-8").read().lower()
    for label, pattern in _BANNED_INTERNAL:
        assert not re.search(pattern, text), f"internal/tooling term '{label}' found in {rel}"
