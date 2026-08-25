"""One source object with several volumes, carried as several real parts.



PrusaSlicer stores an object's volumes as **triangle ranges inside one mesh**:

`<volume firstid="0" lastid="5">` and `<volume firstid="6" lastid="11">` describe

two parts of a twelve-facet cube, each able to carry its own filament. Studio used

to wrap that geometry verbatim and write one `<part>` record over it, so a source

saying "this half prints in filament 2 and that half in filament 5" arrived as one

undifferentiated object and the audit reported the second filament as not carried.



The target dialect can hold it. Two Snapmaker-Orca-family projects in the test

fixtures prove the shape:



    3D/3dmodel.model

      <object id="R" type="model">

        <components>

          <component p:path="/3D/Objects/object_1.model" objectid="1" transform=.../>

          <component p:path="/3D/Objects/object_1.model" objectid="2" transform=.../>

        </components>

      </object>

      <build><item objectid="R" .../></build>



    3D/Objects/object_1.model

      <object id="1" type="model"><mesh>…</mesh></object>

      <object id="2" type="model"><mesh>…</mesh></object>



    Metadata/model_settings.config

      <object id="R">

        <metadata key="extruder" value="…"/>       ← the object's own assignment

        <part id="1" subtype="normal_part">…<metadata key="extruder" value="2"/>

        <part id="2" subtype="normal_part">…<metadata key="extruder" value="5"/>



`part id` in the metadata, `objectid` on the component and the object id inside

the Objects file are **the same number**. That identity is what makes the metadata

describe the geometry rather than decorate it, and it is the thing this module

exists to get right — a `<part>` record over a single mesh is a claim, not a part.



Nothing here invents geometry. Each part's mesh is the source triangles of that

volume's range, with their vertices carried across unchanged and their attributes —

including the per-facet painting Studio spent two releases learning to read —

copied verbatim.

"""

from __future__ import annotations



import re



SCHEMA_VERSION = "multipart/1"



#: The namespaces a root model needs to declare components and the production

#: extension. Taken from what the writer already emits for the single-part path.

_MESH_OBJECT = re.compile(r"<object\b[^>]*\bid=\"(\d+)\"[^>]*>(.*?)</object>", re.S)

_VERTEX = re.compile(r"<vertex\b[^>]*/>")

_TRIANGLE = re.compile(r"<triangle\b[^>]*/>")

_V_ATTR = re.compile(r'\b(x|y|z)="([^"]*)"')

_T_ATTR = re.compile(r'\bv([123])="(\d+)"')





class Unsplittable(Exception):

    """The source object cannot be split into parts without inventing something."""





def _vertex_key(tag: str) -> tuple:

    found = dict(_V_ATTR.findall(tag))

    return (found.get("x", ""), found.get("y", ""), found.get("z", ""))





def read_mesh(object_xml: str) -> tuple[list[str], list[str]]:

    """The vertex and triangle tags of one mesh, verbatim and in order."""

    return _VERTEX.findall(object_xml), _TRIANGLE.findall(object_xml)





def _triangle_indices(tag: str) -> tuple[int, int, int]:

    found = {slot: int(value) for slot, value in _T_ATTR.findall(tag)}

    if len(found) != 3:

        raise Unsplittable(f"a triangle does not name three vertices: {tag[:60]}")

    return found["1"], found["2"], found["3"]





def _retarget(tag: str, mapping: dict[int, int]) -> str:

    """Rewrite a triangle's vertex indices, leaving every other attribute alone.



    Painting lives in the attributes this does not touch —

    `slic3rpe:mmu_segmentation` and its Bambu/Orca equivalents — so a facet keeps

    exactly what it was painted with.

    """

    def swap(match: re.Match) -> str:

        return f'v{match.group(1)}="{mapping[int(match.group(2))]}"'



    return _T_ATTR.sub(swap, tag)





def split_triangles(vertices: list[str], triangles: list[str],

                    ranges: list[tuple[int, int]]) -> list[dict]:

    """Cut one mesh into the meshes its volume ranges describe.



    Each part gets only the vertices its own triangles reference, renumbered from

    zero — which is what makes it a standalone mesh rather than a view into a

    shared one. Vertex *tags* are copied unchanged, so coordinates cross exactly as

    written rather than through a float round-trip.

    """

    if not ranges:

        raise Unsplittable("no volume ranges to split on")

    parts: list[dict] = []

    for order, (first, last) in enumerate(ranges):

        if first < 0 or last < first or last >= len(triangles):

            raise Unsplittable(

                f"volume {order + 1} names triangles {first}-{last} and the mesh has "

                f"{len(triangles)}")

        mine = triangles[first:last + 1]

        mapping: dict[int, int] = {}

        kept: list[str] = []

        for tag in mine:

            for index in _triangle_indices(tag):

                if index >= len(vertices):

                    raise Unsplittable(

                        f"a triangle references vertex {index} and the mesh has "

                        f"{len(vertices)}")

                if index not in mapping:

                    mapping[index] = len(kept)

                    kept.append(vertices[index])

        parts.append({

            "index": order,

            "vertices": kept,

            "triangles": [_retarget(tag, mapping) for tag in mine],

            "source_range": (first, last),

        })

    covered = sum(len(part["triangles"]) for part in parts)

    if covered != len(triangles):

        # Every facet belongs to exactly one volume, or the split would silently

        # drop or duplicate geometry. Refusing is the only honest answer.

        raise Unsplittable(

            f"the volume ranges cover {covered} of {len(triangles)} triangles")

    return parts





def geometry_digest(vertices: list[str], triangles: list[str]) -> str:

    """A digest of what a mesh actually is, independent of vertex numbering.



    Triangles are hashed by their vertices' *coordinates* rather than their

    indices, because splitting a mesh renumbers indices by design. Two meshes with

    the same digest describe the same solid in the same winding order, whatever

    order their vertex table happens to be in.

    """

    import hashlib



    keys = [_vertex_key(tag) for tag in vertices]

    lines = []

    for tag in triangles:

        a, b, c = _triangle_indices(tag)

        try:

            lines.append("|".join(",".join(keys[i]) for i in (a, b, c)))

        except IndexError as exc:

            raise Unsplittable("a triangle references a vertex that is not there") from exc

    digest = hashlib.sha256()

    for line in lines:

        digest.update(line.encode("utf-8"))

        digest.update(b"\n")

    return digest.hexdigest()





# --- emitting the target structure -------------------------------------------



_PROD_NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '

            'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06"')





def objects_model_xml(parts: list[dict], uuids: list[str] | None = None) -> bytes:

    """`3D/Objects/object_1.model` — one mesh object per part, ids from 1.



    The id given here is the number the root's component references and the number

    the metadata calls a part. Keeping the three the same is the whole point.

    """

    uuids = uuids or [""] * len(parts)

    body = []

    for part, uuid in zip(parts, uuids):

        stamp = f' p:UUID="{uuid}"' if uuid else ""

        body.append(

            f'<object id="{part["index"] + 1}"{stamp} type="model"><mesh>'

            f'<vertices>{"".join(part["vertices"])}</vertices>'

            f'<triangles>{"".join(part["triangles"])}</triangles>'

            "</mesh></object>")

    return ('<?xml version="1.0" encoding="UTF-8"?>'

            f'<model unit="millimeter" xml:lang="en-US" {_PROD_NS}>'

            '<metadata name="BambuStudio:3mfVersion">1</metadata>'

            f'<resources>{"".join(body)}</resources></model>').encode("utf-8")





def root_model_xml(part_count: int, transform: str, root_id: int = 2,

                   objects_path: str = "/3D/Objects/object_1.model",

                   uuids: dict | None = None) -> bytes:

    """The root model: one composite object, one component per part, one item."""

    uuids = uuids or {}

    components = "".join(

        f'<component p:path="{objects_path}" objectid="{index + 1}"'

        + (f' p:UUID="{uuids.get(f"comp{index}")}"' if uuids.get(f"comp{index}") else "")

        + ' transform="1 0 0 0 1 0 0 0 1 0 0 0"/>'

        for index in range(part_count))

    meta = "".join(f'<metadata name="{key}"></metadata>' for key in

                   ["Copyright", "CreationDate", "Description", "Designer",

                    "DesignerCover", "DesignerUserId", "License", "ModificationDate",

                    "Origin", "Title"])

    root_uuid = f' p:UUID="{uuids["root"]}"' if uuids.get("root") else ""

    build_uuid = f' p:UUID="{uuids["build"]}"' if uuids.get("build") else ""

    item_uuid = f' p:UUID="{uuids["item"]}"' if uuids.get("item") else ""

    return ('<?xml version="1.0" encoding="UTF-8"?>'

            f'<model unit="millimeter" xml:lang="en-US" {_PROD_NS}>'

            '<metadata name="Application">SnapmakerStudio-u1convert</metadata>'

            '<metadata name="BambuStudio:3mfVersion">1</metadata>' + meta +

            f'<resources><object id="{root_id}"{root_uuid} type="model">'

            f'<components>{components}</components></object></resources>'

            f'<build{build_uuid}><item objectid="{root_id}"{item_uuid} '

            f'transform="{transform}" printable="1"/></build></model>').encode("utf-8")





def object_rels_xml(objects_path: str = "/3D/Objects/object_1.model") -> bytes:

    return ('<?xml version="1.0" encoding="UTF-8"?>'

            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'

            f'<Relationship Target="{objects_path}" Id="rel-1" '

            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'

            '</Relationships>').encode("utf-8")





#: Roles Studio will write into a prepared copy, and the word the target uses.

#: Only `normal_part` is proven here — `modifier_part` appears in a genuine

#: Orca-family project, but nothing has yet proved Studio can *produce* one that

#: Snapmaker Orca reads correctly, so nothing else is emitted.

TARGET_ROLES = {"part": "normal_part"}





def part_records(parts: list[dict], name: str, slots: list, roles: list | None = None) -> str:

    """The `<part>` block for `model_settings.config`, one entry per real part.



    A slot of `None` writes no extruder at all rather than a 1: an object nobody

    assigned is not an object assigned to filament 1, and that distinction is the

    same one the object level already keeps.

    """

    roles = roles or ["part"] * len(parts)

    out = []

    for part, slot, role in zip(parts, slots, roles):

        subtype = TARGET_ROLES.get(role, "normal_part")

        extruder = (f'      <metadata key="extruder" value="{int(slot)}"/>\n'

                    if slot else "")

        out.append(

            f'    <part id="{part["index"] + 1}" subtype="{subtype}">\n'

            f'      <metadata key="name" value="{name}_{part["index"] + 1}"/>\n'

            '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'

            + extruder +

            '      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" '

            'facets_reversed="0" backwards_edges="0"/>\n'

            '    </part>\n')

    return "".join(out)





# --- reading the source's volume graph ---------------------------------------



_PRUSA_OBJECT = re.compile(r"<object(?P<head>[^>]*)>(?P<body>.*?)</object>", re.S)

_PRUSA_VOLUME = re.compile(

    r'<volume[^>]*firstid="(\d+)"[^>]*lastid="(\d+)"[^>]*>(.*?)</volume>', re.S)

_META = re.compile(r'<metadata\s+type="volume"\s+key="([^"]+)"\s+value="([^"]*)"')





def source_volumes(config_xml: str) -> dict[str, list[dict]]:

    """Each Prusa object's volumes: triangle range, filament and role.



    Keyed by the object id the file itself uses, so nothing depends on ordering

    surviving the crossing.

    """

    from .assignments import _int, role_of



    out: dict[str, list[dict]] = {}

    for match in _PRUSA_OBJECT.finditer(config_xml):

        found = re.search(r'id="([^"]+)"', match.group("head"))

        if not found:

            continue

        volumes = []

        for order, (first, last, body) in enumerate(_PRUSA_VOLUME.findall(match.group("body"))):

            meta = dict(_META.findall(body))

            volumes.append({

                "index": order,

                "range": (int(first), int(last)),

                "slot": _int(meta.get("extruder", "")),

                "role": role_of(meta.get("volume_type")),

                "name": meta.get("name"),

            })

        if volumes:

            out[found.group(1)] = volumes

    return out





def worth_splitting(volumes: list[dict]) -> bool:

    """Is there more than one part, and does the split carry a fact?



    A single volume is the existing path and stays on it. Several volumes that all

    say the same thing — or say nothing — carry no information the object level

    cannot hold, and splitting them would churn the geometry for no gain. What

    earns a split is volumes that disagree, or a volume with a role of its own.

    """

    if len(volumes) < 2:

        return False

    slots = {v["slot"] for v in volumes if v["slot"]}

    roles = {v["role"] for v in volumes}

    return len(slots) > 1 or roles != {"part"}



# --- does the archive say the same thing three times? ------------------------

def validate_archive(tm) -> dict:
    """Check that geometry, component graph and metadata all agree.

    A prepared multi-part project makes the same claim in three places: the root
    model's components, the mesh objects they point at, and the `<part>` records
    in `model_settings.config`. If those three drift apart the file is wrong even
    though every one of them is individually well-formed — and Snapmaker Orca
    should not be the first thing to notice.

    Never raises. Returns the findings, so a caller can report them rather than
    lose the file.
    """
    problems: list[str] = []

    def read(name: str) -> str:
        try:
            return tm.read_part(name).decode("utf-8", "ignore") if tm.has_part(name) else ""
        except Exception:
            return ""

    root = read("3D/3dmodel.model")
    settings = read("Metadata/model_settings.config")
    if not root:
        return {"schema_version": SCHEMA_VERSION, "multipart": False,
                "ok": False, "problems": ["no root model in the archive"]}

    components = re.findall(r'<component[^>]*objectid="(\d+)"[^>]*/>', root)
    paths = set(re.findall(r'<component[^>]*p:path="([^"]+)"', root))
    if not components:
        return {"schema_version": SCHEMA_VERSION, "multipart": False,
                "ok": True, "problems": []}

    # every referenced object file exists, and is declared as a relationship
    rels = read("3D/_rels/3dmodel.model.rels")
    mesh_ids: list[str] = []
    for path in sorted(paths):
        name = path.lstrip("/")
        if not tm.has_part(name):
            problems.append(f"a component points at {path}, which is not in the archive")
            continue
        if path not in rels:
            problems.append(f"{path} holds geometry but is not declared in the relationships")
        body = read(name)
        found = re.findall(r'<object id="(\d+)"', body)
        mesh_ids.extend(found)
        for object_id in found:
            block = re.search(rf'<object id="{object_id}".*?</object>', body, re.S)
            if block and "<triangle" not in block.group(0):
                problems.append(f"object {object_id} in {path} carries no geometry")

    missing = [c for c in components if c not in mesh_ids]
    if missing:
        problems.append(
            f"component(s) {sorted(set(missing))} reference an object that no file defines")
    if len(set(components)) != len(components):
        problems.append("the same object is referenced twice by one object's components")

    # build item must place the composite object, not a mesh
    roots = re.findall(r'<object id="(\d+)"[^>]*>\s*<components>', root)
    items = re.findall(r'<item[^>]*objectid="(\d+)"', root)
    if roots and items and not set(items) & set(roots):
        problems.append(
            f"the build places object(s) {sorted(set(items))} and the composite object "
            f"is {sorted(set(roots))}")

    # metadata parts must match the components one for one
    parts = re.findall(r'<part id="(\d+)"', settings)
    if len(parts) != len(components):
        problems.append(
            f"the metadata lists {len(parts)} part(s) and the geometry has "
            f"{len(components)}")
    if sorted(parts) != sorted(components):
        problems.append(
            f"part ids {sorted(parts)} do not match component ids {sorted(components)}")
    if len(set(parts)) != len(parts):
        problems.append("a part id is used twice")

    for matrix in re.findall(r'key="matrix" value="([^"]*)"', settings):
        values = matrix.split()
        if len(values) not in (12, 16):
            problems.append(f"a part matrix has {len(values)} values")
            continue
        try:
            [float(v) for v in values]
        except ValueError:
            problems.append("a part matrix is not numeric")

    return {"schema_version": SCHEMA_VERSION, "multipart": True,
            "parts": len(components), "ok": not problems, "problems": problems}
