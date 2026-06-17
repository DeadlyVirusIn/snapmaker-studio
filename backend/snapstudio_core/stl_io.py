from __future__ import annotations
import struct
from .errors import SnapStudioError


def detect_stl_format(data: bytes) -> str:
    if len(data) >= 84:
        (n,) = struct.unpack_from("<I", data, 80)
        if 84 + n * 50 == len(data):
            return "binary"
    head = data[:512].lstrip().lower()
    if head.startswith(b"solid") or b"facet" in data[:4096].lower():
        return "ascii"
    raise SnapStudioError("unrecognized STL (not binary-size-consistent or ASCII)")


def _add(vmap: dict, verts: list, p: tuple[float, float, float]) -> int:
    i = vmap.get(p)
    if i is None:
        i = len(verts); vmap[p] = i; verts.append(p)
    return i


def parse_stl(data: bytes):
    fmt = detect_stl_format(data)
    verts: list[tuple] = []
    tris: list[tuple] = []
    vmap: dict = {}
    if fmt == "binary":
        (n,) = struct.unpack_from("<I", data, 80)
        off = 84
        for _ in range(n):
            vals = struct.unpack_from("<12f", data, off)
            off += 50  # 12 floats (48) + 2-byte attribute
            p1, p2, p3 = vals[3:6], vals[6:9], vals[9:12]
            tris.append((_add(vmap, verts, p1), _add(vmap, verts, p2), _add(vmap, verts, p3)))
    else:
        cur: list[tuple] = []
        for line in data.decode("utf-8", "replace").splitlines():
            s = line.strip()
            if s.startswith("vertex"):
                _, x, y, z = s.split()[:4]
                cur.append((float(x), float(y), float(z)))
                if len(cur) == 3:
                    tris.append(tuple(_add(vmap, verts, p) for p in cur)); cur = []
    if not tris:
        raise SnapStudioError("STL contained no triangles")
    return verts, tris
