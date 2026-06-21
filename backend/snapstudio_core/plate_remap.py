"""Per-Plate Filament Remapper — read-only inspection (Commit A).

Maps a Bambu/Orca/Snapmaker 3MF to what the USER actually sees: plates by their
UI number, the objects on each, and the filaments in use. Authoritative mapping is
`Metadata/model_settings.config`:

  <plate><metadata key="plater_id" value="4"/> ... <model_instance><object_id>...

**UI Plate N == the <plate> whose plater_id == N** — NOT object order. A prior
automated fix changed the wrong plate by assuming sequential object IDs; this
module never does that.

Validated against a real 9-plate multicolor U1 project: Plate 4 -> objects 12,14
(both extruder 6) and Plate 6 -> objects 18,19 (also extruder 6). A naive
"change object N" or "change all filament 6" would hit the wrong plate — only the
plater_id->object_ids scope is correct.

Two defensive facts baked in:
- base filament is the object/part `extruder` in model_settings.config; painted
  accents are per-triangle `paint_color` in the object .model files.
- object .model files can be SHARED across objects/plates, so the remapper (later)
  must rewrite ONLY model_settings object extruder, never the .model meshes/paint.
  That keeps a remap plate-scoped and preserves painted accents by construction.

Strictly READ-ONLY.
"""
from __future__ import annotations
import json
import re
import zipfile

SCHEMA_VERSION = "plateremap/1"

MODEL_SETTINGS = "Metadata/model_settings.config"
SLICE_INFO = "Metadata/slice_info.config"
PROJECT_SETTINGS = "Metadata/project_settings.config"
ROOT_MODEL = "3D/3dmodel.model"


def _read(z, name):
    try:
        return z.read(name).decode("utf-8", "replace")
    except KeyError:
        return None


def _palette(z):
    """filament id (1-based) -> {color, type}. Prefer slice_info; fall back to
    project_settings.config (Orca stores real colours there; slice_info is often
    empty in exported projects)."""
    pal = {}
    si = _read(z, SLICE_INFO)
    if si:
        for m in re.finditer(r'<filament\s+id="(\d+)"\s+type="([^"]*)"\s+color="([^"]*)"', si):
            pal[int(m.group(1))] = {"type": m.group(2), "color": m.group(3)}
    if pal:
        return pal
    ps = _read(z, PROJECT_SETTINGS)
    if ps:
        try:
            cfg = json.loads(ps)
            colours = cfg.get("filament_colour") or cfg.get("filament_color") or []
            types = cfg.get("filament_type") or []
            for i, c in enumerate(colours):
                pal[i + 1] = {"color": c, "type": types[i] if i < len(types) else None}
        except Exception:
            pass
    return pal


def _parse_objects(ms_xml):
    objs = {}
    for ob in re.finditer(r'<object\s+id="(\d+)">(.*?)</object>', ms_xml or "", re.S):
        oid = int(ob.group(1)); body = ob.group(2)
        name = (re.search(r'key="name"\s+value="([^"]*)"', body) or [None, None])[1]
        extr = re.search(r'key="extruder"\s+value="(\d+)"', body)
        parts = []
        for pt in re.finditer(r'<part\s+id="(\d+)"[^>]*>(.*?)</part>', body, re.S):
            pb = pt.group(2)
            pn = (re.search(r'key="name"\s+value="([^"]*)"', pb) or [None, None])[1]
            pe = re.search(r'key="extruder"\s+value="(\d+)"', pb)
            parts.append({"id": int(pt.group(1)), "name": pn,
                          "extruder": int(pe.group(1)) if pe else None})
        objs[oid] = {"name": name, "extruder": int(extr.group(1)) if extr else None, "parts": parts}
    return objs


def _parse_plates(ms_xml):
    plates = []
    for pl in re.finditer(r'<plate>(.*?)</plate>', ms_xml or "", re.S):
        body = pl.group(1)
        pid = re.search(r'key="plater_id"\s+value="(\d+)"', body)
        pname = (re.search(r'key="plater_name"\s+value="([^"]*)"', body) or [None, ""])[1]
        oids = [int(m.group(1)) for m in re.finditer(r'key="object_id"\s+value="(\d+)"', body)]
        plates.append({"ui_number": int(pid.group(1)) if pid else None,
                       "name": pname, "object_ids": oids})
    plates.sort(key=lambda p: (p["ui_number"] is None, p["ui_number"]))
    return plates


def _object_model_paths(root_xml):
    paths = {}
    for ob in re.finditer(r'<object\s+id="(\d+)"[^>]*>(.*?)</object>', root_xml or "", re.S):
        comp = re.search(r'<component[^>]*p:path="([^"]*)"', ob.group(2))
        if comp:
            paths[int(ob.group(1))] = comp.group(1).lstrip("/")
    return paths


def _painted_facets(z, model_path):
    xml = _read(z, model_path)
    if not xml:
        return 0
    return len(re.findall(r'paint_color="', xml))


def dry_run(path: str, ui_plate: int, from_filament: int, to_filament: int) -> dict:
    """Compute exactly what a remap WOULD change — scoped to one UI plate's objects
    whose base filament == from_filament — without writing anything (Commit B).

    Returns a JSON diff: the object-level extruder changes, plus explicit lists of
    what stays untouched (other plates, other filaments, painted accents). Painted
    accents are never in `changes` by design — the writer only touches object base
    extruder in model_settings.config."""
    rep = inspect(path)
    if not rep.get("available"):
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": rep.get("reason", "could not read 3MF")}
    plate = next((p for p in rep["plates"] if p["ui_number"] == ui_plate), None)
    if plate is None:
        nums = [p["ui_number"] for p in rep["plates"]]
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": f"Plate {ui_plate} not found. Plates present: {nums}"}

    warnings = []
    if from_filament == to_filament:
        warnings.append("source and target filament are the same — nothing to do")
    palette = rep.get("filament_palette", {})
    if str(to_filament) not in palette:
        warnings.append(f"target filament {to_filament} is not in this file's palette")

    changes = []
    unchanged_on_plate = []
    for o in plate["objects"]:
        if o.get("base_filament") == from_filament:
            changes.append({"object_id": o["object_id"], "name": o.get("name"),
                            "from_filament": from_filament, "to_filament": to_filament,
                            "painted_facets_preserved": o.get("painted_facets", 0)})
        else:
            unchanged_on_plate.append({"object_id": o["object_id"], "name": o.get("name"),
                                       "base_filament": o.get("base_filament")})

    if not changes:
        on_plate = sorted({o.get("base_filament") for o in plate["objects"] if o.get("base_filament")})
        warnings.append(f"no object on Plate {ui_plate} uses filament {from_filament}; "
                        f"filaments actually on this plate: {on_plate}")

    def _col(fid):
        return palette.get(str(fid), {}).get("color")

    return {
        "schema_version": SCHEMA_VERSION, "available": True, "dry_run": True,
        "ui_plate": ui_plate,
        "from_filament": {"id": from_filament, "color": _col(from_filament)},
        "to_filament": {"id": to_filament, "color": _col(to_filament)},
        "changes": changes,
        "change_count": len(changes),
        "unchanged_objects_on_plate": unchanged_on_plate,
        "untouched_plates": [p["ui_number"] for p in rep["plates"] if p["ui_number"] != ui_plate],
        "untouched_filaments": sorted(int(k) for k in palette if int(k) != from_filament),
        "painted_accents_preserved": True,
        "warnings": warnings,
        "verdict": (f"Plate {ui_plate}: {len(changes)} object(s) would change filament "
                    f"{from_filament} → {to_filament}; all other plates, filaments, and "
                    f"painted accents untouched." if changes else
                    f"No change: nothing on Plate {ui_plate} uses filament {from_filament}."),
    }


def _set_object_extruder(ms_xml: str, obj_id: int, from_f: int, to_f: int):
    """Change ONLY the object-level extruder of <object id=obj_id> from from_f to
    to_f (the metadata before the first <part>). Returns (new_xml, n_changed)."""
    pat = re.compile(r'(<object\s+id="%d">)(.*?)(</object>)' % obj_id, re.S)
    changed = 0

    def repl(m):
        nonlocal changed
        head = m.group(2)
        idx = head.find("<part")
        pre = head if idx < 0 else head[:idx]
        post = "" if idx < 0 else head[idx:]
        new_pre, n = re.subn(r'(key="extruder"\s+value=")%d(")' % from_f,
                             r"\g<1>%d\g<2>" % to_f, pre, count=1)
        changed += n
        return m.group(1) + new_pre + post + m.group(3)

    return pat.subn(repl, ms_xml, count=1)[0], changed


def _entry_bytes(z, name):
    try:
        return z.read(name)
    except KeyError:
        return None


def _verify_export(src_path: str, out_path: str, ui_plate: int,
                   from_f: int, to_f: int, target_ids: list) -> dict:
    """Reopen output and prove ONLY the intended change happened. Every check must
    pass or the export is failed."""
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        return bool(ok)

    src_rep = inspect(src_path)
    out_rep = inspect(out_path)
    chk("output reopens and validates", out_rep.get("available"), out_rep.get("reason", ""))
    if not out_rep.get("available"):
        return {"passed": False, "checks": checks}

    # byte-identity of every zip entry except model_settings.config (decompressed)
    import zipfile
    with zipfile.ZipFile(src_path) as zs, zipfile.ZipFile(out_path) as zo:
        sn, on = set(zs.namelist()), set(zo.namelist())
        chk("zip entry list unchanged", sn == on, f"+{on-sn} -{sn-on}")
        differing = []
        for n in sorted(sn & on):
            if _entry_bytes(zs, n) != _entry_bytes(zo, n):
                differing.append(n)
        chk("only model_settings.config differs", differing == [MODEL_SETTINGS],
            f"differing entries: {differing}")
        # mesh/paint files byte-identical
        meshes = [n for n in sn if n.startswith("3D/")]
        mesh_ok = all(_entry_bytes(zs, n) == _entry_bytes(zo, n) for n in meshes)
        chk("mesh + paint (.model) byte-identical", mesh_ok)

    src_plates = {p["ui_number"]: p for p in src_rep["plates"]}
    out_plates = {p["ui_number"]: p for p in out_rep["plates"]}

    # exactly the target objects changed, from_f -> to_f
    changed_ids, wrong = [], []
    for pn, sp in src_plates.items():
        op = out_plates.get(pn, {})
        so = {o["object_id"]: o for o in sp["objects"]}
        oo = {o["object_id"]: o for o in op.get("objects", [])}
        for oid, sobj in so.items():
            ob = oo.get(oid, {})
            if sobj.get("base_filament") != ob.get("base_filament"):
                changed_ids.append(oid)
                if not (oid in target_ids and sobj.get("base_filament") == from_f
                        and ob.get("base_filament") == to_f):
                    wrong.append(oid)
            # painted facets must never change
            so_p = {o["object_id"]: o.get("painted_facets") for o in sp["objects"]}
            if oid in oo and oo[oid].get("painted_facets") != so_p.get(oid):
                wrong.append(("paint", oid))
    chk("changed objects == dry-run targets", sorted(set(changed_ids)) == sorted(set(target_ids)),
        f"changed={sorted(set(changed_ids))} expected={sorted(set(target_ids))}")
    chk("every change is from %d -> %d (no wrong/paint change)" % (from_f, to_f), not wrong,
        f"violations: {wrong}")

    # all non-target plates identical (objects' base filaments + painted)
    untouched_ok = True
    for pn, sp in src_plates.items():
        if pn == ui_plate:
            continue
        op = out_plates.get(pn, {})
        sig_s = [(o["object_id"], o.get("base_filament"), o.get("painted_facets")) for o in sp["objects"]]
        sig_o = [(o["object_id"], o.get("base_filament"), o.get("painted_facets")) for o in op.get("objects", [])]
        if sig_s != sig_o:
            untouched_ok = False
    chk("all other plates unchanged (e.g. Plate 6)", untouched_ok)

    return {"passed": all(c["pass"] for c in checks), "checks": checks,
            "changed_objects": sorted(set(changed_ids))}


def export_remap(path: str, ui_plate: int, from_filament: int, to_filament: int,
                 out_path: str = None) -> dict:
    """Commit C: safe per-plate remap export. Dry-runs first, refuses on blocking
    warnings, writes a NEW file (never the source) changing only the target objects'
    object-level extruder in model_settings.config, then verifies — quarantining the
    output if any check fails."""
    import os
    import shutil
    import zipfile

    dr = dry_run(path, ui_plate, from_filament, to_filament)
    if not dr.get("available"):
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "passed": False, "reason": dr.get("reason"), "dry_run": dr}
    if dr.get("warnings") or dr.get("change_count", 0) == 0:
        return {"schema_version": SCHEMA_VERSION, "available": True, "passed": False,
                "reason": "refusing to write: dry-run has blocking warnings or no changes",
                "dry_run": dr}

    target_ids = [c["object_id"] for c in dr["changes"]]

    if not out_path:
        stem, ext = os.path.splitext(path)
        out_path = f"{stem}_plate{ui_plate}_f{from_filament}_to_f{to_filament}{ext or '.3mf'}"
    if os.path.abspath(out_path) == os.path.abspath(path):
        return {"schema_version": SCHEMA_VERSION, "available": True, "passed": False,
                "reason": "output path must differ from source (never mutate original)"}

    # copy every entry verbatim; rewrite only model_settings.config
    with zipfile.ZipFile(path) as zin:
        ms = zin.read(MODEL_SETTINGS).decode("utf-8")
        new_ms = ms
        total = 0
        for oid in target_ids:
            new_ms, n = _set_object_extruder(new_ms, oid, from_filament, to_filament)
            total += n
        if total != len(target_ids):
            return {"schema_version": SCHEMA_VERSION, "available": True, "passed": False,
                    "reason": f"could not edit all targets ({total}/{len(target_ids)}) — aborted, nothing written"}
        tmp = out_path + ".part"
        try:
            with zipfile.ZipFile(tmp, "w") as zout:
                for item in zin.infolist():
                    data = (new_ms.encode("utf-8") if item.filename == MODEL_SETTINGS
                            else zin.read(item.filename))
                    zout.writestr(item, data)
            os.replace(tmp, out_path)
        except Exception as e:
            if os.path.exists(tmp):
                os.remove(tmp)
            return {"schema_version": SCHEMA_VERSION, "available": True, "passed": False,
                    "reason": f"write failed: {e}"}

    verification = _verify_export(path, out_path, ui_plate, from_filament, to_filament, target_ids)
    if not verification["passed"]:
        quarantine = out_path + ".rejected"
        try:
            os.replace(out_path, quarantine)
        except Exception:
            quarantine = None
            if os.path.exists(out_path):
                os.remove(out_path)
        return {"schema_version": SCHEMA_VERSION, "available": True, "passed": False,
                "reason": "verification gate FAILED — output quarantined, original untouched",
                "quarantined": quarantine, "verification": verification, "dry_run": dr}

    return {"schema_version": SCHEMA_VERSION, "available": True, "passed": True,
            "output_path": out_path,
            "changed_objects": dr["changes"],
            "from_filament": from_filament, "to_filament": to_filament,
            "ui_plate": ui_plate,
            "untouched_plates": dr["untouched_plates"],
            "verification": verification, "warnings": [],
            "verdict": f"Plate {ui_plate}: filament {from_filament} -> {to_filament} on "
                       f"{len(target_ids)} object(s); verified only those changed."}


def inspect(path: str) -> dict:
    """Read-only report: plates by UI number, their objects, and filaments used."""
    try:
        z = zipfile.ZipFile(path)
    except Exception as e:
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": f"not a readable 3MF/zip: {e}"}
    with z:
        ms = _read(z, MODEL_SETTINGS)
        if not ms:
            return {"schema_version": SCHEMA_VERSION, "available": False,
                    "reason": "no model_settings.config — not a Bambu/Orca-style 3MF"}
        palette = _palette(z)
        objects = _parse_objects(ms)
        plates = _parse_plates(ms)
        model_paths = _object_model_paths(_read(z, ROOT_MODEL))

        warnings = []
        out = []
        for pl in plates:
            objs_out = []
            base_fids = set()
            painted_present = False
            for oid in pl["object_ids"]:
                o = objects.get(oid, {})
                base = o.get("extruder")
                part_fids = [p["extruder"] for p in o.get("parts", []) if p.get("extruder")]
                if base:
                    base_fids.add(base)
                base_fids.update(part_fids)
                pf = _painted_facets(z, model_paths.get(oid, ""))
                if pf:
                    painted_present = True
                objs_out.append({"object_id": oid, "name": o.get("name"),
                                 "base_filament": base, "part_filaments": part_fids,
                                 "painted_facets": pf})
            if pl["ui_number"] is None:
                warnings.append("a plate has no plater_id; excluded from remap (UI mapping uncertain)")
            filaments_used = [{"id": fid,
                               "color": palette.get(fid, {}).get("color"),
                               "type": palette.get(fid, {}).get("type"),
                               "role": "base"} for fid in sorted(base_fids)]
            out.append({"ui_number": pl["ui_number"], "name": pl["name"],
                        "objects": objs_out, "filaments_used": filaments_used,
                        "painted_accents_present": painted_present})
        return {"schema_version": SCHEMA_VERSION, "available": True,
                "filament_palette": {str(k): v for k, v in palette.items()},
                "plate_count": len(out), "plates": out, "warnings": warnings}
