# Trust Status — Snapmaker Studio

Honest, current verification state for the latest beta. This file does **not**
mark a release "accepted" until the interactive install acceptance below is
completed and recorded.

## v0.4.0-beta.20.1 — PARTIAL / PENDING (not accepted)

| Check | Status |
|---|---|
| Installer integrity / SHA256 | **PASS** |
| Backend / sidecar boot | **PASS** |
| Business Doctor UX (manual Recalculate) | **VERIFIED** |
| Interactive GUI install smoke | **PENDING (Kunal)** |
| Installed-app acceptance | **PENDING (Kunal)** |
| Overall trust status | **PARTIAL / PENDING — not accepted** |

### What was verified automatically (3 clean-room checks passed)

1. **Installer integrity.** The published release asset was downloaded and hashed.
   SHA256 = `5e4092b6589d6f33c4dd8b6e0ea4fe3fd202512febdb7800b41dc5cdb5bc09a9`
   (size 15,877,411 bytes), matching the build output. Valid Windows installer.
2. **Backend / sidecar boot.** The bundled, frozen engine sidecar starts standalone
   on a host with no Python installed, prints its `{port, token}` handshake, and
   answers `GET /health` with `200 {"status":"ok"}`. This confirms the packaged
   engine runs without developer tooling.
3. **Business Doctor UX / recalculate behavior** — verified in code and unit tests:
   - The sidebar shows a single **Cost & Pricing Doctor** item (not separate
     Cost / Pricing / Profit entries).
   - Editing assumptions edits a *draft*; the Cost, Pricing and Profit cards do
     **not** recalculate while typing.
   - A **Recalculate** button applies the draft; until then the page shows
     "Changes not applied yet".
   - The grams field reads "Grams used" with the helper "Leave blank to use Studio
     estimate: <n> g" — blank uses the estimate, a typed value overrides it after
     Recalculate. (No confusing "0 = estimate" label.)

### What was NOT run (12 interactive GUI steps)

The clean-room install smoke test was **not** executed end-to-end. The following
require an interactive Windows session and have not been performed:

install → launch from Start Menu → open an STL → open a 3MF → run Project Doctor →
run Compatibility / prepare a U1 profile copy → open the output in Snapmaker Orca →
run the Cost & Pricing Doctor → close the app → reopen the app → uninstall →
confirm clean uninstall.

**beta.20.1 cannot be called accepted** until install → launch → open STL/3MF →
prepare U1 copy → open in Orca → close/reopen → uninstall are manually verified on
a clean (or as-clean-as-possible) Windows environment.

### Product truths (always true, independent of acceptance)

- Studio prepares **U1 profile copies for review in Snapmaker Orca**.
- Studio **does not slice** — Snapmaker Orca does.
- **Originals are never modified** — preparing a model writes a new copy.
- **No print-success guarantees.**
- **Layout / scale placement remains advisory** and must be verified in Snapmaker
  Orca before slicing.

## Acceptance checklist — for Kunal to complete

Run on a clean Windows environment / VM / fresh user profile. Tick each, then
record the result back into this file (and flip the status to ACCEPTED only when
all pass):

- [ ] 1. Install app
- [ ] 2. Launch from Start Menu
- [ ] 3. Open STL
- [ ] 4. Open 3MF
- [ ] 5. Project Doctor works
- [ ] 6. Compatibility / Prepare U1 copy works (original intact)
- [ ] 7. Output opens in Snapmaker Orca
- [ ] 8. Cost & Pricing Doctor works (Recalculate behavior)
- [ ] 9. Close app (no orphan sidecar process)
- [ ] 10. Reopen app
- [ ] 11. Uninstall app
- [ ] 12. Confirm uninstall (clean removal)
