from __future__ import annotations
import json, shutil, sys
from pathlib import Path
import click
from snapstudio_core.container import ThreeMF
from snapstudio_core.detect import detect_source
from snapstudio_core.fingerprint import compute_fingerprint
from snapstudio_core.filaments import parse_remap
from snapstudio_core.repair import repair as do_repair
from snapstudio_core.validate import validate as do_validate
from snapstudio_core.doctor import diagnose_path as do_diagnose_path
from snapstudio_core.diff import diff_projects as do_diff
from snapstudio_core.report import write_fix_report
from snapstudio_core.errors import SnapStudioError

@click.group()
def cli(): ...

@cli.command()
@click.argument("path", type=click.Path(exists=True))
def inspect(path):
    tm = ThreeMF.open(path)
    src = detect_source(tm)
    fp = compute_fingerprint(tm)
    click.echo(f"source: {src.family}  printer_model: {src.printer_model}  u1: {src.is_u1}")
    click.echo(f"objects: {fp.object_count}  plates: {fp.plate_count}  filaments: {fp.filament_count}")
    click.echo(f"painted_triangles: {sum(fp.painted_triangles.values())}")
    click.echo(f"filament colors: {list(fp.filament_colors)}")

def _run_repair(path, mode, remap, out, dry_run, opt_profile=None):
    if Path(path).suffix.lower() == ".stl":
        from snapstudio_core.stl_wrap import wrap_stl
        if dry_run:
            click.echo("DRY RUN - would wrap STL into U1 3MF; no files written"); return
        tm = wrap_stl(path)
        out_p = Path(out) if out else Path(path).with_name(Path(path).stem + "_SnapmakerU1.3mf")
        tm.save(out_p)
        res = do_validate(ThreeMF.open(out_p), against=None)   # generation -> structural+rules
        write_fix_report(out_p.parent / "FIX_REPORT.json",
                         [{"file": Path(path).name, "output": out_p.name, "source": "stl",
                           "generated": True, "validated_ok": res.ok, "errors": res.errors}])
        click.echo(f"wrapped STL -> {out_p}  (validated_ok={res.ok})")
        return
    src = Path(path)
    tm = ThreeMF.open(src)
    src_fp = compute_fingerprint(tm)
    outcome = do_repair(tm, mode=mode, remap=parse_remap(remap), dry_run=dry_run,
                        opt_profile=opt_profile)
    if dry_run:
        click.echo("DRY RUN - no files written")
        click.echo(str(outcome.report)); return
    backup = src.with_suffix(".orig.3mf")
    if not backup.exists(): shutil.copy2(src, backup)
    out = Path(out) if out else src.with_name(src.stem + "_SnapmakerU1.3mf")
    tm.save(out)
    res = do_validate(ThreeMF.open(out), against=src_fp)
    entry = {"file": src.name, "output": out.name, **outcome.report,
             "validated_ok": res.ok, "errors": res.errors}
    write_fix_report(out.parent / "FIX_REPORT.json", [entry])
    click.echo(f"wrote {out}  (validated_ok={res.ok})")

@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--mode", type=click.Choice(["safe","u1","optimize"]), default="u1")
@click.option("--remap", default=None, help='e.g. "5:1,4:3"')
@click.option("-o", "--out", default=None)
@click.option("--dry-run", is_flag=True)
@click.option("--opt-profile", default=None,
              help="optimization profile name (optimize mode only), e.g. u1_fast_prime_tower")
def repair(path, mode, remap, out, dry_run, opt_profile):
    try:
        _run_repair(path, mode, remap, out, dry_run, opt_profile)
    except SnapStudioError as e:
        raise click.ClickException(str(e))

@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--against", type=click.Path(exists=True), default=None)
def validate(path, against):
    tm = ThreeMF.open(path)
    fp = compute_fingerprint(ThreeMF.open(against)) if against else None
    res = do_validate(tm, against=fp)
    click.echo(f"ok={res.ok} structural={res.structural_ok} rules={res.rules_ok} preservation={res.preservation_ok}")
    for e in res.errors: click.echo(f"  - {e}")
    if not res.ok: sys.exit(1)

@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True)
@click.option("--opt-profile", default=None,
              help="optimization profile name, e.g. u1_fast_prime_tower")
def optimize(path, dry_run, opt_profile):
    try:
        _run_repair(path, "optimize", None, None, dry_run, opt_profile)
    except SnapStudioError as e:
        raise click.ClickException(str(e))

_PROJECT_TYPE = {"bambu-family": "Bambu/Orca project", "stl": "STL model", "unknown": "unknown"}

@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="machine-readable output")
def doctor(path, as_json):
    """Check whether a file will load cleanly on a Snapmaker U1, and what to do if not."""
    d = do_diagnose_path(path)
    if as_json:
        click.echo(json.dumps(d.to_dict(), indent=2, ensure_ascii=False))
    else:
        score = "n/a" if d.score is None else f"{d.score}/100"
        click.echo(f"Diagnosis: {Path(path).name}\n")
        click.echo(f"  Verdict : {d.verdict}")
        click.echo(f"  Score   : {score}\n")
        click.echo(f"  Project type           : {_PROJECT_TYPE.get(d.family, d.family)}")
        if d.input_type == "3mf":
            click.echo(f"  Snapmaker U1 compatible : {'yes' if d.is_u1 else 'no'}")
            click.echo(f"  Objects / plates        : {d.object_count} / {d.plate_count}")
            click.echo(f"  Filaments               : {d.filament_count}")
            click.echo(f"  Painted model           : {'yes' if d.painted else 'no'}")
            if d.validation_issues:
                click.echo("  File structure          :")
                for i in d.validation_issues: click.echo(f"    - {i}")
            if d.compatibility_issues:
                click.echo("  U1 compatibility        :")
                for i in d.compatibility_issues: click.echo(f"    - {i}")
            if not d.validation_issues and not d.compatibility_issues:
                click.echo("  Issues                  : none")
        click.echo(f"\nRecommended action: {d.recommended_action}")
        click.echo("Read-only check - no files were modified.")
    sys.exit(0 if d.verdict == "READY" else 1)

@cli.command()
@click.argument("file_a", type=click.Path(exists=True))
@click.argument("file_b", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="machine-readable output")
def diff(file_a, file_b, as_json):
    """Compare two projects: what changed between FILE_A and FILE_B (read-only)."""
    d = do_diff(ThreeMF.open(file_a), ThreeMF.open(file_b))
    if as_json:
        click.echo(json.dumps(d.to_dict(), indent=2, ensure_ascii=False))
        return
    click.echo(f"Diff: {Path(file_a).name} -> {Path(file_b).name}\n")
    click.echo(f"  Structure : +{len(d.parts_added)} parts / -{len(d.parts_removed)}")
    for n in d.parts_added: click.echo(f"    + {n}")
    for n in d.parts_removed: click.echo(f"    - {n}")
    click.echo(f"  Geometry  : {'changed' if d.geometry_changed else 'unchanged'}")
    click.echo(f"  Objects {d.object_count[0]}->{d.object_count[1]}  "
               f"Plates {d.plate_count[0]}->{d.plate_count[1]}  "
               f"Filaments {d.filament_count[0]}->{d.filament_count[1]}")
    click.echo(f"  Painting  : {d.painted_triangles[0]} -> {d.painted_triangles[1]} painted triangles")
    click.echo(f"  Settings  : {len(d.settings_changed)} changed, "
               f"{len(d.settings_added)} added, {len(d.settings_removed)} removed")
    for c in d.settings_changed[:12]:
        click.echo(f"    {c['key']}: {str(c['old'])[:32]!r} -> {str(c['new'])[:32]!r}")
    if len(d.settings_changed) > 12:
        click.echo(f"    ... +{len(d.settings_changed) - 12} more (use --json for the full list)")
    if not d.has_changes:
        click.echo("\nNo differences.")
