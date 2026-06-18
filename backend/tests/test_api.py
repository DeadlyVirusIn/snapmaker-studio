import json
import struct
import threading
import urllib.request
import urllib.error
from snapstudio_api import service
from snapstudio_api.server import build_server
from snapstudio_core.stl_wrap import wrap_stl


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
