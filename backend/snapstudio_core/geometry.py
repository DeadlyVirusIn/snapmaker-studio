"""Indexed-mesh loader — the shared geometry foundation for Design Intelligence.

Loads an STL or 3MF into one in-memory indexed mesh (deduped vertices + triangle
index triples) so the diagnostics layer can run real geometry analysis (integrity,
overhang, stability, volume) on ANY ecosystem's file. Read-only: never mutates input.

Pure Python, no heavy deps (no trimesh/Open3D) — keeps the frozen sidecar light.
Guarded for size so an interactive call degrades to "too large to analyze" instead
of stalling.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from .container import ThreeMF
from .config_io import load_model_settings

# Mirror intelligence.py's byte guard; plus a triangle cap for analysis cost.
_MAX_BYTES = 80 * 1024 * 1024
_MAX_TRIANGLES = 2_000_000
_3MF_CORE_NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"


class _TooLarge(Exception):
    pass


@dataclass
class Mesh:
    verts: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]

    @property
    def triangle_count(self) -> int:
        return len(self.faces)


def _model_parts(tm: ThreeMF) -> list[str]:
    return [p for p in tm.list_parts() if p.endswith(".model")]


def _parse_3mf_model(raw: bytes, verts: list, faces: list) -> None:
    """Append one .model part's vertices + triangles to the accumulators. Uses the
    hardened XML parser (no XXE/DTD/network). Triangle indices are local to each
    <mesh>, so we offset by the vertex count at the start of that mesh."""
    root = load_model_settings(raw)
    for mesh in root.iter(f"{_3MF_CORE_NS}mesh"):
        vstart = len(verts)
        vnode = mesh.find(f"{_3MF_CORE_NS}vertices")
        tnode = mesh.find(f"{_3MF_CORE_NS}triangles")
        if vnode is None or tnode is None:
            continue
        for v in vnode.iterfind(f"{_3MF_CORE_NS}vertex"):
            verts.append((float(v.get("x", 0)), float(v.get("y", 0)), float(v.get("z", 0))))
        for t in tnode.iterfind(f"{_3MF_CORE_NS}triangle"):
            faces.append((vstart + int(t.get("v1")), vstart + int(t.get("v2")), vstart + int(t.get("v3"))))
            if len(faces) > _MAX_TRIANGLES:
                raise _TooLarge()


def load_mesh(path: str) -> Mesh | None:
    """Load an STL or 3MF into one indexed mesh, or None if unreadable / too large.
    Best-effort and exception-safe (returns None, never raises out to callers)."""
    p = Path(path)
    try:
        if p.suffix.lower() == ".stl":
            data = p.read_bytes()
            if len(data) > _MAX_BYTES:
                return None
            from .stl_io import parse_stl
            verts, faces = parse_stl(data)
            if not verts or not faces or len(faces) > _MAX_TRIANGLES:
                return None
            return Mesh(list(verts), list(faces))
        # 3MF (Bambu/Orca/Prusa) — accumulate every .model part into one mesh.
        tm = ThreeMF.open(path)
        parts = _model_parts(tm)
        if sum(len(tm.read_part(pt)) for pt in parts) > _MAX_BYTES:
            return None
        verts: list = []
        faces: list = []
        for part in parts:
            _parse_3mf_model(tm.read_part(part), verts, faces)
        if not verts or not faces:
            return None
        return Mesh(verts, faces)
    except _TooLarge:
        return None
    except Exception:
        return None
