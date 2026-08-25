# Handoff — after the v0.8.0 stable release

Written 2026-08-25, at the end of the sprint that converged two unreleased runtime
sprints into a minor release. This is the state a fresh session should start from.
Read `docs/SUBMISSION_STATUS.md`, `docs/TRUST_STATUS.md` and
`docs/internal/evidence/0.8.0.json` before trusting any number quoted anywhere
else.

## Authority order for project state

Unchanged from v0.7.2, and it still bites:

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
| Current stable | **v0.8.0** — published, not a prerelease, not a draft, marked latest |
| Tag | `v0.8.0` (annotated `52ac5f2`) on commit `e12bc59` |
| Branch | `main`, at that commit — local `main`, `origin/main` and the tag are identical at release time |
| Installer | `Snapmaker.Studio_0.8.0_x64-setup.exe` |
| Size | 17,011,290 bytes |
| SHA256 | `67776cd1db9f620d3c38e656bf831b0f976e0669ce91398caa998e40cf929af6` |
| Release page | <https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.8.0> |

The asset was re-downloaded from the release page after publishing and re-hashed;
size, name and GitHub's own recorded digest all match the binary that passed every
gate. No rebuild happened after verification.

Verification recorded for this release, all against **that exact installer**:
pytest **1346 passed / 4 skipped**, vitest **321**, `u1convert selfcheck`
**27/27**, installed acceptance **34/34** (including the in-place upgrade from the
*published* v0.7.2 and the whole provider workflow against a real Spoolman), real
Snapmaker U1 read-only **39/39**, with `tsc`, `cargo check` and the production
build clean.

## What this release did

**Material providers became reachable.** Studio's engine had read Spoolman for
several releases and nothing in the desktop ever sent it an address, so the
capability was real and no user could use it. Settings now carries a materials
provider section: None or Spoolman, an address, a connection test that reports
both how many spools exist and how many carry a weight something is actually
keeping, and an explicit slot-to-spool mapping with the numbering stated rather
than guessed. Configuration persists locally and reaches the material plan, the
send check and the upload.

**Sufficiency gained provenance and freshness.** A short, tracked, recent weight
blocks a send. A stale one, a weight derived from a spool's declared size, and a
weight with no date all warn. Nothing tracking the spool stays unknown. The
threshold is a week and its consequence is documented: past it a figure may warn
and may never be the sole reason a send is refused.

**Printer intelligence became data-driven.** `printer_profiles.py` plus
`data/printer_profiles/*.json` hold facts — build volume, tool count, what a
machine reports about its own materials, what it is known not to report — each
with a source and a verification level. Live evidence always beats a profile and a
disagreement is reported. A test parses the generic printer modules with `ast` and
fails the build on a conditional that branches on a model name.

**A second printer profile shipped as proof**: a VORON 2.4 250, derived from the
configuration Klipper itself publishes for that machine.

## Verification levels, and the wording that must not slip

- **Snapmaker U1 — hardware verified.** A physical U1 answered this release's
  read-only harness.
- **VORON 2.4 250 — profile verified; hardware not tested by this project.** No
  VORON has ever been connected to Studio.

Never write "VORON supported", "VORON tested", "multi-printer hardware verified"
or "works on VORON". The qualifier is the claim. `desktop/src/routes/Printers.tsx`
holds the labels and `PrinterVerificationLabels.test.ts` fails the build if the
qualifier is dropped.

## What Spoolman can and cannot answer

Studio reads Spoolman and never writes to it — no creating spools, no decrementing
anyone's remaining weight after a print. Consumption tracking belongs to the tool
that owns the data.

Facts about the real software, learned by running one rather than mocking it, and
pinned in `backend/tests/fixtures/providers/spoolman_0_26_1.json`:

- archived spools are omitted unless `allow_archived=true` is passed;
- a `remaining_weight` is *always* present because Spoolman computes it, so its
  presence proves nothing — Studio calls a figure tracked only when something has
  been recording consumption against that spool;
- there is no `updated` field; `registered` is creation time and `last_used` is
  absent until something has printed, so **no date is the common case**.

## U1Hub — deliberately not integrated

Re-audited 2026-08-25 against its current `main`. `GET /api/spools` and
`GET /api/slots` do exist, but carry no schema or version, are undocumented for
external use, sit behind its own password gate, and serve its own interface. More
decisively, **U1Hub tracks spool identity and not remaining weight**, so it has
nothing to answer the sufficiency question with. The proposal in
`docs/interop/U1HUB_INTEROP_PROPOSAL.md` stays open; the offer is unchanged if a
weight ever exists. No internal file of U1Hub's has ever been read.

## Known limitations, currently true

- **Windows only.** The installer is not code-signed — verify the SHA256.
- **Remaining filament is known only where something tracks it.** Without a
  provider it stays unknown, which is the honest answer on a stock setup.
- **The fitted nozzle cannot be read** from stock firmware; free storage is not
  reported by it either — both traced, not assumed.
- **Purge cannot be separated from printed filament** in Snapmaker Orca output.
- **Painted colour is read, but a shared layer is not proven by it.** Overlapping
  heights show two colours *can* meet on a layer; the slice decides whether one
  does, so such colours have a toolhead **reserved**.
- **A paint state names filament N — proven by slicing in PrusaSlicer only.**
- **A PrusaSlicer object whose volumes use different filaments cannot be fully
  carried**; the audit reports the rest as not representable rather than picking
  one.
- **The VORON profile describes the 250 mm variant only**, and an absence in the
  published base configuration is not evidence that a particular VORON lacks a
  feature — only a live object list settles that.
- **One machine, one firmware version.** The read-only harness generalises; the
  sample does not.

## Automation facts worth keeping

- **The real U1** answers Moonraker on port **7125** at a LAN address; `U1.local`
  and `snapmaker-u1.local` do **not** resolve on this network, so
  `tools/hardware/verify.ps1` needs `-PrinterHost <ip>`. The address is a runtime
  argument and must never reach a tracked file.
- The hardware harness prints its read-only route list before the first request
  and enforces it in `callRoute`; a route added to the script without being added
  to the list cannot reach a printer.
- The acceptance harness takes `-SpoolmanUrl` and drives the real provider UI —
  choose, type, test, map, restart, confirm persistence. Without it those checks
  are skipped and the rest still run.
- A local Spoolman for testing: `docker run -d --name <own-name> -p 7913:8000
  ghcr.io/donkie/spoolman:latest`, seeded through its own REST API. Stop only
  containers this session started.
- **Snapmaker Orca 2.3.5's CLI is unusable** — access violation on every project.
  Do not retry it.

## The three genuine human gates

Each re-checked rather than copied forward:

1. **Send the drafted listing correction** to community@snapmaker.com. Verify the
   thread state before assuming it is still outstanding.
2. **Post the community update** — written in
   `docs/innovation-fund/COMMUNITY_POST.md`.
3. **Submit the SignPath application** for a signed installer; the form accepts
   legal terms on the maintainer's behalf.

Nothing about *entering* the Innovation Fund is outstanding: submitted 24 June
2026, confirmed 29 June, publicly listed. Evaluation closes 22 September 2026.
**Do not submit the form again.**

## Next runtime priorities — ranked, not started

1. **Remaining Prusa semantics** ≈ 90. Instances and copies, multi-volume objects,
   per-object overrides, and writing "unassigned" as Orca does (`extruder="0"`)
   rather than as slot 1. Now the largest piece of outstanding *code*, and the
   defect class is proven real.
2. **A second material provider through the seam** ≈ 70. Spoolman is the only
   implementation, so "generic seam" is currently one example — the same gap the
   VORON profile closed for printers. OpenSpool or a firmware exposing weight
   would do; U1Hub cannot until it tracks one.
3. **Second-printer hardware verification** ≈ 40, if a machine ever becomes
   reachable. The profile and the whole path exist; it needs a printer, which is a
   human gate rather than work.
4. **OBJ/GLB input** ≈ 16 — wide appeal, shallow, and it adds an input format
   before the existing ones are fully honest.

User-reported failures remain unscorable: there are still none, which is itself
the finding.

## Standing rules that bite most often

- Studio never slices, never takes autonomous control of a printer, never sends
  anything off the user's local network, and never modifies an original file.
  Printer Hub *does* transfer a sliced job to the user's own printer on the LAN —
  only when they press the button and confirm it.
- Never force-kill a slicer, printer or user GUI process. Only processes this
  session started, tracked by PID.
- No local paths, usernames, hostnames, printer addresses or private model names
  in tracked files or screenshots.
- Unknown stays unknown. Withdraw an unprovable claim rather than patching it.
- Publishing adds an evidence snapshot; it never edits one. Do not hard-code a
  number a snapshot already carries.
- Do not publish a prerelease to show progress.
- A development build carrying the previous version string is **not** that
  release. Record the commit, size and hash and say which it is.
