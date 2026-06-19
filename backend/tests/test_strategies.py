"""Adaptive Print Strategies (intent profiles) — mapping + recommendation tests.

Strategies are a read-only recommendation layer (Orca slices). These tests pin the
safety invariants from docs/research/U1_PRINT_PROFILE_RESEARCH.md."""
from snapstudio_core import strategies as S


def test_five_strategies_present_with_default_balanced():
    out = S.list_strategies()
    ids = [s["id"] for s in out["strategies"]]
    assert ids == ["fastest", "balanced", "best_quality", "max_reliability", "advanced"]
    assert out["default"] == "balanced"
    # every strategy has novice copy + intent + tradeoffs (Simple Mode needs these)
    for s in out["strategies"]:
        assert s["name"] and s["explanation"] and s["intent"] and s["tradeoffs"]


def test_advanced_has_no_overrides():
    assert S.get_strategy("advanced")["settings"] == {}


def test_safety_invariants_across_all_strategies():
    for s in S.STRATEGIES:
        st = s["settings"]
        # never auto-enable no-sparse-layers (collision risk)
        assert st.get("wipe_tower_no_sparse_layers", "0") == "0"
        # never auto-raise purge speed above the U1-documented safe max (90 mm/s)
        if "wipe_tower_max_purge_speed" in st:
            assert int(st["wipe_tower_max_purge_speed"]) <= S.U1_SAFE_MAX_PURGE_SPEED
        # strategies never touch geometry or per-design filament data
        for k in st:
            assert not k.startswith(("filament_colour", "filament_type", "filament_settings_id"))


def test_reliability_uses_rib_wall_and_bigger_brim():
    rel = S.get_strategy("max_reliability")["settings"]
    bal = S.get_strategy("balanced")["settings"]
    assert rel["wipe_tower_wall_type"] == "rib"
    assert int(rel["prime_tower_brim_width"]) >= int(bal["prime_tower_brim_width"])


def test_best_quality_purges_more_than_fastest():
    bq = float(S.get_strategy("best_quality")["settings"]["flush_multiplier"])
    fast = float(S.get_strategy("fastest")["settings"]["flush_multiplier"])
    assert bq > fast


def test_recommend_single_color_is_fastest():
    r = S.recommend({"colors": 1, "dimensions_mm": {"x": 20, "y": 20, "z": 20}})
    assert r["recommended"] == "fastest"
    assert "color count" in r["signals_used"]


def test_recommend_tall_multicolor_is_reliability():
    r = S.recommend({"colors": 3, "dimensions_mm": {"x": 50, "y": 50, "z": 220}})
    assert r["recommended"] == "max_reliability"
    assert "model height" in r["signals_used"]


def test_recommend_over_four_colors_warns_and_picks_reliability():
    r = S.recommend({"colors": 6, "dimensions_mm": {"x": 50, "y": 50, "z": 40}})
    assert r["recommended"] == "max_reliability"
    assert any("4 toolheads" in w for w in r["warnings"])


def test_recommend_tip_risk_forces_reliability():
    # mesh diagnostics flagged tip-risk on an otherwise unremarkable multi-color print
    r = S.recommend({"colors": 2, "dimensions_mm": {"x": 30, "y": 30, "z": 60}, "tip_risk": True})
    assert r["recommended"] == "max_reliability"
    assert "stability" in r["signals_used"]
    assert "tip" in r["reason"].lower()


def test_recommend_supports_likely_adds_warning():
    r = S.recommend({"colors": 2, "dimensions_mm": {"x": 40, "y": 40, "z": 40}, "supports_likely": True})
    assert "overhangs" in r["signals_used"]
    assert any("supports" in w.lower() for w in r["warnings"])


def test_recommend_default_multicolor_is_balanced():
    r = S.recommend({"colors": 2, "dimensions_mm": {"x": 50, "y": 50, "z": 40}, "complexity": "low"})
    assert r["recommended"] == "balanced"


def test_recommend_never_fakes_tool_changes_or_duration():
    r = S.recommend({"colors": 3, "dimensions_mm": {"x": 50, "y": 50, "z": 40}})
    blob = (r["reason"] + " " + r["estimated_note"]).lower()
    assert "estimated" in r["estimated_note"].lower()
    # no fabricated absolute counts/times
    assert "minutes" not in blob and "hours" not in blob


def _bundled_json(pkg):
    import json
    from importlib.resources import files
    out = {}
    for p in files(pkg).iterdir():
        if p.name.endswith(".json"):
            out[p.name] = json.loads(p.read_text("utf-8"))
    return out


_SPEED_KEYS = ("wipe_tower_max_purge_speed", "max_purge_speed")
_NO_SPARSE_KEYS = ("wipe_tower_no_sparse_layers", "no_sparse_layers")
_PROTECTED = ("filament_colour", "filament_type", "filament_settings_id")


def _iter_setting_blocks():
    """Yield (label, dict-of-settings) for every bundled optimization + profile."""
    for fname, doc in _bundled_json("snapstudio_core.data.optimizations").items():
        yield f"optimization:{fname}", doc.get("set", {})
    for fname, doc in _bundled_json("snapstudio_core.data.profiles").items():
        yield f"profile:{fname}", doc.get("keys", {})


def test_no_bundled_data_exceeds_safe_tower_speed():
    for label, settings in _iter_setting_blocks():
        for k in _SPEED_KEYS:
            if k in settings:
                assert float(settings[k]) <= S.U1_SAFE_MAX_PURGE_SPEED, f"{label}:{k}={settings[k]} > 90"


def test_no_bundled_data_auto_enables_no_sparse_layers():
    off = {"0", "false", "False", 0, False}
    for label, settings in _iter_setting_blocks():
        for k in _NO_SPARSE_KEYS:
            if k in settings:
                assert settings[k] in off, f"{label}:{k}={settings[k]} must be OFF"


def test_optimizations_never_touch_protected_per_design_data():
    # optimization `set` blocks are applied to a real project — they must never
    # overwrite per-design/per-filament/color data.
    import json
    from importlib.resources import files
    for p in files("snapstudio_core.data.optimizations").iterdir():
        if not p.name.endswith(".json"):
            continue
        doc = json.loads(p.read_text("utf-8"))
        for k in doc.get("set", {}):
            assert not k.startswith(_PROTECTED), f"{p.name}: {k} touches protected data"


def test_service_strategies_and_recommend(tmp_path):
    import struct
    from snapstudio_api import service
    out = service.strategies()
    assert out["schema_version"] == "strategies/1" and len(out["strategies"]) == 5
    # recommend on a real STL (single tetra -> single color -> fastest)
    stl = tmp_path / "cube.stl"
    head = b"\x00" * 80 + struct.pack("<I", 1) + struct.pack("<12fH", 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 10, 0, 0)
    stl.write_bytes(head)
    rec = service.strategy_recommend(str(stl))
    assert rec["recommended"] in {s["id"] for s in out["strategies"]}
    assert "estimated_note" in rec
