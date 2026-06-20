"""Failure-Pattern Learning — pure analysis over Moonraker history jobs."""
from snapstudio_core import failure_patterns as fp


def _job(name, status):
    return {"filename": name, "status": status}


def test_empty_history_unavailable():
    out = fp.assess([])
    assert out["available"] is False


def test_all_clean_is_ok():
    jobs = [_job("a.gcode", "completed"), _job("b.gcode", "completed")]
    out = fp.assess(jobs)
    assert out["available"] is True
    assert out["overall_level"] == "ok"
    assert out["failed"] == 0
    assert out["failure_rate"] == 0.0


def test_high_failure_rate_is_risk():
    jobs = [_job(f"f{i}.gcode", "error") for i in range(3)] + [_job("ok.gcode", "completed")]
    out = fp.assess(jobs)
    assert out["failed"] == 3
    assert out["total"] == 4
    assert out["overall_level"] == "risk"  # 75% failure rate


def test_repeat_offender_detected():
    jobs = [
        _job("/sd/boat.gcode", "error"),
        _job("boat.gcode", "cancelled"),
        _job("other.gcode", "completed"),
    ]
    out = fp.assess(jobs)
    ro = out["repeat_offenders"]
    assert ro and ro[0]["filename"] == "boat.gcode" and ro[0]["failures"] == 2


def test_recent_streak_counts_leading_failures_only():
    # newest-first: 2 fails at the top, then a success
    jobs = [_job("a", "error"), _job("b", "klippy_shutdown"), _job("c", "completed"), _job("d", "error")]
    out = fp.assess(jobs)
    assert out["recent_failure_streak"] == 2
    assert out["overall_level"] == "risk"


def test_top_cause_reported():
    jobs = [_job("a", "klippy_disconnect"), _job("b", "klippy_disconnect"), _job("c", "completed")]
    out = fp.assess(jobs)
    assert out["top_cause"] == "klippy_disconnect"
