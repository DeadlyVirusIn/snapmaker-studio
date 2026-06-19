"""Adaptive Print Strategies — research-backed, intent-based U1 print profiles.

These are a RECOMMENDATION + EXPLANATION layer. Studio reads a design and suggests a
strategy; **Snapmaker Orca still slices**. The settings here are slicer process settings
(prime/wipe tower), never firmware commands. Values + ranges come from
docs/research/U1_PRINT_PROFILE_RESEARCH.md (OrcaSlicer/Snapmaker-fork source + the
Snapmaker U1 prime-tower-collapse guide). No GPL/AGPL code is copied — concepts only.

Hard safety rules baked in (from the research "do not auto-change" list):
- never auto-enable `wipe_tower_no_sparse_layers` (explicit collision warning),
- never auto-raise `wipe_tower_max_purge_speed` above the U1-documented 90 mm/s,
- never touch geometry / per-design filament data.
"""
from __future__ import annotations

SCHEMA_VERSION = "strategies/1"
U1_SAFE_MAX_PURGE_SPEED = 90  # mm/s — U1 docs warn above this
U1_TOOLHEADS = 4

# Each strategy: id, name, novice explanation, intent, use cases, tradeoffs, and the
# U1-relevant prime/wipe-tower settings it recommends (shown raw in Advanced mode).
# "advanced" intentionally carries no overrides — power users edit raw values in Orca.
STRATEGIES = [
    {
        "id": "fastest",
        "name": "Fastest Print",
        "explanation": "Less waste and less time. Best for quick single-color or simple prints.",
        "intent": "Reduce purge waste and time while staying mechanically safe.",
        "use_cases": ["Single-color or few-color prints", "Short / low-height models", "Drafts and test fits"],
        "tradeoffs": "Slightly more color bleed at transitions; the simpler tower is less stable on tall jobs.",
        "settings": {
            "wipe_tower_wall_type": "rectangle",
            "prime_tower_width": "60",
            "prime_volume": "45",
            "prime_tower_brim_width": "2",
            "wipe_tower_max_purge_speed": "90",
            "wipe_tower_no_sparse_layers": "0",
            "flush_multiplier": "0.2",
        },
    },
    {
        "id": "balanced",
        "name": "Balanced",
        "explanation": "The recommended default for most prints — a good mix of speed, quality, and reliability.",
        "intent": "Sensible, stable defaults for everyday multi-color prints.",
        "use_cases": ["Most multi-color models", "Everyday prints", "When unsure"],
        "tradeoffs": "Not the absolute fastest nor the cleanest — a dependable middle ground.",
        "settings": {
            "wipe_tower_wall_type": "rib",
            "prime_tower_width": "60",
            "prime_volume": "45",
            "prime_tower_brim_width": "3",
            "wipe_tower_max_purge_speed": "90",
            "wipe_tower_no_sparse_layers": "0",
            "flush_multiplier": "0.3",
        },
    },
    {
        "id": "best_quality",
        "name": "Best Quality",
        "explanation": "Cleaner color transitions. Best when crisp colors matter more than speed.",
        "intent": "Maximize color separation with a safe, stable tower.",
        "use_cases": ["Detailed multi-color models", "Show pieces", "When color bleed is unacceptable"],
        "tradeoffs": "Uses more filament and time for the extra purging.",
        "settings": {
            "wipe_tower_wall_type": "rib",
            "prime_tower_width": "60",
            "prime_volume": "45",
            "prime_tower_brim_width": "3",
            "wipe_tower_max_purge_speed": "90",
            "wipe_tower_no_sparse_layers": "0",
            "flush_multiplier": "0.5",
        },
    },
    {
        "id": "max_reliability",
        "name": "Maximum Reliability",
        "explanation": "The safest tower. Best for tall prints, many colors, or long jobs with lots of tool changes.",
        "intent": "Minimize tower tip-over and nozzle-collision risk on demanding jobs.",
        "use_cases": ["Tall models", "Many tool changes", "Long unattended prints"],
        "tradeoffs": "Largest tower footprint and brim — more waste, but the least likely to fail.",
        "settings": {
            "wipe_tower_wall_type": "rib",
            "prime_tower_width": "60",
            "prime_volume": "45",
            "prime_tower_brim_width": "6",
            "wipe_tower_rib_width": "10",
            "wipe_tower_fillet_wall": "1",
            "wipe_tower_max_purge_speed": "90",
            "wipe_tower_no_sparse_layers": "0",
            "flush_multiplier": "0.4",
        },
    },
    {
        "id": "advanced",
        "name": "Advanced",
        "explanation": "Don't change anything automatically — inspect and edit the raw settings yourself in Snapmaker Orca.",
        "intent": "Full manual control for power users.",
        "use_cases": ["Power users", "Custom tuning", "Reproducing a known-good profile"],
        "tradeoffs": "No guard rails — you own the result.",
        "settings": {},  # passthrough: Studio recommends nothing; user edits raw values
    },
]

DEFAULT_STRATEGY = "balanced"

# Plain-language categories for each setting key (Simple Mode never shows raw keys).
SETTING_CATEGORIES = {
    "wipe_tower_wall_type": "Tower shape",
    "prime_tower_width": "Tower width",
    "prime_volume": "Prime amount",
    "prime_tower_brim_width": "Tower grip (brim)",
    "wipe_tower_rib_width": "Tower rib size",
    "wipe_tower_fillet_wall": "Rounded tower corners",
    "wipe_tower_max_purge_speed": "Tower speed",
    "wipe_tower_no_sparse_layers": "Skip empty tower layers",
    "flush_multiplier": "Color purge amount",
}

_BY_ID = {s["id"]: s for s in STRATEGIES}


def list_strategies() -> dict:
    """All strategies + the default id. Safe to show in both modes (Advanced shows
    the raw `settings`; Simple shows name/explanation only)."""
    return {
        "schema_version": SCHEMA_VERSION,
        "default": DEFAULT_STRATEGY,
        "strategies": STRATEGIES,
        "categories": SETTING_CATEGORIES,
        "notes": "Studio recommends a strategy; Snapmaker Orca does the slicing.",
    }


def get_strategy(strategy_id: str) -> dict | None:
    return _BY_ID.get(strategy_id)


def _height_mm(dimensions_mm) -> float | None:
    if isinstance(dimensions_mm, dict):
        z = dimensions_mm.get("z")
        if isinstance(z, (int, float)):
            return float(z)
    return None


def recommend(signals: dict) -> dict:
    """Pick a strategy from REAL project signals only — never fabricated duration,
    tool-change count, or purge volume. `signals` keys (all optional):
      colors:int, source_family:str, dimensions_mm:{x,y,z}, triangles:int,
      complexity:str, issues:list[str].
    Returns {recommended, reason, warnings, signals_used, estimated_note}.
    """
    colors = signals.get("colors")
    height = _height_mm(signals.get("dimensions_mm"))
    complexity = signals.get("complexity")
    issues = signals.get("issues") or []
    used: list[str] = []
    warnings: list[str] = []

    multicolor = isinstance(colors, int) and colors > 1
    tall = height is not None and height > 150.0  # mm; tall towers tip on the U1
    complex_model = complexity == "high"

    # >4 distinct colors can't each get a dedicated toolhead (U1 has 4).
    if isinstance(colors, int) and colors > U1_TOOLHEADS:
        warnings.append(
            f"This design uses {colors} colors, but the U1 has {U1_TOOLHEADS} toolheads — "
            "some colors will share a toolhead with extra tool changes. Reliability matters here."
        )

    if isinstance(colors, int):
        used.append("color count")
    if height is not None:
        used.append("model height")
    if complexity:
        used.append("complexity")
    if signals.get("source_family"):
        used.append("source ecosystem")

    # Policy (grounded in the research): stability wins on demanding jobs.
    if not multicolor:
        rec = "fastest"
        reason = "This looks like a single-color print, so a heavy multi-color tower isn't needed."
    elif tall or (isinstance(colors, int) and colors > U1_TOOLHEADS) or complex_model:
        rec = "max_reliability"
        bits = []
        if tall:
            bits.append("it's a tall print (taller towers tip over more easily)")
        if isinstance(colors, int) and colors > U1_TOOLHEADS:
            bits.append(f"it has {colors} colors with many tool changes")
        if complex_model:
            bits.append("it's a complex model")
        reason = "We suggest the safest tower because " + " and ".join(bits) + "."
    else:
        rec = "balanced"
        reason = "A balanced tower is a dependable choice for this multi-color print."

    # Honesty: if validation already flagged issues, nudge toward reliability framing.
    if issues:
        warnings.append("This design has open readiness issues — see the Validation Center before printing.")

    return {
        "schema_version": SCHEMA_VERSION,
        "recommended": rec,
        "reason": reason,
        "warnings": warnings,
        "signals_used": used,
        # Tool-change counts/durations are NOT computed — say so rather than fake it.
        "estimated_note": "Recommendation is estimated from color count and model complexity, not an exact tool-change count or print time.",
    }
