"""Freeze a release's evidence at the moment it was published, and never again.

The recurring failure in this project was documents drifting away from the product.
The fix for that was one canonical evidence file — and that fix created a worse
problem, because there is only one of it. Regenerating it for a new release
rewrote the numbers *every* document quoted, including the sections describing
releases that had already shipped. A reader of TRUST_STATUS.md was told that
v0.6.0 had been verified with 967 tests, which is not true of anything: v0.6.0 was
verified with 822, and 967 is a count from a suite that did not exist yet.

So evidence is now per release and immutable:

    docs/internal/evidence/0.6.0.json     what was true when 0.6.0 shipped
    docs/internal/evidence/0.6.1.json     what was true when 0.6.1 shipped
    docs/internal/evidence.json           a copy of the current one, for callers

Publishing a release adds a file. It never edits one.

Historical snapshots are reconstructed here from the only authority there is: what
the repository recorded *at that release's own tag*. Nothing is copied forward
from today's suite, and a value the release did not record comes back as null with
a note saying so, because "not recorded" is a fact and a plausible number is not.

    python tools/evidence/snapshot.py --rebuild-history
    python tools/evidence/snapshot.py --version 0.6.2 --backend 970 --backend-skipped 3 --desktop 293
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOTS = ROOT / "docs" / "internal" / "evidence"
CURRENT = ROOT / "docs" / "internal" / "evidence.json"

SCHEMA = "evidence-snapshot/1"

NOT_RECORDED = "not recorded at this release"


def git_show(ref: str, path: str) -> str | None:
    """A file exactly as it was at a tag, or None if it was not there yet."""
    result = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT,
                            capture_output=True)
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", "replace")


def tag_date(tag: str) -> str | None:
    result = subprocess.run(["git", "log", "-1", "--format=%cs", tag], cwd=ROOT,
                            capture_output=True, text=True)
    return result.stdout.strip() or None if result.returncode == 0 else None


def _table_value(block: str, field: str) -> str | None:
    match = re.search(rf"\|\s*{re.escape(field)}\s*\|\s*(.+?)\s*\|", block)
    return match.group(1).strip() if match else None


def installer_from(metadata: str | None) -> dict:
    """The installer this release actually published, read from its own metadata."""
    if not metadata or "## Current release" not in metadata:
        return {"name": None, "size_bytes": None, "sha256": None, "url": None,
                "note": NOT_RECORDED}
    block = metadata[metadata.index("## Current release"):]
    block = block[:block.index("## ", 10)] if "## " in block[10:] else block
    size = _table_value(block, "Size (bytes)")
    return {
        "name": (_table_value(block, "Installer") or "").strip("`") or None,
        "size_bytes": int(size.replace(",", "")) if size else None,
        "sha256": (_table_value(block, "SHA256") or "").strip("`") or None,
        "url": _table_value(block, "Release URL"),
    }


def _trust_counts(trust: str | None) -> dict:
    """Backend, desktop and self-check counts as that release's own TRUST_STATUS
    stated them. Only the first occurrence: the file lists newest first, so the
    first row is the release the document leads with."""
    out = {"backend": None, "backend_skipped": None, "desktop": None,
           "selfcheck": None, "selfcheck_total": None}
    if not trust:
        return out
    backend = re.search(r"Backend tests \|[^|]*\|[^0-9]*(\d+) passed(?:, (\d+) skipped)?", trust)
    if backend:
        out["backend"] = int(backend.group(1))
        out["backend_skipped"] = int(backend.group(2)) if backend.group(2) else 0
    desktop = re.search(r"Desktop tests \|[^|]*\|[^0-9]*(\d+) passed", trust)
    if desktop:
        out["desktop"] = int(desktop.group(1))
    selfcheck = re.search(r"selfcheck` \|[^|]*—\s*(\d+)/(\d+)", trust)
    if selfcheck:
        out["selfcheck"] = int(selfcheck.group(1))
        out["selfcheck_total"] = int(selfcheck.group(2))
    return out


def _report(ref: str, kind: str, version: str) -> dict:
    name = f"{kind}-{version}.json"
    raw = git_show(ref, f"docs/internal/{name}")
    if not raw:
        return {"passed": None, "total": None, "report": None, "note": NOT_RECORDED}
    data = json.loads(raw)
    return {"passed": data["passed"], "total": data["total"], "report": name}


def reconstruct(version: str) -> dict:
    """Everything a released version recorded about itself, from its own tag."""
    tag = f"v{version}"
    evidence_raw = git_show(tag, "docs/internal/evidence.json")
    evidence = json.loads(evidence_raw) if evidence_raw else {}
    trust = git_show(tag, "docs/TRUST_STATUS.md")
    counts = _trust_counts(trust)

    acceptance = evidence.get("acceptance") or _report(tag, "acceptance", version)
    hardware = evidence.get("hardware") or _report(tag, "hardware", version)
    backend = evidence.get("backend") or (
        {"passed": counts["backend"], "skipped": counts["backend_skipped"]}
        if counts["backend"] is not None else {"passed": None, "skipped": None,
                                               "note": NOT_RECORDED})
    desktop = evidence.get("desktop") or (
        {"passed": counts["desktop"]} if counts["desktop"] is not None
        else {"passed": None, "note": NOT_RECORDED})
    selfcheck = evidence.get("selfcheck") or (
        {"passed": counts["selfcheck"], "total": counts["selfcheck_total"]}
        if counts["selfcheck"] is not None else {"passed": None, "total": None,
                                                 "note": NOT_RECORDED})
    demo = evidence.get("demo") or {"seconds": None, "note": NOT_RECORDED}

    return {
        "schema_version": SCHEMA,
        "version": version,
        "released": tag_date(tag),
        "installer": installer_from(git_show(tag, "docs/RELEASE_METADATA.md")),
        "acceptance": acceptance,
        "hardware": hardware,
        "selfcheck": selfcheck,
        "backend": backend,
        "desktop": desktop,
        "demo": demo,
        "screenshots_dir": evidence.get("screenshots_dir"),
        "source": (f"reconstructed from the repository at tag {tag}: "
                   "its own evidence.json, harness reports and TRUST_STATUS.md"),
    }


def write(snapshot: dict, *, overwrite: bool = False) -> Path:
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    target = SNAPSHOTS / f"{snapshot['version']}.json"
    if target.exists() and not overwrite:
        raise SystemExit(
            f"{target.name} already exists. A published release's evidence does not "
            "change; pass --overwrite only to correct a snapshot that was never right.")
    target.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def load(version: str) -> dict:
    path = SNAPSHOTS / f"{version.lstrip('v')}.json"
    if not path.exists():
        raise FileNotFoundError(f"no evidence snapshot for {version}")
    return json.loads(path.read_text(encoding="utf-8"))


def versions() -> list[str]:
    return sorted(p.stem for p in SNAPSHOTS.glob("*.json"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild-history", action="store_true",
                        help="reconstruct snapshots for every released tag")
    parser.add_argument("--version", help="the release to snapshot")
    parser.add_argument("--backend", type=int)
    parser.add_argument("--backend-skipped", type=int, default=0)
    parser.add_argument("--desktop", type=int)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.rebuild_history:
        tags = subprocess.run(["git", "tag", "--list", "v*"], cwd=ROOT,
                              capture_output=True, text=True).stdout.split()
        released = [t.lstrip("v") for t in tags if re.fullmatch(r"v\d+\.\d+\.\d+", t)]
        for version in sorted(released):
            snapshot = reconstruct(version)
            path = write(snapshot, overwrite=args.overwrite)
            print(f"{path.name}: acceptance {snapshot['acceptance'].get('passed')}/"
                  f"{snapshot['acceptance'].get('total')}, "
                  f"hardware {snapshot['hardware'].get('passed')}/"
                  f"{snapshot['hardware'].get('total')}, "
                  f"selfcheck {snapshot['selfcheck'].get('passed')}/"
                  f"{snapshot['selfcheck'].get('total')}, "
                  f"backend {snapshot['backend'].get('passed')}, "
                  f"desktop {snapshot['desktop'].get('passed')}")
        return

    if not args.version:
        raise SystemExit("give --version, or --rebuild-history")

    # A release that has not been tagged yet cannot be reconstructed from a tag.
    # `tools/evidence/update.py` writes that one, from the harness reports the
    # release itself just produced.
    raise SystemExit(
        "a release that has not been tagged is snapshotted by tools/evidence/update.py, "
        "which reads the harness reports it just produced; this script reconstructs "
        "history from tags")


if __name__ == "__main__":
    main()
