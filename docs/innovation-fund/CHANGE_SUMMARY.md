# Change summary — the 2026-08-22 sprint

What changed in Studio during this cycle, why, and what proves it. Commits are on
`sprint/innovation-fund-2026`.

---

## Baseline

Before any change: **345 backend tests passed, 3 skipped; 161 desktop tests
across 25 files.** Both suites were green, so every failure discussed below was
introduced and fixed inside this sprint rather than inherited.

After: **495 backend tests passed, 3 skipped; 192 desktop tests across 27 files.**
150 backend and 31 desktop tests added, no regressions.

---

## 1. Reliability and security — `b7a82f2`

Studio opens files people download from model sites and talks to an address a
person typed. Both were trusted more than they should have been.

- **Untrusted 3MF reads are bounded.** `ThreeMF.open` meters every part through a
  hard byte budget (1 GiB total, 512 MiB per part, 20,000 entries, all
  env-overridable) instead of trusting the ZIP header. A decompression bomb is
  now refused with a plain-language message rather than exhausting memory.
  `test_container_limits.py` builds real bombs and asserts the refusal.
- **Printer addresses are validated.** Every Moonraker request URL goes through
  `validate_host()`: hostnames, IPv4 and bracketed IPv6 accepted; schemes,
  credentials, paths, queries and embedded newlines rejected. Control POSTs use
  the same gate, so they are not a bypass.
- **The loopback API refuses oversized bodies** before allocating, ahead of the
  token check.
- **Discovery probes both ports the U1 answers on** — Klipper's 7125 and port 80,
  where the U1 serves Moonraker alongside its built-in Fluidd page. Probing one
  made a reachable printer look offline.
- **"Not found" now says the actual fix.** The U1's network interface is gated
  behind Advanced Mode on the printer's touchscreen, so discovery returns that
  instruction instead of a bare failure.

## 2. Ecosystem intelligence — `2b21d15`

The differentiating capability of this sprint, and the answer to "why does Studio
need to exist when forty other projects do".

- **`project_traits.py`** reads a 3MF or STL and reports what it actually
  contains: origin slicer, target printer, plate and object counts, filament
  slots, nozzle sizes, painted colour, textures, per-layer custom G-code, the
  declared model unit, required 3MF extensions, and whether it is already sliced.
  Every trait carries its evidence and one of four confidence tiers. An
  unreadable file yields `unknown`, not an exception.
- It also surfaces the **per-plate time and weight the author's own slicer
  computed**, which is what makes §4 possible.
- **`ecosystem.py`** matches those traits against `data/ecosystem.json`, a
  plain-data registry of the open ecosystem, and names the tool that fits — with
  the reason drawn from the file, the tool's licence, and a caution for
  experimental community forks. A trait Studio could not measure never fires a
  rule. With nothing special detected the answer is the official Snapmaker Orca.
- **Rust owns install detection.** The webview can only ask to open a tool by id;
  it can never hand the shell a path to execute. A tool counts as installed only
  when a known location is a real file on disk.
- **Openness:** `u1convert traits` and `u1convert ecosystem` expose the same data
  as JSON for scripts and other tools.

## 3. Conversion parity and the placement fix — `a6eff05`

- **Snapmaker Orca import compatibility (`orca_import.py`)**, applied in every
  prepare mode because these are corrections, not settings choices: Exclude
  Object enabled; an *automatic* brim suppressed while an explicitly chosen brim
  is kept as intent; tree support with variable layer height switched to hybrid;
  filament array validity repaired, with `filament_self_index` rebuilt
  positionally rather than padded; a negative raft expansion restored from
  Studio's own U1 profile; the authoring slicer's `plate_N.gcode` / `.json`
  removed so Orca re-slices, while plate *images* are kept.
- Every change carries its old value, a reason and a plain-language explanation,
  and flows through the existing preservation guard — which rejected this feature
  during development until it was reported properly. That is what the guard is
  for.
- **Plate placement (`plate_placement.py`)** closes a gap no size check can see: a
  small object at another printer's coordinates lands off the U1 plate. Studio
  names the object, the edge and the millimetres, and can write a new copy with
  the arrangement translated on. For multi-plate projects it **measures** the
  plate grid the file uses, verifies the measurement explains every plate, and
  repositions each plate onto the U1's grid keeping the creator's plate-to-plate
  spacing. All-or-nothing per plate; it refuses outright when an object belongs to
  no plate, when the grid is uneven, or when any plate will not fit.
- Only build-item translations are rewritten. A byte-diff test proves no other
  archive entry changes, and the fix re-validates the file it actually wrote.
- **Project cost (`project_cost.py`)** costs from the slicing result the project
  already carries, with per-material prices, and says where the number came from.
  When there is no real figure it explains why — and distinguishes "not sliced
  yet" from "sliced but records no material figures", because the fix differs.

## 4. The fix, surfaced — `2c7d71e`

The Compatibility page now shows object placement, names each off-plate object,
and offers the move — stating that the original is untouched and that layout,
rotation, scale and height are preserved. When Studio will not move things, it
says which of the three reasons applies rather than hiding the button. A failed
check renders nothing rather than breaking the page around it.

---

## Competitive position, before and after

**Before:** Studio was the only pre-print validation entry in the Fund's Phase 1
field, but it overlapped visibly with the converter projects on the *prepare*
step and had nothing to say about the rest of the ecosystem.

**After:**

- **Conversion parity.** Every documented rule of the closest converter is
  implemented independently, plus self-validation and multi-source input, which
  that converter's own documentation says it does not do.
- **A capability nobody else has.** Reading a file to recommend the right
  *community* tool makes Studio complementary to the rest of the field rather
  than competing with it — the one position that gets more valuable as the
  ecosystem grows.
- **A category with no competition.** Cost estimation had zero other entries;
  Studio now grounds it in a real measurement.
- **A defensible discipline.** Evidence grading, refusal-to-guess, and
  never-modify-the-original are enforced by tests that assert what Studio *will
  not* say.

---

## What was deliberately not done

- **No slicing.** Studio hands off; it does not generate toolpaths.
- **No second printer dashboard.** Fluidd already ships on the machine.
- **No Extended Firmware requirement.** Stock firmware is first-class, and Studio
  never claims extended firmware is absent — only that it did not detect it.
- **No browser extension.** The converter's DOM coupling to one site broke it
  three times in four releases; Studio takes any local file instead.
- **No print-profile matching by layer height** (the converter does this). Studio
  still uses a single U1 base profile. Tracked as remaining work.

---

## Verification

```
backend  pytest        495 passed,  3 skipped
desktop  npm run test  192 passed, 27 files
desktop  npx tsc --noEmit     clean
desktop  npm run build        ok
src-tauri  cargo check        ok
```
