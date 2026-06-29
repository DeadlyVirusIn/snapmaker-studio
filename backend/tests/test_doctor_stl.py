"""STL Project Doctor: readable geometry gets a real design-health score (not '—'),
the GUI never shows raw CLI text, and unreadable geometry fails honestly."""
import snapstudio_core.mesh_diagnostics as mdmod
from snapstudio_core.doctor import diagnose_path, _stl_design_score, CONVERTIBLE


def test_design_score_from_mesh():
    healthy = {"available": True, "integrity": {"watertight": True}, "overhang": {}, "stability": {}}
    assert _stl_design_score(healthy) == 100
    assert _stl_design_score({"available": False}) is None
    rough = {"available": True,
             "integrity": {"watertight": False, "non_manifold_edges": 2},
             "overhang": {"supports_likely": True}, "stability": {"tip_risk": True}}
    assert 0 <= _stl_design_score(rough) < 100


def test_readable_stl_gets_score_and_no_cli(tmp_path, monkeypatch):
    monkeypatch.setattr(mdmod, "analyze", lambda p: {
        "available": True, "integrity": {"watertight": True}, "overhang": {}, "stability": {}})
    d = diagnose_path(str(tmp_path / "model.stl")).to_dict()
    assert d["input_type"] == "stl"
    assert d["verdict"] == CONVERTIBLE
    assert d["score"] == 100                       # real score, not None / "—"
    assert "u1convert" not in d["recommended_action"]
    assert "Orca" in d["recommended_action"]        # novice next step, not CLI


def test_unreadable_stl_no_fake_score(tmp_path, monkeypatch):
    monkeypatch.setattr(mdmod, "analyze", lambda p: {"available": False})
    d = diagnose_path(str(tmp_path / "broken.stl")).to_dict()
    assert d["score"] is None                       # honest "—" only when unreadable
    assert "u1convert" not in d["recommended_action"]
    assert "could not read" in d["recommended_action"].lower()
