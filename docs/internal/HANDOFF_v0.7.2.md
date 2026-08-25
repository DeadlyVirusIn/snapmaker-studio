# Handoff — after the v0.7.2 stable release

Written 2026-08-25, at the end of the sprint that read painted colour, hardened
the public-claim guard, and fixed a defect that had been mis-preparing every
PrusaSlicer project. This is the state a fresh session should start from. Read
`docs/SUBMISSION_STATUS.md`, `docs/TRUST_STATUS.md` and
`docs/internal/evidence/0.7.2.json` before trusting any number quoted anywhere
else.

## Authority order for project state

When two sources disagree about what is true right now, believe them in this
order, and correct the loser rather than working around it:

1. Explicit current facts from the maintainer.
2. The published GitHub release and the live Innovation Fund listing.
3. Live system, account and repository state — `git`, the release API, the mailbox.
4. `docs/internal/evidence/<version>.json` for that version, and
   `docs/internal/evidence.json` for the current one.
5. `docs/SUBMISSION_STATUS.md` and `docs/TRUST_STATUS.md`.
6. Everything else, including README, CHANGELOG and any planning document.

Never turn a stale TODO into new work without proving it is actually incomplete.
Never resurrect finished work. A lower level never overrides a higher one.

## Exact release state

| | |
|---|---|
| Current stable | **v0.7.2** — published, not a prerelease, not a draft, marked latest |
| Tag | `v0.7.2` on commit `fddbc2a` |
| Branch | `main`, at that commit — local `main`, `origin/main` and the tag are identical |
| Installer | `Snapmaker.Studio_0.7.2_x64-setup.exe` |
| Size | 16,980,253 bytes |
| SHA256 | `23298efe76a91dab6c026fab49f48d6c953c89cac587c8f76337e9de2ee47d0c` |
| Release page | <https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.7.2> |

The asset was re-downloaded from the release page after publishing and re-hashed;
it matches. **`main` carries no unreleased work** — the tag is the tip, the tree is
clean, and there are no stashes or extra worktrees.

Verification recorded for this release: pytest **1185 passed / 4 skipped**, vitest
**306**, `u1convert selfcheck` **27/27**, installed acceptance **31/31** (including
the in-place upgrade from v0.7.1), real Snapmaker U1 read-only **26/26**, with
`tsc`, `cargo check` and the production build clean.

## What the last three releases did

**v0.7.0 — painted colour is read.** `paint_codec` decodes the per-facet paint
format the PrusaSlicer and BambuStudio/OrcaSlicer families both write, and
`painted_color` reads the container around it: which filament slots the painting
uses, how many facets carry each, the surface area each covers, and the height band
each occupies once the object is placed. Colour planning answers from that
evidence instead of reporting every painted colour as unclassifiable. Two defects
fixed on the way: `has_painted_color` looked for painting in a settings file no
slicer writes it to, so every painted project read as unpainted; and Fidelity
compared painting by counting markers in the bytes, which cannot tell painting
that survived from painting that was rewritten.

**v0.7.1 — what a real brush writes.** Painting was authored *inside* Snapmaker
Orca 2.3.5 and Bambu Studio 02.08.02.61 and those files became fixtures. Reading
them found a real defect: one facet painted with a round brush is written as a
35,460-character attribute and Studio refused anything over 4,096, so genuine
projects came back partly undecodable. The cap is now a million characters and the
reader streams the string. The same release corrected an overclaim — the colours
card said two colours "share the same layers", which only the slice can establish
— and rebuilt the public-claim guard, which had let four false statements about
v0.7.0 ship because it read one line at a time.

**v0.7.2 — a Prusa object's filament survives the crossing.** Every PrusaSlicer
project Studio prepared came out with all objects on filament 1, whatever the user
had assigned, while the geometry was reported byte-identical and nothing was
reported removed. Prepare carries the assignment now — including a slot above four,
which is never renumbered to fit four toolheads — and the new `assignments.py`
lets Fidelity report one row per object: preserved, changed with the slots named,
lost, or not representable.

## Where the evidence lives

- `docs/PAINTED_COLOUR.md` — what painting Studio reads, where it stops, and the
  cross-slicer matrix with what each PARTIAL cell is still missing.
- `backend/tests/fixtures/painted/PROVENANCE.md` — the four painted fixtures: two
  round-tripped through PrusaSlicer 2.9.6 and OrcaSlicer 2.4.2, two **authored in**
  Snapmaker Orca 2.3.5 and Bambu Studio 02.08.02.61, plus the recorded PrusaSlicer
  slice that proves a paint state names filament *N*.
- `backend/tests/doc_truth.py` + `test_doc_truth_guard.py` — the public-claim
  guard and the regression tests that feed each false claim back into it.
- `backend/snapstudio_core/assignments.py` — per-object filament assignment, read
  from either dialect and comparable across the crossing.
- Evidence snapshots are immutable, one per release, under
  `docs/internal/evidence/`. Publishing adds a file and never edits one.

## Known limitations, currently true

- **Windows only.** The installer is not code-signed — verify the SHA256.
- **Purge cannot be separated from printed filament** in Snapmaker Orca output.
- **The fitted nozzle cannot be read** from stock firmware; free storage is not
  reported by it either — both traced, not assumed.
- **Painted colour is read, but a shared layer is not proven by it.** Overlapping
  heights show two colours *can* meet on a layer; the slice decides whether one
  does, so such colours have a toolhead **reserved** rather than being called
  simultaneous.
- **A paint state names filament N — proven by slicing in PrusaSlicer only.** The
  Bambu, Snapmaker Orca and OrcaSlicer dialects decode identically and are read
  from files those slicers authored, but no slice of theirs has demonstrated the
  mapping.
- **A PrusaSlicer object whose volumes use different filaments cannot be fully
  carried**; a prepared U1 object is a single part, and the audit reports the rest
  as not representable rather than picking one.
- **Provenance is evidence, not proof**, and remaining filament is known only
  where something tracks it.
- **One machine, one firmware version.** The read-only harness generalises; the
  sample does not.

## Automation facts worth keeping

- **The real U1** answers at a LAN address on Moonraker port **7125**; the
  hostnames `U1.local` and `snapmaker-u1.local` do not resolve on this network, so
  `tools/hardware/verify.ps1` needs `-PrinterHost <ip>`.
- **Snapmaker Orca 2.3.5's CLI is unusable** — it terminates with an access
  violation on every project, including BambuStudio's own samples. Do not retry it.
- **Painting can be authored through a slicer's GUI** by driving it with SendInput
  and verifying the *saved file* rather than the screen: put the window on the
  primary display (it renders only partially on this machine's secondary,
  mixed-DPI monitors), load a large slab so clicks cannot miss, then select, `N`,
  pick a filament, paint, Ctrl+S.
- **What GUI automation could not do:** open the slicers' *export* and *save-as*
  dialogs reliably. `Ctrl+E` does nothing in Snapmaker Orca, and the "Export
  G-code file" menu item moves because the window resizes itself between the click
  that opens the dropdown and the click on the item. This blocked both the
  paint→slice proof and the Orca re-import check.
- Screen captures on this machine can include the maintainer's unrelated windows.
  Capture a window only while it is genuinely foreground and owns the region.

## The three genuine human gates

Unchanged, and each re-checked rather than copied forward when last verified:

1. **Send the drafted listing correction** to community@snapmaker.com. The
   confirmation thread of 29 June 2026 still holds exactly one message, so no
   reply has been sent. The draft is written; sending it is the maintainer's.
2. **Post the community update** — written in
   `docs/innovation-fund/COMMUNITY_POST.md`, never posted as far as the project's
   own records show.
3. **Submit the SignPath application** for a signed installer; the form accepts
   legal terms on the maintainer's behalf.

Nothing about *entering* the Innovation Fund is outstanding: submitted 24 June
2026, confirmed 29 June, publicly listed among 41 projects. Evaluation closes
22 September 2026. **Do not submit the form again.**

## Next three runtime priorities — ranked, not started

Scored user value × technical depth × product fit × unknown removed ÷ risk.

1. **Second-printer architecture proof** ≈ 167. "Not U1-only by construction" is
   the openness claim the Fund leans on and the only one with no evidence at all.
   One more machine — profile plus capability detection, no per-check branching —
   proves it and exposes every hard-coded U1 assumption.
2. **Material-provider interoperability / U1Hub** ≈ 120. Remaining-filament
   sufficiency stays `unknown` unless a provider is configured, which is the last
   large unknown in the send path. The U1Hub interop proposal is written and
   unimplemented.
3. **Remaining Prusa semantics** ≈ 90 — instances and copies, multi-volume objects,
   per-object overrides, and writing "unassigned" as Orca does (`extruder="0"`)
   rather than as slot 1. This sprint proved the defect class is real and that the
   audit now catches it.

Below these: OBJ/GLB input ≈ 16 — wide appeal, shallow, and it adds an input
format before the existing ones are fully honest. User-reported failures remain
unscorable: there are still none, which is itself the finding.

## Standing rules that bite most often

- Studio never slices, never takes autonomous control of a printer, never uploads
  anything anywhere, and never modifies an original file.
- Never force-kill a slicer, printer or user GUI process. Only processes this
  session started, tracked by PID.
- No local paths, usernames, hostnames, printer addresses or private model names
  in tracked files or screenshots. Snapmaker Orca records a model's source path in
  `model_settings.config`, so fixtures are authored from a public directory.
- Unknown stays unknown. Withdraw an unprovable claim rather than patching it.
- Publishing adds an evidence snapshot; it never edits one. Do not hard-code a
  number a snapshot already carries.
- Do not publish a prerelease to show progress.
