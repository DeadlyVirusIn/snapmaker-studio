import json
import struct
import threading
import time
import urllib.request
import urllib.error
from snapstudio_api import service
from snapstudio_api.server import build_server
from snapstudio_core.stl_wrap import wrap_stl


def _poll_until_finished(get_status, timeout=15.0):
    """Poll a batch status callable until its result is finished or timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        st = get_status()
        res = (st or {}).get("result")
        if st and st.get("status") in ("done", "error") and res and res.get("finished"):
            return st
        time.sleep(0.05)
    raise AssertionError("batch did not finish in time")


def _bin_tetra():
    head = b"\x00" * 80 + struct.pack("<I", 2)
    for v1, v2, v3 in [((0, 0, 0), (10, 0, 0), (0, 10, 0)),
                       ((0, 0, 0), (0, 10, 0), (0, 0, 10))]:
        head += struct.pack("<12fH", 0, 0, 0, *v1, *v2, *v3, 0)
    return head


def _sample_u1(tmp_path):
    stl = tmp_path / "cube.stl"; stl.write_bytes(_bin_tetra())
    out = tmp_path / "cube_U1.3mf"
    wrap_stl(str(stl)).save(out)
    return out


# ---- adapter functions (no network) ----
def test_service_health():
    h = service.health()
    assert h["status"] == "ok" and h["api_version"] == "api/1"


def test_service_doctor(tmp_path):
    out = _sample_u1(tmp_path)
    d = service.doctor(str(out))
    assert d["verdict"] == "READY" and d["is_compatible"] is True


def test_service_diff(tmp_path):
    a = _sample_u1(tmp_path)
    d = service.diff(str(a), str(a))   # same file vs itself
    assert d["schema_version"] == "diff/1"
    assert d["geometry_changed"] is False
    assert d["has_changes"] is False


def test_service_convert_stl(tmp_path):
    from pathlib import Path
    stl = tmp_path / "cube.stl"; stl.write_bytes(_bin_tetra())
    res = service.convert(str(stl))
    assert res["source_type"] == "stl"
    assert res["validated_ok"] is True
    assert res["output_name"].endswith("_SnapmakerU1.3mf")
    assert Path(res["output_path"]).exists()
    assert stl.exists()  # source untouched


# ---- loopback server round-trip ----
def _run(httpd):
    threading.Thread(target=httpd.serve_forever, daemon=True).start()


def test_server_health_open():
    httpd, token = build_server(port=0)
    _run(httpd)
    try:
        port = httpd.server_address[1]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as r:
            body = json.loads(r.read())
        assert body["status"] == "ok"
    finally:
        httpd.shutdown()


def test_server_doctor_requires_token(tmp_path):
    httpd, token = build_server(port=0)
    _run(httpd)
    try:
        port = httpd.server_address[1]
        out = _sample_u1(tmp_path)
        payload = json.dumps({"path": str(out)}).encode()

        req = urllib.request.Request(f"http://127.0.0.1:{port}/doctor", data=payload,
                                     headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=5)
            assert False, "expected 401 without token"
        except urllib.error.HTTPError as e:
            assert e.code == 401

        req = urllib.request.Request(f"http://127.0.0.1:{port}/doctor", data=payload,
                                     headers={"Content-Type": "application/json",
                                              "X-Auth-Token": token})
        with urllib.request.urlopen(req, timeout=5) as r:
            body = json.loads(r.read())
        assert body["verdict"] == "READY"
    finally:
        httpd.shutdown()


# ---- library index ----
def test_library_record_and_list(tmp_path, monkeypatch):
    monkeypatch.setenv("SNAPSTUDIO_DATA_DIR", str(tmp_path / "data"))
    out = _sample_u1(tmp_path)
    service.record_diagnosis(str(out), service.doctor(str(out)))
    listing = service.library_list()
    assert listing["count"] == 1
    p = listing["projects"][0]
    assert p["name"] == "cube_U1.3mf" and p["verdict"] == "READY"
    assert p["last_action"] == "doctor"


def test_library_convert_records_output(tmp_path, monkeypatch):
    monkeypatch.setenv("SNAPSTUDIO_DATA_DIR", str(tmp_path / "data"))
    stl = tmp_path / "cube.stl"; stl.write_bytes(_bin_tetra())
    res = service.convert(str(stl))
    service.record_conversion(str(stl), res)
    p = service.library_list()["projects"][0]
    assert p["last_action"] == "convert"
    assert p["output_path"] == res["output_path"]


def test_library_search_and_delete(tmp_path, monkeypatch):
    monkeypatch.setenv("SNAPSTUDIO_DATA_DIR", str(tmp_path / "data"))
    out = _sample_u1(tmp_path)
    service.record_diagnosis(str(out), service.doctor(str(out)))
    assert service.library_list("cube")["count"] == 1
    assert service.library_list("nomatch")["count"] == 0
    pid = service.library_list()["projects"][0]["id"]
    service.library_delete(pid)
    assert service.library_list()["count"] == 0


def test_server_library_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("SNAPSTUDIO_DATA_DIR", str(tmp_path / "data"))
    httpd, token = build_server(port=0)
    _run(httpd)
    try:
        port = httpd.server_address[1]
        out = _sample_u1(tmp_path)
        hdr = {"Content-Type": "application/json", "X-Auth-Token": token}

        # diagnose over the wire -> auto-records into the library
        req = urllib.request.Request(f"http://127.0.0.1:{port}/doctor",
                                     data=json.dumps({"path": str(out)}).encode(), headers=hdr)
        urllib.request.urlopen(req, timeout=5).read()

        # list via /library
        req = urllib.request.Request(f"http://127.0.0.1:{port}/library",
                                     data=b"{}", headers=hdr)
        with urllib.request.urlopen(req, timeout=5) as r:
            body = json.loads(r.read())
        assert body["count"] == 1 and body["projects"][0]["name"] == "cube_U1.3mf"
    finally:
        httpd.shutdown()


# ---- batch conversion ----
def test_batch_start_and_status(tmp_path, monkeypatch):
    monkeypatch.setenv("SNAPSTUDIO_DATA_DIR", str(tmp_path / "data"))
    paths = []
    for i in range(3):
        stl = tmp_path / f"cube{i}.stl"; stl.write_bytes(_bin_tetra())
        paths.append(str(stl))

    job = service.batch_start(paths)
    assert job["total"] == 3 and job["job_id"]

    st = _poll_until_finished(lambda: service.batch_status(job["job_id"]))
    res = st["result"]
    assert res["total"] == 3 and res["done"] == 3 and res["failed"] == 0
    assert all(it["status"] == "done" and it["validated_ok"] for it in res["items"])
    # each batched conversion was indexed in the library too
    assert service.library_list()["count"] == 3


def test_batch_isolates_failures(tmp_path, monkeypatch):
    monkeypatch.setenv("SNAPSTUDIO_DATA_DIR", str(tmp_path / "data"))
    good = tmp_path / "ok.stl"; good.write_bytes(_bin_tetra())
    bad = tmp_path / "missing.stl"  # never created -> convert raises
    job = service.batch_start([str(good), str(bad)])
    st = _poll_until_finished(lambda: service.batch_status(job["job_id"]))
    res = st["result"]
    assert res["done"] == 1 and res["failed"] == 1
    by = {it["path"]: it for it in res["items"]}
    assert by[str(good)]["status"] == "done"
    assert by[str(bad)]["status"] == "error" and by[str(bad)]["error"]


def test_batch_status_unknown_job():
    assert service.batch_status("nope-not-a-job") is None


def test_server_batch_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("SNAPSTUDIO_DATA_DIR", str(tmp_path / "data"))
    httpd, token = build_server(port=0)
    _run(httpd)
    try:
        port = httpd.server_address[1]
        hdr = {"Content-Type": "application/json", "X-Auth-Token": token}
        stl = tmp_path / "cube.stl"; stl.write_bytes(_bin_tetra())

        req = urllib.request.Request(f"http://127.0.0.1:{port}/batch",
                                     data=json.dumps({"paths": [str(stl)]}).encode(), headers=hdr)
        with urllib.request.urlopen(req, timeout=5) as r:
            start = json.loads(r.read())
        job_id = start["job_id"]

        def status():
            req = urllib.request.Request(f"http://127.0.0.1:{port}/batch/status",
                                         data=json.dumps({"job_id": job_id}).encode(), headers=hdr)
            with urllib.request.urlopen(req, timeout=5) as r:
                return json.loads(r.read())

        st = _poll_until_finished(status)
        assert st["result"]["done"] == 1
    finally:
        httpd.shutdown()
