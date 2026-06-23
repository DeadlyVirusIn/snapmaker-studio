# Snapmaker Orca integration (reference + handoff design)

Snapmaker Studio aligns with **Snapmaker Orca** as the downstream slicer. Studio
checks/prepares the model; Snapmaker Orca slices it. Studio does not slice and
does not control Orca.

> Reference repo: https://github.com/Snapmaker/OrcaSlicer — **AGPL-3.0**.
> Treat as a compatibility/reference repo only. Do **not** copy source into
> Studio (MIT) without an explicit license review. Nothing in Studio is derived
> from Orca source today.

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

## Confirmed facts (GitHub releases, verified)

- App name: **Snapmaker Orca**. Latest release at audit time: **V2.3.4**.
- Releases page: https://github.com/Snapmaker/OrcaSlicer/releases
- Windows assets: `Snapmaker_Orca_Windows_Installer_V2.3.4.exe` (installer) and
  `Snapmaker_Orca_Windows_V2.3.4_portable.zip` (portable).
- macOS: `Snapmaker_Orca_Mac_universal_V2.3.4.dmg`. Linux: flatpak + Ubuntu zip.

## To verify before building launch/detection (NOT assumed here)

These need confirming against an actual install or the repo — do not hardcode
guesses:
- Installed **executable name + path** on Windows (Program Files vs per-user;
  exe likely named for "Snapmaker Orca" / the Orca binary — confirm).
- **CLI open behavior**: OrcaSlicer-family builds generally open a model when a
  file path is passed as an argument; confirm Snapmaker Orca's exact flags before
  relying on CLI.
- **Snapmaker U1 profile resources**: the printer ID/profile name, bed volume,
  extruder/toolhead count, and filament presets Orca ships for the U1.
- **3MF/project metadata** Orca expects vs what Studio's writer emits.

## Integration design (handoff, not control)

1. After Project Doctor / a safe-copy export exists, offer **"Open in Snapmaker
   Orca"** — hand the prepared 3MF to Orca (open the file with Orca / the OS
   default handler). Requires a verified install (see v2 below).
2. If Orca isn't detected, show **"Install Snapmaker Orca"** → the official
   releases page (link-out only).
3. Never imply Studio slices, controls, or automates Orca. It is a one-way file
   handoff the user initiates.

## Compatibility audit (Studio's U1 assumptions vs Orca)

Studio already targets the U1 with: 270×270×270 mm bed, 4 toolheads, 3MF
("bambu-family") projects, and guidance to "open in Snapmaker Orca and slice."
Action items (read-only audit, no writer changes without tests):
- Cross-check Studio's bed dimensions + toolhead count against Orca's U1 printer
  profile resources.
- Map Studio's compatibility checks to Orca's actual profile/setting names so the
  Compatibility Doctor speaks Orca's vocabulary.
- Confirm Studio's exported 3MF opens cleanly in Snapmaker Orca with the U1
  profile. **Do not change the 3MF writer/export unless a test proves a gap.**

## UX

- Beginner copy: "Studio checks the model first. Snapmaker Orca slices it next."
- Handoff CTA appears **only when a prepared file/safe copy exists**: "Open in
  Snapmaker Orca."
- When Orca isn't installed: "Install Snapmaker Orca" (official releases link).
- No "Studio slices" claim anywhere.

## Prioritized implementation plan

- **v1 (safe, now):** beginner copy + "Install Snapmaker Orca" link-out to the
  official releases page. Pure copy + known-good URL; no new permissions.
- **v2 (beta.11):** detect an installed Orca (verified registry keys / known
  install paths — confirmed, not guessed) and add "Open in Snapmaker Orca" using
  a scoped opener (e.g. `tauri-plugin-opener`) to open the exported 3MF. Falls
  back to the install link when not detected.
- **v3 (later):** align Studio's Compatibility Doctor vocabulary + any profile
  assumptions to Orca's U1 resources, after auditing them. Writer changes only
  with tests.

## Security / trust guardrails

- No AGPL source copied into Studio; reference repo used for compatibility facts
  only.
- Install path is link-out to the official releases page (no third-party mirrors).
- No hardcoded/guessed exe paths — detection ships only with verified paths.
- The opener (v2) is scoped to opening the user's prepared file; Studio never
  passes slicing commands or controls Orca.
- No private filesystem paths surfaced in the UI.

## Verified this gate (Snapmaker Orca repo, main)

- Printer **model/profile name: "Snapmaker U1"** (variants `Snapmaker U1 (0.2/0.4/0.6/0.8 nozzle).json`, all `inherits: fdm_U1`). Studio's "Snapmaker U1" naming matches.
- **printable_height: 270.05 mm** → Z ≈ 270. Studio's 270 Z assumption is correct.
- **Multi-toolhead** (`single_extruder_multi_material: 0`); the 0.4 variant's tool-change/purge handles **T0–T3 = 4 toolheads**. Studio's "4 toolheads" assumption matches.
- Default bed: "Textured PEI Plate".
- **Not numerically captured:** exact X/Y `printable_area`. Studio uses 270×270; Z is confirmed and the bed family is consistent — confirm the X/Y values against the profile before treating 270×270 as exact.

Result: Studio's U1 bed/toolhead/profile-name assumptions align with the Orca U1 profile. No bed/toolhead correction needed for beta.10.

## Manual Windows smoke test (REQUIRED before publishing beta.10)

Cannot be run in this environment (no Snapmaker Orca install, no GUI). Run on a
Windows machine with Snapmaker Orca installed:

1. Install Snapmaker Orca (official release).
2. In Studio, open a sample 3MF (`examples/sample_cube_U1.3mf`), run Project Doctor.
3. "Make U1-ready" to export the safe copy.
4. Open the exported 3MF in Snapmaker Orca; select the **Snapmaker U1** profile.
5. Confirm it loads without errors, geometry/plates/colours intact, and slices.
6. Repeat with a Plate Color Remap export and a multicolor file.

If all open + slice cleanly → the Orca compatibility gate is fully PASS. If any
fail → that's a P0 to fix before publishing.

## Gate result

Code/copy/assumptions: **PASS** — Doctors name Snapmaker Orca + Snapmaker U1
correctly, U1 bed/toolhead facts align with the verified profile, no
slice/control claims, no fake compatibility guarantees. **Conditional on** the
manual Windows smoke test above (real "opens + slices in Snapmaker Orca"), which
this environment can't run. Hold publish until that one manual test passes.
