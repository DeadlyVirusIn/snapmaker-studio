from __future__ import annotations
import json
from importlib.resources import files
from .preserve import CATEGORY_A

# never overwrite per-design / per-filament data during a profile swap
_PROTECTED_PREFIXES = ("filament_colour", "filament_type", "filament_settings_id")

def load_profile(name: str) -> dict:
    return json.loads((files("snapstudio_core.data.profiles") / f"{name}.json").read_text("utf-8"))

def apply_swap(cfg: dict, profile: dict, *, preserve_creator_settings: bool = False) -> list[dict]:
    """Apply U1 profile-owned settings.

    Preserve mode intentionally leaves category-A creator settings alone; the
    bundled policy is the single source of truth for that boundary.
    """
    changes = []
    for k, v in profile["keys"].items():
        if k.startswith(_PROTECTED_PREFIXES):
            continue
        if preserve_creator_settings and k in CATEGORY_A:
            continue
        if cfg.get(k) != v:
            changes.append({"key": k, "old": cfg.get(k), "new": v})
            cfg[k] = v
    return changes
