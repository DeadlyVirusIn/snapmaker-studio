"""How old a figure is, and what Studio is allowed to do about it.

The thresholds here have consequences, so they are tested as consequences rather
than as numbers: past a week, a remaining weight may warn and may never be the
sole reason a send is refused. A person stopped from printing by bookkeeping
nobody has updated in a fortnight learns to ignore the warnings that matter, and
the next one might be true.

The awkward cases are the common ones. Against a real Spoolman most spools carry
no date at all, so `unknown` has to be a first-class answer rather than a fallback.
"""
from __future__ import annotations

import datetime

import pytest

from snapstudio_core import freshness as fr

NOW = datetime.datetime(2026, 8, 25, 12, 0, 0, tzinfo=datetime.timezone.utc)


def ago(**delta) -> str:
    return (NOW - datetime.timedelta(**delta)).isoformat()


@pytest.mark.parametrize("value, state", [
    (ago(minutes=1), fr.FRESH),
    (ago(hours=1), fr.FRESH),
    (ago(hours=23), fr.FRESH),
    (ago(hours=25), fr.AGEING),
    (ago(days=6), fr.AGEING),
    (ago(days=8), fr.STALE),
    (ago(days=90), fr.STALE),
])
def test_age_maps_to_a_state(value, state):
    assert fr.assess(value, NOW)["state"] == state


@pytest.mark.parametrize("value", [None, "", "   "])
def test_no_date_is_unknown_not_fresh(value):
    out = fr.assess(value, NOW)
    assert out["state"] == fr.UNKNOWN
    assert out["trustworthy"] is False
    assert "cannot tell you how current" in out["detail"]


@pytest.mark.parametrize("value", ["yesterday", "2026-13-45T99:99:99Z", "{}", "0"])
def test_a_date_studio_cannot_read_is_unusable_not_fresh(value):
    out = fr.assess(value, NOW)
    assert out["state"] == fr.UNUSABLE
    assert out["trustworthy"] is False


def test_a_date_in_the_future_is_unusable_rather_than_very_fresh():
    out = fr.assess((NOW + datetime.timedelta(days=2)).isoformat(), NOW)
    assert out["state"] == fr.UNUSABLE
    assert "clock" in out["detail"]


def test_a_few_minutes_of_clock_skew_is_not_a_broken_date():
    """Two machines on one network disagreeing by seconds is ordinary."""
    out = fr.assess((NOW + datetime.timedelta(seconds=30)).isoformat(), NOW)
    assert out["state"] == fr.FRESH
    assert out["age_s"] == 0


def test_spoolmans_own_z_suffix_is_read():
    assert fr.parse("2026-08-25T11:28:49Z") is not None


def test_a_naive_timestamp_is_read_as_utc():
    stamp = fr.parse("2026-08-25T11:28:49")
    assert stamp is not None and stamp.tzinfo is not None


def test_an_offset_timestamp_is_read():
    out = fr.assess("2026-08-25T13:00:00+02:00", NOW)
    assert out["state"] == fr.FRESH


@pytest.mark.parametrize("seconds, expected", [
    (10, "just now"),
    (60 * 30, "30 minutes ago"),
    (3600 * 5, "5 hours ago"),
    (86400 * 3, "3 days ago"),
    (86400 * 21, "3 weeks ago"),
    (86400 * 300, "10 months ago"),
])
def test_ages_are_described_the_way_a_person_would(seconds, expected):
    assert fr.describe(seconds) == expected


def test_the_phrase_says_who_reported_it_and_when():
    text = fr.phrase("Spoolman", 43.0, ago(days=3), NOW)
    assert text == "Spoolman last reported 43 g 3 days ago"


def test_there_is_no_phrase_when_there_is_no_date():
    assert fr.phrase("Spoolman", 43.0, None, NOW) is None


# --- the consequence, which is the part that matters ------------------------

def test_only_fresh_and_ageing_figures_are_trustworthy():
    assert fr.assess(ago(hours=2), NOW)["trustworthy"] is True
    assert fr.assess(ago(days=3), NOW)["trustworthy"] is True
    assert fr.assess(ago(days=30), NOW)["trustworthy"] is False
    assert fr.assess(None, NOW)["trustworthy"] is False


def test_the_documented_threshold_matches_the_behaviour():
    """The docstring states a week; a test that agrees with it is the proof."""
    assert fr.STALE_HOURS == 24 * 7
    assert fr.assess(ago(hours=fr.STALE_HOURS - 1), NOW)["state"] == fr.AGEING
    assert fr.assess(ago(hours=fr.STALE_HOURS + 1), NOW)["state"] == fr.STALE
