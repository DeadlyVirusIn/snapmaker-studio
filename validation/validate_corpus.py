"""Real-world conversion validator.

Runs the Snapmaker Studio engine over a corpus of real Bambu/Orca/STL files and
measures how reliably they convert to clean Snapmaker U1 projects. For each input
it converts a TEMP copy (the source directory is never touched), runs Doctor on
the output, and records the result. Failures are root-caused into categories.

Usage:
    python validation/validate_corpus.py --input "D:/STL Files" --report validation/report.md

Inputs are referenced by path, never copied into the repo (they are large and
often personal). Only the validator and the generated report.md are tracked.
"""
from __future__ import annotations
import argparse
import json
import shutil
import tempfile
import traceback
import zipfile
from pathlib import Path

from snapstudio_core.convert import convert_to_u1
from snapstudio_core.doctor import diagnose_path
from snapstudio_core.config_io import load_project_settings
from snapstudio_core.u1_identity import find_foreign

SETTINGS = "Metadata/project_settings.config"
# Skip already-converted / backup / sample artifacts so we only test real inputs.
SKIP_SUBSTR = ("_snapmakeru1", "_fixed", ".orig", "stock_u1", "_u1.", "sample")
# Skip whole directories of generated output / repo / dependencies.
SKIP_DIRS = {"snapmaker-studio", "snapmaker-studio-public", "validation-out",
             "sample", ".git", "node_modules", "target", "dist", "__pycache__"}

CATEGORIES = ("Identity", "Filament", "Preset", "Geometry", "Thumbnail",
              "Slice metadata", "Geometry-only 3MF", "Unknown")


def _is_input(p: Path) -> bool:
    name = p.name.lower()
    if p.suffix.lower() not in (".3mf", ".stl"):
        return False
    if any(s in name for s in SKIP_SUBSTR):
        return False
    return not any(part.lower() in SKIP_DIRS for part in p.parts)


def _src_info(path: Path) -> dict:
    """Classify the source: family, colour count, custom-preset flag, size."""
    size_mb = round(path.stat().st_size / 1e6, 1)
    non_english = any(ord(c) > 127 for c in path.name)
    info = {"size_mb": size_mb, "family": "stl", "filament_count": 0,
            "custom_preset": False, "multicolor": False,
            "large": size_mb >= 50, "non_english": non_english}
    if path.suffix.lower() != ".3mf":
        return info
    try:
        z = zipfile.ZipFile(path)
        names = set(z.namelist())
        if SETTINGS in names:
            cfg = load_project_settings(z.read(SETTINGS))
            pm = str(cfg.get("printer_model", ""))
            # Distinguish Bambu vs OrcaSlicer vs U1 by printer identity.
            if pm == "Snapmaker U1":
                info["family"] = "u1"
            elif "bambu" in pm.lower():
                info["family"] = "bambu"
            elif pm:
                info["family"] = "orca"
            else:
                info["family"] = "3mf"
            n = len(cfg.get("filament_colour", []))
            info["filament_count"] = n
            info["multicolor"] = n > 1
            dsts = cfg.get("different_settings_to_system") or []
            info["custom_preset"] = any(isinstance(s, str) and s for s in dsts)
        elif any(p.startswith("Metadata/Slic3r") for p in names):
            info["family"] = "prusa(geometry)"
        else:
            info["family"] = "geometry-3mf"
    except Exception:
        info["family"] = "unreadable"
    return info


def _categorize(error: str, out_path: str | None, doctor: dict | None) -> str:
    if error:
        e = error.lower()
        if "partnotfound" in e and "project_settings" in e:
            return "Geometry-only 3MF"
        if "stl" in e or "mesh" in e or "geometry" in e or "object" in e:
            return "Geometry"
        return "Unknown"
    issues = " ".join((doctor or {}).get("compatibility_issues", [])
                      + (doctor or {}).get("validation_issues", [])).lower()
    try:
        z = zipfile.ZipFile(out_path)
        cfg = load_project_settings(z.read(SETTINGS)) if SETTINGS in z.namelist() else {}
        if find_foreign(cfg):
            return "Identity"
        if "Metadata/slice_info.config" in z.namelist():
            si = z.read("Metadata/slice_info.config").decode("utf-8", "replace")
            if "02.05" in si:
                return "Slice metadata"
    except Exception:
        pass
    if "filament" in issues and "inconsistent" in issues:
        return "Filament"
    if "preset" in issues:
        return "Preset"
    if "object" in issues or "geometry" in issues or "plate" in issues:
        return "Geometry"
    if "thumbnail" in issues:
        return "Thumbnail"
    return "Unknown"


def validate_one(src: Path, workdir: Path) -> dict:
    row = {"file": src.name, **_src_info(src),
           "success": False, "error": "", "before_verdict": None,
           "doctor_verdict": None, "doctor_score": None, "validated_ok": None,
           "out_size_mb": None, "out_filament_count": None, "category": None}
    try:
        row["before_verdict"] = diagnose_path(str(src)).verdict
    except Exception:
        pass
    try:
        # Convert a temp COPY so the source directory is never written to.
        copy = workdir / src.name
        shutil.copy2(src, copy)
        res = convert_to_u1(str(copy), out_dir=str(workdir))
        d = diagnose_path(res.output_path).to_dict()
        out = Path(res.output_path)
        row.update(
            success=True,
            validated_ok=res.validated_ok,
            doctor_verdict=d.get("verdict"),
            doctor_score=d.get("score"),
            out_size_mb=round(out.stat().st_size / 1e6, 1),
            out_filament_count=d.get("filament_count"),
        )
        ok = res.validated_ok and d.get("verdict") == "READY"
        if not ok:
            row["category"] = _categorize("", res.output_path, d)
            row["error"] = "; ".join(d.get("compatibility_issues", [])[:3]) or "not READY"
    except Exception as e:
        row["error"] = f"{type(e).__name__}: {e}"
        row["category"] = _categorize(row["error"], None, None)
        row["_trace"] = traceback.format_exc()
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="directory to scan")
    ap.add_argument("--report", default="validation/report.md")
    ap.add_argument("--limit", type=int, default=0, help="cap number of files (0 = all)")
    ap.add_argument("--recursive", action="store_true", default=True,
                    help="scan subdirectories (default on; SKIP_DIRS are excluded)")
    args = ap.parse_args()

    walker = Path(args.input).rglob("*") if args.recursive else Path(args.input).glob("*")
    inputs = sorted({p for p in walker if _is_input(p)})
    if args.limit:
        inputs = inputs[:args.limit]

    rows = []
    with tempfile.TemporaryDirectory() as td:
        for i, src in enumerate(inputs, 1):
            # ASCII-safe progress: Windows consoles are often cp1252 and would
            # crash printing non-ASCII filenames.
            safe = src.name.encode("ascii", "replace").decode("ascii")
            print(f"[{i}/{len(inputs)}] {safe}", flush=True)
            work = Path(td) / f"w{i}"
            work.mkdir()
            rows.append(validate_one(src, work))
            shutil.rmtree(work, ignore_errors=True)

    clean = [r for r in rows if r["success"] and r["validated_ok"] and r["doctor_verdict"] == "READY"]
    failures = [r for r in rows if r not in clean]
    by_cat = {c: [r for r in failures if r["category"] == c] for c in CATEGORIES}

    lines = ["# Snapmaker U1 Conversion — Real-World Validation", ""]
    rate = (len(clean) / len(rows) * 100) if rows else 0
    lines += [f"**Corpus:** {len(rows)} files  ", f"**Clean (READY + validated):** {len(clean)}  ",
              f"**Failures:** {len(failures)}  ", f"**SUCCESS RATE: {rate:.0f}%**", ""]

    fam = {}
    for r in rows:
        fam[r["family"]] = fam.get(r["family"], 0) + 1
    multi = sum(1 for r in rows if r.get("multicolor"))
    large = sum(1 for r in rows if r.get("large"))
    custom = sum(1 for r in rows if r.get("custom_preset"))
    noneng = sum(1 for r in rows if r.get("non_english"))
    lines += ["## Corpus composition", "",
              "| Family | Count |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in sorted(fam.items(), key=lambda kv: -kv[1])]
    lines += ["", f"- multi-color: {multi}  ", f"- single-color: {len(rows) - multi}  ",
              f"- large (>=50MB): {large}  ", f"- custom-preset: {custom}  ",
              f"- non-English filenames: {noneng}", ""]

    lines += ["## Failures by category", "", "| Category | Count |", "|---|---|"]
    for c in CATEGORIES:
        if by_cat[c]:
            lines.append(f"| {c} | {len(by_cat[c])} |")
    lines.append("")

    lines += ["## Top failure patterns", ""]
    pats = {}
    for r in failures:
        key = (r["category"], (r["error"] or "")[:80])
        pats[key] = pats.get(key, 0) + 1
    for (cat, err), n in sorted(pats.items(), key=lambda kv: -kv[1])[:10]:
        lines.append(f"- **{cat}** x{n}: {err}")
    if not failures:
        lines.append("- none")
    lines.append("")

    lines += ["## Per-file results", "",
              "| File | Family | MB | Filaments | Before | After | Score | Valid | Cat | Notes |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(
            f"| {r['file']} | {r['family']} | {r['size_mb']} | {r['filament_count']} | "
            f"{r['before_verdict']} | {r['doctor_verdict']} | {r['doctor_score']} | "
            f"{r['validated_ok']} | {r['category'] or ''} | {(r['error'] or '')[:60]} |")

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSUCCESS_RATE {rate:.0f}%  CLEAN {len(clean)}/{len(rows)}  FAILURES {len(failures)}")
    print("BY_CATEGORY " + json.dumps({c: len(by_cat[c]) for c in CATEGORIES if by_cat[c]}))
    print(f"REPORT {args.report}")


if __name__ == "__main__":
    main()
