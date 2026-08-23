"""Fetch the real slicer project files Studio is tested against.

These are genuine OrcaSlicer, BambuStudio and PrusaSlicer project 3MFs. They are
not committed: all three projects are AGPL-3.0, and one of the files embeds an
upstream developer's local path including their username, which Studio's own
rules forbid in tracked files. Fetching them costs nothing and keeps both
problems out of the repository.

See REAL_WORLD_PROVENANCE.md for what each file is and why it is useful.

    python tests/fixtures/fetch_real_world.py            # download and verify
    python tests/fixtures/fetch_real_world.py --check    # report only
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "real-world"

# name -> (url, sha256, why)
FIXTURES: dict[str, tuple[str, str, str]] = {
    "orca-pa-line-dual.3mf": (
        "https://raw.githubusercontent.com/SoftFever/OrcaSlicer/main/"
        "resources/calib/pressure_advance/auto_pa_line_dual.3mf",
        "",
        "a real multi-material OrcaSlicer project with external object parts",
    ),
    "orca-badge.3mf": (
        "https://raw.githubusercontent.com/SoftFever/OrcaSlicer/main/"
        "resources/handy_models/OrcaBadge.3mf",
        "",
        "spaces in part names and a 6-byte project_settings.config",
    ),
    "bambu-pa-pattern.3mf": (
        "https://raw.githubusercontent.com/bambulab/BambuStudio/master/"
        "resources/calib/pressure_advance/pa_pattern.3mf",
        "",
        "90 KB of real custom_gcode_per_layer.xml",
    ),
    "prusa-seam-test.3mf": (
        "https://raw.githubusercontent.com/prusa3d/PrusaSlicer/master/"
        "tests/data/seam_test_object.3mf",
        "",
        "the PrusaSlicer dialect: Metadata/Slic3r_PE.config",
    ),
}

# Upstream files can change. Hashes are recorded on first successful fetch into
# MANIFEST-real-world.txt so a later change is visible rather than silent.
MANIFEST = HERE / "MANIFEST-real-world.txt"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest() -> dict[str, str]:
    if not MANIFEST.exists():
        return {}
    out = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, _, name = line.partition("  ")
        if digest and name:
            out[name] = digest
    return out


def save_manifest(entries: dict[str, str]) -> None:
    lines = [
        "# SHA-256 of each fetched fixture, recorded on first successful download.",
        "# A mismatch on a later run means upstream changed — check before accepting.",
    ]
    lines += [f"{digest}  {name}" for name, digest in sorted(entries.items())]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fetch(name: str, url: str, expected: str) -> tuple[bool, str]:
    TARGET.mkdir(parents=True, exist_ok=True)
    dest = TARGET / name
    if dest.exists():
        return True, f"already present ({dest.stat().st_size:,} bytes)"
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "snapmaker-studio-tests"})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
    except Exception as exc:  # noqa: BLE001 — the message is the whole point
        return False, f"download failed: {type(exc).__name__}: {exc}"
    if not data:
        return False, "download was empty"
    dest.write_bytes(data)
    digest = sha256(dest)
    if expected and digest != expected:
        dest.unlink(missing_ok=True)
        return False, f"sha256 mismatch (expected {expected[:12]}…, got {digest[:12]}…)"
    return True, f"{len(data):,} bytes, sha256 {digest[:12]}…"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="report what is present without downloading")
    args = parser.parse_args()

    manifest = load_manifest()
    failures = 0

    for name, (url, expected, why) in FIXTURES.items():
        dest = TARGET / name
        if args.check:
            state = "present" if dest.exists() else "missing"
            print(f"{state:8} {name}  — {why}")
            continue
        ok, detail = fetch(name, url, expected or manifest.get(name, ""))
        print(f"{'ok  ' if ok else 'FAIL'}  {name}  — {detail}")
        if ok and dest.exists():
            manifest[name] = sha256(dest)
        else:
            failures += 1

    if not args.check:
        save_manifest(manifest)
        print(f"\n{len(FIXTURES) - failures}/{len(FIXTURES)} fixtures available in {TARGET}")
        print("These files are AGPL-3.0 and are deliberately not committed —"
              " see REAL_WORLD_PROVENANCE.md")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
