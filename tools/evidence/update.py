"""Write the canonical evidence numbers the public documents must agree with.

The recurring defect in this project is not wrong code, it is documents that
describe a state the product has left. Counts in particular: a README claiming
21/21 when the harness now runs 27, or 15/15 when the self-check has 18.

The fix is to have exactly one source. This reads the artefacts the harnesses
themselves wrote, runs the self-check to count its own checks, and records the
result in docs/internal/evidence.json. `test_evidence_consistency.py` then fails
the build when a current-state document disagrees with it.

    python tools/evidence/update.py --backend 716 --backend-skipped 3 --desktop 263

Backend and desktop counts are passed in because running both suites from inside
this script would be slower and no more truthful than running them and reading the
number off the end.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METADATA = ROOT / "docs" / "RELEASE_METADATA.md"
INTERNAL = ROOT / "docs" / "internal"
OUT = INTERNAL / "evidence.json"


def current_version() -> str:
    text = METADATA.read_text(encoding="utf-8")
    block = text[text.index("## Current release"):]
    match = re.search(r"\|\s*Version\s*\|\s*v?([^\s|]+)\s*\|", block)
    if not match:
        raise SystemExit("RELEASE_METADATA.md has no current version")
    return match.group(1)


def harness(kind: str, version: str) -> dict:
    path = INTERNAL / f"{kind}-{version}.json"
    if not path.exists():
        raise SystemExit(f"missing {path.name} — run the {kind} harness against the release first")
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"passed": data["passed"], "total": data["total"], "report": path.name}


def mp4_seconds(path: Path) -> int | None:
    """Duration of an MP4, read from its own `mvhd` box.

    Done here rather than with ffprobe because the demo's length is quoted in
    public documents, and a claim in a document should be checkable by the same
    test run that checks everything else — without needing a tool installed.
    """
    if not path.exists():
        return None
    data = path.read_bytes()
    marker = data.find(b"mvhd")
    if marker == -1:
        return None
    # After the four-byte type comes a one-byte version and three flag bytes,
    # then creation and modification times, then the timescale and duration. The
    # times are 32-bit in version 0 and 64-bit in version 1.
    version = data[marker + 4]
    if version == 1:
        scale = int.from_bytes(data[marker + 8 + 16:marker + 8 + 20], "big")
        duration = int.from_bytes(data[marker + 8 + 20:marker + 8 + 28], "big")
    else:
        scale = int.from_bytes(data[marker + 8 + 8:marker + 8 + 12], "big")
        duration = int.from_bytes(data[marker + 8 + 12:marker + 8 + 16], "big")
    return round(duration / scale) if scale else None


def selfcheck_total() -> dict:
    sys.path.insert(0, str(ROOT / "backend"))
    from snapstudio_core import selfcheck
    report = selfcheck.run()
    return {"passed": report["passed"], "total": report["total"]}


def _screenshots_dir(version: str) -> str:
    """Which screenshot folder the public documents should be pointing at."""
    candidate = ROOT / "docs" / "screenshots" / f"v{version}"
    return f"docs/screenshots/v{version}" if candidate.exists() else ""


def _today() -> str:
    import datetime

    return datetime.date.today().isoformat()


def _installer_block() -> dict:
    """The installer this release publishes, read from the canonical metadata."""
    text = METADATA.read_text(encoding="utf-8")
    block = text[text.index("## Current release"):]
    if "## Previous release" in block:
        block = block[:block.index("## Previous release")]

    def field(name: str):
        found = re.search(r"\|\s*" + re.escape(name) + r"\s*\|\s*(.+?)\s*\|", block)
        return found.group(1).strip() if found else None

    size = field("Size (bytes)")
    return {
        "name": (field("Installer") or "").strip("`") or None,
        "size_bytes": int(size.replace(",", "")) if size else None,
        "sha256": (field("SHA256") or "").strip("`") or None,
        "url": field("Release URL"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", type=int, required=True, help="pytest passed count")
    parser.add_argument("--backend-skipped", type=int, default=0)
    parser.add_argument("--desktop", type=int, required=True, help="vitest passed count")
    args = parser.parse_args()

    version = current_version()
    evidence = {
        "schema_version": "evidence/1",
        "version": version,
        "acceptance": harness("acceptance", version),
        "hardware": harness("hardware", version),
        "selfcheck": selfcheck_total(),
        "backend": {"passed": args.backend, "skipped": args.backend_skipped},
        "desktop": {"passed": args.desktop},
        "demo": {
            "seconds": mp4_seconds(ROOT / "docs" / "media" / "snapmaker-studio-demo.mp4"),
            "file": "docs/media/snapmaker-studio-demo.mp4",
        },
        "screenshots_dir": _screenshots_dir(version),
    }
    OUT.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")

    # And the immutable copy. `evidence.json` points at the current release and is
    # rewritten every time; the snapshot is what a document describing *that*
    # release quotes for as long as the release exists. Overwriting one would
    # rewrite what was true when somebody downloaded that installer — which is how
    # a shipped release came to be described by a later release's numbers.
    snapshot_dir = INTERNAL / "evidence"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = snapshot_dir / f"{version}.json"
    snapshot = dict(evidence)
    snapshot["schema_version"] = "evidence-snapshot/1"
    snapshot["installer"] = _installer_block()
    snapshot["released"] = _today()
    snapshot["source"] = "recorded when this release was published"
    if snapshot_path.exists():
        existing = json.loads(snapshot_path.read_text(encoding="utf-8"))
        differing = [key for key in ("acceptance", "hardware", "selfcheck", "backend",
                                     "desktop", "demo", "installer")
                     if existing.get(key) != snapshot.get(key)]
        if differing:
            raise SystemExit(
                f"{snapshot_path.name} already records this release and differs in "
                f"{differing}. A published release's evidence does not change — if "
                "these numbers are the truth, this is a different release and needs "
                "its own version.")
    else:
        snapshot_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")
        print(f"wrote {snapshot_path.relative_to(ROOT)}")
    for key in ("acceptance", "hardware", "selfcheck"):
        block = evidence[key]
        print(f"  {key}: {block['passed']}/{block['total']}")
    print(f"  backend: {args.backend} passed, {args.backend_skipped} skipped")
    print(f"  desktop: {args.desktop} passed")
    print(f"  demo: {evidence['demo']['seconds']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
