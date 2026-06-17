from __future__ import annotations
import zipfile
from pathlib import Path
from .errors import PartNotFound

class ThreeMF:
    """In-memory 3MF (OPC ZIP). Reads all parts; rewrites only replaced ones on save."""
    def __init__(self, parts: dict[str, bytes], order: list[str]):
        self._parts = parts          # name -> bytes
        self._order = order          # preserve original entry order
        self._dirty: set[str] = set()

    @classmethod
    def open(cls, path: str | Path) -> "ThreeMF":
        parts, order = {}, []
        with zipfile.ZipFile(path) as z:
            for info in z.infolist():
                parts[info.filename] = z.read(info.filename)
                order.append(info.filename)
        return cls(parts, order)

    def has_part(self, name: str) -> bool: return name in self._parts
    def read_part(self, name: str) -> bytes:
        if name not in self._parts: raise PartNotFound(name)
        return self._parts[name]
    def replace_part(self, name: str, data: bytes) -> None:
        if name not in self._parts: raise PartNotFound(name)
        self._parts[name] = data; self._dirty.add(name)
    def list_parts(self) -> list[str]: return list(self._order)

    def save(self, path: str | Path) -> None:
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for name in self._order:
                z.writestr(name, self._parts[name])
