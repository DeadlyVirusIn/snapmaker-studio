"""Which U1 process preset actually describes this project.

Studio's prepare step preserves the creator's layer height — that is the whole
point of preserve mode. But it also stamped one fixed preset name onto every
project, so a 0.12 mm project came out labelled *0.20 Standard*. The settings were
right and the label was wrong, which is worse than either: Snapmaker Orca then
shows a preset name that does not describe the project, and the difference surfaces
as a "customised preset" notice with no explanation.

This picks the preset name that matches the layer height the project actually
uses, so the label tells the truth.

It is deliberately narrow. It does **not** pull settings out of a base profile the
way a converter would — that would overwrite creator intent, which Studio does not
do. It changes a name, and only when a name genuinely fits:

* the layer height must match a known U1 system preset within a small tolerance,
* the nozzle must be one the U1 ships,
* otherwise the project keeps its existing identity and the conversion reports
  that Orca will show it as a customised preset, which is the truth.

Preset names follow Snapmaker Orca's own published naming for the U1 process
profiles (``"<layer> Standard @Snapmaker U1 (<nozzle> nozzle)"``). Studio does not
invent a name for a layer height that has no system preset.
"""
from __future__ import annotations

SCHEMA_VERSION = "preset/1"

# Layer heights the U1's system process presets are published at, and the nozzle
# variants they exist for. A project that does not land on one of these is a
# customised preset by definition, and Studio says so rather than mislabelling it.
SYSTEM_LAYER_HEIGHTS = (0.08, 0.12, 0.16, 0.20, 0.24, 0.28)
SYSTEM_NOZZLES = ("0.2", "0.4", "0.6", "0.8")

DEFAULT_NOZZLE = "0.4"
DEFAULT_LAYER_HEIGHT = 0.20

# A layer height is a float written as text; treat anything within half a micron
# of a system height as that height rather than as a custom value.
TOLERANCE_MM = 0.0005


def _float(value):
    if isinstance(value, list):
        value = value[0] if value else None
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def preset_name(layer_height: float, nozzle: str = DEFAULT_NOZZLE) -> str:
    return f"{layer_height:.2f} Standard @Snapmaker U1 ({nozzle} nozzle)"


def printer_settings_id(nozzle: str = DEFAULT_NOZZLE) -> str:
    return f"Snapmaker U1 ({nozzle} nozzle)"


def _match_layer_height(value: float | None) -> float | None:
    if value is None or value <= 0:
        return None
    for candidate in SYSTEM_LAYER_HEIGHTS:
        if abs(value - candidate) <= TOLERANCE_MM:
            return candidate
    return None


def _match_nozzle(cfg: dict) -> str | None:
    raw = cfg.get("nozzle_diameter")
    values = raw if isinstance(raw, list) else [raw]
    seen = {str(v).strip() for v in values if str(v).strip()}
    if len(seen) != 1:
        # Mixed nozzle sizes are a real configuration, but no single system preset
        # describes them, so there is no honest name to stamp.
        return None
    nozzle = next(iter(seen))
    try:
        normalised = f"{float(nozzle):.1f}"
    except ValueError:
        return None
    return normalised if normalised in SYSTEM_NOZZLES else None


def choose(cfg: dict) -> dict:
    """Pick the preset identity that describes this project.

    Returns ``{"matched": bool, "print_settings_id", "printer_settings_id",
    "printer_variant", "layer_height", "nozzle", "reason"}``. When ``matched`` is
    False the caller must keep the project's existing identity and surface
    ``reason`` to the user.
    """
    layer_height = _match_layer_height(_float(cfg.get("layer_height")))
    nozzle = _match_nozzle(cfg)

    if layer_height is None:
        raw = _float(cfg.get("layer_height"))
        return {
            "schema_version": SCHEMA_VERSION,
            "matched": False,
            "layer_height": raw,
            "nozzle": nozzle,
            "reason": (
                f"This project prints at {raw:g} mm layers, which is not one of the U1's "
                "system presets, so Snapmaker Orca will show it as a customised preset. "
                "Your layer height is unchanged."
                if raw else
                "This project does not record a layer height, so Studio kept the default "
                "U1 preset name."),
        }
    if nozzle is None:
        return {
            "schema_version": SCHEMA_VERSION,
            "matched": False,
            "layer_height": layer_height,
            "nozzle": None,
            "reason": ("This project does not use a single standard U1 nozzle size, so no "
                       "system preset describes it. Snapmaker Orca will show it as a "
                       "customised preset."),
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "matched": True,
        "layer_height": layer_height,
        "nozzle": nozzle,
        "print_settings_id": preset_name(layer_height, nozzle),
        "printer_settings_id": printer_settings_id(nozzle),
        "printer_variant": nozzle,
        "reason": (f"matched to the U1 system preset for {layer_height:.2f} mm layers on a "
                   f"{nozzle} mm nozzle"),
    }
