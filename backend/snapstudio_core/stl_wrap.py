from __future__ import annotations
import copy, json, re, uuid
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape


#: What Snapmaker Orca writes for an object nobody has assigned to a filament.
#: Not slot zero — the absence of a choice, said in the target's own words.
UNASSIGNED = 0


def _attr(value: str) -> str:
    """Escape a string for safe use inside an XML attribute value."""
    return _xml_escape(value, {'"': "&quot;"})
from importlib.resources import files
from .container import ThreeMF
from .config_io import dump_project_settings
from .stl_io import parse_stl
from .filaments import PER_FILAMENT_KEYS
from .assignments import _NOT_AN_OVERRIDE
from . import overrides as object_overrides

BED_CENTER = (135.5, 136.0)   # from U1 printable_area 0.5x1..270.5x271
SNAPMAKER_FILAMENT = "Snapmaker PLA SnapSpeed @U1"   # U1 filament preset
DEFAULT_COLORS = ("#FFFFFFFF",)                      # default single colour (STL carries no colour data)
MIN_FILAMENTS = 4             # minimum filament slots in a U1 project
PAD_COLOUR = "#FFFFFFFF"      # unused padding slots


def effective_colours(colours) -> list:
    """Pad the colour list up to MIN_FILAMENTS slots; counts above the minimum are
    kept as-is (never capped)."""
    c = list(colours)
    while len(c) < MIN_FILAMENTS:
        c.append(PAD_COLOUR)
    return c


#: How many logical filaments a prepared project may declare. Snapmaker Orca
#: keeps a part on slot N whenever N is within the project's declared filament
#: count, and discards the assignment to unassigned when it is not — measured
#: across a ten-cell matrix against Orca 2.3.5: with four declared, slots 1 and 4
#: survived and 5 and 6 came back 0; with five declared, 5 survived and 6 did not;
#: with six declared, all of 4, 5 and 6 survived. The four physical nozzles never
#: changed, and neither did the bed. Logical filaments and toolheads are separate
#: things, and this is the logical one.
MAX_DECLARED_FILAMENTS = 16


def slots_referenced(src, model: bytes) -> int:
    """The highest logical filament slot anything in the source refers to.

    Object assignments, the volumes underneath them and painted colour all name
    slots, and a prepared copy that declares fewer than the largest of them hands
    Snapmaker Orca a reference it will silently drop.
    """
    from . import multipart, painted_color

    highest = 0
    for stated in (source_assignments(src) or {}).values():
        for slot in [stated.get("extruder")] + list(stated.get("volume_extruders") or []):
            if isinstance(slot, int) and slot > highest:
                highest = slot

    config = "Metadata/Slic3r_PE_model.config"
    if src.has_part(config):
        try:
            volumes_by_object = multipart.source_volumes(
                src.read_part(config).decode("utf-8", "ignore"))
        except Exception:
            volumes_by_object = {}
        for volumes in volumes_by_object.values():
            for volume in volumes:
                slot = volume.get("slot")
                if isinstance(slot, int) and slot > highest:
                    highest = slot

    try:
        painted = painted_color.read_container(src)
    except Exception:
        painted = {}
    for slot in painted.get("slots_referenced") or ():
        if isinstance(slot, int) and slot > highest:
            highest = slot

    return min(highest, MAX_DECLARED_FILAMENTS)


def filaments_in_use(src, model: bytes) -> int:
    """How many different filaments this plate will actually print with.

    Not how many slots it declares. A U1 project always declares at least four,
    and a single-colour print uses one of them — and that difference decides
    whether Snapmaker Orca builds a prime tower, which decides whether a
    per-object layer height is allowed. Measured: two cubes on filaments 1 and 2
    with a per-object layer height would not slice; the same two cubes both on
    filament 1, in a project declaring the same four slots, sliced normally.

    An object nobody assigned still prints, on the project's first filament, so
    it counts as one.
    """
    from . import multipart, painted_color

    used: set[int] = set()
    unassigned = False
    for stated in (source_assignments(src) or {}).values():
        slot = stated.get("extruder")
        if isinstance(slot, int) and slot > 0:
            used.add(slot)
        else:
            unassigned = True
        for slot in stated.get("volume_extruders") or ():
            if isinstance(slot, int) and slot > 0:
                used.add(slot)

    config = "Metadata/Slic3r_PE_model.config"
    if src.has_part(config):
        try:
            volumes_by_object = multipart.source_volumes(
                src.read_part(config).decode("utf-8", "ignore"))
        except Exception:
            volumes_by_object = {}
        for volumes in volumes_by_object.values():
            for volume in volumes:
                slot = volume.get("slot")
                if isinstance(slot, int) and slot > 0:
                    used.add(slot)

    try:
        painted = painted_color.read_container(src)
    except Exception:
        painted = {}
    # `slots_referenced` is every slot the project declares, which is four or
    # more on any U1 file whether anything is painted or not. What counts here is
    # the slots painting actually puts on the plate.
    for entry in painted.get("slots") or ():
        if isinstance(entry, dict) and entry.get("from_painting"):
            slot = entry.get("slot")
            if isinstance(slot, int) and slot > 0:
                used.add(slot)

    if unassigned:
        used.add(1)
    return max(1, len(used))


def declared_colours(colours, needed: int) -> list:
    """The colour list a copy must declare to keep every slot the source names.

    The extra entries are padding and say so: the source gave no colour, vendor or
    material for them, and inventing one would be a claim about a spool nobody
    mentioned. What they buy is that the assignment survives being opened.
    """
    out = effective_colours(colours)
    while len(out) < needed:
        out.append(PAD_COLOUR)
    return out


def _filament_maps(count: int) -> str:
    """One entry per declared filament, all in the first group.

    Snapmaker Orca writes `1 1 1 1` for four filaments and `1 1 1 1 1 1` for six;
    a single `1` against six filaments is a shorter statement than the project it
    describes.
    """
    return " ".join(["1"] * max(1, count))

_PROD_NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
            'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
            'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" '
            'requiredextensions="p"')

CONTENT_TYPES = (b'<?xml version="1.0" encoding="UTF-8"?>\n'
  b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
  b'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
  b'<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
  b'</Types>')

RELS = (b'<?xml version="1.0" encoding="UTF-8"?>\n'
  b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
  b'<Relationship Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" '
  b'Target="/3D/3dmodel.model"/></Relationships>')

OBJECT_RELS = (b'<?xml version="1.0" encoding="UTF-8"?>\n'
  b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
  b'<Relationship Target="/3D/Objects/object_1.model" Id="rel-1" '
  b'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')


def bed_center_transform(verts) -> list:
    xs = [v[0] for v in verts]; ys = [v[1] for v in verts]; zs = [v[2] for v in verts]
    cx = (min(xs) + max(xs)) / 2; cy = (min(ys) + max(ys)) / 2
    tx = BED_CENTER[0] - cx; ty = BED_CENTER[1] - cy; tz = -min(zs)
    return [1, 0, 0, 0, 1, 0, 0, 0, 1, tx, ty, tz]


def _f(v) -> str:
    return repr(float(v))


def _mesh_xml(verts, tris) -> str:
    out = ['<mesh><vertices>']
    out += [f'<vertex x="{_f(x)}" y="{_f(y)}" z="{_f(z)}"/>' for (x, y, z) in verts]
    out.append('</vertices><triangles>')
    out += [f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for (a, b, c) in tris]
    out.append('</triangles></mesh>')
    return "".join(out)


def build_object_model_xml(verts, tris, obj_uuid: str) -> bytes:
    # 3D/Objects/object_1.model: the raw mesh as object id=1 (geometry preserved verbatim)
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            f'<model unit="millimeter" xml:lang="en-US" {_PROD_NS}>'
            '<metadata name="BambuStudio:3mfVersion">1</metadata>'
            f'<resources><object id="1" p:UUID="{obj_uuid}" type="model">'
            f'{_mesh_xml(verts, tris)}</object></resources></model>').encode("utf-8")


def build_root_model_xml(transform, u_obj1, u_obj2, u_comp, u_build, u_item) -> bytes:
    # root 3dmodel.model: object id=2 references the mesh via <component>; build item places it.
    t = " ".join(_f(x) for x in transform)
    meta = "".join(f'<metadata name="{k}"></metadata>' for k in
                   ["Copyright", "CreationDate", "Description", "Designer", "DesignerCover",
                    "DesignerUserId", "License", "ModificationDate", "Origin", "Title"])
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            f'<model unit="millimeter" xml:lang="en-US" {_PROD_NS}>'
            '<metadata name="Application">SnapmakerStudio-u1convert</metadata>'
            '<metadata name="BambuStudio:3mfVersion">1</metadata>' + meta +
            f'<resources><object id="2" p:UUID="{u_obj2}" type="model"><components>'
            f'<component p:path="/3D/Objects/object_1.model" objectid="1" p:UUID="{u_comp}" '
            'transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object></resources>'
            f'<build p:UUID="{u_build}"><item objectid="2" p:UUID="{u_item}" '
            f'transform="{t}" printable="1"/></build></model>').encode("utf-8")


def build_model_settings(name: str = "object", object_id: int = 2, extruder: int = 0) -> bytes:
    # Maps the build object to its plate and filament/extruder slot.
    name = _attr(name)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'
            f'  <object id="{object_id}">\n'
            f'    <metadata key="name" value="{name}"/>\n'
            f'    <metadata key="extruder" value="{extruder}"/>\n'
            '    <part id="1" subtype="normal_part">\n'
            f'      <metadata key="name" value="{name}"/>\n'
            '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
            '      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" '
            'facets_reversed="0" backwards_edges="0"/>\n'
            '    </part>\n  </object>\n'
            '  <plate>\n'
            '    <metadata key="plater_id" value="1"/>\n'
            '    <metadata key="plater_name" value=""/>\n'
            '    <metadata key="locked" value="false"/>\n'
            '    <metadata key="filament_map_mode" value="Auto For Flush"/>\n'
            '    <metadata key="filament_maps" value="1"/>\n'
            '    <model_instance>\n'
            f'      <metadata key="object_id" value="{object_id}"/>\n'
            '      <metadata key="instance_id" value="0"/>\n'
            '    </model_instance>\n  </plate>\n  <assemble>\n  </assemble>\n</config>\n').encode("utf-8")


def build_slice_info(colors) -> bytes:
    rows = "".join(
        f'    <filament id="{i + 1}" type="PLA" color="{c}" used_m="0" used_g="0"/>\n'
        for i, c in enumerate(colors))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n  <header>\n'
            '    <header_item key="X-BBL-Client-Type" value="slicer"/>\n'
            '    <header_item key="X-BBL-Client-Version" value=""/>\n  </header>\n'
            '  <plate>\n' + rows + '  </plate>\n</config>\n').encode("utf-8")


def set_filament_block(cfg: dict, colors) -> dict:
    """Set the project's filament block to N declared colours using the U1 filament preset.
    Every per-filament array is set to length N; the purge structures resize to match
    (matrix N*N, vector N*2). N is arbitrary."""
    n = len(colors)
    for k in PER_FILAMENT_KEYS:
        v = cfg.get(k)
        if isinstance(v, list) and v:
            cfg[k] = [v[0]] * n                     # replicate slot 0 to N
    cfg["filament_colour"] = list(colors)
    cfg["filament_settings_id"] = [SNAPMAKER_FILAMENT] * n
    m = cfg.get("flush_volumes_matrix") or ["0"]
    off = next((x for x in m if str(x) not in ("0",)), "492")   # off-diagonal purge volume
    cfg["flush_volumes_matrix"] = ["0" if i == j else off for i in range(n) for j in range(n)]
    vec = cfg.get("flush_volumes_vector") or ["140", "140"]
    pair = vec[:2] if len(vec) >= 2 else ["140", "140"]
    cfg["flush_volumes_vector"] = pair * n
    return cfg


def _base_settings(colors, profile_name: str = "snapmaker_u1") -> dict:
    # Base template is a complete clean Snapmaker U1 project_settings (printer/process identity
    # already correct). We only set the filament block to the declared colours.
    cfg = json.loads((files("snapstudio_core.data.templates")
                      / "u1_base_project_settings.json").read_text("utf-8"))
    cfg = copy.deepcopy(cfg)
    set_filament_block(cfg, colors)
    return cfg


def wrap_stl_bytes(data: bytes, name: str = "model", colors=DEFAULT_COLORS,
                   profile_name: str = "snapmaker_u1", scale: float = 1.0) -> ThreeMF:
    verts, tris = parse_stl(data)
    if scale != 1.0:
        # Uniform scale: multiply every vertex coordinate. Geometry (and so the output
        # bounding box) scales by exactly `scale`; bed_center_transform re-centers the
        # scaled mesh on the bed. Triangle topology is unchanged.
        verts = [(x * scale, y * scale, z * scale) for (x, y, z) in verts]
    transform = bed_center_transform(verts)
    eff_colours = effective_colours(colors)
    u_obj1, u_obj2, u_comp, u_build, u_item = (str(uuid.uuid4()) for _ in range(5))
    parts = {
        "[Content_Types].xml": CONTENT_TYPES,
        "_rels/.rels": RELS,
        "3D/3dmodel.model": build_root_model_xml(transform, u_obj1, u_obj2, u_comp, u_build, u_item),
        "3D/Objects/object_1.model": build_object_model_xml(verts, tris, u_obj1),
        "3D/_rels/3dmodel.model.rels": OBJECT_RELS,
        "Metadata/model_settings.config": build_model_settings(name=name),  # object uses extruder 0 / filament 1
        "Metadata/slice_info.config": build_slice_info(eff_colours),
        "Metadata/project_settings.config": dump_project_settings(_base_settings(eff_colours, profile_name)),
    }
    order = ["[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model", "3D/Objects/object_1.model",
             "3D/_rels/3dmodel.model.rels", "Metadata/model_settings.config",
             "Metadata/slice_info.config", "Metadata/project_settings.config"]
    return ThreeMF(parts, order)


def wrap_stl(stl_path, colors=DEFAULT_COLORS, profile_name: str = "snapmaker_u1",
             scale: float = 1.0) -> ThreeMF:
    p = Path(stl_path)
    return wrap_stl_bytes(p.read_bytes(), name=p.stem, colors=colors,
                          profile_name=profile_name, scale=scale)


# ---- geometry-only / foreign-slicer 3MF (no project_settings.config) ----

def build_model_settings_multi(object_ids, name: str = "object", extruder: int = 1,
                               assignments: dict | None = None,
                               filaments: int = MIN_FILAMENTS,
                               nozzle_mm: float = object_overrides.DEFAULT_NOZZLE_MM,
                               filaments_used: int = 1) -> bytes:
    """model_settings.config for an arbitrary set of build objects.

    ``assignments`` maps a build object id to what the *source project* said about
    it — ``{"extruder": int | None, "name": str | None}``. A project that put an
    object on filament 3 meant it, and writing 1 instead is a different print of
    the same shape. That is what this did for every PrusaSlicer project Studio
    prepared, silently.

    A slot number is never renumbered to fit four toolheads. A project may
    legitimately reference more colours than the machine has; what to do about
    that is colour planning's question, answered with the user in the loop.
    """
    name = _attr(name)
    assignments = assignments or {}

    def block(oid: int) -> str:
        stated = assignments.get(oid) or {}
        slot = stated.get("extruder")
        if not slot:
            # An object with no slot of its own takes its volumes' — but only
            # when they agree. A U1 object here is one part, so volumes that
            # disagree cannot all be represented, and guessing which one wins
            # would be inventing the user's intent. That case keeps the default
            # and is reported by the fidelity audit as not carried.
            volumes = {v for v in (stated.get("volume_extruders") or []) if v}
            if len(volumes) == 1:
                slot = volumes.pop()
        if not slot and oid in assignments:
            # The source project exists and says nobody assigned this object.
            # Writing 1 would state a choice the project never made, and both
            # slicers treat that as a different fact: PrusaSlicer round-trips an
            # absent extruder as absent and an explicit 1 as explicit, and
            # Snapmaker Orca writes `extruder="0"` for an object nobody assigned
            # — seen in a file Orca 2.3.5 wrote itself. So unassigned crosses as
            # unassigned, in the target's own vocabulary.
            slot = UNASSIGNED
        slot = slot if slot is not None else extruder
        label = _attr(stated.get("name") or f"{name}_{oid}")
        carried = object_overrides.plan(
            stated.get("overrides"), nozzle_mm, filaments_used)["carry"]
        overrides_xml = "".join(
            line + "\n" for line in _override_lines(carried, nozzle_mm, filaments_used))
        return (
            f'  <object id="{oid}">\n'
            f'    <metadata key="name" value="{label}"/>\n'
            f'    <metadata key="extruder" value="{slot}"/>\n'
            + overrides_xml +
            '    <part id="1" subtype="normal_part">\n'
            f'      <metadata key="name" value="{label}"/>\n'
            '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
            '      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" '
            'facets_reversed="0" backwards_edges="0"/>\n'
            '    </part>\n  </object>\n')

    objs = "".join(block(oid) for oid in object_ids)
    instances = "".join(
        '    <model_instance>\n'
        f'      <metadata key="object_id" value="{oid}"/>\n'
        '      <metadata key="instance_id" value="0"/>\n'
        '    </model_instance>\n'
        for oid in object_ids)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + objs +
            '  <plate>\n'
            '    <metadata key="plater_id" value="1"/>\n'
            '    <metadata key="plater_name" value=""/>\n'
            '    <metadata key="locked" value="false"/>\n'
            '    <metadata key="filament_map_mode" value="Auto For Flush"/>\n'
            f'    <metadata key="filament_maps" value="{_filament_maps(filaments)}"/>\n'
            + instances +
            '  </plate>\n  <assemble>\n  </assemble>\n</config>\n').encode("utf-8")


def _build_object_ids(model_xml: bytes) -> list[int]:
    """Object ids referenced by the root model's <build> items (preserve order)."""
    text = model_xml.decode("utf-8", "replace")
    m = re.search(r"<build.*?</build>", text, re.S)
    seg = m.group(0) if m else text
    ids, seen = [], set()
    for s in re.findall(r'objectid="(\d+)"', seg):
        i = int(s)
        if i not in seen:
            seen.add(i)
            ids.append(i)
    return ids or [1]


def source_assignments(src: ThreeMF) -> dict:
    """What the source project says each build object prints in.

    The PrusaSlicer dialect only, because that is the one Studio wraps: its model
    config lists objects by the same id the 3MF uses, so the correlation is the
    file's own rather than an assumption about ordering. Volume-level slots are
    collected too, so a caller can tell an object whose volumes disagree from one
    that speaks with a single voice.
    """
    part = "Metadata/Slic3r_PE_model.config"
    if not src.has_part(part):
        return {}
    try:
        raw = src.read_part(part).decode("utf-8", "ignore")
    except Exception:
        return {}
    out: dict = {}
    for chunk in re.split(r"<object\b", raw)[1:]:
        head = chunk.split(">", 1)[0]
        found = re.search(r'id="(\d+)"', head)
        if not found:
            continue
        entry = {"extruder": None, "name": None, "volume_extruders": [],
                 "overrides": {}}
        for kind, key, value in re.findall(
                r'<metadata\s+type="(object|volume)"\s+key="([^"]+)"\s+value="([^"]*)"',
                chunk.split("<volume", 1)[0]):
            if key == "extruder" and value.strip().isdigit():
                entry["extruder"] = int(value)
            elif key == "name":
                entry["name"] = value
            elif key not in _NOT_AN_OVERRIDE:
                # A setting somebody changed on this object alone. Recorded here
                # as a fact; whether it may cross is `overrides.plan`'s decision,
                # and the answer for most keys is no.
                entry["overrides"][key] = value
        for volume in re.split(r"<volume\b", chunk)[1:]:
            slot = None
            for key, value in re.findall(
                    r'<metadata\s+type="volume"\s+key="([^"]+)"\s+value="([^"]*)"', volume):
                if key == "extruder" and value.strip().isdigit():
                    slot = int(value)
            entry["volume_extruders"].append(slot)
        out[int(found.group(1))] = entry
    return out


def wrap_geometry_3mf(path, colors=DEFAULT_COLORS, profile_name: str = "snapmaker_u1") -> ThreeMF:
    """Wrap a geometry-only / foreign-slicer 3MF (no project_settings.config) into
    a clean U1 project. The source 3D geometry and build items/transforms are kept
    verbatim; foreign slicer metadata is dropped and a clean U1 project_settings /
    model_settings / slice_info is injected."""
    src = ThreeMF.open(path)
    model = src.read_part("3D/3dmodel.model")
    object_ids = _build_object_ids(model)
    eff = declared_colours(colors, slots_referenced(src, model))

    parts: dict[str, bytes] = {}
    order: list[str] = []

    def put(n: str, b: bytes):
        if n not in parts:
            order.append(n)
        parts[n] = b

    # Preserve container essentials + ALL geometry + thumbnails; drop foreign
    # slicer configs (Slic3r_PE*, Bambu/Orca metadata, wipe-tower info, etc.).
    for n in src.list_parts():
        if n in ("[Content_Types].xml", "_rels/.rels") or n.startswith("3D/") \
                or (n.startswith("Metadata/") and n.lower().endswith(".png")):
            data = src.read_part(n)
            if n == "3D/3dmodel.model":
                data = _own_the_root_model(data)
            put(n, data)
    if "[Content_Types].xml" not in parts:
        put("[Content_Types].xml", CONTENT_TYPES)
    if "_rels/.rels" not in parts:
        put("_rels/.rels", RELS)

    # A source object whose volumes carry facts of their own becomes real parts
    # rather than one mesh with a metadata row over it. Only when the split earns
    # itself: a single volume, or volumes that all say the same thing, stay on the
    # path that has been shipping.
    settings = _base_settings(eff, profile_name)
    split = _try_multipart(src, model, Path(path).stem, filaments=len(eff),
                           nozzle_mm=_nozzle_mm(settings))
    if split is not None:
        for name, data in split["parts"].items():
            put(name, data)
        put("Metadata/model_settings.config", split["model_settings"])
    else:
        put("Metadata/model_settings.config",
            build_model_settings_multi(object_ids, name=Path(path).stem,
                                       assignments=source_assignments(src),
                                       filaments=len(eff),
                                       nozzle_mm=_nozzle_mm(settings)))
    put("Metadata/slice_info.config", build_slice_info(eff))
    put("Metadata/project_settings.config", dump_project_settings(settings))
    return ThreeMF(parts, order)


# ---- one source object, several real parts ----------------------------------

def carries_painting(src: ThreeMF) -> bool:
    """Does the source paint any facet at all?"""
    for name in src.list_parts():
        if not name.lower().endswith(".model"):
            continue
        try:
            blob = src.read_part(name)
        except Exception:
            continue
        if b'slic3rpe:mmu_segmentation="' in blob or b'paint_color="' in blob:
            return True
    return False


#: Scanning the root model for its objects, written without a single backslash
#: escape: a `\b` that travels through a shell heredoc arrives as a backspace
#: byte, and the pattern then matches nothing while still looking right.
OBJECT_WITH_ID = re.compile(r'<object[^>]* id="([0-9]+)"[^>]*>.*?</object>', re.S)
OBJECT_BLOCK = re.compile(r'<object[^>]*>.*?</object>', re.S)
BUILD_ITEM = re.compile(r'<item[^>]* objectid="([0-9]+)"[^>]*'
                        r' transform="([^"]*)"')


def _try_multipart(src: ThreeMF, model: bytes, stem: str,
                   filaments: int = MIN_FILAMENTS,
                   nozzle_mm: float = object_overrides.DEFAULT_NOZZLE_MM):
    """Emit the target's own layout for every logical object the source has.

    Returns the archive parts to write, or None to leave the caller on the path
    that copies the source geometry verbatim. Refusing is always safe: the
    objects still cross, and the fidelity audit still reports what could not be
    carried.

    The shape is what Snapmaker Orca writes for a project of several objects —
    its own badge fixture holds three, each with its own object file, its own
    components and its own build item, and part ids unique across the project:

        3D/3dmodel.model            one composite <object> per logical object,
                                    one <item> per composite, no meshes
        3D/Objects/object_N.model   that object's part meshes
        3D/_rels/…rels              every object file declared
        model_settings.config       one <object> per logical object, its parts
                                    numbered the same as its components

    Two things earn the layout. Volumes that carry facts of their own become real
    parts. And painting earns it by itself: measured against Orca 2.3.5, the
    identical painting in the root model opens with nothing painted, and behind a
    component in its own object file opens complete.

    If any object cannot be carried the whole project declines. A half-converted
    project would leave some objects in a shape the target does not read from,
    which is worse than a project that crosses whole and says so.
    """
    from . import multipart

    config = "Metadata/Slic3r_PE_model.config"
    if not src.has_part(config):
        return None
    try:
        volumes_by_object = multipart.source_volumes(
            src.read_part(config).decode("utf-8", "ignore"))
    except Exception:
        return None
    if not volumes_by_object:
        return None

    text = model.decode("utf-8", "replace")
    blocks = OBJECT_WITH_ID.findall(text)
    bodies = OBJECT_BLOCK.findall(text)
    if len(blocks) != len(bodies) or not blocks:
        return None
    placements = dict(BUILD_ITEM.findall(text))

    painted = carries_painting(src)
    assignments = source_assignments(src)
    plan = []
    next_part_id = 1
    earns_it = painted
    for source_id, body in zip(blocks, bodies):
        volumes = volumes_by_object.get(source_id)
        if not volumes:
            # The root holds geometry the model config says nothing about. Studio
            # cannot say what its parts are, so it does not invent any.
            return None
        try:
            vertices, triangles = multipart.read_mesh(body)
            parts = multipart.split_triangles(
                vertices, triangles, [v["range"] for v in volumes])
        except multipart.Unsplittable:
            # The ranges do not describe this mesh. Carrying the object whole is
            # honest; inventing a split is not.
            return None
        roles = [v["role"] for v in volumes]
        if any(role not in multipart.TARGET_ROLES for role in roles):
            # A role Studio cannot prove the target represents. It is not written
            # as a normal part — that is how a modifier becomes solid plastic — so
            # the object stays whole and the audit reports the role as not carried.
            return None
        stated = (assignments.get(int(source_id))
                  if str(source_id).isdigit() else None) or {}
        earns_it = earns_it or multipart.worth_splitting(volumes)
        plan.append({
            "source_id": source_id,
            "parts": parts,
            "roles": roles,
            "slots": [v["slot"] for v in volumes],
            "part_ids": list(range(next_part_id, next_part_id + len(parts))),
            "object_slot": stated.get("extruder"),
            "carry_overrides": object_overrides.plan(
                stated.get("overrides"), nozzle_mm, filaments)["carry"],
            "name": stated.get("name") or (stem if len(blocks) == 1
                                           else f"{stem}_{len(plan) + 1}"),
            "transform": placements.get(source_id, "1 0 0 0 1 0 0 0 1 0 0 0"),
        })
        next_part_id += len(parts)

    if not earns_it:
        return None

    # Composite ids follow the parts rather than sharing their numbers, which is
    # what Orca's own multi-object projects do.
    root_id = next_part_id
    files: dict[str, bytes] = {}
    graph = []
    for order, entry in enumerate(plan, start=1):
        path = f"3D/Objects/object_{order}.model"
        files[path] = multipart.objects_model_xml(
            entry["parts"], roles=entry["roles"], ids=entry["part_ids"])
        entry["root_id"] = root_id
        graph.append({"root_id": root_id, "part_ids": entry["part_ids"],
                      "path": "/" + path, "transform": entry["transform"]})
        root_id += 1

    parts_to_write = {
        "3D/3dmodel.model": multipart.root_model_multi_xml(graph),
        "3D/_rels/3dmodel.model.rels": multipart.object_rels_multi_xml(
            [entry["path"] for entry in graph]),
    }
    parts_to_write.update(files)
    return {
        "parts": parts_to_write,
        "model_settings": _target_settings(plan, filaments),
    }


#: The one thing in a copied root model that is no longer true of it. Everything
#: else — every object, every build item, every coordinate — is the source's and
#: stays the source's.
_APPLICATION = re.compile(r'(<metadata\s+name="Application"\s*>)(.*?)(</metadata>)', re.S)
APPLICATION = "SnapmakerStudio-u1convert"


def _own_the_root_model(data: bytes) -> bytes:
    """Say who wrote this file, because Snapmaker Orca asks.

    A prepared copy used to keep the source's `<metadata name="Application">
    PrusaSlicer-2.9.6</metadata>`, and Orca answered with *"The 3mf is not
    supported by Snapmaker Orca, loading geometry data only"* — then loaded the
    geometry and **ignored `model_settings.config` entirely**.

    What that cost, measured on Orca 2.3.6 by handing it a prepared copy and
    reading the project Orca saved back: object names replaced by the file's
    name, and an object Studio had written as filament 3 came back as
    **filament 0, unassigned**. The per-object assignment this converter exists
    to protect was intact in the file and never reached the slicer.

    Isolated to this one line, one variable per file: the same copy with the
    Application renamed opened as a project with every name and every per-object
    setting intact, and so did the same copy with the line removed. Adding
    `BambuStudio:3mfVersion` while leaving the Application alone changed nothing.

    So the value is corrected and nothing else is touched. The copy is Studio's
    file; claiming to be PrusaSlicer's was the untrue part.
    """
    text = data.decode("utf-8", "replace")
    if "<metadata" not in text:
        return data
    if _APPLICATION.search(text):
        text = _APPLICATION.sub(lambda m: m.group(1) + APPLICATION + m.group(3), text, count=1)
    else:
        # No claim to correct. Orca is content with a file that makes none, so
        # nothing is inserted: an added line is a change to a file this path
        # exists to copy verbatim.
        return data
    return text.encode("utf-8")


def _nozzle_mm(settings: dict) -> float:
    """The nozzle the prepared copy is for, in millimetres.

    Snapmaker Orca refuses to slice a plate whose layer height exceeds the nozzle
    diameter, and names the object and the setting when it does. So a layer
    height is measured against this before it is allowed to cross, and the
    smallest declared nozzle is the one that has to be satisfied.
    """
    raw = (settings or {}).get("nozzle_diameter")
    if isinstance(raw, str):
        raw = [raw]
    sizes = []
    for value in raw or ():
        number = object_overrides._ascii_number(str(value))
        if number and number > 0:
            sizes.append(number)
    return min(sizes) if sizes else object_overrides.DEFAULT_NOZZLE_MM


def _override_lines(carried: dict | None, nozzle_mm: float = object_overrides.DEFAULT_NOZZLE_MM,
                    filaments: int = 1) -> list[str]:
    """The object-level `<metadata>` rows for the settings that may cross.

    Written inside `<object>` and nowhere else: that is where Snapmaker Orca puts
    a per-object override when the setting is changed through its own per-object
    panel, and where it looks for one.

    Validated immediately before it is written rather than only where it was
    decided. An override Orca cannot read does not degrade gracefully — it takes
    the object with it — so a copy that cannot be written correctly is not
    written at all.
    """
    if not carried:
        return []
    faults = object_overrides.validate_emitted(carried, nozzle_mm, filaments)
    if faults:
        raise ValueError("refusing to write a per-object override that would not "
                         "survive: " + "; ".join(faults))
    return [f'    <metadata key="{key}" value="{_attr(value)}"/>'
            for key, value in sorted(carried.items())]


def _target_settings(plan: list[dict], filaments: int = MIN_FILAMENTS) -> bytes:
    """model_settings.config for every logical object and its parts.

    Built by joining lines rather than by embedding escapes, because a newline
    that has to survive several layers of quoting is a newline that eventually
    does not.
    """
    from . import multipart

    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<config>"]
    for entry in plan:
        name = _attr(entry["name"])
        slot = entry["object_slot"] if entry["object_slot"] else UNASSIGNED
        lines.extend([
            f'  <object id="{entry["root_id"]}">',
            f'    <metadata key="name" value="{name}"/>',
            f'    <metadata key="extruder" value="{slot}"/>',
        ])
        lines.extend(_override_lines(entry.get("carry_overrides"), filaments=filaments))
        body = multipart.part_records(entry["parts"], name, entry["slots"],
                                      entry["roles"], entry["part_ids"])
        lines.extend(line for line in body.split(chr(10)) if line.strip())
        lines.append("  </object>")

    lines.extend([
        "  <plate>",
        '    <metadata key="plater_id" value="1"/>',
        '    <metadata key="plater_name" value=""/>',
        '    <metadata key="locked" value="false"/>',
        '    <metadata key="filament_map_mode" value="Auto For Flush"/>',
        f'    <metadata key="filament_maps" value="{_filament_maps(filaments)}"/>',
    ])
    for entry in plan:
        lines.extend([
            "    <model_instance>",
            f'      <metadata key="object_id" value="{entry["root_id"]}"/>',
            '      <metadata key="instance_id" value="0"/>',
            "    </model_instance>",
        ])
    lines.extend(["  </plate>", "  <assemble>", "  </assemble>", "</config>", ""])
    return chr(10).join(lines).encode("utf-8")


def _multipart_settings(stem: str, parts, slots, roles, object_slot,
                        filaments: int = MIN_FILAMENTS) -> bytes:
    """model_settings.config for one composite object and its real parts.

    Built by joining lines rather than by embedding escapes, because a newline
    that has to survive several layers of quoting is a newline that eventually
    does not.
    """
    from . import multipart

    name = _attr(stem)
    slot = object_slot if object_slot else UNASSIGNED
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<config>",
        '  <object id="2">',
        f'    <metadata key="name" value="{name}"/>',
        f'    <metadata key="extruder" value="{slot}"/>',
    ]
    body = multipart.part_records(parts, name, slots, roles)
    lines.extend(line for line in body.split(chr(10)) if line.strip())
    lines.extend([
        "  </object>",
        "  <plate>",
        '    <metadata key="plater_id" value="1"/>',
        '    <metadata key="plater_name" value=""/>',
        '    <metadata key="locked" value="false"/>',
        '    <metadata key="filament_map_mode" value="Auto For Flush"/>',
        f'    <metadata key="filament_maps" value="{_filament_maps(filaments)}"/>',
        "    <model_instance>",
        '      <metadata key="object_id" value="2"/>',
        '      <metadata key="instance_id" value="0"/>',
        "    </model_instance>",
        "  </plate>",
        "  <assemble>",
        "  </assemble>",
        "</config>",
        "",
    ])
    return chr(10).join(lines).encode("utf-8")
