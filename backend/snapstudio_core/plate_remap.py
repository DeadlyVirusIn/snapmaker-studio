"""Per-Plate Filament Remapper — read-only inspection (Commit A).

Maps a Bambu/Orca/Snapmaker 3MF to what the USER actually sees: plates by their
UI number, the objects on each, and the filaments in use. Authoritative mapping is
`Metadata/model_settings.config`:

  <plate><metadata key="plater_id" value="4"/> ... <model_instance><object_id>...

**UI Plate N == the <plate> whose plater_id == N** — NOT object order. A prior
automated fix changed the wrong plate by assuming sequential object IDs; this
module never does that.

Validated against a real 9-plate file (Freedom Torch): Plate 4 -> objects 12,14
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
