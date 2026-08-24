"""Builders for painted 3MF projects, in both dialects Studio has to read.

These are synthetic on purpose: a test that needs a specific shape of damage —
a facet index pointing past the end of the mesh, a paint attribute that stops
half-way — cannot get one from a real slicer, because a real slicer does not
write broken files. The proof that the *format* here matches what slicers really
write lives in test_painted_real_slicers.py, which runs against genuine slicer
output when a slicer is available.

Geometry is a unit-ish wedge with a known area and a known height, so a test can
assert on real numbers rather than on "something non-zero".
"""
from __future__ import annotations

import json
import zipfile

from snapstudio_core import paint_codec as codec

# Two stacked triangles: the first spans z 0–0, the second z 10–10, so a test can
# paint "low" and "high" and get provable separation in Z.
VERTICES = [
    (0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (0.0, 10.0, 0.0),
    (0.0, 0.0, 10.0), (10.0, 0.0, 10.0), (0.0, 10.0, 10.0),
]
TRIANGLES = [(0, 1, 2), (3, 4, 5)]
TRIANGLE_AREA = 50.0


def paint(state_or_tree) -> str:
    return codec.encode_tree(state_or_tree)


def _vertex_xml(vertices=VERTICES) -> str:
    return "".join(f'<vertex x="{x}" y="{y}" z="{z}"/>' for x, y, z in vertices)


def _triangle_xml(attribute_name, painted, triangles=TRIANGLES) -> str:
    out = []
    for index, (v1, v2, v3) in enumerate(triangles):
        attribute = painted.get(index)
        extra = f' {attribute_name}="{attribute}"' if attribute is not None else ""
        out.append(f'<triangle v1="{v1}" v2="{v2}" v3="{v3}"{extra}/>')
    return "".join(out)


def bambu_project(tmp_path, name="painted.3mf", *, meshes=None, colours=None,
                  version=1, transform="1 0 0 0 1 0 0 0 1 0 0 0",
                  item_transform="1 0 0 0 1 0 0 0 1 0 0 0", extra_parts=None,
                  triangles=TRIANGLES, vertices=VERTICES):
    """A project in the dialect Snapmaker Orca, OrcaSlicer and BambuStudio write.

    ``meshes`` is a list of dicts: ``{"painted": {triangle index: attribute},
    "extruder": slot or None, "subtype": "normal_part"}``.
    """
    meshes = meshes or [{"painted": {0: paint(2)}, "extruder": 1}]
    colours = colours or ["#000000", "#FFFFFF", "#FF0000", "#00FF00"]

    components, part_xml, parts = [], [], {}
    for index, mesh in enumerate(meshes, start=1):
        part_name = f"3D/Objects/object_{index}.model"
        parts[part_name] = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"'
            ' xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">'
            f'<metadata name="BambuStudio:MmPaintingVersion">{version}</metadata>'
            f'<resources><object id="{index}" type="model"><mesh>'
            f"<vertices>{_vertex_xml(mesh.get('vertices', vertices))}</vertices>"
            f"<triangles>{_triangle_xml('paint_color', mesh.get('painted', {}), mesh.get('triangles', triangles))}</triangles>"
            "</mesh></object></resources></model>")
        components.append(
            f'<component p:path="/{part_name}" objectid="{index}" transform="{transform}"/>')
        slot = mesh.get("extruder")
        subtype = mesh.get("subtype", "normal_part")
        slot_xml = (f'<metadata key="extruder" value="{slot}"/>' if slot else "")
        part_xml.append(f'<part id="{index}" subtype="{subtype}">'
                        f'<metadata key="name" value="part_{index}"/>{slot_xml}</part>')

    model = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"'
        ' xmlns:BambuStudio="http://schemas.bambulab.com/package/2021"'
        ' xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06">'
        '<metadata name="Application">SnapmakerOrca-test</metadata>'
        f'<metadata name="BambuStudio:MmPaintingVersion">{version}</metadata>'
        f'<resources><object id="100" type="model"><components>{"".join(components)}'
        "</components></object></resources>"
        f'<build><item objectid="100" transform="{item_transform}"/></build></model>')

    settings = {
        "printer_model": "Snapmaker U1",
        "filament_colour": list(colours),
        "filament_type": ["PLA"] * len(colours),
        "layer_height": "0.2",
        "initial_layer_print_height": "0.2",
    }
    parts["3D/3dmodel.model"] = model
    parts["Metadata/project_settings.config"] = json.dumps(settings)
    parts["Metadata/model_settings.config"] = (
        f'<config><object id="100">{"".join(part_xml)}</object>'
        '<plate><metadata key="plater_id" value="1"/>'
        '<model_instance><metadata key="object_id" value="100"/>'
        '<metadata key="instance_id" value="0"/></model_instance></plate></config>')
    parts.update(extra_parts or {})

    path = tmp_path / name
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for part, data in parts.items():
            archive.writestr(part, data)
    return str(path)


def prusa_project(tmp_path, name="painted-prusa.3mf", *, painted=None,
                  volumes=None, version=1, item_transform="1 0 0 0 1 0 0 0 1 0 0 0",
                  triangles=TRIANGLES, vertices=VERTICES):
    """A project in the PrusaSlicer dialect: one mesh, volumes as index ranges."""
    painted = painted if painted is not None else {0: paint(2)}
    volumes = volumes or [{"first": 0, "last": len(triangles) - 1, "extruder": 1}]

    model = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"'
        ' xmlns:slic3rpe="http://schemas.slic3r.org/3mf/2017/06">'
        '<metadata name="slic3rpe:Version3mf">1</metadata>'
        f'<metadata name="slic3rpe:MmPaintingVersion">{version}</metadata>'
        '<metadata name="Application">PrusaSlicer-test</metadata>'
        '<resources><object id="1" type="model"><mesh>'
        f"<vertices>{_vertex_xml(vertices)}</vertices>"
        f"<triangles>{_triangle_xml('slic3rpe:mmu_segmentation', painted, triangles)}</triangles>"
        "</mesh></object></resources>"
        f'<build><item objectid="1" transform="{item_transform}"/></build></model>')

    volume_xml = "".join(
        f'<volume firstid="{volume["first"]}" lastid="{volume["last"]}">'
        f'<metadata type="volume" key="name" value="volume"/>'
        + (f'<metadata type="volume" key="extruder" value="{volume["extruder"]}"/>'
           if volume.get("extruder") else "")
        + "</volume>"
        for volume in volumes)

    parts = {
        "3D/3dmodel.model": model,
        "Metadata/Slic3r_PE_model.config": (
            f'<config><object id="1"><metadata type="object" key="name" '
            f'value="obj"/>{volume_xml}</object></config>'),
        "Metadata/Slic3r_PE.config": "; printer_model = MK4\n",
    }
    path = tmp_path / name
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for part, data in parts.items():
            archive.writestr(part, data)
    return str(path)
