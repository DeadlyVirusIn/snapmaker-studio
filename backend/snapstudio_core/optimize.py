from __future__ import annotations
import json
from importlib.resources import files
from .errors import SnapStudioError


def load_optimization(name: str) -> dict:
    try:
        text = (files("snapstudio_core.data.optimizations") / f"{name}.json").read_text("utf-8")
    except (FileNotFoundError, ModuleNotFoundError):
        raise SnapStudioError(f"unknown optimization profile: {name}")
    return json.loads(text)


def apply_optimization(cfg: dict, opt: dict) -> list[dict]:
    """Apply opt['set'] to cfg. Record only keys whose value actually changes,
    as {key, old, new}. Reversible: caller keeps `old` (and the .orig backup)."""
    changes = []
    for k, new in opt.get("set", {}).items():
        old = cfg.get(k)
        if str(old) != str(new):
            changes.append({"key": k, "old": old, "new": new})
            cfg[k] = new
    return changes
