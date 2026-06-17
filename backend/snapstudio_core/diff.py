from __future__ import annotations
from dataclasses import dataclass, field, asdict
from .container import ThreeMF
from .config_io import load_project_settings
from .fingerprint import compute_fingerprint

SETTINGS = "Metadata/project_settings.config"
SCHEMA_VERSION = "diff/1"


@dataclass
class ProjectDiff:
    parts_added: list           # parts in B not in A
    parts_removed: list         # parts in A not in B
    geometry_changed: bool      # object .model bytes differ (preservation check)
    object_count: list          # [a, b]
    plate_count: list           # [a, b]
    filament_count: list        # [a, b]
    painted_triangles: list     # [a, b]
    settings_changed: list = field(default_factory=list)   # [{key, old, new}]
    settings_added: list = field(default_factory=list)     # keys in B not in A
    settings_removed: list = field(default_factory=list)   # keys in A not in B

    @property
    def has_changes(self) -> bool:
        return bool(self.parts_added or self.parts_removed or self.geometry_changed
                    or self.settings_changed or self.settings_added or self.settings_removed)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["schema_version"] = SCHEMA_VERSION
        d["has_changes"] = self.has_changes
        return d


def _settings(tm: ThreeMF) -> dict:
    return load_project_settings(tm.read_part(SETTINGS)) if tm.has_part(SETTINGS) else {}


def diff_projects(a: ThreeMF, b: ThreeMF) -> ProjectDiff:
    """Read-only structural/geometry/settings comparison of two 3MF projects."""
    pa, pb = set(a.list_parts()), set(b.list_parts())
    fa, fb = compute_fingerprint(a), compute_fingerprint(b)

    # geometry: same preservation logic validate() uses — compare object .model hashes
    geometry_changed = fa.object_part_sha256 != fb.object_part_sha256

    sa, sb = _settings(a), _settings(b)
    settings_added = sorted(set(sb) - set(sa))
    settings_removed = sorted(set(sa) - set(sb))
    settings_changed = [{"key": k, "old": sa[k], "new": sb[k]}
                        for k in sorted(set(sa) & set(sb)) if sa[k] != sb[k]]

    return ProjectDiff(
        parts_added=sorted(pb - pa),
        parts_removed=sorted(pa - pb),
        geometry_changed=geometry_changed,
        object_count=[fa.object_count, fb.object_count],
        plate_count=[fa.plate_count, fb.plate_count],
        filament_count=[fa.filament_count, fb.filament_count],
        painted_triangles=[sum(fa.painted_triangles.values()), sum(fb.painted_triangles.values())],
        settings_changed=settings_changed,
        settings_added=settings_added,
        settings_removed=settings_removed,
    )
