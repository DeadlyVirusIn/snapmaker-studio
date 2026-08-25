# Second-printer architecture proof — the result

Run 2026-08-25 on `main` at `c98ab12`, after v0.7.2. **No release was made.**

## The question

Not "does Studio support another printer". The narrower and harder one:

> Is Studio's printer intelligence genuinely data- and capability-driven, or is it
> U1 logic hidden behind abstractions?

The Innovation Fund submission leans on an openness claim — that Studio is not
U1-only by construction — and that was the one claim in the project with no
evidence at all behind it.

## Outcome

**A — architecture proved, profile verified, no hardware verification.**

The same printer-intelligence path now runs against a second public
Klipper/Moonraker printer profile. The U1 remains the only printer this project
has verified on physical hardware.

That is the strongest sentence the evidence permits, and it is the one used
publicly. It is not "Studio supports the VORON 2.4".

## The printer, and why this one

Requirements were scored before any name was chosen. The winner is the **VORON 2.4
(250 mm)**.

| Requirement | How it is met |
|---|---|
| Klipper + Moonraker genuinely used | VORON's own docs: "All stock Voron printers run on the Klipper firmware", and the project recommends Mainsail or Fluidd. Mainsail's README: "Without Moonraker, Mainsail would not be possible." |
| Public authoritative configuration | Klipper *itself* ships `config/kit-voron2-250mm.cfg`, whose header says it "matches the manual/build guide exactly". Upstream, not a community fork. |
| Build volume from source, not marketing | `stepper_x/y/z position_max: 250`, and `stepper_z position_min: -2` for gantry-squaring headroom. |
| Tool count establishable | Exactly one `[extruder]`; no `[extruder1]`, no toolchanger. |
| Capabilities reasonable from evidence | Section list is a capability manifest in the same shape Moonraker's object list takes. |
| No proprietary or cloud API | Moonraker over LAN, identical to the U1 path. |
| Licence permits factual use | GPL-3.0 source; only facts taken, no text copied. See `THIRD_PARTY_NOTICES.md`. |
| Structurally different enough to expose assumptions | See below. |

The last row is why it beat the more famous options. The VORON disagrees with the
U1 about nearly everything Studio might have assumed:

- **one extruder, not four** — the single most load-bearing U1 number in the code;
- **250 mm cube** against the U1's 270 mm plate and 335 mm of Y travel;
- **no `exclude_object`, no `bed_mesh`, no `input_shaper`, no `pause_resume`, no
  runout sensor** in the published configuration;
- **no `print_task_config`** — nothing whatsoever reporting loaded filament, where
  the U1 exposes Snapmaker-specific parallel arrays.

Candidates considered and dropped: Sovol SV08 (only community configuration
repositories, none authoritative); Creality K1/K2 and Qidi (Klipper-derived but
modified stacks, weaker public evidence); Prusa Core One (Buddy firmware, not
Klipper). Bare "Voron 2.4" without a size variant was rejected because build
volume must come from a specific configuration, and the 250 file is the one
Klipper publishes.

## U1 assumptions found, and what happened to each

Classified A (legitimate U1 profile data), B (already generic), C (accidental
hard-code), D (U1-only feature needing a capability gate).

| Where | Assumption | Class | Disposition |
|---|---|---|---|
| `post_slice._machine_match` | `looks_u1 = "u1" in model or "snapmaker" in model` | **C** | Rewritten to compare the job's machine with the *identified* printer, falling back to the prepare target and saying so. This was the worst one: a job correctly sliced for any other printer was reported wrong, with an instruction to re-slice it in Snapmaker Orca. |
| `toolhead_fit.U1_TOOLHEADS = 4` | Offline fallback told everyone they had four toolheads | **C** | Read from the profile; the answer now carries `toolhead_count_source` and `measured_against`. |
| `bed_fit.U1_BED` | Module constant | **C** | Read from the profile; output carries `bed_mm_source` and `measured_against`. |
| `scale_doctor._PRINTER_BEDS` | A printer-keyed dict with one key, defaulting to the U1 whatever printer was named | **C** | Built from the shipped profiles, so `printer=` is a real parameter. |
| `plate_placement` summaries | "the U1's printable area" printed while measuring a *live* bed from another machine | **C** | Takes `bed_name`; the U1 is still named when the fallback plate is the U1's. |
| `firmware_caps` summary | "Your U1 reports …" for any Klipper machine | **C** | Takes `printer_name`; an unidentified printer is "This printer". |
| `firmware_caps` eddy probe | "the U1's contactless probe" | **C** | Described by what it is, not whose it is. |
| `post_slice._nozzle` | "stock firmware does not report which nozzle is fitted" asserted for every machine | **C** | Offered only for a printer whose profile records that, established by looking. |
| `send_check` free space | U1-traced `total_bytes 0` evidence quoted as the reason for any printer | **C** | Travels with the machine it was gathered on. |
| `moonraker._TOOLHEAD_OBJECTS` | Fixed four extruder objects in `status()` | **C** | Derived from the printer's own tool count. A machine with more than four was silently truncated. |
| `moonraker.NOT_FOUND_HINT` | "Turn on Advanced Mode on the U1 touchscreen" for any address that failed | **C** | Kept for the U1-hostname discovery path; a typed address gets a hint that does not assume the machine. |
| `moonraker.discover` defaults | Hard-coded U1 hostnames | **C** | Read from the profiles' own `default_hostnames`. |
| 10 × "Connect your U1" strings | Preflight, Post-Slice, send check, material plan | **C** | "Connect your printer". |
| `Printers.tsx` | `"U1 found — ready"` / `"not a U1"` for any Moonraker host | **C** | "printer found — ready" / "no answer", plus an identity line when the machine identified itself. |
| `preflight` bed fallback | "checked against the published U1 volume" | **C** | Names the prepare-target profile. |
| `loaded_filaments` `print_task_config` | Snapmaker-specific object | **D** | Now a *profile fact* (`material_state.source`), and its absence resolves to unknown rather than to empty. |
| `convert`, `repair`, `u1_identity`, `stl_wrap`, `data/profiles/snapmaker_u1.json`, `_placed_U1.3mf` | The whole prepare path | **A** | Untouched. Studio prepares U1 copies; that is the product, not an assumption. |
| `preflight._sliced_state`, `_object_exclusion` | "Studio removes toolpaths when it prepares a U1 copy" | **A** | Untouched — true statements about what Studio does. |
| `preflight`, `post_slice` checks generally | Tool/bed/exclusion/state/material joins | **B** | Already read from what the printer reported. This is why the sprint was cheap. |

## What became data

`snapstudio_core/printer_profiles.py` plus `data/printer_profiles/*.json`.

A profile carries **facts and no behaviour**. There is no per-printer function
anywhere in the package, and `tests/test_no_printer_model_branching.py` parses the
generic modules with `ast` and fails the build on a *conditional* that turns on a
model name. It deliberately does not police strings — Studio names the U1 and
Snapmaker Orca in prose constantly, correctly — and it proves it can catch the
exact shape `post_slice` used to carry.

Two rules govern the layer:

1. **Live evidence beats the profile, always.** `resolve()` records which source
   won and reports a disagreement rather than smoothing it. A profile claiming four
   tools against a printer reporting three yields three, plus a conflict saying so.
2. **How a fact was established travels with it.** Verification level, source refs
   and known unknowns are part of the profile, and the exact label wording lives in
   one place so nothing can shorten "profile verified — hardware not tested by this
   project" to "verified".

Build volume is the one field where live and profile answer *different* questions
— Klipper reports toolhead travel, a machine profile records printable area, and
the U1 travels 335 mm in Y over a 270 mm plate — so a difference there is not
reported as a conflict.

## Which checks worked unchanged

Everything except the two that were about the U1 by construction. Preflight's
toolhead, bed, exclusion, busy-state and nozzle checks; the Post-Slice Doctor's
tool availability, slot loading, material match, bed fit, exclusion and busy
checks; the send check's composition; the material plan; the firmware capability
interpreter; the Moonraker client's own object-list and axis-limit parsing. Each
ran against the VORON with no branch added.

The two that broke were `_machine_match` (hard-coded to the string `"u1"`) and
every offline fallback (module constants named after the U1). Both are fixed
generically.

## What deliberately stays unknown

- What filament a VORON has loaded. Nothing on the machine reports it, and
  **Studio does not manufacture a spool slot from an extruder**. Preflight still
  produces a useful report without it.
- Which nozzle is fitted, on either machine.
- Free storage, on either machine — and the U1's traced reason for that is no
  longer offered as an explanation for other hardware.
- What any *particular* VORON has installed. The base configuration is a starting
  point owners edit; only a live object list settles a capability.
- Whether a machine that did not answer is a U1, or anything else.

## U1 regression

No U1 behaviour was changed to make the abstraction tidier.

- Backend **1247 passed / 4 skipped**, including every U1 preflight, loaded
  filament, send-check and hardware-fixture test. Measured against the same tree
  at `c98ab12`, which passes 1186 / skips 4; `docs/internal/evidence/0.7.2.json`
  records 1185 for the environment that release was verified in. Collection is
  the environment-independent comparison: **1190 tests before, 1251 after**.
- `test_printer_real_shapes.py` gained six tests that replay the shape a real U1
  reported — four extruders, 271 × 335 × 281 mm, `print_task_config` — through the
  *new* profile layer, and assert every value still resolves from the machine
  (`source: live`) with no conflicts. That is where a regression would hide: an
  abstraction answering from a profile looks identical until the machine disagrees.
- `u1convert selfcheck` **27/27**, unchanged.
- `tsc` clean, `cargo check` clean, production build clean.
- Desktop **311 passed** (306 + 5 new).

**The real-U1 read-only harness was not re-run this session.** `U1.local` and
`snapmaker-u1.local` do not resolve on this network — confirmed again here,
`getaddrinfo failed` on both — so `tools/hardware/verify.ps1` needs
`-PrinterHost <ip>`, which is not in tracked files and must not be. Studio does
not scan the LAN. The last hardware verification stands at **26/26 against
v0.7.2**, and re-running it needs the printer powered on and its address supplied.
Until then the U1 hardware evidence is v0.7.2's, and the offline proof above is
what this sprint adds.

## Tests

| | Before (`c98ab12`) | After |
|---|---|---|
| Backend, collected | 1190 | **1251** (+61) |
| Backend, run in this tree | 1186 passed / 4 skipped | **1247 passed / 4 skipped** |
| Desktop | 306 | **311** |
| selfcheck | 27/27 | **27/27** |
| Real U1 | 26/26 (v0.7.2) | not re-run — see above |

The +61 accounts exactly: `test_second_printer.py` (19),
`test_second_printer_failures.py` (24), `test_no_printer_model_branching.py`
(12), and six added to `test_printer_real_shapes.py`. Desktop gains
`PrinterVerificationLabels.test.ts` (5).

`docs/internal/evidence/0.7.2.json` records 1185 backend tests for the
environment v0.7.2 was verified in, one fewer than the same commit passes here.
That snapshot is immutable history and is not edited; the row above is measured
rather than copied from it, which is why both numbers appear.

## Release decision

**No release.** This sprint found no defect affecting current U1 users. The
`status()` toolhead-list fix is real but caps at four, and the U1 has four, so no
shipped U1 behaviour was wrong. `main` carries the work; v0.7.2 remains stable.

A future minor release can carry genuine multi-printer product capability. A patch
would need a real shipped defect, and there isn't one.

## Reranked priorities

1. **Material-provider interoperability / U1Hub** — now clearly first. This sprint
   made "unknown filament" a first-class, correctly-reported state on a machine
   that reports none, which sharpens rather than solves the problem: remaining-
   filament sufficiency is still the last large unknown in the send path, and a
   provider is the only thing that can answer it. It is also now the *portable*
   answer — a provider works for any printer, where `print_task_config` works for
   one.
2. **Remaining Prusa semantics** — unchanged: instances and copies, multi-volume
   objects, per-object overrides, `extruder="0"` for unassigned.
3. **Second-printer hardware verification, if a machine ever becomes reachable** —
   new, and small. The profile and the whole path already exist; it needs a
   printer, which is a human gate rather than work.
4. **OBJ/GLB input** — unchanged, and still below the others.

Nothing found during this sprint was a runtime failure. The `status()` truncation
above five toolheads is the only latent bug, and no printer Studio knows about has
more than four.
