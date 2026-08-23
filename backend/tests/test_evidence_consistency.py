"""Public evidence counts must agree with the artefacts that produced them.

This project's recurring defect is documents that describe a state the product
has left. Counts are the worst case, because they look precise: a README saying
21/21 when the harness runs 27, or 15/15 when the self-check has 18, is a
verifiable claim that happens to be false — which is worse for a project whose
entire argument is "check it yourself".

`docs/internal/evidence.json` is the single source, written by
`tools/evidence/update.py` from the harness reports and a real self-check run.
Every current-state document is checked against it here.

Historical documents are exempt, and say so.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs" / "internal" / "evidence.json"

# Documents that speak in the present tense about what has been verified.
CURRENT_DOCS = [
    ROOT / "README.md",
    ROOT / "docs" / "INNOVATION_FUND.md",
    ROOT / "docs" / "SUBMISSION_STATUS.md",
    ROOT / "docs" / "innovation-fund" / "JUDGE_OVERVIEW.md",
    ROOT / "docs" / "innovation-fund" / "JUDGE_WALKTHROUGH.md",
    ROOT / "docs" / "innovation-fund" / "FINAL_SUBMISSION.md",
]

# A line mentioning one of these words is talking about that capability, so any
# "n/n" on it has to be that capability's real number.
SUBJECTS = {
    "acceptance": ("installed-application acceptance", "installed application acceptance",
                   "acceptance harness", "installed-build acceptance", "acceptance run"),
    "hardware": ("real snapmaker u1", "real u1", "hardware verification",
                 "read-only verification"),
    "selfcheck": ("selfcheck", "self-check"),
}

_RATIO = re.compile(r"\b(\d{1,3})\s*/\s*(\d{1,3})\b")
_HISTORICAL = ("historical", "superseded", "was accepted", "an earlier version",
               "corrected 2026", "at the time")


@pytest.fixture(scope="module")
def evidence() -> dict:
    assert EVIDENCE.exists(), (
        "docs/internal/evidence.json is missing — run tools/evidence/update.py "
        "after the harnesses have run against the release")
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_the_canonical_file_matches_the_harness_reports(evidence):
    """evidence.json must not drift from the reports it was derived from."""
    version = evidence["version"]
    for kind in ("acceptance", "hardware"):
        report = ROOT / "docs" / "internal" / f"{kind}-{version}.json"
        assert report.exists(), f"{report.name} is missing for the current release"
        data = json.loads(report.read_text(encoding="utf-8"))
        assert evidence[kind]["passed"] == data["passed"]
        assert evidence[kind]["total"] == data["total"]


def test_the_canonical_version_is_the_released_version(evidence):
    metadata = (ROOT / "docs" / "RELEASE_METADATA.md").read_text(encoding="utf-8")
    block = metadata[metadata.index("## Current release"):]
    assert evidence["version"] in block, (
        f"evidence.json is for {evidence['version']}, which is not the released version")


@pytest.mark.parametrize("doc", CURRENT_DOCS, ids=lambda p: p.name)
def test_public_counts_match_the_canonical_evidence(doc, evidence):
    """No current-state line may quote a ratio for a capability that is not its
    real one."""
    assert doc.exists(), f"missing document: {doc}"
    offenders = []
    for number, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
        lowered = line.lower()
        if any(marker in lowered for marker in _HISTORICAL):
            continue
        for key, words in SUBJECTS.items():
            if not any(word in lowered for word in words):
                continue
            expected = f"{evidence[key]['passed']}/{evidence[key]['total']}"
            for found in _RATIO.finditer(line):
                ratio = f"{int(found.group(1))}/{int(found.group(2))}"
                if ratio != expected:
                    offenders.append(f"{doc.name}:{number} says {ratio} for {key}, "
                                     f"canonical is {expected}")
    assert not offenders, "\n  " + "\n  ".join(offenders)


@pytest.mark.parametrize("doc", CURRENT_DOCS, ids=lambda p: p.name)
def test_public_suite_counts_match(doc, evidence):
    """Backend and desktop pass counts, wherever a current-state document quotes
    them next to the word that identifies them."""
    backend = str(evidence["backend"]["passed"])
    desktop = str(evidence["desktop"]["passed"])
    offenders = []
    for number, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
        lowered = line.lower()
        if any(marker in lowered for marker in _HISTORICAL):
            continue
        if "backend" in lowered and "passed" in lowered:
            if backend not in line:
                offenders.append(f"{doc.name}:{number} quotes a backend count that is not {backend}")
        if "desktop" in lowered and "passed" in lowered:
            if desktop not in line:
                offenders.append(f"{doc.name}:{number} quotes a desktop count that is not {desktop}")
    assert not offenders, "\n  " + "\n  ".join(offenders)


def test_current_documents_do_not_call_the_release_a_beta(evidence):
    """The release is stable. 'Unsigned beta' and friends are current-state
    claims, and they are now false."""
    banned = re.compile(r"unsigned beta|this beta|beta release|shipped \(beta\)", re.I)
    offenders = []
    for doc in CURRENT_DOCS:
        for number, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
            if any(marker in line.lower() for marker in _HISTORICAL):
                continue
            if banned.search(line):
                offenders.append(f"{doc.name}:{number}: {line.strip()[:80]}")
    assert not offenders, "\n  " + "\n  ".join(offenders)


def test_the_workflow_description_includes_the_post_slice_half():
    """The product gained a second half in 0.4.0. A description that stops at the
    slicer is describing the old product."""
    for doc in (ROOT / "docs" / "INNOVATION_FUND.md",
                ROOT / "docs" / "innovation-fund" / "JUDGE_OVERVIEW.md",
                ROOT / "README.md"):
        text = doc.read_text(encoding="utf-8").lower()
        assert "g-code" in text or "gcode" in text, (
            f"{doc.name} never mentions the sliced job — it describes the pre-0.4.0 product")
