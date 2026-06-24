# Snapmaker Studio v0.4.0-beta.16.2 — Printer Hub control timeout patch

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

A small reliability patch on top of beta.16.1. No feature changes.

## Fixes

- **No more false timeout errors on U1 control actions.** On a real U1, pause/resume
  park and restore the toolhead, which can take **more than 20 seconds**. The previous
  5-second control timeout would report an error even though the printer action actually
  succeeded. Control request timeouts (start / pause / resume / cancel / emergency-stop)
  are now **60 seconds**.

## Real-U1 resume verification (2026-06-24, firmware 1.4.1.6)

- **Resume — hardware-verified** on a real, supervised, homed cold-motion print:
  `printing → paused → printing → cancelled → ready`, no anomaly. The earlier "anomaly"
  came from an unhomed/no-motion synthetic test (an invalid resume context) plus the
  too-short timeout — not an app endpoint bug.
- Already hardware-verified: connection, monitoring (state, bed + 4 toolhead temps, bed
  volume, firmware, history), upload/send, start, pause, cancel.
- **Emergency Stop** remains confirmation-gated and uses `M112` via `/printer/gcode/script`
  (beta.16.1 fix). It was **not fired** on hardware — firing forces a klipper shutdown +
  firmware restart, so it needs explicit operator approval.

Studio does not slice and never takes autonomous control. Printer Hub provides local,
user-confirmed printer actions; Studio never auto-starts a print.

## Download (unsigned beta)

```
File:    Snapmaker.Studio_0.4.0-beta.16.2_x64-setup.exe
Size:    16118302 bytes
SHA256:  76106b28e8824875cbbb0ba5969522cecd39bb733bddfc1fbcf8689e00d4853f
```

Unsigned — SmartScreen may show "Unknown publisher." Verify the SHA256 before installing.

Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.16.2/docs/windows-install.md).
Verification details: [docs/PRINTER_HUB_VERIFICATION.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.16.2/docs/PRINTER_HUB_VERIFICATION.md).
