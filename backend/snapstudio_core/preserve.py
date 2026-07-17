"""Policy and accounting for preserving creator-owned slicer settings."""
from __future__ import annotations

import copy
import json
from importlib.resources import files


def load_policy() -> dict:
    return json.loads((files("snapstudio_core.data") / "u1_preserve_keys.json")
                      .read_text("utf-8"))


POLICY = load_policy()
CATEGORY_A = frozenset(POLICY["category_a"])
PER_EXTRUDER_VECTORS = frozenset(POLICY["per_extruder_vectors"])
VALID_BED_TYPES = frozenset(POLICY["valid_bed_types"])


def machine_compat_keys(profile: dict) -> set[str]:
    """The profile-owned (category B) keys; category A is deliberately absent."""
    return set(profile["keys"]) - CATEGORY_A


def prepare_preserved_values(cfg: dict, filament_total: int) -> tuple[list[dict], list[str]]:
    """Apply the few U1 representation constraints without replacing values."""
    changes: list[dict] = []
    warnings: list[str] = []
    for key in ("curr_bed_type", "default_bed_type"):
        value = cfg.get(key)
        if value is not None and value not in VALID_BED_TYPES:
            cfg[key] = "Textured PEI Plate"
            changes.append({"key": key, "old": value, "new": cfg[key],
                            "reason": "mapped to a supported U1 plate"})

    for key in PER_EXTRUDER_VECTORS:
        if key not in cfg:
            continue
        old = copy.deepcopy(cfg[key])
        values = old if isinstance(old, list) else [old]
        if not values:
            continue
        if len(values) == 4:
            continue
        if len(values) == 1:
            new = values * 4
        elif len(values) < 4:
            new = values + [values[0]] * (4 - len(values))
            warnings.append("Source tool mapping was replicated to four U1 toolheads.")
        else:
            new = values[:4]
            warnings.append("Source tool mapping was reduced to four U1 toolheads.")
        cfg[key] = new
        changes.append({"key": key, "old": old, "new": new,
                        "reason": "resized to 4 toolheads (values preserved)"})

    key = "wipe_tower_filament"
    if key in cfg:
        old = cfg[key]
        try:
            index = int(old)
        except (TypeError, ValueError):
            index = -1
        if not (0 <= index < max(1, filament_total)):
            cfg[key] = "0" if isinstance(old, str) else 0
            changes.append({"key": key, "old": old, "new": cfg[key],
                            "reason": "mapped to an available filament"})
    return changes, warnings


def config_diff(before: dict, after: dict) -> list[dict]:
    """Independent whole-config diff used for the preservation invariant."""
    missing = object()
    result = []
    for key in sorted(set(before) | set(after)):
        old, new = before.get(key, missing), after.get(key, missing)
        if old != new:
            result.append({"key": key,
                           "old": None if old is missing else old,
                           "new": None if new is missing else new,
                           "removed": new is missing})
    return result


def display_value(value, limit: int = 120):
    """Keep summaries useful without exposing multi-kilobyte G-code blobs."""
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if len(encoded) > limit:
        return encoded[:limit - 1] + "…"
    return copy.deepcopy(value)
