# Snapmaker Studio — Innovation Fund submission status (frozen)

> Independent open-source project — not affiliated with or endorsed by Snapmaker.
> "Snapmaker" is a trademark of its respective owner.

## Latest release

- **Version:** v0.4.0-beta.16.2 — Printer Hub Control Timeout Patch
- **URL:** https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.4.0-beta.16.2
- **Installer:** `Snapmaker.Studio_0.4.0-beta.16.2_x64-setup.exe`
- **SHA256:** `76106b28e8824875cbbb0ba5969522cecd39bb733bddfc1fbcf8689e00d4853f`
- Unsigned beta — verify the SHA256 before installing.

## Real-U1 hardware-verified (2026-06-24, firmware 1.4.1.6)

- Connection (by IP; mDNS fallback)
- Monitoring — live state, bed + 4 toolhead temps, bed volume, firmware, job history
- Upload / send (no print started)
- Start
- Pause
- Resume — on a supervised homed cold-motion print: `printing → paused → printing → cancelled → ready`, no anomaly
- Cancel

## Code-verified but intentionally NOT fired on hardware

- **Emergency Stop** — uses `M112` via `/printer/gcode/script` (the `/printer/emergency_stop`
  endpoint 404s on the U1's Moonraker; `gcode/script` confirmed HTTP 200). Not fired
  because firing forces a klipper shutdown + firmware restart; needs explicit operator
  approval.

## Known limitations

- Windows installer is **unsigned** (deferred until adoption / Innovation Fund); SmartScreen
  may warn — verify SHA256.
- Actual Emergency Stop firing not performed on hardware (M112 path is code-verified).
- Studio **does not slice** — it hands a prepared copy to Snapmaker Orca.
- Studio **never takes autonomous control** — Printer Hub actions are local and
  user-confirmed; Studio never auto-starts a print.

## Best demo / proof docs

- [JUDGE_OVERVIEW.md](JUDGE_OVERVIEW.md) — what it is, why, how it differs
- [JUDGE_DEMO.md](JUDGE_DEMO.md) — 5 / 15-minute walkthrough
- [DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md) — 60–90s shot list + voiceover
- [PRINTER_HUB_VERIFICATION.md](PRINTER_HUB_VERIFICATION.md) — hardware-verification record
- [SCREENSHOTS_BETA16.md](SCREENSHOTS_BETA16.md) — proof captures + manual shot list
