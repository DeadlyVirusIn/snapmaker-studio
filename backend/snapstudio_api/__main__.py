"""Entry point: `python -m snapstudio_api` — start the local loopback server.

Port may be fixed via SNAPSTUDIO_API_PORT (default 0 = ephemeral).
"""
from __future__ import annotations
import os
from .server import serve

if __name__ == "__main__":
    serve(port=int(os.environ.get("SNAPSTUDIO_API_PORT", "0")))
