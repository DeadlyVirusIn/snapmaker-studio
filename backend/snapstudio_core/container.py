from __future__ import annotations
import os
import zipfile
from pathlib import Path
from .errors import PartNotFound, UnsafeArchive

# ---------------------------------------------------------------------------
# Untrusted-archive limits.
#
# A 3MF is an OPC ZIP, and Studio routinely opens files a user downloaded from a
# model site. A hostile (or merely broken) archive can claim a tiny compressed
# size and expand to gigabytes — reading it into memory would take the whole app
# down. ThreeMF therefore reads every part through a hard byte budget and refuses
# archives that blow past it, instead of trusting the ZIP header.
#
# Limits are deliberately generous: a big real multi-plate project 3MF is tens of
# MB uncompressed, so a 1 GiB total budget never fires on legitimate work. All
# three are overridable via env for power users with unusual files.
# ---------------------------------------------------------------------------
def _limit(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        v = int(raw)
    except (TypeError, ValueError):
        return default
    return v if v > 0 else default


MAX_TOTAL_UNCOMPRESSED = _limit("SNAPSTUDIO_MAX_3MF_BYTES", 1024 * 1024 * 1024)   # 1 GiB
MAX_PART_UNCOMPRESSED = _limit("SNAPSTUDIO_MAX_3MF_PART_BYTES", 512 * 1024 * 1024)  # 512 MiB
MAX_PARTS = _limit("SNAPSTUDIO_MAX_3MF_PARTS", 20_000)

_CHUNK = 1024 * 1024


def _read_bounded(zf: zipfile.ZipFile, info: zipfile.ZipInfo, budget: int) -> bytes:
    """Read one archive member, refusing to exceed `budget` bytes.

    The declared `file_size` is only a hint (a hostile archive can lie), so the
    actual decompressed stream is what gets metered.
    """
    cap = min(budget, MAX_PART_UNCOMPRESSED)
    chunks: list[bytes] = []
    read = 0
    with zf.open(info, "r") as fh:
        while True:
            chunk = fh.read(_CHUNK)
            if not chunk:
                break
            read += len(chunk)
            if read > cap:
                raise UnsafeArchive(
                    "This 3MF expands to far more data than Studio will open "
                    "(it may be corrupt or deliberately malformed)."
                )
            chunks.append(chunk)
    return b"".join(chunks)


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
            infos = z.infolist()
            if len(infos) > MAX_PARTS:
                raise UnsafeArchive(
                    f"This 3MF contains {len(infos)} entries, more than Studio will open."
                )
            declared = sum(max(0, int(i.file_size or 0)) for i in infos)
            if declared > MAX_TOTAL_UNCOMPRESSED:
                raise UnsafeArchive(
                    "This 3MF is larger uncompressed than Studio will open."
                )
            remaining = MAX_TOTAL_UNCOMPRESSED
            for info in infos:
                if info.is_dir():
                    # Directory entries carry no payload; keep the name so save()
                    # reproduces the original archive layout.
                    parts[info.filename] = b""
                    order.append(info.filename)
                    continue
                data = _read_bounded(z, info, remaining)
                remaining -= len(data)
                if remaining < 0:
                    raise UnsafeArchive(
                        "This 3MF is larger uncompressed than Studio will open."
                    )
                parts[info.filename] = data
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
