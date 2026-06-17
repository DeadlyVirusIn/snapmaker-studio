from __future__ import annotations
import json
from importlib.resources import files

def load_rules() -> dict:
    return json.loads((files("snapstudio_core.data") / "u1_rules.json").read_text("utf-8"))

def apply_clamps(cfg: dict, rules: dict) -> list[dict]:
    findings = []
    for c in rules["clamps"]:
        k = c["key"]
        if k in cfg and str(cfg[k]) == c["bad"]:
            findings.append({"key": k, "old": cfg[k], "new": c["good"]})
            cfg[k] = c["good"]
    return findings
