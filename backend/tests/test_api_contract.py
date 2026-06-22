"""API contract guard: required response fields the frontend (desktop/src/api.ts)
relies on must not silently disappear. Shape/field-presence checks (not brittle
full snapshots). Hermetic — uses payloads that need no real mesh.
"""
import json
import threading
import urllib.request

from snapstudio_api.server import build_server


def _run(httpd):
    threading.Thread(target=httpd.serve_forever, daemon=True).start()


def _post(port, route, payload, token):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{route}", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-Auth-Token": token})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())


# route -> (payload, [required top-level keys])
_CONTRACT = {
    "/quality_check": ({"symptom": "stringing"}, ["result", "warnings"]),
    "/first_layer_check": ({"symptom": "not_stick"}, ["result", "warnings"]),
    "/model_search": ({"query": "x"}, ["results", "warnings"]),
    "/scale_options": ({"path": "none"}, ["available", "schema_version"]),
    "/print_failure_troubleshoot": ({"path": "none"},
        ["available", "summary", "findings", "troubleshooting_steps", "disclaimers"]),
}


def test_api_response_contract():
    httpd, token = build_server(port=0)
    _run(httpd)
    try:
        port = httpd.server_address[1]
        for route, (payload, required) in _CONTRACT.items():
            body = _post(port, route, payload, token)
            for key in required:
                assert key in body, f"{route} dropped required field '{key}'"
        # print_failure findings carry the fields the UI renders
        pf = _post(port, "/print_failure_troubleshoot",
                   {"path": "none", "known_good_print": True}, token)
        assert pf["findings"], "expected at least one finding"
        for f in pf["findings"]:
            for key in ("id", "title", "explanation", "suggested_action"):
                assert key in f, f"finding dropped '{key}'"
    finally:
        httpd.shutdown()
