"""Read-only Moonraker spike, tested against a mock Moonraker (no real printer).
Proves discovery/connect/status parsing + that only GET is ever issued."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from snapstudio_core import moonraker

_SERVER_INFO = {"result": {"klippy_state": "ready", "moonraker_version": "v0.9.3",
                           "api_version_string": "1.5.0"}}
_STATUS = {"result": {"status": {
    "print_stats": {"state": "printing", "filename": "liberty_eagle.gcode"},
    "heater_bed": {"temperature": 60.0, "target": 60.0},
    "toolhead": {},
    "virtual_sdcard": {"progress": 0.42},
    "extruder": {"temperature": 210.0, "target": 210.0},
    "extruder1": {"temperature": 25.0, "target": 0.0},
}}}


def _mock_moonraker():
    methods_seen = []

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _send(self, obj):
            b = json.dumps(obj).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        def do_GET(self):
            methods_seen.append(("GET", self.path))
            if self.path == "/server/info": self._send(_SERVER_INFO)
            elif self.path.startswith("/printer/objects/query"): self._send(_STATUS)
            else: self.send_response(404); self.end_headers()
        def do_POST(self):  # must NEVER be hit by the read-only client
            methods_seen.append(("POST", self.path)); self.send_response(405); self.end_headers()

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1], methods_seen


def test_probe_connects():
    httpd, port, _ = _mock_moonraker()
    try:
        p = moonraker.probe("127.0.0.1", port, timeout=5)
        assert p["reachable"] is True
        assert p["klippy_state"] == "ready"
        assert p["moonraker_version"] == "v0.9.3"
    finally:
        httpd.shutdown()


def test_probe_unreachable_never_raises():
    p = moonraker.probe("127.0.0.1", 9, timeout=0.5)  # nothing listening
    assert p["reachable"] is False and "error" in p


def test_status_parses_toolheads_and_state():
    httpd, port, seen = _mock_moonraker()
    try:
        s = moonraker.status("127.0.0.1", port, timeout=5)
        assert s["schema_version"] == "printer/1"
        assert s["print_state"] == "printing"
        assert s["filename"] == "liberty_eagle.gcode"
        assert s["progress"] == 0.42
        assert s["bed"]["temperature"] == 60.0
        assert len(s["toolheads"]) == 2  # extruder + extruder1 present
        assert s["toolheads"][0]["temperature"] == 210.0
        # read-only guarantee: the client issued only GETs
        assert all(m == "GET" for m, _ in seen)
    finally:
        httpd.shutdown()
