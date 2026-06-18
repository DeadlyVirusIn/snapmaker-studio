"""Frozen-binary entry point for the Snapmaker Studio engine sidecar.

PyInstaller bundles this into `snapstudio-api-<target-triple>.exe`. It mirrors
`python -m snapstudio_api`: start the loopback server, which prints a single
handshake line `{"port", "token"}` to stdout for the desktop shell to read.

Port may be pinned via SNAPSTUDIO_API_PORT (default 0 = ephemeral).
"""
from __future__ import annotations
import os
from snapstudio_api.server import serve

if __name__ == "__main__":
    serve(port=int(os.environ.get("SNAPSTUDIO_API_PORT", "0")))
