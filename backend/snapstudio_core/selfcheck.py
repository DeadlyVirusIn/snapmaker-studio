"""Self-check — run the real pipeline end to end and report what worked.

Written for someone evaluating Studio who does not want to install a desktop app
first. It exercises production code paths on a real 3MF: the same parser, the same
Doctors, the same prepare pipeline, the same fidelity audit. Nothing is stubbed
and nothing is compared against a stored constant — each check asserts a property
of the result, so a check can only pass if the feature genuinely worked.

The fixture is built at runtime rather than shipped, so this works from a frozen
install with no `examples/` directory. It is a real project archive: an object
placed at a larger printer's coordinates, authored for another machine, with two
extra colours introduced part-way up.

Everything is written to a temporary directory. The check verifies the input file
is byte-identical afterwards, which is the one property that would matter most if
it were ever wrong.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

SCHEMA_VERSION = "selfcheck/1"

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"

# A 10 mm cube. Small on purpose: the point of the fixture is where it sits, not
# how big it is.
_CUBE_VERTS = [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0),
               (0, 0, 10), (10, 0, 10), (10, 10, 10), (0, 10, 10)]
_CUBE_TRIS = [(0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6), (0, 5, 1), (0, 4, 5),
              (2, 6, 7), (2, 7, 3), (1, 5, 6), (1, 6, 2), (0, 3, 7), (0, 7, 4)]


def _model_xml(x: float, y: float) -> str:
    verts = "".join(f'<vertex x="{vx}" y="{vy}" z="{vz}"/>' for vx, vy, vz in _CUBE_VERTS)
    tris = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in _CUBE_TRIS)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xml:lang="en-US"'
        ' xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        '<metadata name="Application">SelfCheckFixture-1</metadata>'
        f'<resources><object id="1" type="model"><mesh>'
        f"<vertices>{verts}</vertices><triangles>{tris}</triangles>"
        "</mesh></object></resources>"
        f'<build><item objectid="1" transform="1 0 0 0 1 0 0 0 1 {x} {y} 0"/></build>'
        "</model>"
    )


def build_fixture(directory: Path) -> Path:
    """A foreign project with a real problem in it: authored for a 350 mm bed and
    placed near that bed's right edge, so it lands off a U1 plate."""
    settings = {
        "printer_model": "Bambu Lab H2D",
        "printer_settings_id": "Bambu Lab H2D 0.4 nozzle",
        "printable_area": ["0x0", "350x0", "350x350", "0x350"],
        "printable_height": "325",
        "filament_colour": ["#FF0000", "#00FF00", "#0000FF", "#FFFFFF", "#111111", "#EEEE00"],
        "filament_type": ["PLA"] * 6,
        "nozzle_diameter": ["0.4", "0.4", "0.4", "0.4"],
        "layer_height": "0.12",
        "initial_layer_print_height": "0.2",
        "exclude_object": "0",
        "brim_type": "auto_brim",
    }
    model_settings = (
        "<config>"
        '<object id="1"><metadata key="extruder" value="0"/></object>'
        '<object id="2"><metadata key="extruder" value="1"/></object>'
        '<object id="3"><metadata key="extruder" value="2"/></object>'
        '<object id="4"><metadata key="extruder" value="3"/></object>'
        '<plate><metadata key="plater_id" value="1"/></plate>'
        "</config>"
    )
    custom_gcode = (
        "<custom_gcodes_per_layer><plate>"
        '<layer top_z="8.2" type="2" extruder="5" color="#111111"/>'
        '<layer top_z="19.4" type="2" extruder="6" color="#EEEE00"/>'
        "</plate></custom_gcodes_per_layer>"
    )
    path = directory / "selfcheck_sample.3mf"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("_rels/.rels", "<Relationships/>")
        z.writestr("3D/3dmodel.model", _model_xml(305.0, 175.0))
        z.writestr("Metadata/project_settings.config", json.dumps(settings, indent=2))
        z.writestr("Metadata/model_settings.config", model_settings)
        z.writestr("Metadata/custom_gcode_per_layer.xml", custom_gcode)
        z.writestr("Metadata/plate_1.gcode", "; toolpaths from the original printer\nG1 X0\n")
    return path


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class _Runner:
    def __init__(self) -> None:
        self.checks: list[dict] = []

    def check(self, name: str, fn) -> object:
        """Run one check. A raised exception is a failure with its reason, never a
        crash — the whole point is to produce a report even when something breaks."""
        try:
            detail = fn()
        except Exception as exc:  # noqa: BLE001 - the report is the error channel
            self.checks.append({"name": name, "status": FAIL,
                                "detail": f"{type(exc).__name__}: {exc}"})
            return None
        if detail is False:
            self.checks.append({"name": name, "status": FAIL, "detail": "check returned false"})
            return None
        self.checks.append({"name": name, "status": PASS,
                            "detail": detail if isinstance(detail, str) else ""})
        return detail


def run(sample: str | None = None) -> dict:
    """Execute the pipeline and return a structured report. Never raises."""
    from . import (color_plan, ecosystem, fidelity, geometry, plate_placement,
                   project_cost, project_traits)
    from .container import ThreeMF
    from .convert import convert_to_u1
    from .errors import UnsafeArchive

    runner = _Runner()
    workdir = Path(tempfile.mkdtemp(prefix="snapstudio-selfcheck-"))
    fixture_source = "generated"
    try:
        if sample:
            source = workdir / Path(sample).name
            shutil.copy2(sample, source)
            fixture_source = str(Path(sample).name)
        else:
            source = build_fixture(workdir)
        before_hash = _sha(source)

        def parse():
            tm = ThreeMF.open(source)
            assert "3D/3dmodel.model" in tm.list_parts()
            return f"{len(tm.list_parts())} parts read"

        runner.check("Project parsing", parse)

        def geom():
            items = geometry.build_item_dims(str(source))
            assert items, "no placed objects found"
            return f"{len(items)} placed object(s) measured"

        runner.check("Geometry analysis", geom)

        def traits():
            t = project_traits.extract(str(source))
            assert t["readable"] is True
            graded = [k for k in project_traits.TRAIT_KEYS
                      if isinstance(t.get(k), dict) and t[k].get("confidence")]
            assert len(graded) == len(project_traits.TRAIT_KEYS)
            return f"{len(graded)} traits, each with a confidence tier"

        runner.check("Project traits", traits)

        placement = runner.check(
            "Placement diagnosis",
            lambda: _placement_detects(plate_placement, source))

        prepared = runner.check("Safe prepared copy",
                                lambda: _prepare(convert_to_u1, source, workdir))

        runner.check("Orca import compatibility",
                     lambda: _compat_applied(prepared))

        runner.check("Fidelity audit", lambda: _fidelity(fidelity, source, prepared))

        moved = runner.check("Placement fix",
                             lambda: _placement_fix(plate_placement, source, workdir))

        runner.check("Cost evidence", lambda: _cost(project_cost, source))

        runner.check("Colour planning", lambda: _colors(color_plan, source))

        runner.check("Ecosystem recommendation", lambda: _ecosystem(ecosystem, source))

        runner.check("Preflight without a printer", lambda: _preflight(source))

        runner.check("Untrusted archive limits",
                     lambda: _archive_limits(ThreeMF, UnsafeArchive, workdir))

        runner.check("Original unchanged",
                     lambda: _unchanged(source, before_hash))

        runner.check("API schema", _api_schema)

        passed = sum(1 for c in runner.checks if c["status"] == PASS)
        total = len(runner.checks)
        return {
            "schema_version": SCHEMA_VERSION,
            "sample": fixture_source,
            "checks": runner.checks,
            "passed": passed,
            "total": total,
            "ok": passed == total,
            "summary": f"{passed}/{total} checks passed",
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


# --- individual checks ------------------------------------------------------

def _placement_detects(plate_placement, source: Path) -> str:
    report = plate_placement.assess(str(source))
    assert report["available"], report.get("reason")
    assert report["off_plate"], "the off-plate object was not detected"
    edge = report["off_plate"][0]["edges"]
    return f"{len(report['off_plate'])} object(s) off the plate, past the {edge} edge"


def _prepare(convert_to_u1, source: Path, workdir: Path):
    result = convert_to_u1(str(source), out_dir=str(workdir / "prepared"))
    assert result.output_path, "no prepared file was written"
    assert Path(result.output_path).exists()
    assert Path(result.output_path).resolve() != Path(source).resolve()
    return result


def _compat_applied(prepared) -> str:
    assert prepared is not None, "prepare did not run"
    with zipfile.ZipFile(prepared.output_path) as z:
        names = z.namelist()
        cfg = json.loads(z.read("Metadata/project_settings.config"))
    assert cfg.get("exclude_object") == "1", "object exclusion was not enabled"
    assert cfg.get("brim_type") == "no_brim", "the automatic brim was not suppressed"
    assert not any(n.endswith(".gcode") for n in names), "stale toolpaths survived"
    assert cfg.get("print_settings_id", "").startswith("0.12"), \
        "the preset label does not describe the project's layer height"
    return "exclusion on, auto-brim off, stale toolpaths removed, preset label matches"


def _fidelity(fidelity, source: Path, prepared) -> str:
    assert prepared is not None, "prepare did not run"
    report = fidelity.audit(str(source), prepared.output_path)
    assert report["available"], report.get("reason")
    assert not report["unverified"], f"unaccounted elements: {report['unverified']}"
    assert report["claims"]["fully_accounted"] is True
    kept = len(report["kept"])
    return f"{kept} element(s) accounted for, none unverified"


def _placement_fix(plate_placement, source: Path, workdir: Path) -> str:
    result = plate_placement.prepare_placed_copy(str(source), out_dir=str(workdir / "placed"))
    assert result["ok"], result.get("reason")
    assert not result["after"]["off_plate"], "objects are still off the plate"
    return f"{result['objects_moved']} object(s) moved, re-checked clean"


def _cost(project_cost, source: Path) -> str:
    """The fixture carries stale toolpaths but no material figures, so the correct
    behaviour is a refusal that says which of the two situations it is — the fix
    differs. A number here would be the bug."""
    report = project_cost.estimate(str(source))
    assert report["available"] is False, "a cost was invented for a project with no figures"
    reason = report["reason"]
    assert ("not been sliced" in reason) or ("does not record how much" in reason), reason
    assert report["basis"] == project_cost.BASIS_NONE

    # And the other half: a project that *does* carry figures must be costed from
    # them rather than refused.
    priced = project_cost.from_traits({
        "is_sliced": {"value": True, "confidence": "confirmed", "evidence": "selfcheck"},
        "plate_predictions": [{
            "index": "1", "predicted_seconds": 3600.0, "predicted_weight_g": 100.0,
            "filaments": [{"id": "1", "type": "PLA", "used_g": 100.0, "used_m": 33.5}],
        }],
    }, price_per_kg=20.0)
    assert priced["available"] is True and priced["cost"] == 2.0, priced
    return "no figures → refused with a reason; real figures → costed from them"


def _colors(color_plan, source: Path) -> str:
    report = color_plan.analyse(str(source), toolheads=4)
    assert report["available"], report.get("reason")
    assert report["color_count"] == 6
    assert len(report["simultaneous"]) == 4
    assert len(report["layer_based"]) == 2
    assert report["verdict"] == color_plan.POSSIBLE_WITH_SWAPS
    heights = ", ".join(f"{c['from_z_mm']:g} mm" for c in report["layer_based"])
    return f"6 colours on 4 toolheads; 2 arrive at {heights}"


def _ecosystem(ecosystem, source: Path) -> str:
    advice = ecosystem.advise(str(source))
    assert advice["primary"], "no tool was recommended"
    assert advice["primary"]["why"], "the recommendation carried no reason"
    assert advice["primary"]["installed"] is False, \
        "a tool was claimed installed without a path being found"
    return f"{advice['primary']['name']} — {advice['primary']['why'][0][:60]}…"


def _preflight(source: Path) -> str:
    from snapstudio_api import service

    report = service.preflight(str(source), host=None)
    assert report["printer_reachable"] is False
    assert report["unknowns"], "no printer, yet nothing was reported as unknown"
    for check in report["unknowns"]:
        blob = f"{check['title']} {check['consequence']}".lower()
        assert "not supported" not in blob, "an undetected capability was called unsupported"
    return f"{len(report['unknowns'])} check(s) correctly reported as unknown"


def _archive_limits(ThreeMF, UnsafeArchive, workdir: Path) -> str:
    from . import container

    bomb = workdir / "bomb.3mf"
    with zipfile.ZipFile(bomb, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("big.bin", b"\0" * (64 * 1024 * 1024))
    original = container.MAX_TOTAL_UNCOMPRESSED
    container.MAX_TOTAL_UNCOMPRESSED = 4 * 1024 * 1024
    try:
        try:
            ThreeMF.open(bomb)
        except UnsafeArchive:
            return "a highly compressible archive was refused, not buffered"
        raise AssertionError("an oversized archive was accepted")
    finally:
        container.MAX_TOTAL_UNCOMPRESSED = original


def _unchanged(source: Path, before_hash: str) -> str:
    assert _sha(source) == before_hash, "the input file was modified"
    return "input file is byte-identical after every operation"


def _api_schema() -> str:
    """Start the real loopback service and call the documented routes."""
    import threading
    import urllib.request

    from snapstudio_api.server import build_server

    httpd, token = build_server(port=0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        port = httpd.server_address[1]
        routes = {
            "/project_traits": ({"path": "none"}, ["schema_version", "readable"]),
            "/ecosystem_advice": ({"path": "none"}, ["primary", "summary", "traits"]),
            "/project_cost": ({"path": "none"}, ["available", "basis"]),
            "/placement_check": ({"path": "none"}, ["available", "items"]),
            "/color_plan": ({"path": "none"}, ["verdict", "headline"]),
            "/fidelity": ({"original": "none", "prepared": "none"}, ["rows", "claims"]),
            "/fix_history": ({}, ["entries"]),
        }
        for route, (payload, required) in routes.items():
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}{route}", data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", "X-Auth-Token": token})
            with urllib.request.urlopen(req, timeout=10) as response:
                body = json.loads(response.read())
            missing = [field for field in required if field not in body]
            assert not missing, f"{route} is missing {missing}"
        return f"{len(routes)} documented routes answered with their fields"
    finally:
        httpd.shutdown()
        httpd.server_close()


def format_table(report: dict) -> str:
    """The human-readable form. Deliberately plain so it pastes into an issue."""
    lines = ["Snapmaker Studio self-check", ""]
    width = max((len(c["name"]) for c in report["checks"]), default=20) + 4
    for check in report["checks"]:
        lines.append(f"{check['name'].ljust(width)}{check['status']}")
        if check["detail"]:
            lines.append(f"{'':{width}}  {check['detail']}")
    lines.append("")
    lines.append(report["summary"])
    return "\n".join(lines)
