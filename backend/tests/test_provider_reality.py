"""What a real Spoolman actually does, and the three things mocks agreed with.

Studio's Spoolman support was written against invented payloads, and every one of
its thirty adversarial tests passed. Then a real Spoolman 0.26.1 was run locally,
seeded through its own REST API with eight controlled spools, and three of those
agreed-upon behaviours turned out not to be Spoolman's:

1. **Archived spools were invisible.** `GET /api/v1/spool` omits them unless asked.
   Studio had careful handling for an archived spool and never saw one; a slot
   mapped to a spool somebody archived reported "no spool with that id", which
   reads as deleted.
2. **A remaining weight is always present.** Spoolman computes it from the spool's
   declared size minus what has been recorded used. So the field being there
   proved nothing, and Studio called every figure `tracked` — the label a blocker
   is built on — including a spool registered a minute ago and never printed from.
3. **There is no `updated` field.** Studio read `last_used or updated` for its
   freshness date; `updated` does not exist, and `last_used` is absent until
   something has actually printed. So the common case is *no date at all*, which
   is the case the old code handled least.

The fixture in `fixtures/providers/` is the captured response, with its own
provenance block. These tests replay it, so the findings stay pinned without
needing Docker on every run.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from snapstudio_core import freshness, material_plan, material_providers as providers

FIXTURE = Path(__file__).parent / "fixtures" / "providers" / "spoolman_0_26_1.json"


@pytest.fixture(scope="module")
def captured() -> dict:
    return json.loads(FIXTURE.read_text("utf-8"))


@pytest.fixture
def real_spoolman(monkeypatch, captured):
    """Replay the captured response through the real provider, asserting the URL."""
    seen: dict = {}

    def fake_get(url, timeout=4.0):
        seen["url"] = url
        return captured["spools"]

    monkeypatch.setattr(providers, "_get_json", fake_get)
    return seen


def test_the_fixture_says_plainly_what_it_is(captured):
    provenance = captured["_provenance"]
    assert provenance["kind"] == "captured_from_real_software"
    assert provenance["spoolman_version"] == "0.26.1"
    assert "not about any printer" in provenance["statement"]


# --- finding 1: archived spools ---------------------------------------------

def test_studio_asks_for_archived_spools(real_spoolman):
    providers.spoolman("http://spoolman.local:7912")
    assert "allow_archived=true" in real_spoolman["url"], (
        "without this, an archived spool is indistinguishable from a deleted one")


def test_an_archived_spool_is_found_and_flagged_rather_than_missing(real_spoolman, captured):
    archived = [s for s in captured["spools"] if s.get("archived")]
    assert archived, "the captured fixture must contain an archived spool"
    spool_id = archived[0]["id"]

    state = providers.spoolman("http://spoolman.local:7912", slot_map={"0": spool_id})
    slot = state["slots"][0]
    assert slot["spool_id"] == spool_id
    assert any("archived" in note for note in slot["notes"])
    assert not any("no spool with id" in note for note in slot["notes"])


# --- finding 2: a computed weight is not a tracked one -----------------------

def test_a_never_used_spool_is_not_called_tracked(real_spoolman, captured):
    """Spoolman reports a full kilogram for a spool nothing has printed from."""
    never_used = next(s for s in captured["spools"]
                      if not s.get("last_used") and not s.get("used_weight"))
    state = providers.spoolman("http://s")
    spool = next(s for s in state["spools"] if s["id"] == never_used["id"])
    assert spool["remaining_g"] is not None
    assert spool["remaining_quality"] == providers.DERIVED, (
        "a declared spool size is arithmetic, not a record of consumption")


def test_a_spool_something_has_printed_from_is_tracked(real_spoolman, captured):
    used = next(s for s in captured["spools"] if s.get("last_used") and s.get("used_weight"))
    state = providers.spoolman("http://s")
    spool = next(s for s in state["spools"] if s["id"] == used["id"])
    assert spool["remaining_quality"] == providers.TRACKED
    assert spool["remaining_as_of"] is not None


# --- finding 3: the missing date --------------------------------------------

def test_registration_time_is_not_treated_as_a_freshness_date(real_spoolman, captured):
    """`registered` is when the spool was added, not when its weight was true."""
    never_used = next(s for s in captured["spools"] if not s.get("last_used"))
    assert never_used.get("registered"), "the fixture spool does have a registered date"

    state = providers.spoolman("http://s")
    spool = next(s for s in state["spools"] if s["id"] == never_used["id"])
    assert spool["remaining_as_of"] is None
    assert spool["registered"] == never_used["registered"]


def test_most_real_spools_have_no_freshness_date_at_all(real_spoolman):
    state = providers.spoolman("http://s")
    undated = [s for s in state["spools"] if s["remaining_as_of"] is None]
    assert len(undated) > len(state["spools"]) / 2, (
        "no date is the common case against a real Spoolman, not the edge case")


# --- the end-to-end consequence ---------------------------------------------

def test_a_real_full_spool_never_blocks_a_send(real_spoolman, captured):
    """The whole point: Spoolman saying 1000 g must not become a Studio fact."""
    never_used = next(s for s in captured["spools"]
                      if not s.get("last_used") and not s.get("used_weight"))
    state = providers.spoolman("http://s", slot_map={"0": never_used["id"]})
    loaded = providers.as_loaded_filaments(providers.combine(state))
    plan = material_plan.plan(
        [{"tool": 0, "used": True, "grams": 2000.0, "type": "PLA"}], loaded, [0])
    sufficiency = plan["slots"][0]["sufficiency"]
    assert sufficiency["verdict"] == "probably_short"
    assert sufficiency["trusted"] is False
    assert sufficiency["freshness"] == freshness.UNKNOWN


def test_a_real_tracked_shortfall_still_blocks(real_spoolman, captured, monkeypatch):
    """The corrections must not have cost Studio the sentence worth saying."""
    import datetime

    used = next(s for s in captured["spools"] if s.get("last_used") and s.get("used_weight"))
    fresh = (datetime.datetime.now(datetime.timezone.utc)
             - datetime.timedelta(hours=3)).isoformat()
    payload = [dict(s, last_used=fresh) if s["id"] == used["id"] else s
               for s in captured["spools"]]
    monkeypatch.setattr(providers, "_get_json", lambda url, timeout=4.0: payload)

    state = providers.spoolman("http://s", slot_map={"0": used["id"]})
    loaded = providers.as_loaded_filaments(providers.combine(state))
    grams = state["spools"][0] and next(
        sp["remaining_g"] for sp in state["spools"] if sp["id"] == used["id"])
    plan = material_plan.plan(
        [{"tool": 0, "used": True, "grams": grams * 3, "type": "PLA"}], loaded, [0])
    sufficiency = plan["slots"][0]["sufficiency"]
    assert sufficiency["verdict"] == "insufficient"
    assert sufficiency["trusted"] is True
