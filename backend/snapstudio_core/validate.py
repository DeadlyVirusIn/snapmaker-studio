from __future__ import annotations
from dataclasses import dataclass, field
from .container import ThreeMF
from .config_io import load_project_settings
from .rules import load_rules
from .fingerprint import Fingerprint, compute_fingerprint

REQUIRED = ["[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"]

@dataclass
class ValidationResult:
    structural_ok: bool
    rules_ok: bool
    preservation_ok: bool | None
    errors: list = field(default_factory=list)
    @property
    def ok(self) -> bool:
        return self.structural_ok and self.rules_ok and (self.preservation_ok is not False)

def validate(tm: ThreeMF, against: Fingerprint | None) -> ValidationResult:
    errors = []
    parts = set(tm.list_parts())
    structural_ok = all(r in parts for r in REQUIRED)
    if not structural_ok:
        errors += [f"missing required part: {r}" for r in REQUIRED if r not in parts]

    rules_ok = True
    if "Metadata/project_settings.config" in parts:
        cfg = load_project_settings(tm.read_part("Metadata/project_settings.config"))
        for c in load_rules()["clamps"]:
            if c["key"] in cfg and str(cfg[c["key"]]) == c["bad"]:
                rules_ok = False
                errors.append(f"bad value remains: {c['key']}={c['bad']}")

    preservation_ok = None
    if against is not None:
        now = compute_fingerprint(tm)
        if now.object_part_sha256 != against.object_part_sha256:
            preservation_ok = False; errors.append("object .model bytes changed")
        elif (now.object_count, now.plate_count) != (against.object_count, against.plate_count):
            preservation_ok = False; errors.append("object/plate count changed")
        elif now.filament_count < against.filament_count:
            preservation_ok = False; errors.append("filament count reduced")
        else:
            preservation_ok = True
    return ValidationResult(structural_ok, rules_ok, preservation_ok, errors)
