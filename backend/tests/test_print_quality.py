"""Print Quality Doctor MVP — advisory knowledge base tests (static, offline)."""
from snapstudio_core import print_quality as pq

_EXPECTED = {
    "stringing", "ringing", "layer_shift", "warping", "first_layer",
    "blobs", "under_extrusion", "rough_surface", "bridging", "color_bleed",
    "bed_adhesion", "support_failure",
}


def test_all_symptoms_present():
    ids = {s["id"] for s in pq.symptoms()}
    assert ids == _EXPECTED


def test_each_symptom_has_nonempty_causes_and_checks():
    for sid in _EXPECTED:
        r = pq.lookup(sid)["result"]
        assert r is not None
        assert r["likely_causes"] and r["first_checks"]
        assert r["orca_paths"] and r["avoid"] and r["evidence_needed"]
        assert r["disclaimer"]


def test_hedged_language_no_guarantee_claims():
    for sid in _EXPECTED:
        r = pq.lookup(sid)["result"]
        # advisory fields must not promise a guaranteed outcome
        blob = " ".join(r["likely_causes"] + r["first_checks"] + r["avoid"]
                        + r["orca_paths"] + r["hardware_checks"]).lower()
        assert "guarante" not in blob
        # the disclaimer hedges explicitly
        assert "not a guarantee" in r["disclaimer"].lower()


def test_no_autofix_claim_and_states_no_setting_edits():
    for sid in _EXPECTED:
        r = pq.lookup(sid)["result"]
        blob = " ".join(r["likely_causes"] + r["first_checks"] + r["avoid"]).lower()
        assert "auto-fix" not in blob and "automatically" not in blob
    # disclaimer makes the read-only stance explicit
    d = pq.lookup("stringing")["result"]["disclaimer"].lower()
    assert "does not change your settings" in d
    assert "never ignore a bad slice preview" in d


def test_no_paid_model_names():
    blob = []
    for sid in _EXPECTED:
        r = pq.lookup(sid)["result"]
        blob += r["likely_causes"] + r["first_checks"] + r["avoid"] + [r["title"]]
    joined = " ".join(blob).lower()
    for name in ("freedom torch", "fox sake", "jesus", "shadow_ams"):
        assert name not in joined


def test_unknown_symptom_is_safe():
    out = pq.lookup("does_not_exist")
    assert out["result"] is None
    assert out["warnings"] and "unknown symptom" in out["warnings"][0]
