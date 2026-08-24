# Trust Status — Snapmaker Studio

Honest, current verification state for the current release. A release is only marked
**ACCEPTED** once the automated suites, the acceptance harness running against the
published installer, and — from beta.24 onward — read-only verification against a
real Snapmaker U1 have all passed and are recorded here.

## v0.6.0 — ACCEPTED

**The workflow becomes one thing.** Everything below ran against *this installer*
— the exact asset on the release page, verified by SHA256. Canonical values:
[RELEASE_METADATA.md](RELEASE_METADATA.md).

### CI / software

| Check | Command | Result |
|---|---|---|
| Backend tests | `pytest` | **PASS** — 822 passed, 3 skipped |
| Desktop tests | `npm run test` | **PASS** — 284 passed |
| End-to-end pipeline | `u1convert selfcheck` | **PASS** — 23/23 over 15 documented routes |
| TypeScript | `npx tsc --noEmit` | **PASS** — clean |
| Production frontend build | `npm run build` | **PASS** |
| Rust shell | `cargo check` | **PASS** — clean, green in CI |
| Release-document consistency | `pytest tests/test_release_docs.py` | **PASS** |
| Evidence consistency | `pytest tests/test_evidence_consistency.py` | **PASS** — now reads prose, the demo's own length, the screenshot folder and the README's "What's new", not only tables |
| Local-first invariant | `pytest tests/test_local_first.py` | **PASS** |

### Installed application — 28/28, including the upgrade

`pwsh -File tools/acceptance/run.ps1 -Installer <published installer> -UpgradeFrom <v0.5.0 installer>`
Full report: [internal/acceptance-0.6.0.json](internal/acceptance-0.6.0.json).

New in this release: the folder watcher and provenance answer from the frozen
sidecar; the After Slicing page offers to pick jobs up automatically; and one
surface — *This print* — renders the real findings for all three stages, keeps the
honest unknown, and still says Snapmaker Orca slices. Everything v0.5.0 checked
still passes, and the sliced job is byte-identical afterwards.

**Upgrade path:** v0.5.0 is installed, run so it creates real state, then upgraded
in place. The user's data survives and only one installation is registered.

### Real Snapmaker U1 — read-only, 20/20

`pwsh -File tools/hardware/verify.ps1 -PrinterHost <printer>`
Full report: [internal/hardware-0.6.0.json](internal/hardware-0.6.0.json), with the
printer's address replaced before anything reached disk.

Beyond the harness, and on the same machine: the upload-confirmation path was
exercised read-only against a job already on the printer — metadata present,
size matching, parse complete — and against a filename that does not exist, which
correctly reported that the printer has not listed it. Free storage was traced
rather than assumed: `/machine/system_info` reports `total_bytes: 0`,
`/server/files/roots` reports no sizes, and no other endpoint on stock firmware
exposes disk usage.

### Known limitations — stated plainly

- **Windows only.** See [internal/CROSS_PLATFORM_ASSESSMENT.md](internal/CROSS_PLATFORM_ASSESSMENT.md).
- **The installer is not code-signed.** Verify the SHA256.
- **Purge cannot be separated from printed filament** in Snapmaker Orca output.
- **The fitted nozzle cannot be read** from stock firmware.
- **Free storage is not reported** by stock firmware — traced, not assumed.
- **Painted colour cannot be classified** without slicing.
- **Provenance is evidence, not proof.** A job with no object names and no colour
  data can only be `unknown`, and Studio says so rather than matching on the name.
- **Remaining filament is only known when something tracks it.** A stock U1 cannot,
  so sufficiency is unknown unless a provider such as Spoolman is configured.
- **PrusaSlicer projects are read in full but not yet fully carried into a U1
  copy.** What cannot be carried is named in the fidelity report.
- **No print-success guarantee**, and no autonomous printer control.

## v0.5.0 — superseded by v0.6.0 (was ACCEPTED)

**The loop gets intelligent.** Everything below ran against *this installer* — the
exact asset on the release page, verified by SHA256. Canonical values:
[RELEASE_METADATA.md](RELEASE_METADATA.md).

### CI / software

| Check | Command | Result |
|---|---|---|
| Backend tests | `pytest` | **PASS** — 773 passed, 3 skipped |
| Desktop tests | `npm run test` | **PASS** — 282 passed |
| End-to-end pipeline | `u1convert selfcheck` | **PASS** — 21/21 over 13 documented routes |
| TypeScript | `npx tsc --noEmit` | **PASS** — clean |
| Production frontend build | `npm run build` | **PASS** |
| Rust shell | `cargo check` | **PASS** — clean, and green in CI |
| Release-document consistency | `pytest tests/test_release_docs.py` | **PASS** |
| Evidence consistency | `pytest tests/test_evidence_consistency.py` | **PASS** — public counts are generated from the harness reports, not copied |
| Local-first invariant | `pytest tests/test_local_first.py` | **PASS** — the shell reaches one host on one user action; the engine reaches none |

### Installed application — 27/27, including the upgrade

`pwsh -File tools/acceptance/run.ps1 -Installer <published installer> -UpgradeFrom <v0.4.0 installer>`
Full report: [internal/acceptance-0.5.0.json](internal/acceptance-0.5.0.json).

New in this release, on top of everything 0.4.0 checked: the After Slicing page
opens a real `.gcode` and renders the ready-to-send verdict, the what-to-load list
and — on request — the whole print plan with its evidence; the send confirmation
blocks nothing when there is no printer to check against; and the three new engine
routes answer from the frozen sidecar. The sliced job is byte-identical
afterwards, as the project file already was.

**Upgrade path:** v0.4.0 is installed, run so it creates real state, then upgraded
in place. The user's data survives and only one installation is registered.

### Real Snapmaker U1 — read-only, 20/20

`pwsh -File tools/hardware/verify.ps1 -PrinterHost <printer>`
Full report: [internal/hardware-0.5.0.json](internal/hardware-0.5.0.json), with the
printer's address replaced before anything reached disk.

Confirmed against the machine: 196 Klipper objects, its own 271 × 335 × 281 mm
bed, four toolheads, four loaded filaments read with colour and material, the
fitted nozzle still honestly unknown before *and* after slicing, and a sliced job
joined to the live machine — the tool it needs exists, the slot it prints from is
loaded, its material matches at family level.

Read-only by construction: the route allow-list is asserted before the first
request. Nothing started, uploaded or queued; no temperature, motion, homing,
pause, resume, cancel, emergency-stop or configuration call.

Beyond the harness, the same code was run by hand against **real jobs pulled
read-only from the printer's own storage**, including an 89 MB four-colour job
with 764 tool changes — scanned in 0.53 s using 8 MB of memory, with the timeline,
the material comparison and the cost all derived from it. Those files are the
maintainer's own models and are not committed.

### Known limitations — stated plainly

- **Windows only.** macOS and Linux are not built or tested.
- **The installer is not code-signed.** Verify the SHA256. See
  [CODE_SIGNING_POLICY.md](CODE_SIGNING_POLICY.md).
- **Purge cannot be separated from printed filament** in Snapmaker Orca output.
- **The fitted nozzle cannot be read** from stock firmware — confirmed on hardware.
- **Free storage is not reported** by this firmware, so whether a job will fit is
  an honest unknown rather than a guess.
- **Painted colour cannot be classified** without slicing.
- **The Post-Slice Doctor reads; it does not simulate.** It reports what the file
  says the printer will do, which is not a prediction of the print.
- **PrusaSlicer projects are read, not yet fully converted.** Printer, bed,
  filaments, colours, layer heights, supports and per-object assignments are read;
  variable layer height, per-object overrides and support styling cannot be
  carried into a U1 copy and are named in the fidelity report.
- **One outbound request exists** — the update check, on an explicit button. It
  sends nothing about the user, and a test fails the build if that changes.
- **No print-success guarantee**, and no autonomous printer control.

## v0.4.0 — superseded by v0.5.0 (was ACCEPTED; the first stable release)

**The workflow is complete end to end, and this is the build that says so.**
Every check below ran against *this installer* — the exact asset published on the
release page, verified by SHA256 — not against the source tree or a development
server. Canonical hash, size and installer name: [RELEASE_METADATA.md](RELEASE_METADATA.md).

### CI / software

| Check | Command | Result |
|---|---|---|
| Backend tests | `pytest` | **PASS** — 716 passed, 3 skipped |
| Desktop tests | `npm run test` | **PASS** — 263 passed |
| End-to-end pipeline | `u1convert selfcheck` | **PASS** — 18/18, now including the sliced-job reader, the post-slice join and the refusal to invent a purge split |
| TypeScript | `npx tsc --noEmit` | **PASS** — clean |
| Production frontend build | `npm run build` | **PASS** |
| Rust shell | `cargo check` | **PASS** — and green in CI, which it was not before beta.24 |
| Installer builds | `npm run release:windows` | **PASS** |
| Release-document consistency | `pytest tests/test_release_docs.py` | **PASS** |
| Project-state consistency | `pytest tests/test_project_state.py` | **PASS** — no current-state document describes a superseded state |

### Installed application — 27/27

`pwsh -File tools/acceptance/run.ps1 -Installer <published installer> -UpgradeFrom <beta.24 installer>`
Full report: [internal/acceptance-0.4.0.json](internal/acceptance-0.4.0.json).

Six checks are new in this release:

- **Upgrade from beta.24.** The previous version is installed, run so it creates
  real state, then upgraded in place. The user's data survives and only one
  installation is registered afterwards.
- **The sliced job is read in the installed app** — the After Slicing page opens
  a `.gcode`, and the job's own facts render from the file.
- **The purge split is refused** in the shipped UI, not just in tests.
- **The sliced job is byte-identical afterwards**, the same invariant the project
  file has always had.
- Three new engine routes answer from the frozen sidecar, plus the diagnostics
  preview.

Everything from beta.24 still passes: install, launch, sidecar from the install
directory, CDP, `/health` from the app origin, tool and Orca detection, all engine
routes, the launch file, placement, preflight, an honest unknown, "unsupported"
never appearing, prepare, fidelity, not-carried-over, ledger, return-to-original,
best tool, no print-success promise, colour plan with its source, the input file
byte-identical, no orphan sidecar, reopen, uninstall, cleanup, and the
pre-existing installation restored.

**Fixed while running it:** the harness had been reusing a WebView2 profile from
earlier runs, which put a real model name into a screenshot and made one check
pass on stale state rather than on the launch it was meant to prove. It now
starts from nothing, and that check reads the surface that names the open file.

### Real Snapmaker U1 — read-only, 20/20

`pwsh -File tools/hardware/verify.ps1 -PrinterHost <printer>`
Full report: [internal/hardware-0.4.0.json](internal/hardware-0.4.0.json), with the
printer's address replaced before anything reached disk.

| What was proved | Observed |
|---|---|
| Printer discovered | Moonraker on 7125, print state `standby` |
| Firmware object list | 196 Klipper objects |
| The printer's own bed | 271 × 335 × 281 mm, used by the checks |
| Toolhead count | 4 |
| Loaded filament | `#000000 PLA Matte`, `#2D9E59 PLA Silk`, `#F8F81C PLA Basic`, `#FFFFFF PLA Matte` |
| Fitted nozzle | unknown, before *and* after slicing |
| Project vs machine | 6 filament slots against 4 toolheads; 4 loaded against 6 needed |
| **Sliced job vs machine** | the job prints from slot 2 — that toolhead exists, that slot is loaded, and its material matches at family level |
| **Sliced bed vs real bed** | 270 × 270 mm sliced against 271 × 335 mm reported |
| "unsupported" | does not appear anywhere, before or after slicing |

**Read-only by construction.** The route allow-list is asserted before the first
request. No print started, nothing uploaded or queued, no temperature, motion,
homing, pause, resume, cancel, emergency-stop or configuration call.

The same code path was also run by hand against a **real 350 KB Snapmaker Orca
job taken from the printer's own storage**, which read correctly: Snapmaker Orca
2.3.4, Snapmaker U1, 45 layers, 6m 31s, 0.91 g, printing from slot 2. That file is
the maintainer's own model and is not committed.

### Known limitations — stated plainly

- **Windows only.** macOS and Linux are not built or tested.
- **The installer is not code-signed.** SmartScreen shows an unknown publisher
  until reputation accumulates; verify the SHA256. See
  [CODE_SIGNING_POLICY.md](CODE_SIGNING_POLICY.md).
- **Purge cannot be separated from printed filament** in Snapmaker Orca output.
  Studio reports the total and says why it will not split it.
- **The fitted nozzle cannot be read** from stock firmware — confirmed against
  hardware, not assumed.
- **Painted colour cannot be classified** without slicing.
- **The Post-Slice Doctor reads; it does not simulate.** It reports what the file
  says the printer will do, which is not the same as predicting the print.
- **No print-success guarantee**, and no autonomous printer control.
- **Multi-plate repositioning remains withdrawn.**

## v0.4.0-beta.24 — superseded by v0.4.0 (was ACCEPTED)

**The first build verified against a real Snapmaker U1.** Everything below was
checked against *this installer* — the exact asset published on the release page,
verified by SHA256 — not against the source tree or a development server. The
canonical hash, size and installer name are in
[RELEASE_METADATA.md](RELEASE_METADATA.md).

### CI / software — verified in this environment

| Check | Command | Result |
|---|---|---|
| Backend tests | `pytest` | **PASS** — 663 passed, 3 skipped (629 passed, 37 skipped without the fetched real-slicer fixtures) |
| Real-slicer regression fixtures | `pytest tests/test_real_world_3mf.py` | **PASS** — 34 tests against genuine OrcaSlicer, BambuStudio and PrusaSlicer projects |
| End-to-end pipeline | `u1convert selfcheck` | **PASS** — 15/15 over production code paths, also run in CI |
| Desktop tests | `npm run test` | **PASS** — 247 passed across 31 files |
| TypeScript | `npx tsc --noEmit` | **PASS** — clean |
| Production frontend build | `npm run build` | **PASS** |
| Rust shell | `cargo check` | **PASS locally.** The CI job for it had never once passed: Tauri's build script refuses to run when the frozen sidecar is missing, and CI does not freeze it. Fixed after this release by giving CI a placeholder for the resource to resolve against. |
| Installer builds | `npm run release:windows` | **PASS** — NSIS installer produced |
| Release-document consistency | `pytest tests/test_release_docs.py` | **PASS** — including a new check that the Rust crate version matches the released version, which had silently drifted to beta.21.3 |

### Installed application — the acceptance harness

`pwsh -File tools/acceptance/run.ps1 -Installer <the published installer>` —
**21/21 checks passed**. Full report:
[internal/acceptance-beta24.json](internal/acceptance-beta24.json).

The harness installs the built installer into an isolated directory, launches it
with an isolated WebView2 profile and engine data directory, drives the real
window over the Chrome DevTools Protocol, and uninstalls. It stops only the
processes it started, and it exports and restores any pre-existing installation's
uninstall registry entry.

What it proves, in order: the scripted install completes; the application and the
frozen engine sidecar are both present; the app launches and the sidecar boots
from the install directory; the shipped webview is reachable; the engine answers
`/health` from the app's own origin; ecosystem tool detection and Snapmaker Orca
detection work against this machine; all seven engine routes answer from the
frozen sidecar, including `/project_cost`; a model handed to the app on its
command line opens; the placement finding, the preflight card, an honest unknown
and the absence of the word "unsupported" all render; preparing a copy produces
the fidelity report, the not-carried-over list, the fix ledger, the
return-to-original offer, the original-untouched wording and the best-tool panel,
with no print-success promise anywhere; the colour plan renders with its verdict
and the source of its toolhead count; **the input file is byte-identical
afterwards**; closing leaves no orphan sidecar; the app reopens; uninstalling
completes, removes every file, and leaves no sidecar running.

**Deliberately not automated:** launching Snapmaker Orca with a prepared copy. The
handoff target is verified — Orca is detected and its executable resolved — but
actually starting it would leave a user GUI process this harness would then have
to terminate, and this project does not terminate user processes it did not
start. The launch itself is a one-click action a person performs.

### Real Snapmaker U1 — read-only

`pwsh -File tools/hardware/verify.ps1 -PrinterHost <printer>` — **13/13 checks
passed** against a real machine running stock firmware, using this installer.
Full report: [internal/hardware-beta24.json](internal/hardware-beta24.json), with
the printer's address replaced before anything was written to disk.

| What was proved | Observed |
|---|---|
| Printer discovered and answering | Moonraker on port 7125, print state `standby` |
| Firmware object list enumerated | 196 Klipper objects |
| The printer reports its own bed | 271 × 335 × 281 mm — used by the bed check, not a hard-coded default |
| The printer reports its toolhead count | 4 |
| **Loaded filament read correctly** | `#000000 PLA Matte`, `#2D9E59 PLA Silk`, `#F8F81C PLA Basic`, `#FFFFFF PLA Matte` — the bug this release fixes |
| Every loaded slot carries a material and a colour | yes |
| Fitted nozzle reported as unknown, not unsupported | "Nozzle size — check this yourself" |
| Nothing undetected is called unsupported | the word does not appear in the report |
| Project materials vs the machine's toolheads | "project uses 6 filament slot(s); printer reports 4 toolheads" |
| Project materials vs what is actually loaded | "printer reports 4 loaded; project uses 6" |

**This was read-only.** The route allow-list is asserted in the script before the
first request. No print was started, nothing was uploaded or queued, and no
temperature, motion, homing, pause, resume, cancel, emergency-stop or
configuration call was made.

### Known limitations — stated plainly

- **The fitted nozzle cannot be read.** Stock U1 firmware does not expose nozzle
  diameter. This was assumed until beta.24 and is now confirmed against hardware.
  Studio says "check this yourself" and explains the consequence; it will never
  turn that silence into "your printer can't do it".
- **Painted colour cannot be classified without slicing.** A colour applied by
  painting rather than by object assignment is reported as unclassified, not
  quietly counted in the optimistic direction.
- **No print-success guarantee.** Every check is advisory. Studio does not slice,
  and a project that passes every check can still fail on the plate.
- **No autonomous physical control.** Studio never starts, heats, moves or homes
  a printer on its own. Printer Hub's actions each require an explicit
  confirmation.
- **The installer is not code-signed.** SmartScreen will show an unknown
  publisher. Verify the SHA256 before running it — see
  [CODE_SIGNING_POLICY.md](CODE_SIGNING_POLICY.md).
- **Multi-plate repositioning remains withdrawn.** Plate spacing is not recorded
  in a project file, so any move would be a guess. Each plate is still checked on
  whether its own contents fit.

## v0.4.0-beta.23 — SUPERSEDED by v0.4.0-beta.24

**Project to printer preflight, fidelity audit, fix ledger, colour planning,
preset labelling, one-command self-check.** This release also removes a feature —
see "Withdrawn" below — and fixes two defects an independent review found in
beta.22, one of which broke the engine package on a clean install.

### Automated — verified in this environment

| Check | Status | Evidence |
|---|---|---|
| Backend tests | **PASS** | `pytest` — 621 passed, 3 skipped |
| End-to-end pipeline | **PASS** | `u1convert selfcheck` — 15/15 over production code paths, also run in CI |
| Desktop tests | **PASS** | `npm run test` — 247 passed across 31 files |
| TypeScript | **PASS** | `npx tsc --noEmit` clean |
| Production frontend build | **PASS** | `npm run build` |
| Rust shell | **PASS** | `cargo check` clean locally. *Corrected 2026-08-23: this row originally said the check was "now enforced in CI". The CI job existed but failed on every run — Tauri's build script needs the frozen sidecar to exist and CI does not build it — so it enforced nothing until it was fixed after beta.24.* |
| Installer builds | **PASS** | `build:sidecar` + `tauri build` produced the NSIS installer |
| Installer integrity / SHA256 | **PASS** | See [RELEASE_METADATA.md](RELEASE_METADATA.md) |
| Release-document consistency | **PASS** | `test_release_docs.py` — it failed against this tree until the notes and this file were updated, which is what it is for |
| Clean-install package contents | **PASS** | `snapstudio_api` is now included. On beta.22 it was not, so the loopback service could not be imported and `selfcheck` scored 13/15 |
| Preflight honesty | **PASS** | `test_preflight.py` — every unknown stays unknown, asserted on the wording of every unknown the module can produce |
| Fidelity audit | **PASS** | `test_fidelity.py` — 22 cases, most building a deliberately wrong copy and asserting Studio reports it as unverified |
| Fix ledger | **PASS** | `test_fix_ledger.py` — the original is never written to; a shared export cannot carry a directory layout |
| Colour planning | **PASS** | `test_color_plan.py` — painted colour never classified as swappable; layer numbers only ever estimates |
| Ecosystem registry | **PASS** | `test_ecosystem.py` — every entry is reachable; licences are bare identifiers |
| Preset labelling | **PASS** | `test_process_preset.py` — a 0.12 mm project is no longer labelled 0.20 Standard, and an unmatched height gets no invented name |

### Withdrawn in this release

| Item | Why |
|---|---|
| Multi-plate repositioning | An independent review reproduced a derived plate stride wrong by 79%, placing a plate off the bed while reporting success, and the guard meant to catch it was a tautology for two-plate projects. The plate spacing is not in the file, so it was removed rather than patched. Multi-plate projects are still checked per plate. |

### Requires the installed application or real hardware — PENDING at the time

*Historical. Every item below was subsequently completed by the beta.24 harnesses:
`tools/acceptance/run.ps1` (21/21) and `tools/hardware/verify.ps1` (13/13). See the
beta.24 section at the top of this file.*

Observed in the **development build** on 2026-08-23 and evidenced by
`docs/screenshots/beta22/`: the placement card and its fix, the preflight card and
its unknowns, the fidelity report, the fix ledger, the colour plan and the
best-tool panel. That proves the features work; it does not prove the installer
ships them.

| Check | Status | Exact manual check |
|---|---|---|
| Scripted install smoke | **PENDING** | Run the published installer on a clean Windows 10/11 x64 profile; it completes and appears in the Start menu |
| Launch | **PENDING** | Launch from the Start menu; the main window appears with no error dialog |
| Sidecar boot | **PENDING** | One `snapstudio-api.exe` runs and the app shows live data |
| Close / no orphan | **PENDING** | Close the window; no `snapstudio-api.exe` remains |
| Reopen | **PENDING** | Launch again; previously used files still open |
| Uninstall | **PENDING** | Uninstall; the install directory is removed and no sidecar remains |
| Beginner path (GUI) | **PENDING** | Open a 3MF via "Check my model" and confirm placement, colours and preflight all render there |
| Fix Ledger return (GUI) | **PENDING** | Press "Return to the original" and confirm the workflow reopens the untouched original |
| Open in Snapmaker Orca | **PENDING** | With Orca installed, the handoff opens the prepared file and Studio issues no further commands |
| Printer discovery (real U1) | **PENDING** | With a U1 on the LAN and Advanced Mode on, discovery finds it; with it off, the message names Advanced Mode |
| Preflight against real hardware | **PENDING** | Confirm `loaded_filaments()` recognises this firmware's object, or correctly reports "not reported" |
| Interactive GUI acceptance | **PENDING** | Full beginner walkthrough on the installed build |

| Overall trust status | **PARTIAL / PENDING — not accepted** |
|---|---|

## v0.4.0-beta.22 — historical (was PARTIAL / PENDING; superseded by beta.24)

**Object placement, project ↔ printer preflight, fidelity audit, fix ledger, colour
planning, ecosystem tool intelligence, Orca import compatibility.** This
release adds capabilities that write files and make claims about a user's project,
so acceptance is tracked item by item below. Automated checks are recorded with the
command that produced them; anything requiring a person in front of the installed
application stays **PENDING** with the exact check needed. No item is marked PASS
on the basis of an author's expectation.

### Automated — verified in this environment

| Check | Status | Evidence |
|---|---|---|
| Backend tests | **PASS** | `pytest` — see the count in the release commit; suite covers the placement fix, Orca import rules, ecosystem rules, cost basis and the untrusted-archive limits |
| Desktop tests | **PASS** | `npm run test` — vitest, all files |
| TypeScript | **PASS** | `npx tsc --noEmit` clean |
| Production frontend build | **PASS** | `npm run build` (tsc + vite) |
| Rust shell | **PASS** | `cargo check` clean |
| Installer builds | **PASS** | `npm run build:sidecar` + `tauri build` produced the NSIS installer |
| Installer integrity / SHA256 | **PASS** | See [RELEASE_METADATA.md](RELEASE_METADATA.md) for the canonical name, size and hash |
| Release-document consistency | **PASS** | `backend/tests/test_release_docs.py` — no duplicate changelog entries, README hash/size/installer match the canonical metadata, no superseded hash left in a download instruction, app manifests match the released version, trust status covers the current release |
| API response contract | **PASS** | `backend/tests/test_api_contract.py` — every documented top-level field present, including the new routes |
| Project Doctor (engine) | **PASS** | Backend doctor suite over STL and 3MF fixtures |
| Placement detection | **PASS** | `test_plate_placement.py` — off-plate objects detected by edge and millimetres, on real archives |
| Placement fixed-copy workflow | **PASS** | `test_plate_placement.py` — the written copy is re-assessed and every object is on the plate afterwards |
| Original remains untouched | **PASS** | `test_fix_never_modifies_the_original` (byte comparison) and `test_fix_only_touches_the_model_part` (whole-archive byte diff) |
| Ecosystem recommendation accuracy | **PASS** | `test_ecosystem.py` — recommendations only fire from measured traits; unmeasured traits fire nothing; the shipped registry is validated against the trait vocabulary |
| Project Cost with a sliced project | **PASS** | `test_project_cost.py::test_end_to_end_from_a_real_file` |
| Honest refusal on an unsliced project | **PASS** | `test_project_cost.py::test_unsliced_project_gets_an_explanation_not_a_number` |
| Prepare U1 copy + preservation summary | **PASS** | `test_preserve_mode.py` — the preservation invariant fails a conversion on any unreported change |
| Advanced Mode failure message | **PASS** | `test_printer_discovery.py` — unreachable discovery returns the touchscreen instruction, not a bare failure |
| End-to-end pipeline | **PASS** | `u1convert selfcheck` — 15/15, running production code paths over a generated project: parsing, geometry, traits, placement, prepare, import compatibility, fidelity, placement fix, cost, colour planning, ecosystem, preflight, archive limits, input-file integrity and the documented API routes |
| Colour planning beyond four toolheads | **PASS** | `test_color_plan.py` — painted colour is never classified as swappable; layer numbers are only ever offered as estimates |
| Project ↔ printer preflight | **PASS** | `test_preflight.py` — every unknown stays unknown; `test_never_reports_not_detected_as_not_supported` asserts it on the wording of every unknown the module can produce |
| Fidelity audit | **PASS** | `test_fidelity.py` — 22 cases, most of which build a deliberately wrong prepared copy and assert Studio reports it as unverified rather than excusing it |
| Fix ledger and return-to-original | **PASS** | `test_fix_ledger.py` — the original is never written to, and a shared export cannot carry a user's directory layout |

### Requires the installed application or real hardware — PENDING at the time

*Historical. Every item below was subsequently completed by the beta.24 harnesses:
`tools/acceptance/run.ps1` (21/21) and `tools/hardware/verify.ps1` (13/13). See the
beta.24 section at the top of this file.*

Each row states the smallest check that would settle it.

| Check | Status | Exact manual check |
|---|---|---|
| Scripted install smoke | **PENDING** | Run the published installer on a clean Windows 10/11 x64 profile; it completes without error and Snapmaker Studio appears in the Start menu |
| Launch | **PENDING** | Launch from the Start menu; the main window appears with no error dialog |
| Sidecar boot | **PENDING** | With the app open, one `snapstudio-api.exe` is running and the app shows live data (open any Doctor and load a file) |
| Close / no orphan | **PENDING** | Close the window; no `snapstudio-api.exe` remains in Task Manager |
| Reopen | **PENDING** | Launch again; the app starts cleanly and previously used files still open |
| Uninstall | **PENDING** | Uninstall from Apps & features; the install directory is removed and no `snapstudio-api.exe` remains |
| Best Tool panel (GUI) | **PARTIAL** | Observed rendering with its reason and licence in the **development build** on 2026-08-23 (`docs/screenshots/beta22/fidelity_and_ledger.jpg`). Installed-build check: prepare a U1 copy and confirm the panel renders with at least one reason, a licence, and a caution on any preview-maturity tool |
| Placement card (GUI) | **PARTIAL** | Observed in the **development build** naming the object, the edge and the millimetres, and writing a new copy (`placement_and_preflight.jpg`, `placement_fixed.jpg`). Installed-build check: repeat on `examples/demo_u1_showcase.3mf` |
| Preflight card (GUI) | **PARTIAL** | Observed in the **development build** reporting unknowns as "Studio can't tell" with the Advanced Mode instruction (`preflight_unknowns.jpg`). Installed-build check: repeat with and without a printer on the network |
| Fidelity report (GUI) | **PARTIAL** | Observed in the **development build** listing what could not be carried over with its reason (`fidelity_and_ledger.jpg`). Installed-build check: repeat after preparing a copy |
| Colour plan (GUI) | **PARTIAL** | Observed in the **development build** answering "6 colours, 4 toolheads — possible without repainting" with per-colour evidence (`colour_plan.jpg`). Installed-build check: repeat on the same sample |
| Fix Ledger (GUI) | **PARTIAL** | Observed in the **development build** listing both operations with before/after and the return control (`fidelity_and_ledger.jpg`). Installed-build check: press "Return to the original" and confirm the workflow reopens the untouched original |
| Open in Snapmaker Orca | **PENDING** | With Snapmaker Orca installed, the handoff opens the prepared file in Orca and Studio issues no further commands |
| Printer discovery (real U1) | **PENDING** | With a U1 on the LAN and Advanced Mode enabled, discovery finds it; with Advanced Mode disabled, the failure message names Advanced Mode |
| Interactive GUI acceptance | **PENDING** | Full beginner walkthrough end to end on the installed build |

| Overall trust status | **PARTIAL / PENDING — not accepted** |
|---|---|

## v0.4.0-beta.21.3 — historical (was PARTIAL / PENDING; superseded by beta.24)

**Preserve-settings summary cleanup.** Interactive GUI testing of beta.21.2 confirmed
the preserve workflow works (U1 copy created, original untouched, recommended settings
opt-in), but found three presentation problems: value-preserved temperature/retraction
mappings were listed under "Changed for U1 compatibility" (reads as "Studio changed my
temperatures"), a source file already named `..._SnapmakerU1` produced a doubled
`..._SnapmakerU1_SnapmakerU1.3mf` output name, and the default summary exposed raw
technical keys. This release reclassifies value-preserved toolhead mappings under
"Kept" (with mapping note), fixes output naming, and moves raw keys behind a
Technical detail disclosure while keeping real changes and "Could not carry over"
visible.

| Check | Status |
|---|---|
| Backend tests | **PASS** — 345 passed, 3 skipped (adds mapped-classification, type-coercion strictness, and suffix regression tests) |
| Frontend | **PASS** — tsc clean; vitest 161 passed across 25 files (test runner now actually collects `.test.tsx` UI tests — previously eight UI tests were silently never run) |
| Independent code review | Two independent review passes per area; all CRITICAL/HIGH findings fixed (type-coercing equality could hide a real value change as "mapped"; overclaim wording on Dashboard; test-collection gap). Remaining known non-blocking notes: wording-guard count-drift is silent, non-start/end G-code keys fold into the G-code bullet, guard test does not pin its own file list. |
| Installer integrity / SHA256 | **PASS** — `Snapmaker.Studio_0.4.0-beta.21.3_x64-setup.exe`, 16,160,350 bytes, SHA256 `7f69f6716d9a042973bffb0468cc49d13cd17fa273d0a6d283f7f97d9b4cad92` (see [RELEASE_METADATA.md](RELEASE_METADATA.md)) |
| Scripted install smoke | **PENDING** |
| Interactive GUI acceptance | **PENDING (manual installed-app acceptance)** |
| Overall trust status | **PARTIAL / PENDING — not accepted** |

Acceptance checklist for beta.21.3 (on top of the beta.21.2 checklist):

- [ ] A. Prepare a creator-tuned 3MF → temperatures/retraction that were only mapped to the U1 toolhead layout appear under "Kept from the original file" with the mapping note, NOT under "Adjusted/Changed"
- [ ] B. Default summary shows plain language; raw keys only under "Technical detail"; "Could not carry over" visible
- [ ] C. Prepare a file already named `..._SnapmakerU1.3mf` → output has a single `_SnapmakerU1` marker with a numeric copy suffix
- [ ] D. Dashboard prepare step no longer says "safe"

## v0.4.0-beta.21.2 — superseded by beta.21.3 (was PARTIAL / PENDING, not accepted; GUI flow verified, summary presentation fixes required)

**P0 trust fix: preserve creator settings by default.** Multiple users reported that
prepared U1 copies changed the original creator's slicer settings and caused print
problems (webbing/stringing). Confirmed by an original-vs-prepared settings diff:
the U1 profile swap silently replaced nozzle temperatures (e.g. PETG 235/240 → PLA
220/220), Z-hop (0.2 "Normal Lift" → 0.4 "Auto Lift"), prime tower width, wipe tower
position/shape/spacing, and print order ("by object" → "by layer"). Classified **P0**
(silent changes affecting print quality).

Fix shipped in this release: preparing defaults to **Preserve creator settings**
(only minimum U1 wrapper/machine fields change, every change reported); Studio
recommended settings are opt-in; a Kept / Changed for U1 compatibility / Could not
carry over summary is always shown; a runtime preservation invariant fails the
conversion on any unreported change.

| Check | Status |
|---|---|
| Backend tests | **PASS** — 341 passed, 3 skipped (adds preserve-mode + invariant suite) |
| Frontend | **PASS** — tsc clean; vitest 150 passed (adds mode-chooser, summary, race-safety, copy-guard tests) |
| Original-vs-prepared diff proof | **PASS** — creator-tuned fixture: all quality settings preserved byte-identical (temps, retraction, speed, accel, cooling, supports, layer height, tower, print order); zero unaccounted changes; recommended mode reproduces the old swap only when selected |
| Independent code review | Two independent review passes (initial BLOCK verdicts; all CRITICAL/HIGH findings fixed: summary secret redaction, per-extruder value loss, scrub allowlist, invariant tautology, UI races, overclaim copy) — final re-review recorded in `docs/internal/` |
| Installer integrity / SHA256 | **PASS** — `Snapmaker.Studio_0.4.0-beta.21.2_x64-setup.exe`, 16,156,282 bytes, SHA256 `febd9d1be9e3a96a9567cad987c5cf14352815868e3d29ca9ef030045d98aa4a` (see [RELEASE_METADATA.md](RELEASE_METADATA.md)) |
| Scripted install smoke | **PENDING** |
| Interactive GUI acceptance | **PENDING (manual installed-app acceptance)** |
| Overall trust status | **PARTIAL / PENDING — not accepted** |

Acceptance checklist additions for beta.21.2 (on top of the beta.21 checklist):

- [ ] A. Open a creator-tuned 3MF → Prepare U1 copy defaults to "Preserve creator settings"; summary shows Kept / Changed for U1 compatibility / Could not carry over
- [ ] B. Prepared copy opened in Orca shows the creator's temperatures/settings (not 220/220 defaults)
- [ ] C. "Apply Studio recommended U1 settings" changes print behavior only when explicitly selected
- [ ] D. Open an STL → notice says it has no creator slicer settings and uses a U1 starter profile

## v0.4.0-beta.21.1 — superseded by beta.21.2 (was PARTIAL / PENDING, not accepted)

Wording patch on beta.21. The beta.21 GUI check found the flow works but surfaced a
P1 copy-truth issue: fit/profile checks read as print-readiness ("Prints on
Snapmaker U1 — Ready as-is / Ready after preparation", "clean to slice") while the
same report says spacing/layout are not verified by Studio. beta.21.1 replaces that
wording ("Fits U1 profile checks — review in Orca before slicing"; "readable by the
slicer") and pins it with tests (`backend/tests/test_readiness_wording.py`).

| Check | Status |
|---|---|
| Installer integrity / SHA256 | **PASS** — `53f5de884f5e39eba7843deeda119c44049043cb3cc5b8323cf6ce95ba22bf22` (16,136,737 bytes), see `RELEASE_METADATA.md` |
| Backend tests | **PASS** — 330 passed, 3 skipped (adds readiness-wording guards) |
| Frontend | **PASS** — tsc clean; vitest 144 passed |
| Scripted install smoke | **PASS** — silent install → launch (app + sidecar) → exit (no orphan) → uninstall (exit 0) |
| Interactive GUI acceptance | **PENDING (manual installed-app acceptance)** — re-check the beta.21 checklist below on the 21.1 build, plus the new wording row |
| Overall trust status | **PARTIAL / PENDING — not accepted** |

Additional acceptance row for beta.21.1:

- [ ] 0. Validation Center shows "Fits U1 profile checks — … review in Orca" (no "Ready as-is / Ready after preparation / Prints on Snapmaker U1"); Design Health says "readable by the slicer" (no "clean to slice")

## v0.4.0-beta.21 — superseded by beta.21.1 (was PARTIAL / PENDING; GUI flow verified, wording patch required)

Release theme: **one clear path for a novice.** Simple-mode IA collapse (5 nav
items), a prioritized beginner Fix Plan on the open model, dead-end/duplicate
cleanup, developer copy tucked behind disclosures. Advanced mode unchanged. No
backend analysis changes — the Fix Plan reuses checks that already run.

| Check | Status |
|---|---|
| Installer integrity / SHA256 | **PASS** — `792ea37dc8e620cbd9be44fd475d0b1f6531f20a81cec8b44f5a621f43bea2b2` (16,137,296 bytes), see `RELEASE_METADATA.md` |
| Backend tests | **PASS** — 326 passed, 3 skipped (no backend changes) |
| Frontend | **PASS** — tsc clean; vitest 144 passed (new: Simple-IA nav tests, future-tense copy guard) |
| Scripted install smoke | **PASS** — silent install → launch (app + sidecar) → exit (no orphan) → reopen → silent uninstall; same P2 empty-folder leftover as beta.20.4 |
| Interactive GUI acceptance | **PENDING (manual installed-app acceptance)** |
| Overall trust status | **PARTIAL / PENDING — not accepted** |

### Acceptance checklist — manual installed-app acceptance (beta.21)

- [ ] 1. Fresh install lands in Simple mode; sidebar shows exactly: Home · Check my model · My designs · Printer · Help (+ More tools)
- [ ] 2. Existing install that chose Advanced stays Advanced
- [ ] 3. Open STL → "Your fix plan" appears with ≤5 numbered actions, each labelled "Do this in Studio" or "Do this in Orca"
- [ ] 4. Open multi-object 3MF → fix plan includes the arrange/spacing step (honest "Studio can't verify spacing")
- [ ] 5. Check my model → with no model open: honest landing with Open a model; with a model open: goes to the results
- [ ] 6. /doctor/pricing and /doctor/profit land on the Cost page
- [ ] 7. Colors & Materials shows Plate Color Remap directly (no explainer tab); Scale page 3MF rows say "Preview only — resize in Orca" with no disabled button
- [ ] 8. Compatibility findings hide Setting/Evidence behind "Technical detail"
- [ ] 9. Prepare U1 copy → wording stays "review in Orca before slicing"; original untouched
- [ ] 10. Advanced mode nav unchanged from beta.20.4
- [ ] 11. Close/reopen/uninstall clean (as in beta.20.4)

## v0.4.0-beta.20.4 — ACCEPTED — installed-app acceptance passed

Accepted 2026-07-01 after the maintainer completed the interactive GUI acceptance on the
installed build (rows 3–8 + X-button close). Honest limits stay in force:

- Studio prepares **U1 profile copies for review in Snapmaker Orca** — Studio does not slice.
- **Originals are never modified** — preparing a model writes a new copy.
- **No print-success guarantees.**
- **Layout, scale and object spacing remain advisory / unknown** unless verified in
  Snapmaker Orca. **No Orca PartPlate-equivalent validation is claimed.**

Release theme: **release acceptance + trust cleanup** — no new features. App changes
are naming/copy consistency only (Printer Hub naming, no future-tense promises);
everything else is documentation truth repairs, a canonical release-metadata source,
and two new regression tests (naming guard, 3MF zip path-traversal guard).

| Check | Status |
|---|---|
| Installer integrity / SHA256 | **PASS** — `6b1feb43458112c72452f83c20f4d082f30a56f9afaabb91e3bf6d853d48a81b` (16,138,638 bytes), see `RELEASE_METADATA.md` |
| Backend tests | **PASS** — 326 passed, 3 skipped (includes new `test_container_paths.py`) |
| Frontend | **PASS** — tsc clean; vitest 139 passed (includes new `naming.test.ts`) |
| Scripted install smoke (this machine) | **PASS** — silent install → launch (app + sidecar up) → exit (no orphan sidecar) → reopen → silent uninstall (exit 0) |
| Uninstall cleanliness | **PASS with note (P2)** — all files, Start-Menu shortcut and processes removed; one *empty* folder remains at `%LOCALAPPDATA%\Snapmaker Studio` |
| Interactive GUI acceptance (rows 3–8: open STL/3MF, Project Doctor, Prepare U1 copy, opens in Orca, Cost & Pricing) | **PASS** — completed by the maintainer on the installed app, 2026-07-01 |
| Graceful window close (X button) | **PASS** — the maintainer, 2026-07-01: normal X close, no orphan sidecar |
| Overall trust status | **ACCEPTED — installed-app acceptance passed** |

### Acceptance checklist — completed (beta.20.4)

Rows 1/2/9–12 from the scripted smoke; rows 3–8 and the X-button close verified
by the maintainer on the installed app, 2026-07-01. All 12 pass → status ACCEPTED.

- [x] 1. Install app *(scripted: silent install exit 0)*
- [x] 2. Launch from Start Menu *(scripted: shortcut target launches; app + sidecar processes up)*
- [x] 3. Open STL *(maintainer)*
- [x] 4. Open 3MF *(maintainer)*
- [x] 5. Project Doctor works and wording is honest *(maintainer)*
- [x] 6. Compatibility / Prepare U1 copy works (original intact) *(maintainer)*
- [x] 7. Output opens in Snapmaker Orca *(maintainer)*
- [x] 8. Cost & Pricing Doctor works *(maintainer)*
- [x] 9. Close app — no orphan sidecar *(scripted + the maintainer: normal X close, no orphan)*
- [x] 10. Reopen app *(scripted: relaunch OK)*
- [x] 11. Uninstall app *(scripted: silent uninstall exit 0)*
- [x] 12. Confirm uninstall *(scripted: files/shortcut/processes removed; one empty folder left — P2 cosmetic)*

## v0.4.0-beta.20.3 — superseded (was PARTIAL / PENDING, never accepted)

| Check | Status |
|---|---|
| Installer integrity / SHA256 | **PASS** |
| Backend / sidecar boot | **PASS** |
| STL Project Doctor — design score, no CLI text | **VERIFIED** |
| Business Doctor — manual grams entry | **VERIFIED** |
| Object spacing / collision honesty | **VERIFIED (honest "unknown")** |
| Support-enforcer-without-support warning | **VERIFIED** |
| Interactive GUI install smoke | **PENDING (manual installed-app acceptance)** |
| Installed-app acceptance | **PENDING (manual installed-app acceptance)** |
| Overall trust status | **PARTIAL / PENDING — not accepted** |

### What changed (most recent first)

- **beta.20.3 — STL Project Doctor consistency.** A readable STL now gets a real
  design-health score (mesh quality) instead of "—", and the GUI no longer shows raw
  `repair` command-line text — it reads "Create a U1 profile copy, then review it in
  Snapmaker Orca" with a Prepare U1 copy step. Design health and U1-profile
  preparation are shown separately; a healthy STL is never called "ready". (Verified:
  a real STL with readable geometry scores from its mesh, no CLI text.)

Earlier (beta.20.2) — gaps on complex multi-object 3MF projects, fixed:

- **Cost & Pricing Doctor — manual grams.** When Studio can't read grams/volume,
  the calculator no longer dead-ends; it shows the assumptions form, and manual
  grams + Recalculate produces cost / suggested price / profit. (Verified: a file
  with unreadable geometry returns no cost until grams are entered, then computes
  from the entered weight.)
- **Object spacing / collisions — honest "unknown".** Studio does **not** yet
  verify object-to-object spacing for multi-part 3MF layouts (Bambu instancing /
  source_object_id / part matrices / assemble-vs-build coordinate semantics are not
  implemented). An attempted bounding-box detector mis-placed instanced objects —
  it flagged the wrong objects and missed the real Orca-reported collision — so it
  is **intentionally not shipped**. Instead the Project Doctor, Compatibility Doctor
  and Intelligence Report report spacing as unknown: they never say
  ready / no issues / no major blockers for a multi-object plate, and direct the
  user to check Orca for too-close / collision warnings. (Verified on two real
  multi-object files: both report not-ready + the spacing warning.)
- **Support enforcers vs support.** The Compatibility Doctor warns when a model has
  support enforcers but support generation is disabled. (Verified on a real file.)

### Automatically verified (3 clean-room checks passed)

1. **Installer integrity.** Release asset SHA256 =
   `ac69c78ceb081054066378258603c7abd98bf1d0fb66f706a64d5e4460a6acd9`
   (size 15,882,349 bytes). Valid Windows installer.
2. **Backend / sidecar boot.** The re-frozen engine sidecar starts standalone (no
   Python on host) and prints its `{port, token}` handshake.
3. **Business Doctor / spacing / enforcer behaviour** verified in code + unit tests
   (backend 321 passing; frontend tsc clean, 138 passing).

### What is NOT verified / NOT claimed

- The interactive GUI install smoke + installed-app acceptance were **not run** —
  install → launch → open STL/3MF → prepare U1 copy → open in Orca → close/reopen →
  uninstall require a hands-on Windows session. **beta.20.3 is not accepted** until
  these pass.
- Studio does **not** detect object collisions / boundary / bed-clearance itself —
  these are reported as **advisory / not verified** and must be checked in Snapmaker
  Orca. Real Orca-equivalent collision + boundary/clearance detection is deferred to
  a later release.

### Product truths (always true)

- Studio prepares **U1 profile copies for review in Snapmaker Orca**.
- Studio **does not slice** — Snapmaker Orca does.
- **Originals are never modified** — preparing a model writes a new copy.
- **No print-success guarantees.**
- **Object placement / scale / spacing / bed-boundary fit remain advisory** and must
  be verified in Snapmaker Orca before slicing. No Orca PartPlate-equivalent
  validation is claimed.

### beta.20.3 acceptance checklist — superseded

The beta.20.3 checklist was never completed; it is superseded by the beta.20.4
checklist at the top of this file.
