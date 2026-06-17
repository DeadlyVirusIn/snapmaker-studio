from __future__ import annotations
import json
from importlib.resources import files

# never overwrite per-design / per-filament data during a profile swap
_PROTECTED_PREFIXES = ("filament_colour", "filament_type", "filament_settings_id")

def load_profile(name: str) -> dict:
    return json.loads((files("snapstudio_core.data.profiles") / f"{name}.json").read_text("utf-8"))

def apply_swap(cfg: dict, profile: dict) -> list[dict]:
    changes = []
    for k, v in profile["keys"].items():
        if k.startswith(_PROTECTED_PREFIXES):
            continue
        if cfg.get(k) != v:
            changes.append({"key": k, "old": cfg.get(k), "new": v})
            cfg[k] = v
    return changes
