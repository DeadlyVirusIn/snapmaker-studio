from __future__ import annotations
import re
from .container import ThreeMF
from .config_io import load_project_settings

# keys that define machine/printer/gcode identity (overwritten on U1 swap)
IDENTITY_RE = re.compile(
    r"^(printer_|machine_|bed_|nozzle|extruder_|gcode_|printable_|"
    r"single_extruder|change_filament_gcode|default_(bed|nozzle)|"
    r"before_layer_change_gcode|layer_change_gcode|wipe_tower|prime_tower_width|prime_volume|"
    r"z_hop|supported_bed_type|curr_bed_type|emit_machine|adaptive_bed)"
)

def extract_profile(u1_3mf, name="Snapmaker U1") -> dict:
    cfg = load_project_settings(ThreeMF.open(u1_3mf).read_part("Metadata/project_settings.config"))
    keys = {k: v for k, v in cfg.items() if IDENTITY_RE.match(k)}
    return {"schema": "u1-profile/1", "name": name,
            "printer_model": cfg.get("printer_model"),
            "nozzle": (cfg.get("nozzle_diameter") or ["0.4"])[0],
            "orca_version": cfg.get("version"),
            "source_file": str(u1_3mf), "keys": keys}
