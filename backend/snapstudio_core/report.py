from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RepairOutcome:
    mode: str
    report: dict
    preserved: bool | None = None


class ReportPathError(ValueError):
    """The requested report output path is unsafe and was refused."""


# Never write a report over a model/source file.
_MODEL_SUFFIXES = {".3mf", ".stl", ".obj", ".step", ".stp", ".gcode", ".zip"}


def write_fix_report(path, entries: list[dict], *, base_dir=None) -> Path:
    """Write the fix report as JSON to ``path``. Returns the written path.

    Safety: the report must be a ``.json`` file, must not overwrite a model/source
    file, and — when ``base_dir`` is given — must resolve inside that directory
    (blocks ``..`` traversal). Raises ``ReportPathError`` on an unsafe path and
    writes nothing.
    """
    p = Path(path)
    if p.suffix.lower() != ".json":
        raise ReportPathError("report path must end in .json")
    if p.suffix.lower() in _MODEL_SUFFIXES:  # defensive; .json is never a model ext
        raise ReportPathError("refusing to overwrite a model/source file")
    resolved = p.resolve()
    if resolved.is_dir():
        raise ReportPathError("report path is a directory")
    if base_dir is not None:
        base = Path(base_dir).resolve()
        if base != resolved.parent and base not in resolved.parents:
            raise ReportPathError("report path escapes the allowed output directory")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(entries, indent=2, ensure_ascii=False), "utf-8")
    return resolved
