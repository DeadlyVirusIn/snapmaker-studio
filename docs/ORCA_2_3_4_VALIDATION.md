# Open-in-Snapmaker-Orca — validation vs OrcaSlicer 2.3.4

> Independent open-source project — not affiliated with or endorsed by Snapmaker.
> Snapmaker Orca / OrcaSlicer is **AGPL-3.0**. Studio does **not** copy, embed, or link
> its code — it only detects an installed copy and launches it with a file. Validation
> below is behavioural only.

## Reference point
- Snapmaker/OrcaSlicer latest release: **v2.3.4** (published 2026-06-11), AGPL-3.0
  (verified via the GitHub API at beta.16 authoring).

## How the handoff works (from Studio's code)
- `detect_orca` checks **verified install locations only** and returns a path **only if
  the exe actually exists on disk** (never a guessed path): `%ProgramFiles%\Snapmaker_Orca\
  snapmaker-orca.exe`, the `(x86)` variant, and `%LOCALAPPDATA%\Programs\Snapmaker_Orca\…`.
- `open_in_orca` launches that exact exe with the prepared 3MF as a **single argument** —
  no shell, no extra flags, no slicing commands. One-way: Studio prepares, the user
  slices in Orca. Studio does not control Orca.

## What is verified vs unverified

| Item | Status | How |
|------|--------|-----|
| Orca detection logic (exists-on-disk only) | **Verified** | `orca.test.ts` + `detect_orca` reads real paths |
| Launch contract (exe + file arg, no shell) | **Verified (code review)** | `open_in_orca` in `main.rs` |
| "Orca not installed" fallback (Install / Copy path) | **Verified** | UI handles null detection |
| Prepared U1 3MF opens cleanly in Orca 2.3.4 | **Unverified here** | No Orca install in this environment |
| Profile/handoff against the 2.3.4 U1 profile | **Unverified here** | Needs Orca 2.3.4 + a U1 profile |

There is **no Snapmaker Orca install in this environment**, so opening a prepared file
in Orca 2.3.4 was not executed here. The export format is unchanged from prior betas,
whose handoff was smoke-tested (see `snapmaker-orca-integration.md`); 2.3.4 is a point
release of the same OrcaSlicer lineage, so regressions are unlikely but **not proven**.

## Manual validation steps (with Orca 2.3.4 installed)
1. Prepare a validated U1 copy in Studio (Project Doctor → Prepare).
2. Click **Open in Snapmaker Orca** → Orca 2.3.4 launches with the file.
3. Confirm the project opens with the **Snapmaker U1 profile**, plates/colours intact.
4. Confirm no error dialog; slice succeeds; export gcode.
5. (With a U1) send the exported gcode via Printer Hub → print.
6. Record the Orca version string and any profile mismatch.

## Error handling to check
- Orca missing → Studio shows Install / Copy-path fallback (no crash).
- File missing/locked → Studio reports `prepared-file-missing` cleanly.
- Wrong/older Orca → Studio still launches the detected exe; the user updates if needed.
