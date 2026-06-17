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
