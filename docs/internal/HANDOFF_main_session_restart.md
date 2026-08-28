# Start here — session restart, 2026-08-28

The single file a fresh session should read first. Everything below is current as
of the commit that carries it.

## Exact state

| | |
|---|---|
| Current stable release | **v0.8.0**, published, latest, untouched |
| Release tag | `v0.8.0` → `e12bc59` |
| `main` and `origin/main` | in step, tree clean, no stashes |
| Release evidence | `docs/internal/evidence/0.8.0.json` unchanged; no snapshot edited |

No exact HEAD is written here on purpose: a handoff naming the hash of the commit
that contains it is stale the moment it is committed. What matters is that the
tree is clean, `main` and `origin/main` agree, and the gates below pass.

## Verification on `main`

Backend **1731 passed / 4 skipped** · desktop **335** · `u1convert selfcheck`
**27/27** · `tsc --noEmit` clean · `cargo check` clean · production build clean.

**Not run:** installed-app acceptance and the real-U1 hardware harness. `main` is
**not hardware verified**. **There is no release**, and the next one is a minor —
**v0.9.0**, not v0.8.1.

## Start here

```
cd "D:/STL Files/snapmaker-studio"
git status --short                       # expect clean
git rev-parse HEAD origin/main           # expect the two to match
cd backend && py -m pytest -q            # expect 1731 passed, 4 skipped
```

Python is `py` on this machine — there is no `python` on PATH and no virtualenv.
Backend tests run from `backend/`; the desktop gates are `npm run test`,
`npx tsc --noEmit` and `npm run build` from `desktop/`; `cargo check` from
`desktop/src-tauri`. The selfcheck is
`py -c "from u1convert.cli import cli; cli(['selfcheck'])"`.

## What is settled — do not reopen without a measured defect

Each of these was established by handing Snapmaker Orca a project, letting Orca
save it back, and reading what Orca wrote — never from a warning, a screenshot or
a matching key name, and always with a control that discriminates.

- **Per-object overrides.** `layer_height` (exact), `fill_density` →
  `sparse_infill_density` and `support_material` → `enable_support` (semantic).
  A per-object layer height is withheld on a multi-filament plate, because Orca
  refuses to slice a prime-tower plate whose objects differ.
- **The preset-deviation mechanism.** A value a project states is used **only**
  when the project declares it in `different_settings_to_system`. Entry 0 is the
  process preset, entries 1..N the filaments, the **last** the printer. A key in
  the wrong entry is ignored; an unrecognised key costs nothing.
- **Target readability.** `Metadata/model_settings.config` and
  `3D/_rels/3dmodel.model.rels` are required; `[Content_Types].xml` is ignored;
  `slice_info`, `filament_maps`, `model_instance`, `assemble` and `printer_model`
  are reconstructed by Orca.
- **The Application gate.** Geometry-only mode needs **both** a flat root model
  and the case-sensitive substring `PrusaSlicer` in the Application. An invented
  name, `SuperSlicer`, `Slic3r` and lower case are all fine.
- **The U1 project contract.** Closed 2026-08-28 — see
  `HANDOFF_main_contract_closed.md`. Template is **541 keys**. The remaining 274
  preset-equal values are **REDUNDANT_BUT_HARMLESS / DEFERRED**.

Full measurement record: `docs/internal/PRUSA_SEMANTICS.md`. Template rule:
`backend/snapstudio_core/data/templates/PROVENANCE.md`.

## The next engineering item

**A second material provider.** Spoolman is the only implementation of the
material-provider seam, so nothing proves the seam is actually provider-generic.
Read `docs/MATERIAL_PROVIDERS.md` and `docs/internal/PROVIDER_AUDIT.md` first.

Nothing has been researched, chosen or written. The shape the work should take:

1. **Research before choosing.** At least three candidates, each recorded with
   repository, maintenance status, licence, interface, remaining-weight
   semantics, freshness/timestamp, slot association, authentication and local
   deployment path. Rank on evidence. Re-check U1Hub, but it stays ineligible
   unless it now has **both** an intentional external integration API **and**
   remaining-filament quantity. If no credible second provider exists, that is a
   valid result — do not invent a weak integration.
2. **Prove the seam before writing an adapter.** Equivalent normalised facts from
   Spoolman and the new provider must produce identical downstream decisions —
   enough, clearly short, stale, derived, unknown, provider unavailable, material
   conflict, unmapped spool. The provider's name may appear as provenance and
   nowhere else. If generic consumer code needs provider-specific branching,
   stop: the abstraction is wrong, and hiding it is worse than fixing it.
3. **A real instance**, session-owned, seeded through its documented API. No
   mocks-only proof. Never touch a container this session did not start.
4. **Reuse the existing address-safety boundary** — local accepted, public
   internet / `file://` / `ftp://` / embedded credentials / redirect escape all
   rejected, plus timeout, oversized and malformed response. No new arbitrary
   network path.
5. **No new page.** The existing Materials Provider settings become
   None / Spoolman / the new one, showing only the fields that provider needs.

Existing suites to keep green: `test_provider_reality.py`,
`test_provider_address_safety.py`, `test_provider_printer_conflicts.py`,
`test_material_providers_adversarial.py`, `test_freshness.py` (125 tests).

## Backlog after that

1. Second material provider (above).
2. Individual per-object placement, if the product ever wants it — the check
   already reports which objects are off the plate; it needs its own user intent
   and its own audit rows.
3. OBJ/GLB input — unchanged, still last.

The 274 preset-equal template values are **not** on this list. They are
deferred, not unfinished.

## Things that will bite

Everything under this heading in the earlier handoffs still applies. The ones
that cost the most time recently:

- **GUI automation needs an exclusive desktop.** The harness drives the
  foreground and is built to lose to whoever is using the machine. `GetLastInputInfo`
  measures *human* input only — another agent session on the same desktop makes
  the idle counter read quiet while stealing the foreground. Check both: no human
  input **and** a foreground that stays put.
- **Keep evidence paths short.** A 160-character path typed into Orca's file
  dialog loses its leading characters, and the failure reads as a save timeout.
  `WM_SETTEXT` and clipboard paste were both tried and neither could be verified.
  A short destination worked first time.
- **Orca reorders objects on save.** Compare per object by name; position and id
  are both the wrong key.
- **A fixture off the plate is `plate_placement` working.** The `prusa-semantics`
  sources land 1.0/1.5 mm off the U1 bed and Orca greys out Slice.
  `plate_placement.assess` names it and offers the one-piece move.
- **`prusa-multi-object` cubes are open shells** — "No layers were detected".
  Use solid geometry for anything that must slice.
- **The template is not the output.** `set_filament_block` rewrites every
  per-filament array at prepare time. Classify the prepared project, never the
  template.
- **`\d` in a Python regex matches Unicode digits.** Spell out `[0-9]`. This has
  been hit twice in this codebase.
- **Grep before building.** More than one sprint has started by writing a feature
  that already existed.

## The harness

It lives in a session scratchpad and goes when the session does — that is
correct, it does not belong in the repository. Rebuilding is about an hour and
the method is described in `HANDOFF_main_contract.md` and
`HANDOFF_main_contract_closed.md`. Its safety contract is not optional: refuse if
any slicer this session does not own is running, own the temp directory and the
pid, prove foreground ownership before every keystroke and click, never
force-kill anything this session did not start, and audit the machine afterwards.

## Release policy

**NO RELEASE** until a convergence sprint that runs, against the **final** built
installer: version bump, full software gates, installed acceptance, the
v0.8.0 → v0.9.0 in-place upgrade, the real-U1 hardware harness, an immutable
v0.9.0 evidence snapshot, and publish / re-download / re-hash.
