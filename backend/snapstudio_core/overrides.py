"""Per-object setting overrides, and the three of them that can cross.

A per-object override is a setting somebody changed on one object and not on the
rest of the plate: this part at 0.3 mm layers, that one at 80% infill, this one
with supports on. Studio has been reading them for a while and reporting them as
not carried. This module is what decides, for each one, whether it may cross —
and the answer is *almost always no*.

## Why an allowlist rather than a copy

Handing Snapmaker Orca the source's own key is not carrying the setting across.
Measured on 2.3.6 by writing one key into an otherwise byte-identical project,
opening it, and reading the project Orca saved back:

| written on the object          | Orca wrote back |
|--------------------------------|-----------------|
| `layer_height="0.3"`           | `layer_height="0.3"` |
| `sparse_infill_density="45%"`  | `sparse_infill_density="45%"` |
| `enable_support="1"`           | `enable_support="1"` |
| `fill_density="15%"`           | **gone** |
| `support_material="1"`         | **gone** |
| `snapstudio_nonsense_setting`  | **gone** |

`fill_density` and `support_material` are PrusaSlicer's own words for the second
and third rows. Orca discards them exactly as it discards a key that was invented
for the experiment. So a generic "copy every override" path writes nonsense with
a straight face: the file looks like it carries the setting and the slicer never
sees it.

The invented key is what makes the top three rows evidence rather than
coincidence. Without it, survival would only show that Orca preserves whatever it
is given.

## Why a value gate, and why it is not politeness

The same experiment with a value Orca cannot parse:

| written on the object            | what Orca did |
|----------------------------------|---------------|
| `layer_height="not-a-number"`    | **opened with an empty plate — the object was gone** |
| `layer_height="٠.٣"` (Arabic-Indic digits) | **object gone** |
| `enable_support="true"`          | **object gone** |
| `enable_support="2"`             | **object gone** |
| `layer_height="0"`               | **Orca hung on load, spinning, unresponsive** |
| `layer_height="-0.2"`            | **Orca hung on load** |
| `layer_height="0.5"` (nozzle is 0.4) | refused to slice: *"Layer height cannot exceed nozzle diameter"* |

A malformed override does not fail safely. It takes the geometry with it, or it
takes the slicer with it. So every value is checked here before it is written,
and a value that does not pass leaves the setting **uncarried and named** — never
carried and broken.

## What the values mean on each side

Measured by slicing the same two-object plate in both slicers, one object
overridden and one not, and reading the G-code:

| override | PrusaSlicer 2.9.6 | Snapmaker Orca 2.3.6 |
|---|---|---|
| layer height 0.3, global 0.2 | overridden object 100 layers at 0.3, other 150 at 0.2 | **identical** |
| infill 80%, global 15% | overridden object's infill ×3.6, other unchanged | overridden ×4.1, other unchanged |
| support on, global off | support under the overridden object only | support under the overridden object only |

Both slicers change only the object that was overridden. The absolute lengths
differ because the two slicers do not draw infill or support the same way; the
statement each setting makes is the same one.
"""
from __future__ import annotations

import re

#: Studio's own name for each fact, independent of either dialect's spelling.
LAYER_HEIGHT = "layer_height"
INFILL_DENSITY = "infill_density"
SUPPORT = "support"

#: How each fact is classified when it crosses. `exact` means the target uses the
#: same word for it; `semantic` means the word changes and the meaning does not.
EXACT = "exact"
SEMANTIC = "semantic"

#: The default nozzle diameter of a prepared U1 copy, in millimetres. Orca
#: refuses to slice a layer taller than the nozzle and says so by name, so this
#: is a gate rather than a preference. Callers that know the real profile pass
#: their own.
DEFAULT_NOZZLE_MM = 0.4

#: Studio will not treat anything outside this as a layer height, whatever the
#: nozzle is. Below zero and at zero, Orca hangs rather than complains.
_MIN_LAYER_MM = 0.001


def _ascii_number(value: str):
    """A plain decimal, or nothing.

    ASCII only. `float("٣")` is 3.0 in Python, and Orca deleted the object it was
    written on — a value neither program agrees about is not a value.
    """
    text = (value or "").strip()
    # `\d` matches Unicode digits, so a pattern written with it accepts "٠.٣"
    # and float() then turns it into 0.3 — a value no slicer wrote, normalised
    # in silence. Orca does not read it either: handed that string it deleted
    # the whole object. ASCII, spelled out.
    if not re.fullmatch(r"[+-]?[0-9]*\.?[0-9]+", text):
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _percent(value: str):
    """A percentage, with or without the sign, as a number.

    Both dialects treat a bare number as a percentage — Orca normalises `45` to
    `45%` when it saves — so the sign is optional on the way in and always
    written on the way out.
    """
    text = (value or "").strip()
    if text.endswith("%"):
        text = text[:-1].strip()
    return _ascii_number(text)


def _carry_layer_height(value: str, nozzle_mm: float):
    number = _ascii_number(value)
    if number is None:
        return None, ("the value is not a plain number, and Snapmaker Orca deletes "
                      "the whole object when it cannot read one")
    if number < _MIN_LAYER_MM:
        return None, ("a layer height of zero or less hangs Snapmaker Orca when the "
                      "project is opened")
    if number > nozzle_mm:
        return None, (f"{number:g} mm is taller than the {nozzle_mm:g} mm nozzle this "
                      "copy is prepared for, and Snapmaker Orca refuses to slice a "
                      "layer taller than the nozzle")
    # Written back in the form Orca itself writes: it normalises "0.300" to "0.3".
    return f"{number:g}", None


def _carry_infill(value: str, nozzle_mm: float):
    number = _percent(value)
    if number is None:
        return None, ("the value is not a plain percentage, and Snapmaker Orca deletes "
                      "the whole object when it cannot read one")
    if not 0.0 <= number <= 100.0:
        return None, f"{number:g}% is not a density between 0 and 100"
    return f"{number:g}%", None


def _carry_support(value: str, nozzle_mm: float):
    text = (value or "").strip()
    if text not in ("0", "1"):
        return None, ("the value is neither 0 nor 1, and Snapmaker Orca deletes the "
                      "whole object rather than ignoring one it cannot read")
    return text, None


class Carried:
    """One source override that may cross, and everything that says why."""

    __slots__ = ("fact", "source_key", "target_key", "level", "kind", "convert", "meaning")

    def __init__(self, fact, source_key, target_key, level, kind, convert, meaning):
        self.fact = fact
        self.source_key = source_key
        self.target_key = target_key
        self.level = level
        self.kind = kind
        self.convert = convert
        self.meaning = meaning


#: Every setting Studio carries, and nothing else. Each row is here because the
#: target was measured to recognise the key, store it at this level, and act on
#: it the way the source acts on its own — see this module's docstring.
#:
#: `level` is `object`: Snapmaker Orca writes a per-object override as a
#: `<metadata>` inside `<object>` in `Metadata/model_settings.config`, which is
#: how Orca itself wrote all three when they were set through its own per-object
#: settings panel.
CARRIED: dict[str, Carried] = {
    "layer_height": Carried(
        LAYER_HEIGHT, "layer_height", "layer_height", "object", EXACT,
        _carry_layer_height, "how tall each layer of this object is"),
    "fill_density": Carried(
        INFILL_DENSITY, "fill_density", "sparse_infill_density", "object", SEMANTIC,
        _carry_infill, "how dense this object's infill is"),
    "support_material": Carried(
        SUPPORT, "support_material", "enable_support", "object", SEMANTIC,
        _carry_support, "whether this object is printed with support"),
}

#: The target's spelling for each source key, for a reader that has to find the
#: carried value in the prepared copy.
TARGET_KEY = {entry.source_key: entry.target_key for entry in CARRIED.values()}

#: Every key this module knows how to *write*. A prepared copy must never carry
#: an object-level setting outside this set: Studio would be stating something it
#: has not measured.
WRITABLE = frozenset(entry.target_key for entry in CARRIED.values())


def plan(source_overrides: dict, nozzle_mm: float = DEFAULT_NOZZLE_MM) -> dict:
    """Decide, for each source override, whether it crosses and in what words.

    Returns ``{"carry": {target_key: value}, "rows": [...]}``. Every source
    override produces exactly one row, carried or not, so nothing is dropped
    without being named.
    """
    carry: dict[str, str] = {}
    rows: list[dict] = []
    for source_key, raw in sorted((source_overrides or {}).items()):
        entry = CARRIED.get(source_key)
        if entry is None:
            rows.append({
                "source_key": source_key, "source_value": raw,
                "target_key": None, "target_value": None, "kind": None,
                "carried": False,
                "why": ("Studio has not established what this setting means to "
                        "Snapmaker Orca, so it is reported rather than guessed at"),
            })
            continue
        value, why = entry.convert(raw, nozzle_mm)
        if value is None:
            rows.append({
                "source_key": source_key, "source_value": raw,
                "target_key": entry.target_key, "target_value": None,
                "kind": entry.kind, "carried": False, "why": why,
            })
            continue
        carry[entry.target_key] = value
        rows.append({
            "source_key": source_key, "source_value": raw,
            "target_key": entry.target_key, "target_value": value,
            "kind": entry.kind, "carried": True, "why": None,
            "meaning": entry.meaning,
        })
    return {"carry": carry, "rows": rows}


def validate_emitted(carried: dict, nozzle_mm: float = DEFAULT_NOZZLE_MM) -> list[str]:
    """Faults in what a writer is about to put in a prepared copy.

    Prepare fails on any of these rather than writing them. An override Orca
    cannot read does not degrade — it takes the object with it — so a copy that
    cannot be written correctly must not be written at all.
    """
    faults = []
    reverse = {entry.target_key: entry for entry in CARRIED.values()}
    for key, value in sorted((carried or {}).items()):
        entry = reverse.get(key)
        if entry is None:
            faults.append(f"{key} is not a setting Studio has proved Snapmaker Orca "
                          "acts on, so it must not be written into a prepared copy")
            continue
        again, why = entry.convert(value, nozzle_mm)
        if again is None:
            faults.append(f"{key}={value!r} would not survive: {why}")
        elif again != value:
            faults.append(f"{key}={value!r} is not in the form Studio writes "
                          f"({again!r})")
    return faults
