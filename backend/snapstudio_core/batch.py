"""Batch orchestration — convert many files in sequence, reporting progress.

Pure and synchronous: it takes a `convert_fn` and loops, calling an optional
`on_item` callback after every state change so a caller can surface live
progress. The threading / job registry that powers the desktop queue lives in
the API layer (snapstudio_api), keeping this module testable with a fake
convert_fn and no I/O of its own.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Optional

SCHEMA_VERSION = "batch/1"


@dataclass
class BatchItem:
    path: str
    status: str = "pending"          # pending | running | done | error
    output_path: Optional[str] = None
    output_name: Optional[str] = None
    validated_ok: Optional[bool] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "path": self.path, "status": self.status,
            "output_path": self.output_path, "output_name": self.output_name,
            "validated_ok": self.validated_ok, "error": self.error,
        }


@dataclass
class BatchResult:
    items: list[BatchItem] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.items)

    @property
    def done(self) -> int:
        return sum(1 for i in self.items if i.status == "done")

    @property
    def failed(self) -> int:
        return sum(1 for i in self.items if i.status == "error")

    @property
    def finished(self) -> bool:
        return all(i.status in ("done", "error") for i in self.items)

    def to_dict(self) -> dict:
        return {
            "items": [i.to_dict() for i in self.items],
            "total": self.total, "done": self.done, "failed": self.failed,
            "finished": self.finished, "schema_version": SCHEMA_VERSION,
        }


def run_batch(
    paths: list[str],
    convert_fn: Callable[..., dict],
    out_dir: Optional[str] = None,
    on_item: Optional[Callable[[BatchResult], None]] = None,
) -> BatchResult:
    """Convert each path via convert_fn(path, out_dir). One failure never stops
    the batch — it's recorded on its item and the rest continue. `on_item` (if
    given) is called after each state transition so callers can poll progress.
    """
    result = BatchResult(items=[BatchItem(p) for p in paths])

    def notify():
        if on_item:
            on_item(result)

    notify()  # initial all-pending snapshot
    for item in result.items:
        item.status = "running"
        notify()
        try:
            r = convert_fn(item.path, out_dir)
            item.output_path = r.get("output_path")
            item.output_name = r.get("output_name")
            item.validated_ok = r.get("validated_ok")
            item.status = "done"
        except Exception as e:  # isolate per-file failures
            item.error = str(e)
            item.status = "error"
        notify()
    return result
