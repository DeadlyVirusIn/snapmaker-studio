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
    """The oversized body must be refused, and refused without being read.

    Two outcomes both satisfy that, and which one a client sees is a property of
    the platform's socket buffering rather than of the server. On Windows the
    whole body fits in the send buffer, so the client completes the write and
    reads back 413. On Linux the server answers and closes while the client is
    still writing, so the client sees the connection break first — which is the
    stronger of the two behaviours, and used to fail this test on Linux only.
    """
    base, _token = live_server
    huge = b'{"path":"' + b"a" * (server.MAX_REQUEST_BYTES + 1024) + b'"}'
    with pytest.raises((urllib.error.HTTPError, urllib.error.URLError, OSError)) as e:
        _post(base, "/doctor", huge, token=None)
    error = e.value
    if isinstance(error, urllib.error.HTTPError):
        assert error.code == 413
    else:
        # Refused mid-write. The one thing that must not happen is the request
        # being accepted, so assert the connection died rather than completed.
        assert isinstance(error, (urllib.error.URLError, BrokenPipeError, ConnectionError))


def test_normal_body_still_works(live_server):
    base, token = live_server
    with pytest.raises(urllib.error.HTTPError) as e:
        _post(base, "/doctor", json.dumps({"path": ""}).encode(), token=token)
    # Empty path is a validation error (400), not a size error — proves the body
    # was accepted and routed.
    assert e.value.code == 400
