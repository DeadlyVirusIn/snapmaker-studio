# Snapmaker Studio v0.4.0-beta.16 — first-print clarity

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

**A beginner-first polish release: a guided "start your first print" path, a clear
slice→send handoff, safer printer controls, and plain-language wording — on top of
everything shipped in beta.13–15. Local-first, advisory, no guarantees.**

## What's new (novice first-print polish)

- **Dashboard "Start your first print" card** — the whole path in one place: find a
  model → Source Check → Project Doctor → prepare a safe copy → Open in Snapmaker Orca →
  export gcode → upload in Printer Hub. One "Start guided flow" button, plus a link to
  each step. Cuts through the full Doctors sidebar for first-timers.
- **Slice → export → send hint** — after **Open in Snapmaker Orca**, Studio shows the
  next step: *slice in Orca, export the .gcode, then return to Printer Hub and upload it.*
  A "what is gcode?" tooltip explains it. Studio does not slice — Orca does.
- **Safer emergency stop** — in Printer Hub the emergency stop now sits in its own clearly
  marked danger box (not next to the everyday controls), with a stronger confirm: *halts
  motion/heaters and may require a firmware restart before printing again.* Still confirmed.
- **Plain-language verdicts** — Project Doctor results now pair the verdict with an action:
  "Looks ready to prepare", "Needs a fix first", "Can prepare a U1 copy", "Review before
  printing". Advisory — no "will print" guarantees.
- **Source Check framing** — "what needs Snapmaker Orca" instead of "cannot convert", so a
  detected PrusaSlicer/Cura file reads as a next step, not a failure.

## Carried forward (all live)

Studio Model Browser, Printer Hub (monitor + confirmed control + send sliced gcode),
Source Check, Print Quality evidence, Plate Color Remap 2D preview, Project/Compatibility/
Scale/First-Layer/Multi-Material Doctors, Batch, Library, one-click Open in Snapmaker Orca.

## Judge / proof package

Real screenshots and a 5/15-minute demo path: [JUDGE_DEMO.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.16/docs/JUDGE_DEMO.md),
[SCREENSHOTS_BETA16.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.16/docs/SCREENSHOTS_BETA16.md).
Printer Hub control/send is contract-tested (mocked Moonraker); real-U1 verification is a
manual checklist ([PRINTER_HUB_VERIFICATION.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.16/docs/PRINTER_HUB_VERIFICATION.md)) — there is no U1 in CI.

## Security / trust

Local-first; no cloud, no account. Printer control is user-confirmed (no auto-start).
The installer is **not code-signed** (deferred until adoption / Innovation Fund) — verify
the SHA256 below.

## Download (unsigned beta)

```
File:    Snapmaker.Studio_0.4.0-beta.16_x64-setup.exe
Size:    16117828 bytes
SHA256:  bfdcf855e69361a1aa4d15e5725a3709f1a1909ae074f26a299d5c06609f0788
```

SmartScreen may show "Unknown publisher." Verify the SHA256 before installing.

Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.16/docs/windows-install.md).
