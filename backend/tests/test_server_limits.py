"""Loopback server request limits."""
from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

import pytest

from snapstudio_api import server


@pytest.fixture()
def live_server():
    httpd, token = server.build_server(port=0)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}", token
    finally:
        httpd.shutdown()
        httpd.server_close()


def _post(base, path, body: bytes, token: str | None):
    req = urllib.request.Request(base + path, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("X-Auth-Token", token)
    return urllib.request.urlopen(req, timeout=5)


def test_oversized_body_is_refused_before_auth(live_server):
    base, _token = live_server
    huge = b'{"path":"' + b"a" * (server.MAX_REQUEST_BYTES + 1024) + b'"}'
    with pytest.raises(urllib.error.HTTPError) as e:
        _post(base, "/doctor", huge, token=None)
    assert e.value.code == 413


def test_normal_body_still_works(live_server):
    base, token = live_server
    with pytest.raises(urllib.error.HTTPError) as e:
        _post(base, "/doctor", json.dumps({"path": ""}).encode(), token=token)
    # Empty path is a validation error (400), not a size error — proves the body
    # was accepted and routed.
    assert e.value.code == 400
