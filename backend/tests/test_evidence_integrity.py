"""A published release's evidence is a historical fact, and facts do not move.

Studio's public argument is "check it yourself", so its counts are load-bearing.
There was one canonical evidence file, rewritten on every release — and because
there was only one of it, publishing a new release silently rewrote the numbers
that *every* document quoted, including the sections describing releases that had
already shipped. A reader of TRUST_STATUS.md was told v0.6.0 had been verified with
967 tests and 26 hardware checks. Neither is true of v0.6.0: it shipped with 822
and 20, and those larger numbers come from a suite and a harness that did not exist
when it was published.

So evidence is now one immutable snapshot per release under
`docs/internal/evidence/`, and this module holds the line in three directions:

* **Current state** — the documents that speak in the present tense must agree
  with the snapshot for the release that is actually current, down to the
  installer's name, size and hash.
* **Historical state** — every versioned section of TRUST_STATUS.md must agree
  with *that version's* snapshot, and must not contain the current one's numbers.
* **Immutability** — a snapshot for a released version must still match what that
  release's own tag recorded. Publishing cannot rewrite history, and this fails if
  it ever does.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOTS = ROOT / "docs" / "internal" / "evidence"
CURRENT = ROOT / "docs" / "internal" / "evidence.json"
METADATA = ROOT / "docs" / "RELEASE_METADATA.md"
TRUST = ROOT / "docs" / "TRUST_STATUS.md"
README = ROOT / "README.md"

#: The fields that are evidence about a release, as opposed to bookkeeping about
#: the snapshot itself. Only these are compared across time.
EVIDENCE_FIELDS = ("acceptance", "hardware", "selfcheck", "backend", "desktop",
                   "demo", "installer", "screenshots_dir")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def current() -> dict:
    assert CURRENT.exists(), "docs/internal/evidence.json is missing"
    return json.loads(read(CURRENT))


@pytest.fixture(scope="module")
def snapshot(current) -> dict:
    path = SNAPSHOTS / f"{current['version']}.json"
    assert path.exists(), (
        f"no immutable snapshot for the current release ({path.name}) — "
        "tools/evidence/update.py writes one when the release is prepared")
    return json.loads(read(path))


def sections() -> list[tuple[str, str]]:
    """Every versioned section of TRUST_STATUS.md, as (version, text).

    Only released versions — `## v0.6.0 — …`. Beta sections carry their own
    suffix and are matched exactly so `v0.4.0-beta.24` is never read as `v0.4.0`.
    """
    text = read(TRUST)
    # Every heading, including the beta ones — a section ends where the next
    # section begins, and reading a beta's text as part of the release above it
    # would attribute that beta's reports to the release.
    headings = [(m.group(1), m.start()) for m in
                re.finditer(r"^## v([\w.\-]+)\s+[—-]", text, re.M)]
    out = []
    for index, (version, start) in enumerate(headings):
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            continue
        end = headings[index + 1][1] if index + 1 < len(headings) else len(text)
        out.append((version, text[start:end]))
    return out


def stated(block: str) -> dict:
    """The counts a TRUST_STATUS section states about itself."""
    def one(pattern: str, group: int = 1):
        found = re.search(pattern, block)
        return int(found.group(group)) if found else None

    return {
        "backend": one(r"Backend tests \|[^|]*\|[^0-9]*(\d+) passed"),
        "desktop": one(r"Desktop tests \|[^|]*\|[^0-9]*(\d+) passed"),
        "selfcheck": one(r"selfcheck` \|[^|]*[—-]\s*(\d+)/\d+"),
        "acceptance": one(r"Installed application [—-] (\d+)/\d+"),
        "hardware": one(r"Real Snapmaker U1 [—-] read-only, (\d+)/\d+"),
    }


def recorded(snap: dict) -> dict:
    """The same shape, from a snapshot."""
    return {
        "backend": snap["backend"].get("passed"),
        "desktop": snap["desktop"].get("passed"),
        "selfcheck": snap["selfcheck"].get("passed"),
        "acceptance": snap["acceptance"].get("passed"),
        "hardware": snap["hardware"].get("passed"),
    }


# --- current state -------------------------------------------------------------

def test_the_current_pointer_and_the_current_snapshot_agree(current, snapshot):
    """`evidence.json` is a copy of the current release's snapshot. If they differ,
    one of them is describing a release that is not the one being shipped."""
    for field in ("acceptance", "hardware", "selfcheck", "backend", "desktop", "demo"):
        assert current.get(field) == snapshot.get(field), (
            f"{field} differs between evidence.json and {snapshot['version']}.json")


def test_the_snapshot_matches_the_harness_reports_it_came_from(snapshot):
    for kind in ("acceptance", "hardware"):
        name = snapshot[kind].get("report")
        assert name, f"the {kind} run for this release is not recorded"
        data = json.loads(read(ROOT / "docs" / "internal" / name))
        assert snapshot[kind]["passed"] == data["passed"]
        assert snapshot[kind]["total"] == data["total"]


def test_the_snapshot_describes_the_installer_that_is_being_published(snapshot):
    """Size and hash are what a reader checks a download against. A snapshot that
    does not match the canonical metadata means one of the two is stale."""
    metadata = read(METADATA)
    block = metadata[metadata.index("## Current release"):]
    block = block[:block.index("## Previous release")]
    installer = snapshot["installer"]

    assert snapshot["version"] in block
    assert installer["name"] and installer["name"] in block
    assert installer["sha256"] and installer["sha256"] in block
    assert f"{installer['size_bytes']:,}" in block
    assert installer["url"] and installer["url"] in block


def test_the_readme_download_block_matches_the_snapshot(snapshot):
    """The one duplication the project allows: the README repeats the size and
    hash so a reader can verify without opening a second document."""
    readme = read(README)
    installer = snapshot["installer"]
    assert installer["sha256"] in readme
    assert f"{installer['size_bytes']:,}" in readme
    assert installer["name"] in readme
    assert f"v{snapshot['version']}" in readme


def test_the_readme_combined_row_is_read_as_counts(snapshot):
    """`| Backend / desktop / TypeScript / Rust | 967 · 290 · clean · clean |`.

    This row said 822 · 284 through an entire release, because the old guard only
    recognised a count next to the word "passed" on the same line. A number in a
    table is a claim whatever the row's shape.
    """
    row = re.search(r"^\|\s*Backend\s*/\s*desktop[^|]*\|\s*([^|]+)\|\s*$",
                    read(README), re.M)
    assert row, "the README no longer has a combined backend/desktop row"
    fields = [cell.strip() for cell in row.group(1).split("·")]
    assert len(fields) == 4, f"unexpected combined row: {row.group(1)!r}"
    assert fields[0] == str(snapshot["backend"]["passed"]), (
        f"README combined row says backend {fields[0]}, snapshot says "
        f"{snapshot['backend']['passed']}")
    assert fields[1] == str(snapshot["desktop"]["passed"]), (
        f"README combined row says desktop {fields[1]}, snapshot says "
        f"{snapshot['desktop']['passed']}")
    assert fields[2] == fields[3] == "clean"


def test_the_current_release_is_described_as_stable(snapshot):
    """A stable release must not be described as a prerelease anywhere current."""
    for doc in (README, METADATA, ROOT / "docs" / "SUBMISSION_STATUS.md"):
        text = read(doc)
        assert not re.search(r"\bcurrent (?:pre-?release|beta)\b", text, re.I), doc.name
    assert "not a prerelease" in read(METADATA)


def test_the_current_release_is_named_by_every_document_that_claims_one():
    """A document naming a current build must name the one that is current."""
    version = json.loads(read(CURRENT))["version"]
    submission = read(ROOT / "docs" / "SUBMISSION_STATUS.md")
    row = re.search(r"^\|\s*Version\s*\|\s*\*\*v([^\s*]+)\*\*", submission, re.M)
    assert row, "SUBMISSION_STATUS.md no longer states a current version"
    assert row.group(1) == version, (
        f"SUBMISSION_STATUS.md calls v{row.group(1)} current; the release is v{version}")
    assert f"releases/tag/v{version}" in submission, (
        "SUBMISSION_STATUS.md links to a release that is not the current one")


def test_the_demo_length_and_screenshot_folder_belong_to_this_release(snapshot):
    seconds = snapshot["demo"].get("seconds")
    if seconds:
        assert f"{seconds} second" in read(README)
    folder = snapshot.get("screenshots_dir")
    if folder:
        stale = {m for m in re.findall(r"docs/screenshots/(v[\d.]+)/", read(README))
                 if m != folder.rsplit("/", 1)[-1]}
        assert not stale, f"README shows screenshots from {sorted(stale)}"


# --- historical state ----------------------------------------------------------

def test_every_release_section_has_its_own_snapshot():
    missing = [version for version, _ in sections()
               if not (SNAPSHOTS / f"{version}.json").exists()]
    assert not missing, f"TRUST_STATUS.md describes releases with no snapshot: {missing}"


@pytest.mark.parametrize("version", [v for v, _ in sections()])
def test_a_release_section_states_that_release_s_own_evidence(version):
    """The defect this whole module exists for: a later release's numbers written
    into an earlier release's section."""
    block = dict(sections())[version]
    snap = json.loads(read(SNAPSHOTS / f"{version}.json"))
    said, truth = stated(block), recorded(snap)
    wrong = {key: (said[key], truth[key]) for key in said
             if said[key] is not None and truth[key] is not None and said[key] != truth[key]}
    assert not wrong, (
        f"the v{version} section states {wrong} — (document, {version}'s own record). "
        "A released version's evidence does not change when a later one ships.")


@pytest.mark.parametrize("version", [v for v, _ in sections()])
def test_a_release_section_links_to_that_release_s_reports(version):
    block = dict(sections())[version]
    for name in re.findall(r"internal/((?:acceptance|hardware)-[\w.]+)\.json", block):
        kind, tail = name.split("-", 1)
        assert tail == version or tail.startswith(version), (
            f"the v{version} section links {kind} report {tail}, which belongs to "
            "another release")


# Which words identify which check, so a ratio is only read as belonging to the
# check its own line is about.
_SUBJECT_WORDS = {
    "acceptance": ("acceptance", "installed application", "installed-build"),
    "hardware": ("hardware", "real snapmaker u1", "real printer"),
    "selfcheck": ("selfcheck", "self-check", "u1convert selfcheck"),
}


def test_no_older_section_carries_the_current_release_s_counts(current):
    """Stronger than the per-section check: even where a section states nothing in
    the table shapes above, the current numbers must not appear in it."""
    marks = sections()
    version = current["version"]
    offenders = []
    for other, block in marks:
        if other == version:
            continue
        snap = json.loads(read(SNAPSHOTS / f"{other}.json"))
        for key in ("acceptance", "hardware", "selfcheck"):
            now = current[key]["passed"]
            then = snap[key].get("passed")
            if then is None or then == now:
                continue
            # Only on a line that is about *that* check. Two different checks can
            # legitimately arrive at the same ratio — an older release's 27-check
            # acceptance run and this one's 27-check self-check — and reading one
            # as the other reports a section as stale when it is exactly right.
            for line in block.splitlines():
                if not any(word in line.lower() for word in _SUBJECT_WORDS[key]):
                    continue
                if re.search(rf"\b{now}/{current[key]['total']}\b", line):
                    offenders.append(
                        f"v{other} section quotes {now}/{current[key]['total']} "
                        f"for {key}; that release recorded {then}")
    assert not offenders, "\n  " + "\n  ".join(offenders)


# --- immutability ---------------------------------------------------------------

def tagged_versions() -> list[str]:
    tags = subprocess.run(["git", "tag", "--list", "v*"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split()
    return sorted(t.lstrip("v") for t in tags if re.fullmatch(r"v\d+\.\d+\.\d+", t))


@pytest.mark.parametrize("version", tagged_versions())
def test_a_published_release_s_snapshot_still_matches_what_it_published(version):
    """The regression test for the whole architecture.

    Every snapshot for a version that has been tagged must still say what that
    tag's own files say. Shipping a new release cannot change it — if this fails,
    something rewrote history, which is the exact defect the snapshots replaced.
    """
    path = SNAPSHOTS / f"{version}.json"
    if not path.exists():
        pytest.skip(f"no snapshot for v{version}")
    import sys

    sys.path.insert(0, str(ROOT / "tools" / "evidence"))
    import snapshot as snapshot_tool

    here = json.loads(read(path))
    from_tag = snapshot_tool.reconstruct(version)
    differing = [field for field in EVIDENCE_FIELDS
                 if here.get(field) != from_tag.get(field)]
    assert not differing, (
        f"the recorded evidence for v{version} no longer matches what tag v{version} "
        f"published, in {differing}. A published release's evidence is a fact about "
        "that release and does not change.")
