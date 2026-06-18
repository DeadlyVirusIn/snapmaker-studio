from snapstudio_core.batch import run_batch, BatchResult


def test_run_batch_mixed_success_and_failure():
    def fake_convert(path, out_dir=None):
        if "bad" in path:
            raise ValueError("nope")
        return {"output_path": path + ".3mf", "output_name": "x.3mf", "validated_ok": True}

    res = run_batch(["a", "bad", "c"], fake_convert)
    assert res.total == 3 and res.done == 2 and res.failed == 1
    assert res.finished is True
    by_path = {i.path: i for i in res.items}
    assert by_path["a"].status == "done" and by_path["a"].output_path == "a.3mf"
    assert by_path["bad"].status == "error" and by_path["bad"].error == "nope"


def test_run_batch_reports_progress_monotonically():
    snapshots = []

    def fake_convert(path, out_dir=None):
        return {"output_path": path, "output_name": path, "validated_ok": True}

    def on_item(res: BatchResult):
        snapshots.append((res.done, res.failed))

    run_batch(["a", "b"], fake_convert, on_item=on_item)
    # progress never decreases and ends complete
    dones = [d for d, _ in snapshots]
    assert dones == sorted(dones)
    assert snapshots[-1] == (2, 0)


def test_run_batch_empty():
    res = run_batch([], lambda p, o=None: {})
    assert res.total == 0 and res.finished is True
