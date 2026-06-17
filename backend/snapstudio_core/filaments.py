from __future__ import annotations
import json
from importlib.resources import files
from .errors import FilamentLimitError

FILAMENT_ARRAY_KEYS = (
    "filament_colour", "filament_type", "filament_settings_id",
    "filament_map", "filament_ids", "filament_is_support",
)


def load_per_filament_keys() -> tuple[str, ...]:
    """Project setting keys whose array length tracks the filament count;
    bundled as data/u1_filament_arrays.json."""
    data = json.loads((files("snapstudio_core.data") / "u1_filament_arrays.json")
                      .read_text("utf-8"))
    return tuple(data["per_filament_keys"])


PER_FILAMENT_KEYS = load_per_filament_keys()


def conform_filament_arrays(cfg: dict, keep: int) -> dict:
    """Make every per-filament array exactly `keep` long, keeping the first `keep`
    entries (kept values unchanged), and resize the purge structures to match:
      per-filament arrays -> length n
      flush_volumes_matrix -> n*n   (square submatrix of kept indices)
      flush_volumes_vector -> n*2
      wiping_volumes_extruders -> unchanged
    Per-extruder/machine arrays are untouched."""
    orig = len(cfg.get("filament_colour", []))
    for k in PER_FILAMENT_KEYS:
        v = cfg.get(k)
        if isinstance(v, list):
            cfg[k] = v[:keep]
    m = cfg.get("flush_volumes_matrix")
    if isinstance(m, list) and orig and len(m) == orig * orig:
        cfg["flush_volumes_matrix"] = [m[i * orig + j] for i in range(keep) for j in range(keep)]
    fv = cfg.get("flush_volumes_vector")
    if isinstance(fv, list):
        cfg["flush_volumes_vector"] = fv[:keep * 2]
    # wiping_volumes_extruders intentionally left as-is (stock keeps it length 10)
    return cfg

def filament_count(cfg: dict) -> int:
    return len(cfg.get("filament_colour", []))

def parse_remap(s: str | None) -> dict[int, int]:
    if not s: return {}
    out = {}
    for pair in s.split(","):
        src, dst = pair.split(":")
        out[int(src)] = int(dst)
    return out

def apply_remap(cfg: dict, remap: dict[int, int], max_tools: int = 4) -> dict:
    n = filament_count(cfg)
    if n <= max_tools and not remap:
        return {"removed_indices": []}
    over = [i for i in range(1, n + 1) if i > max_tools]
    unmapped = [i for i in over if i not in remap]
    if unmapped:
        raise FilamentLimitError(
            f"{n} filaments exceed {max_tools} tools; remap required for {unmapped}")
    removed = sorted(set(remap))                 # 1-based source indices folded away
    keep = [i for i in range(1, n + 1) if i not in removed]   # 1-based kept
    for k in FILAMENT_ARRAY_KEYS:
        if k in cfg and isinstance(cfg[k], list) and len(cfg[k]) == n:
            cfg[k] = [cfg[k][i - 1] for i in keep]
    return {"removed_indices": removed, "kept": keep}
