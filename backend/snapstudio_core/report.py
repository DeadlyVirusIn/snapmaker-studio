from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RepairOutcome:
    mode: str
    report: dict
    preserved: bool | None = None


def write_fix_report(path, entries: list[dict]) -> None:
    Path(path).write_text(json.dumps(entries, indent=2, ensure_ascii=False), "utf-8")
