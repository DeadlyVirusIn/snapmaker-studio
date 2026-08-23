"""Ecosystem intelligence — which open tool is the right next step for *this* project.

The Snapmaker U1 has an unusually rich open-source ecosystem: slicer forks that
do things the official slicer cannot, browser extensions that convert projects at
download time, printer dashboards, command-line toolkits. The problem for a
person who bought a printer last week is not that these tools are missing. It is
that you have to already know all of them before any of them can help you.

Studio closes that gap. It reads what a project actually contains (see
``project_traits``) and matches those facts against a registry of the ecosystem
(``data/ecosystem.json``), then explains — in the user's language, citing the
evidence — which tool fits and why.

Three rules keep this honest:

* **Recommendations are earned from evidence.** A tool is only suggested when a
  trait Studio actually read from the file triggers one of its rules, and the
  rule's reason is shown next to the suggestion.
* **Installed is a fact, not a guess.** Studio marks a tool installed only when
  the caller passed in an executable it found on disk. Everything else is a link.
* **The default is the boring, official answer.** With nothing special detected,
  the recommendation is Snapmaker Orca. Studio does not manufacture novelty.

The registry is plain data on purpose: adding a tool is a pull request against a
JSON file, not a code change. That is the extension seam described in
docs/EXTENDING.md.
"""
from __future__ import annotations

import json
from pathlib import Path

SCHEMA_VERSION = "ecosystem/1"

_DATA = Path(__file__).parent / "data" / "ecosystem.json"

# Rule operators. Deliberately tiny: a registry contributor should be able to
# read the whole vocabulary in one sitting, and every operator must be decidable
# from a trait Studio genuinely measured.
_OPS = {
    "is_true": lambda actual, expected: actual is True,
    "is_false": lambda actual, expected: actual is False,
    "equals": lambda actual, expected: actual == expected,
    "at_least": lambda actual, expected: (
        isinstance(actual, (int, float)) and not isinstance(actual, bool)
        and actual >= expected
    ),
}

_registry_cache: dict | None = None


def load_registry(path: str | Path | None = None) -> dict:
    """Load the ecosystem registry. Cached for the default path."""
    global _registry_cache
    if path is not None:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    if _registry_cache is None:
        _registry_cache = json.loads(_DATA.read_text(encoding="utf-8"))
    return _registry_cache


def tools(registry: dict | None = None) -> list[dict]:
    return list((registry or load_registry()).get("tools") or [])


def _matches(rule: dict, trait_values: dict) -> bool:
    op = _OPS.get(str(rule.get("op")))
    if op is None:
        return False
    key = rule.get("trait")
    if key not in trait_values:
        return False
    actual = trait_values[key]
    if actual is None:
        # An unmeasured trait never fires a rule — silence beats a guess.
        return False
    try:
        return bool(op(actual, rule.get("value")))
    except TypeError:
        return False


def _score_tool(tool: dict, trait_values: dict) -> tuple[int, list[str]]:
    score = int(tool.get("base_score") or 0)
    reasons: list[str] = []
    for rule in tool.get("recommend_when") or []:
        if _matches(rule, trait_values):
            score += int(rule.get("weight") or 0)
            reason = str(rule.get("reason") or "").strip()
            if reason:
                reasons.append(reason)
    return score, reasons


def _entry(tool: dict, score: int, reasons: list[str], installed_path: str | None) -> dict:
    return {
        "id": tool.get("id"),
        "name": tool.get("name"),
        "kind": tool.get("kind"),
        "official": bool(tool.get("official")),
        "role": tool.get("role"),
        "url": tool.get("url"),
        "license": tool.get("license"),
        "install_hint": tool.get("install_hint"),
        "caution": tool.get("caution"),
        "maturity": tool.get("maturity") or "stable",
        "handoff": tool.get("handoff") or "link",
        "stage": tool.get("stage") or "before-slicing",
        "score": score,
        "why": reasons,
        "installed": installed_path is not None,
        "path": installed_path,
    }


def recommend(traits: dict, installed: dict | None = None,
              registry: dict | None = None) -> dict:
    """Rank ecosystem tools for a project.

    ``traits`` is the graded dict from ``project_traits.extract`` (a flat
    ``{key: value}`` mapping is accepted too). ``installed`` maps tool id to the
    executable path the shell found on disk; anything absent is treated as not
    installed, never as unavailable.

    Returns ``{schema_version, primary, alternatives, discover, summary}``.
    ``primary`` is the single recommended next step. ``alternatives`` are other
    tools whose rules fired. ``discover`` lists matched tools that are not
    installed, so the UI can offer a link without pretending they are ready.
    """
    reg = registry or load_registry()
    installed = {k: v for k, v in (installed or {}).items() if v}

    trait_values = _flatten(traits)

    scored: list[dict] = []
    for tool in tools(reg):
        score, reasons = _score_tool(tool, trait_values)
        if score <= 0 and not reasons:
            continue
        scored.append(_entry(tool, score, reasons, installed.get(str(tool.get("id")))))

    # An installed tool outranks an equally-scored one the user would have to go
    # and download — the recommendation should be actionable right now.
    scored.sort(key=lambda e: (e["score"], e["installed"]), reverse=True)

    primary = scored[0] if scored else None
    alternatives = scored[1:]
    discover = [e for e in scored if not e["installed"] and e["why"]]

    return {
        "schema_version": SCHEMA_VERSION,
        "registry_updated": reg.get("updated"),
        "primary": primary,
        "alternatives": alternatives,
        "discover": discover,
        "summary": _summary(primary, alternatives, trait_values),
    }


def _flatten(traits: dict) -> dict:
    """Accept either graded traits or an already-flat value map."""
    if not isinstance(traits, dict):
        return {}
    out = {}
    for k, v in traits.items():
        if isinstance(v, dict) and "value" in v and "confidence" in v:
            out[k] = v["value"]
        elif not isinstance(v, dict):
            out[k] = v
    return out


def _summary(primary: dict | None, alternatives: list[dict], trait_values: dict) -> str:
    if primary is None:
        return ("Studio could not read enough of this file to suggest a next step. "
                "Open it in Snapmaker Orca to see what your slicer makes of it.")
    if not primary["why"]:
        return f"{primary['name']} is the next step for this project."
    lead = primary["why"][0]
    extra = ""
    special = [a for a in alternatives if a["why"] and not a["official"]]
    if special:
        names = ", ".join(a["name"] for a in special[:2])
        extra = f" {names} could also do something specific with this file — see the reasons below."
    return f"{primary['name']}: {lead}{extra}"


def advise(path: str, installed: dict | None = None) -> dict:
    """Read a project and return both its traits and the tool recommendation.

    This is the call the API and CLI use. Kept here so the "read the file, then
    reason about it" pairing lives in one place.
    """
    from . import project_traits

    traits = project_traits.extract(path)
    out = recommend(traits, installed=installed)
    out["traits"] = traits
    return out
