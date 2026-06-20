"""Community Knowledge Doctor (MVP) — turn scattered U1 tribal knowledge into help.

The community has already solved most U1 friction (out-of-bounds, prime-tower
collisions, multi-material failures, first-layer adhesion, cryptic errors) across
Facebook, Reddit, GitHub and the Snapmaker forums. This MVP curates those into a
matchable knowledge base so Studio can surface the known fix in-app. Offline +
honest: it's labelled curated community knowledge, every entry cites its theme.
"""
from snapstudio_core import community_knowledge as ck


def test_has_a_curated_knowledge_base():
    assert len(ck.KNOWN_ISSUES) >= 5
    for e in ck.KNOWN_ISSUES:
        assert e["id"] and e["title"] and e["cause"] and e["community_fix"]
        assert e["symptoms"] and isinstance(e["symptoms"], list)
        assert e["sources"] and isinstance(e["sources"], list)


def test_match_finds_out_of_bounds():
    hits = ck.match("Orca says out of bounds and won't slice")
    assert hits
    assert hits[0]["id"] == "out-of-bounds"


def test_match_finds_prime_tower():
    hits = ck.match("prime tower keeps falling over / wipe tower collision")
    assert any(h["id"] == "prime-tower" for h in hits)


def test_match_ranks_by_relevance_and_caps():
    hits = ck.match("multi material colour bleed and out of bounds", limit=2)
    assert 1 <= len(hits) <= 2


def test_match_empty_query_returns_nothing():
    assert ck.match("") == []
    assert ck.match("a totally unrelated kitchen recipe") == []


def test_match_from_report_risks():
    # Accepts a list of risk texts (as the Report produces) and returns guidance.
    hits = ck.match_risks(["Too big for the bed — out of bounds",
                           "5 colours but only 4 toolheads"])
    ids = {h["id"] for h in hits}
    assert "out-of-bounds" in ids
    assert "multi-material-limit" in ids
