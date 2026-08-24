"""Regenerate the painted 3MF fixtures by round-tripping them through real slicers.

The fixtures in `backend/tests/fixtures/painted/` are committed, so the test suite
runs everywhere. This script is how they were produced and how they would be
produced again — against a newer slicer, say, or after a change to Studio's
encoder. It needs a slicer on the machine and is deliberately not part of CI.

    python tools/fixtures/make_painted.py --prusa "C:/…/prusa-slicer-console.exe"
    python tools/fixtures/make_painted.py --orca  "C:/…/orca-slicer.exe"

What it does, per dialect:

1. Writes paint onto a copy of a project using Studio's own encoder — four whole
   facets in slot 1, two in slot 2, one subdivided across slots 1-4 with a
   quarter left unpainted, and one in slot 5.
2. Hands that file to the slicer and asks it to write the project back out.
3. Checks the result: the slicer must have kept every attribute, and Studio's
   reader must decode the slots that were painted.

Step 3 is the point. The slicer re-serialises paint from its own decoded model,
so a byte-identical result means Studio and the slicer read the format the same
way. A mismatch is a real finding and the script says so rather than overwriting
a good fixture with a bad one.

Nothing here writes into the repository unless every check passes, and the
original project is never modified — the paint is injected into a copy.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from snapstudio_core import paint_codec  # noqa: E402
from snapstudio_core import painted_color  # noqa: E402

FIXTURES = ROOT / "backend" / "tests" / "fixtures" / "painted"
CUBE_STL = ROOT / "examples" / "sample_cube.stl"
U1_PROJECT = ROOT / "examples" / "sample_cube_U1.3mf"

# facet index -> what is painted on it. Chosen to exercise a whole-facet state, a
# subdivision, an unpainted region inside a painted facet, and a slot past the
# first four.
PLAN = {
    0: 1, 1: 1, 2: 1, 3: 1,
    4: 2, 5: 2,
    6: (0, [1, (1, [2, 3]), 0, 4]),
    8: 5,
}
EXPECTED_SLOTS = [1, 2, 3, 4, 5]


def inject(source: Path, target: Path, attribute: str) -> int:
    """Write the paint plan onto a copy of `source`. The original is untouched."""
    with zipfile.ZipFile(source) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    painted_facets = 0
    for name, blob in list(parts.items()):
        if not name.lower().endswith(".model") or b"<triangle" not in blob:
            continue
        text = blob.decode("utf-8")
        index = 0

        def paint(match):
            nonlocal index, painted_facets
            facet, index = index, index + 1
            tree = PLAN.get(facet)
            if tree is None:
                return match.group(0)
            painted_facets += 1
            encoded = paint_codec.encode_tree(tree)
            return match.group(0)[:-2] + f' {attribute}="{encoded}"/>'

        text = re.sub(r"<triangle\b[^>]*/>", paint, text)
        if attribute.startswith("slic3rpe") and "MmPaintingVersion" not in text:
            text = text.replace(
                '<metadata name="slic3rpe:Version3mf">1</metadata>',
                '<metadata name="slic3rpe:Version3mf">1</metadata>'
                '<metadata name="slic3rpe:MmPaintingVersion">1</metadata>')
        parts[name] = text.encode("utf-8")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, blob in parts.items():
            archive.writestr(name, blob)
    return painted_facets


def attributes(path: Path) -> list[str]:
    out = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if name.endswith(".model"):
                out += re.findall(
                    r'(?:paint_color|slic3rpe:mmu_segmentation)="([^"]*)"',
                    archive.read(name).decode("utf-8", "ignore"))
    return out


def run(command: list[str]) -> None:
    print("   ", " ".join(command))
    result = subprocess.run(command, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        tail = (result.stderr or result.stdout or "").strip().splitlines()[-3:]
        raise SystemExit(f"the slicer refused: {' / '.join(tail)}")


def build_prusa(exe: Path, work: Path) -> Path:
    project = work / "cube.3mf"
    run([str(exe), "--datadir", str(work / "datadir"), "--export-3mf",
         "-o", str(project), str(CUBE_STL)])
    painted_in = work / "painted-in.3mf"
    facets = inject(project, painted_in, "slic3rpe:mmu_segmentation")
    print(f"    painted {facets} facets")
    out = work / "prusaslicer-painted-cube.3mf"
    run([str(exe), "--datadir", str(work / "datadir"), "--export-3mf",
         "-o", str(out), str(painted_in)])
    return out


def build_orca(exe: Path, work: Path) -> Path:
    painted_in = work / "painted-u1-in.3mf"
    facets = inject(U1_PROJECT, painted_in, "paint_color")
    print(f"    painted {facets} facets")
    # Orca resolves the export name against --outputdir, so it takes a bare name.
    run([str(exe), "--export-3mf=orcaslicer-painted-cube.3mf",
         "--outputdir", str(work), str(painted_in)])
    return work / "orcaslicer-painted-cube.3mf"


def verify(original_plan_source: Path, produced: Path) -> None:
    """The slicer's output must say what was painted, or the fixture is not one."""
    written = attributes(produced)
    intended = attributes(original_plan_source)
    if written != intended:
        raise SystemExit(
            "the slicer rewrote the paint data. That is a genuine finding about "
            "the format and must be understood before this fixture is trusted:\n"
            f"  wrote:    {written}\n  expected: {intended}")
    result = painted_color.read(str(produced))
    if result["slots_referenced"] != EXPECTED_SLOTS:
        raise SystemExit(f"Studio read slots {result['slots_referenced']}, "
                         f"expected {EXPECTED_SLOTS}")
    if result["malformed_triangle_count"]:
        raise SystemExit("Studio could not decode part of the slicer's own output")
    print(f"    ok — {result['painted_triangle_count']} painted facets, "
          f"slots {result['slots_referenced']}, "
          f"sha256 {hashlib.sha256(produced.read_bytes()).hexdigest()[:12]}…")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prusa", type=Path, help="path to prusa-slicer-console.exe")
    parser.add_argument("--orca", type=Path, help="path to orca-slicer.exe")
    parser.add_argument("--install", action="store_true",
                        help="copy the verified results into the fixtures directory")
    args = parser.parse_args()
    if not args.prusa and not args.orca:
        parser.error("give at least one slicer to drive")

    work = Path(tempfile.mkdtemp(prefix="snapstudio-painted-"))
    produced: list[Path] = []
    if args.prusa:
        print("PrusaSlicer dialect (slic3rpe:mmu_segmentation)")
        out = build_prusa(args.prusa, work)
        verify(work / "painted-in.3mf", out)
        produced.append(out)
    if args.orca:
        print("Orca/Bambu dialect (paint_color)")
        out = build_orca(args.orca, work)
        verify(work / "painted-u1-in.3mf", out)
        produced.append(out)

    if args.install:
        FIXTURES.mkdir(parents=True, exist_ok=True)
        for path in produced:
            shutil.copy2(path, FIXTURES / path.name)
            print(f"installed {FIXTURES / path.name}")
        print("Update PROVENANCE.md with the new sizes, hashes and slicer versions.")
    else:
        print(f"\nleft in {work} — pass --install to put them in the repository")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
