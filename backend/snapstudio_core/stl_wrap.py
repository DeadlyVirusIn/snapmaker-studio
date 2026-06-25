from __future__ import annotations
import copy, json, re, uuid
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape


def _attr(value: str) -> str:
    """Escape a string for safe use inside an XML attribute value."""
    return _xml_escape(value, {'"': "&quot;"})
from importlib.resources import files
from .container import ThreeMF
from .config_io import dump_project_settings
from .stl_io import parse_stl
from .filaments import PER_FILAMENT_KEYS

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

def build_model_settings_multi(object_ids, name: str = "object", extruder: int = 1) -> bytes:
    """model_settings.config for an arbitrary set of build objects: map each to a
    filament/extruder slot and list them on plate 1."""
    name = _attr(name)
    objs = "".join(
        f'  <object id="{oid}">\n'
        f'    <metadata key="name" value="{name}_{oid}"/>\n'
        f'    <metadata key="extruder" value="{extruder}"/>\n'
        '    <part id="1" subtype="normal_part">\n'
        f'      <metadata key="name" value="{name}_{oid}"/>\n'
        '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
        '      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" '
        'facets_reversed="0" backwards_edges="0"/>\n'
        '    </part>\n  </object>\n'
        for oid in object_ids)
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
            '    <metadata key="filament_maps" value="1"/>\n' + instances +
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


def wrap_geometry_3mf(path, colors=DEFAULT_COLORS, profile_name: str = "snapmaker_u1") -> ThreeMF:
    """Wrap a geometry-only / foreign-slicer 3MF (no project_settings.config) into
    a clean U1 project. The source 3D geometry and build items/transforms are kept
    verbatim; foreign slicer metadata is dropped and a clean U1 project_settings /
    model_settings / slice_info is injected."""
    src = ThreeMF.open(path)
    model = src.read_part("3D/3dmodel.model")
    object_ids = _build_object_ids(model)
    eff = effective_colours(colors)

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
            put(n, src.read_part(n))
    if "[Content_Types].xml" not in parts:
        put("[Content_Types].xml", CONTENT_TYPES)
    if "_rels/.rels" not in parts:
        put("_rels/.rels", RELS)

    # Inject a clean U1 project around the preserved geometry.
    put("Metadata/model_settings.config", build_model_settings_multi(object_ids, name=Path(path).stem))
    put("Metadata/slice_info.config", build_slice_info(eff))
    put("Metadata/project_settings.config", dump_project_settings(_base_settings(eff, profile_name)))
    return ThreeMF(parts, order)
