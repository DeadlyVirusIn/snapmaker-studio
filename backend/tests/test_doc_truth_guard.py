"""The guard that should have stopped v0.7.0's false public claims.

Checking that today's documents are right proves today. It does not prove the
check would notice if they went wrong — and that is exactly what failed: the
per-document tests were green while the README's main download button pointed at
the previous release.

So each of these feeds the guard a document containing one of the claims that
actually shipped, and requires it to be caught. Where a claim is legitimately
about the past, the same guard has to stay quiet, because a check that fires on
history would be turned off within a release.
"""
from __future__ import annotations

import pytest

from doc_truth import (blocks, count_offenders, demo_offenders, is_historical,
                       release_offenders, suite_offenders)

EVIDENCE = {
    "version": "0.7.0",
    "acceptance": {"passed": 31, "total": 31},
    "hardware": {"passed": 26, "total": 26},
    "selfcheck": {"passed": 27, "total": 27},
    "backend": {"passed": 1104, "skipped": 3},
    "desktop": {"passed": 304},
    "demo": {"seconds": 66},
}


def caught(offenders, fragment):
    assert offenders, f"nothing was caught; expected something about {fragment!r}"
    assert any(fragment in line for line in offenders), offenders


# --- the three claims v0.7.0 actually shipped --------------------------------

def test_a_download_link_to_the_previous_release_is_caught():
    """v0.7.0's README kept its top call to action on v0.6.2 for the whole
    release. It was outside the Download section, so the old guard never looked."""
    doc = ("### [Watch it work](docs/media/demo.mp4) · "
           "[Download for Windows](https://github.com/x/y/releases/tag/v0.6.2) · "
           "[What it is](docs/judge.md)\n")
    caught(release_offenders(doc, EVIDENCE), "links release v0.6.2")


def test_a_count_split_across_a_wrapped_sentence_is_caught():
    """"…prints a 25-check pass/fail table" wrapped, so the word "selfcheck" and
    the number were on different lines and neither test could see the other."""
    doc = ("- **One command anyone can run.** `u1convert selfcheck` runs the real\n"
           "  pipeline end to end and prints a 25-check pass/fail table, so the\n"
           "  claims can be verified without reading the source.\n")
    caught(count_offenders(doc, EVIDENCE), "'25-check'")


def test_crediting_the_wrong_installer_for_the_current_numbers_is_caught():
    """The Evidence section said the numbers came from the published v0.6.2
    installer while listing v0.7.0's numbers directly underneath."""
    doc = ("## Evidence\n\n"
           "Everything below was verified against the **published v0.6.2 installer**,\n"
           "not a development build.\n\n"
           "| What | Result |\n|---|---|\n"
           "| Installed-application acceptance, through the real UI | 31/31 |\n")
    caught(release_offenders(doc, EVIDENCE), "published v0.6.2 installer")


# --- the rest of the surface -------------------------------------------------

def test_an_acceptance_ratio_from_an_older_release_is_caught():
    doc = "| Installed-application acceptance, through the real UI | 30/30 |\n"
    caught(count_offenders(doc, EVIDENCE), "says 30/30 for acceptance")


def test_a_prose_check_count_next_to_the_capability_name_is_caught():
    doc = ("**An acceptance harness that drives the installed application**, not a\n"
           "dev server: 30 checks over the real window and the frozen engine.\n")
    caught(count_offenders(doc, EVIDENCE), "'30 checks'")


def test_a_stale_combined_evidence_row_is_caught():
    doc = "| Backend / desktop / TypeScript / Rust | 1004 · 293 · clean · clean |\n"
    offenders = suite_offenders(doc, EVIDENCE)
    caught(offenders, "combined row says backend 1004")
    caught(offenders, "combined row says desktop 293")


def test_a_screenshot_from_the_previous_release_is_caught():
    doc = "| ![the problem](docs/screenshots/v0.6.2/problem.jpg) | the fix |\n"
    caught(release_offenders(doc, EVIDENCE), "screenshots from v0.6.2")


def test_a_demo_length_that_is_not_the_demo_s_length_is_caught():
    doc = "### [Watch it work — 90 seconds](docs/media/snapmaker-studio-demo.mp4)\n"
    caught(demo_offenders(doc, EVIDENCE), "says the demo is 90 seconds")


def test_a_hardware_ratio_that_is_not_the_hardware_run_is_caught():
    doc = "| Read-only verification against a real Snapmaker U1 | 20/20 |\n"
    caught(count_offenders(doc, EVIDENCE), "says 20/20 for hardware")


# --- and the history it must not touch ---------------------------------------

def test_a_versioned_history_section_keeps_its_own_numbers():
    """TRUST_STATUS records what every past release was verified with. A guard
    that flagged those would be deleted, and the immutable snapshots with it."""
    doc = ("## v0.6.2 — ACCEPTED (superseded by v0.7.0)\n\n"
           "| Installed application | 30/30 |\n"
           "| Backend tests | 1004 passed, 3 skipped |\n")
    assert count_offenders(doc, EVIDENCE) == []
    assert suite_offenders(doc, EVIDENCE) == []


def test_a_sentence_about_the_past_keeps_its_own_numbers():
    doc = ("An earlier version of this page said the self-check ran 25/25; it was\n"
           "corrected when the checks were counted again.\n")
    assert count_offenders(doc, EVIDENCE) == []


def test_a_release_link_inside_a_history_section_is_left_alone():
    doc = ("## v0.6.1 — ACCEPTED (superseded by v0.6.2)\n\n"
           "Installer: <https://github.com/x/y/releases/tag/v0.6.1>\n")
    assert release_offenders(doc, EVIDENCE) == []


def test_the_changelog_style_history_heading_is_recognised():
    doc = ("## [0.6.2] - 2026-08-24\n\n"
           "pytest 1004 passed / 3 skipped · self-check 25/25.\n")
    # The heading names a version that is not current, so the block is history.
    assert count_offenders(doc, EVIDENCE) == []


# --- how the reading itself behaves ------------------------------------------

def test_a_wrapped_paragraph_is_one_block():
    doc = "one line\nand its continuation\n\na second paragraph\n"
    found = blocks(doc)
    assert [b.text for b in found] == ["one line and its continuation",
                                       "a second paragraph"]


def test_table_rows_and_list_items_stay_separate():
    doc = "| a | 1/1 |\n| b | 2/2 |\n- first\n- second\n"
    assert [b.text for b in blocks(doc)] == ["| a | 1/1 |", "| b | 2/2 |",
                                             "- first", "- second"]


def test_a_block_carries_the_headings_above_it():
    doc = "# Title\n\n## v0.6.2 — ACCEPTED\n\nsome claim\n"
    claim = [b for b in blocks(doc) if b.text == "some claim"][0]
    assert claim.headings == ("Title", "v0.6.2 — ACCEPTED")
    assert is_historical(claim, "0.7.0")
    assert not is_historical(claim, "0.6.2")


@pytest.mark.parametrize("line", [
    "### [⬇ Download for Windows](https://github.com/x/y/releases/tag/v0.7.0)",
    "Everything below was verified against the **published v0.7.0 installer**.",
    "| ![shot](docs/screenshots/v0.7.0/painted.jpg) |",
])
def test_the_current_release_passes_every_link_check(line):
    assert release_offenders(line + "\n", EVIDENCE) == []
