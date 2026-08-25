"""How long ago was this figure true?

Spool bookkeeping drifts. Every print run outside the tool that keeps the number
moves it away from reality, and so does every spool swapped without being
recorded. A remaining weight is therefore two facts, not one: how much, and when
that was last so — and the second decides how hard Studio is allowed to lean on
the first.

This is a small pure module because the answer has to be the same everywhere it
is asked, and because the awkward cases are the common ones rather than the edge:
against a real Spoolman, most spools have **no** timestamp at all, since the field
that carries one is only set once something has printed from that spool.

Nothing here guesses. A missing timestamp is `unknown`, not `fresh`; a timestamp
in the future is `unusable`, not `very fresh`.
"""
from __future__ import annotations

import datetime

SCHEMA_VERSION = "freshness/1"

FRESH = "fresh"
AGEING = "ageing"
STALE = "stale"
UNKNOWN = "unknown"
UNUSABLE = "unusable"     # a date that cannot be right — malformed, or in the future

#: Under a day, a tracked figure is as good as the tool keeping it. This is not a
#: guess about filament; it is the window in which a spool is unlikely to have
#: been swapped or printed from without the tool noticing.
FRESH_HOURS = 24

#: Past a week, Studio stops treating a figure as something to block a print over.
#: The consequence is stated rather than implied: **a stale weight can warn, and
#: can never be the sole reason a send is blocked.** A person told "you will run
#: out" on a number nobody has updated in a fortnight learns to ignore the
#: warnings that matter.
STALE_HOURS = 24 * 7

#: A clock somewhere is wrong, but a few minutes of skew between two machines on
#: one network is ordinary and not worth reporting as a broken date.
SKEW_TOLERANCE_S = 300


def parse(value) -> datetime.datetime | None:
    """Read an ISO-8601 timestamp, or return None. Never raises.

    Spoolman writes `2026-08-25T11:28:49Z`; other providers may write an offset,
    or no zone at all. A naive timestamp is read as UTC, which is what every
    provider Studio has looked at actually means by one.
    """
    if isinstance(value, datetime.datetime):
        stamp = value
    else:
        text = str(value or "").strip()
        if not text:
            return None
        if text.endswith(("Z", "z")):
            text = text[:-1] + "+00:00"
        try:
            stamp = datetime.datetime.fromisoformat(text)
        except (ValueError, TypeError):
            return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=datetime.timezone.utc)
    return stamp


def assess(value, now: datetime.datetime | None = None) -> dict:
    """How old is this figure, and what may Studio do with it?

    `now` is injectable so every branch is testable without waiting.
    """
    now = now or datetime.datetime.now(datetime.timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=datetime.timezone.utc)

    out = {"schema_version": SCHEMA_VERSION, "state": UNKNOWN, "age_s": None,
           "as_of": None, "trustworthy": False}

    # A blank field is an absent date, not an unreadable one. The difference is
    # what the user is told: "nothing records when this was true" sends them to
    # look at the spool, "Studio could not read the date" sends them to look for a
    # bug that is not there.
    if value is None or (isinstance(value, str) and not value.strip()):
        out["detail"] = ("Nothing records when this figure was last true, so Studio "
                         "cannot tell you how current it is.")
        return out

    stamp = parse(value)
    if stamp is None:
        out["state"] = UNUSABLE
        out["detail"] = "Studio could not read the date on this figure."
        return out

    out["as_of"] = stamp.astimezone(datetime.timezone.utc).isoformat()
    age = (now - stamp).total_seconds()
    if age < -SKEW_TOLERANCE_S:
        # Dated in the future. One of the two clocks is wrong, and Studio has no
        # way to know which, so the age is not a number it may reason from.
        out["state"] = UNUSABLE
        out["age_s"] = round(age)
        out["detail"] = ("This figure is dated in the future, so Studio cannot tell how "
                         "old it is. Check the clock on the machine keeping it.")
        return out

    age = max(age, 0.0)
    out["age_s"] = round(age)
    hours = age / 3600.0
    if hours <= FRESH_HOURS:
        out["state"] = FRESH
        out["trustworthy"] = True
    elif hours <= STALE_HOURS:
        out["state"] = AGEING
        out["trustworthy"] = True
    else:
        out["state"] = STALE
    out["detail"] = f"Last updated {describe(age)}."
    return out


def describe(age_s: float) -> str:
    """"3 days ago" — the phrase a person reads, not a duration."""
    if age_s < 90:
        return "just now"
    minutes = age_s / 60.0
    if minutes < 90:
        return f"{round(minutes)} minutes ago"
    hours = minutes / 60.0
    if hours < 36:
        return f"{round(hours)} hours ago"
    days = hours / 24.0
    if days < 14:
        return f"{round(days)} days ago"
    weeks = days / 7.0
    if weeks < 9:
        return f"{round(weeks)} weeks ago"
    return f"{round(days / 30.0)} months ago"


def phrase(provider: str, grams, value, now=None) -> str | None:
    """"Spoolman last reported 43 g three days ago" — or None when there is no date."""
    state = assess(value, now)
    if state["state"] in (UNKNOWN,):
        return None
    amount = f"{grams:g} g" if isinstance(grams, (int, float)) else "this figure"
    if state["state"] == UNUSABLE:
        return f"{provider} reports {amount}, dated in a way Studio could not read"
    return f"{provider} last reported {amount} {describe(state['age_s'])}"
