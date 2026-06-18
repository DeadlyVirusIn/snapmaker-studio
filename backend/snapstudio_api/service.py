"""Adapter functions — delegate to the pure engine, return JSON-ready dicts."""
from __future__ import annotations
from snapstudio_core.doctor import diagnose_path
from snapstudio_core.convert import convert_to_u1
from snapstudio_core.diff import diff_projects
from snapstudio_core.container import ThreeMF

API_VERSION = "api/1"


def health() -> dict:
    return {"status": "ok", "api_version": API_VERSION}


def doctor(path: str) -> dict:
    """Read-only U1 compatibility diagnosis for a file path. Never modifies the file."""
    return diagnose_path(path).to_dict()


def convert(path: str, out_dir: str | None = None) -> dict:
    """Make a file U1-ready and save it next to the source. Returns the result."""
    return convert_to_u1(path, out_dir).to_dict()


def diff(a: str, b: str) -> dict:
    """Compare two projects (read-only): what changed between A and B."""
    return diff_projects(ThreeMF.open(a), ThreeMF.open(b)).to_dict()
