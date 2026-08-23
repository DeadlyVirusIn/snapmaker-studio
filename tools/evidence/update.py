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


def selfcheck_total() -> dict:
    sys.path.insert(0, str(ROOT / "backend"))
    from snapstudio_core import selfcheck
    report = selfcheck.run()
    return {"passed": report["passed"], "total": report["total"]}


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
    }
    OUT.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    for key in ("acceptance", "hardware", "selfcheck"):
        block = evidence[key]
        print(f"  {key}: {block['passed']}/{block['total']}")
    print(f"  backend: {args.backend} passed, {args.backend_skipped} skipped")
    print(f"  desktop: {args.desktop} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
