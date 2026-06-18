"""Adapter functions — delegate to the pure engine, return JSON-ready dicts."""
from __future__ import annotations
from snapstudio_core.doctor import diagnose_path

API_VERSION = "api/1"


def health() -> dict:
    return {"status": "ok", "api_version": API_VERSION}


def doctor(path: str) -> dict:
    """Read-only U1 compatibility diagnosis for a file path. Never modifies the file."""
    return diagnose_path(path).to_dict()
