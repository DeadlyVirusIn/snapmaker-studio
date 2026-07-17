# Trust Status — Snapmaker Studio

Honest, current verification state for the latest beta. This file does **not**
mark a release "accepted" until the interactive install acceptance below is
completed and recorded.

## v0.4.0-beta.21.2 — PARTIAL / PENDING (not accepted)

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
| Installer integrity / SHA256 | **PENDING** — build not yet produced |
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
