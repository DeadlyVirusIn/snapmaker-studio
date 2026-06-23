# Screenshots Checklist (beta.11)

Captured from the live beta.11 UI on a sample U1 3MF (`examples/sample_cube_U1.3mf`,
opened from a neutral demo folder so no private or commercial paths are shown).
Everything is local; nothing is uploaded.

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

## New / changed in beta.11

- [x] Dashboard — simplified navigation, the Doctors grid, local library (beta.11). ![Dashboard](screenshots/beta11/dashboard-beta11.png)
- [x] Find Models — browse approved sites in Studio's locked Model Browser, then open the downloaded STL/3MF. Manual download only; no scraping, no API keys. ![Find Models](screenshots/beta11/find-models-beta11.png)
- [x] **Open in Snapmaker Orca (headline)** — once a validated U1 copy is prepared, one click hands it to an installed Snapmaker Orca to slice. Falls back to Install Snapmaker Orca + Copy path when not installed. Advisory, one-way handoff — Studio never slices or controls Orca. ![Open in Snapmaker Orca](screenshots/beta11/orca-handoff-beta11.png)
- [x] Print Quality Doctor — symptom-based advisory checks incl. the "fails even with supports" path. ![Print Quality Doctor](screenshots/beta11/print-quality-beta11.png)

## Carried over from beta.10 (visually unchanged apart from the version footer)

The Project Doctor result, Scale Options Ladder, and Plate Color Remap screens are
unchanged in beta.11 except for the `v0.4.0-beta.11` footer. See
[SCREENSHOTS_BETA10.md](SCREENSHOTS_BETA10.md) for those captures.

## Note on the in-app Model Browser

The Model Browser opens approved sites in a separate, locked Tauri window
(navigation off the allowlist is blocked; no scraping, no import, no login
bypass; the remote page gets no app IPC). It is a native window rather than part
of the main app surface, so the Find Models screenshot above is the canonical
capture of that workflow. To screenshot the native window itself, open Find
Models in the installed app, click an approved site, and capture the window with
the OS screenshot tool.

## Capture tips

- Use a sample file from `examples/`, not a private or commercial model.
- Keep wording on screen advisory ("readiness estimate"), not a guarantee.
- Don't show private local paths; use a neutral demo folder for the sample file.

See also: [JUDGE_OVERVIEW.md](JUDGE_OVERVIEW.md),
[WHAT_TO_TEST_FIRST.md](WHAT_TO_TEST_FIRST.md).
