"""Model Discovery Hub v1 — search/normalize/gating tests.

No live network: normalization is tested against recorded fixture dicts; search()
with no API keys returns empty results + disabled warnings.
"""
import pytest

from snapstudio_core import model_search as ms

# Recorded-style provider payloads (shape only; no real/paid model names).
_THINGIVERSE = {
    "name": "Sample Bracket", "public_url": "https://www.thingiverse.com/thing:1",
    "thumbnail": "https://img/thing.png", "license": "Creative Commons - Attribution",
    "creator": {"name": "maker_a"}, "tags": ["bracket"], "formats": ["STL"],
}
_MMF_FREE = {
    "name": "Sample Vase", "url": "https://www.myminifactory.com/object/2",
    "images": [{"thumbnail": "https://img/mmf.png"}], "license": "CC BY",
    "designer": {"name": "maker_b"}, "is_paid": False,
}
_MMF_PAID = {**_MMF_FREE, "name": "Premium Vase", "is_paid": True, "price": 500}
_CULTS_PAID = {
    "name": "Sample Mini", "url": "https://cults3d.com/en/3d-model/x",
    "illustrationImageUrl": "https://img/cults.png", "license": "Standard",
    "price": {"cents": 300}, "creator": {"nick": "maker_c"},
}


def test_normalize_thingiverse_fixture():
    r = ms.normalize_thingiverse(_THINGIVERSE)
    assert r["source"] == "thingiverse"
    assert r["title"] == "Sample Bracket"
    assert r["source_url"].startswith("https://www.thingiverse.com")
    assert r["thumbnail_url"] == "https://img/thing.png"
    assert r["price_status"] == "free"
    assert r["attribution"] == "maker_a"
    assert r["license"]


def test_normalize_myminifactory_fixture():
    r = ms.normalize_myminifactory(_MMF_FREE)
    assert r["source"] == "myminifactory"
    assert r["price_status"] == "free"
    assert r["thumbnail_url"] == "https://img/mmf.png"
    assert r["attribution"] == "maker_b"


def test_paid_item_import_disabled_reason_paid():
    r = ms.normalize_myminifactory(_MMF_PAID)
    assert r["price_status"] == "paid"
    assert r["import_allowed"] is False
    assert r["reason_import_not_allowed"] == "paid"


def test_cults3d_import_disabled_no_download_api():
    r = ms.normalize_cults3d(_CULTS_PAID)
    assert r["source"] == "cults3d"
    assert r["import_allowed"] is False
    # cults3d structural rule wins regardless of price
    assert r["reason_import_not_allowed"] == "no_download_api"


def test_unclear_license_disabled():
    allowed, reason = ms.compute_import_allowed("thingiverse", "free", None)
    assert allowed is False and reason == "license_unclear"


def test_eligible_item_still_disabled_in_v1():
    # free + licensed Thingiverse item: principle-eligible, but import not in v1.
    r = ms.normalize_thingiverse(_THINGIVERSE)
    assert r["import_allowed"] is False
    assert r["reason_import_not_allowed"] == "source_link_out_only"


def test_no_scrape_guard_rejects_non_whitelisted():
    with pytest.raises(ValueError):
        ms.assert_sanctioned("printables")
    with pytest.raises(ValueError):
        ms.assert_sanctioned("makerworld")


def test_link_out_url_builders():
    assert ms.link_out_url("printables", "cat toy").startswith("https://www.printables.com/search")
    assert ms.link_out_url("thangs", "cat toy").startswith("https://thangs.com/search")
    assert ms.link_out_url("makerworld", "cat toy").startswith("https://makerworld.com")


def test_search_without_keys_no_network(monkeypatch):
    for env in ("THINGIVERSE_APP_TOKEN", "MYMINIFACTORY_API_KEY", "CULTS3D_API_KEY"):
        monkeypatch.delenv(env, raising=False)
    out = ms.search("cat toy")
    assert out["results"] == []
    assert out["providers_queried"] == []
    assert any("disabled" in w for w in out["warnings"])
