# Trust Status — Snapmaker Studio

Honest, current verification state for the latest beta. This file does **not**
mark a release "accepted" until the interactive install acceptance below is
completed and recorded.

## v0.4.0-beta.21 — PARTIAL / PENDING (not accepted)

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
