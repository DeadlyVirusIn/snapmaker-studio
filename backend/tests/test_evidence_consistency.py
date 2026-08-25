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

The reading itself lives in `doc_truth.py`, which works on blocks — a paragraph, a
table row, a list item — rather than lines. Three false claims shipped in v0.7.0
because the old line-by-line reading could not see a sentence that wrapped, a call
to action outside the Download section, or a "published vX installer" line sitting
above the current numbers. Those three are regression-tested in
test_doc_truth_guard.py against the guard itself, not only against today's files.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from doc_truth import (count_offenders, demo_offenders, release_offenders,
                       suite_offenders)

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
                   "acceptance harness", "installed-build acceptance", "acceptance run",
                   "drives the installed application"),
    "hardware": ("real snapmaker u1", "real u1", "hardware verification",
                 "read-only verification"),
    "selfcheck": ("selfcheck", "self-check"),
}

#: Prose forms of the same claim. "a 15-check pass/fail table" and "27 checks over
#: the real window" are counts too, and they drifted while the tables were right.
_PROSE_COUNT = re.compile(r"(\d{1,3})[- ]check(?:s)?", re.I)

_RATIO = re.compile(r"\b(\d{1,3})\s*/\s*(\d{1,3})\b")
_HISTORICAL = ("historical", "superseded", "was accepted", "an earlier version",
               "corrected 2026", "at the time")


def _report(offenders: list[str]) -> str:
    """One offender per line, so a failure reads as a list rather than a blob."""
    joined = chr(10) + "  "
    return joined + joined.join(offenders)


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
    """No present-tense claim may quote a ratio, or an "n-check" count, that is not
    the real one for the capability the claim is about."""
    assert doc.exists(), f"missing document: {doc}"
    offenders = count_offenders(doc.read_text(encoding="utf-8"), evidence,
                                name=doc.name)
    assert not offenders, _report(offenders)


@pytest.mark.parametrize("doc", CURRENT_DOCS, ids=lambda p: p.name)
def test_public_suite_counts_match(doc, evidence):
    """Backend and desktop counts, including the combined row that once carried
    `822 · 284` through an entire release."""
    offenders = suite_offenders(doc.read_text(encoding="utf-8"), evidence,
                                name=doc.name)
    assert not offenders, _report(offenders)


@pytest.mark.parametrize("doc", CURRENT_DOCS, ids=lambda p: p.name)
def test_current_documents_point_at_the_current_release(doc, evidence):
    """Every download link, release link, "published vX installer" credit and
    screenshot path in present-tense prose names the release being shipped.

    Not only the ones inside a section called Download: v0.7.0 shipped with the
    README's top call to action still pointing at v0.6.2, which is the link most
    readers actually use.
    """
    offenders = release_offenders(doc.read_text(encoding="utf-8"), evidence,
                                  name=doc.name)
    assert not offenders, _report(offenders)


@pytest.mark.parametrize("doc", CURRENT_DOCS, ids=lambda p: p.name)
def test_the_demo_length_is_the_demo_s_length(doc, evidence):
    offenders = demo_offenders(doc.read_text(encoding="utf-8"), evidence,
                               name=doc.name)
    assert not offenders, _report(offenders)


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


# --- the other things that go stale -----------------------------------------

def _released_version() -> str:
    metadata = (ROOT / "docs" / "RELEASE_METADATA.md").read_text(encoding="utf-8")
    block = metadata[metadata.index("## Current release"):]
    found = re.search(r"\|\s*Version\s*\|\s*v?([^\s|]+)\s*\|", block)
    assert found, "RELEASE_METADATA.md has no current version"
    return found.group(1)


@pytest.mark.parametrize("doc", CURRENT_DOCS, ids=lambda p: p.name)
def test_the_demo_length_matches_the_demo(doc, evidence):
    """The length is quoted in prose and read here from the file's own header."""
    seconds = (evidence.get("demo") or {}).get("seconds")
    if not seconds:
        pytest.skip("no demo recorded")
    offenders = []
    for number, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
        lowered = line.lower()
        if any(marker in lowered for marker in _HISTORICAL):
            continue
        # Only lines actually talking about the recording. "In 30 seconds" is a
        # heading about reading time, not a claim about the video.
        if not any(word in lowered for word in ("demo", "recording", "video", ".mp4", "watch it")):
            continue
        for found in re.finditer(r"(\d{1,3})[- ]second", line, re.I):
            if abs(int(found.group(1)) - seconds) > 1:
                offenders.append(f"{doc.name}:{number} says {found.group(0)}, "
                                 f"the file is {seconds}s")
    assert not offenders, _report(offenders)


@pytest.mark.parametrize("doc", CURRENT_DOCS, ids=lambda p: p.name)
def test_screenshots_are_not_from_an_older_release(doc, evidence):
    """A screenshot path carries a version. Pointing at an old one shows a judge
    the wrong product."""
    expected = (evidence.get("screenshots_dir") or "").split("/")[-1]
    if not expected:
        pytest.skip("no versioned screenshot folder for this release")
    text = doc.read_text(encoding="utf-8")
    stale = {m for m in re.findall(r"docs/screenshots/([A-Za-z0-9._]+)/", text)
             if m != expected}
    assert not stale, f"{doc.name} shows screenshots from {sorted(stale)}, current is {expected}"


@pytest.mark.parametrize("doc", CURRENT_DOCS, ids=lambda p: p.name)
def test_current_copy_does_not_describe_the_pre_0_4_product(doc):
    """"The step before the slicer" stopped being the whole truth in v0.4.0."""
    offenders = []
    for number, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
        lowered = line.lower()
        if any(marker in lowered for marker in _HISTORICAL):
            continue
        if "step before the slicer" in lowered or "step before that" in lowered:
            offenders.append(f"{doc.name}:{number}: {line.strip()[:80]}")
    assert not offenders, _report(offenders)


def test_the_readme_whats_new_names_the_current_release():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    version = _released_version()
    found = re.search(r"^##\s+What's new in ([^\s—-]+)", readme, re.M)
    assert found, "README has no 'What's new' section"
    assert found.group(1).lstrip("v") == version, (
        f"README leads with What's new in {found.group(1)}, released version is {version}")


def test_the_evidence_file_names_the_released_version(evidence):
    assert evidence["version"] == _released_version()
