# Snapmaker Studio v0.4.0-beta.16.1 — Printer Hub safety patch

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

A small safety patch on top of beta.16. No feature changes.

## Fixes

- **Emergency Stop now works on the Snapmaker U1.** On a real U1, the printer's
  Moonraker build returns **404** for `POST /printer/emergency_stop`, so the beta.16
  Emergency Stop action errored and did nothing. Studio now sends the canonical Klipper
  **`M112`** via `/printer/gcode/script` (confirmed available on the real U1). Emergency
  stop still requires explicit in-app confirmation.

## Real-U1 hardware verification (2026-06-24, firmware 1.4.1.6)

- **Monitoring — hardware-verified:** live state, bed + 4 toolhead temps, bed volume,
  firmware, and job history read correctly from a real U1.
- **Upload / send — hardware-verified:** a test gcode uploaded via the same path the app
  uses (`print_started:false` — no print started).
- **Start / pause / cancel — hardware-tested** on a supervised, no-motion/no-heat
  (dwell-only) test gcode: all worked.
- **Resume** produced a U1 firmware "System Anomaly" because a no-motion/unhomed test is
  not a valid resume context — final verification needs a normal supervised print.
- **Emergency stop was not fired on hardware** intentionally (the fix is verified by the
  available `gcode/script` path); firing it forces a klipper shutdown + restart.

Studio does not slice and never takes autonomous control. Printer Hub provides local,
user-confirmed printer actions; Studio never auto-starts a print.

## Download (unsigned beta)

```
File:    Snapmaker.Studio_0.4.0-beta.16.1_x64-setup.exe
Size:    16119421 bytes
SHA256:  1cef1ce0288cdffbb6382eb74cbaa51569b4e7fe3fc9a1c2d3c034101889f0c4
```

Unsigned — SmartScreen may show "Unknown publisher." Verify the SHA256 before installing.

Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.16.1/docs/windows-install.md).
Verification details: [docs/PRINTER_HUB_VERIFICATION.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.16.1/docs/PRINTER_HUB_VERIFICATION.md).
