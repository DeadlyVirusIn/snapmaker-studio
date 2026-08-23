# Innovation Fund — submission status

> Independent open-source project — not affiliated with or endorsed by Snapmaker.
> "Snapmaker" is a trademark of its respective owner.

**The current submission package is
[innovation-fund/FINAL_SUBMISSION.md](innovation-fund/FINAL_SUBMISSION.md).** The
text that goes in the form is [INNOVATION_FUND.md](INNOVATION_FUND.md). This page
is the status record only.

## Current build

| | |
|---|---|
| Version | **v0.4.0-beta.24** — the first build verified against a real Snapmaker U1 |
| Installer, size, SHA256 | [RELEASE_METADATA.md](RELEASE_METADATA.md) — canonical |
| Verification state | [TRUST_STATUS.md](TRUST_STATUS.md) — **ACCEPTED** |
| Release | <https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.4.0-beta.24> |

Unsigned beta — verify the SHA256 before installing. See
[windows-install.md](windows-install.md) and
[CODE_SIGNING_POLICY.md](CODE_SIGNING_POLICY.md).

## Has anything been submitted?

**Not by this repository, and not by any tooling in it.** Phase 1 of the Open
Competition closes 7 September 2026 and the package above is prepared but not
sent — the form asks for the maintainer's name and email.

An earlier version of this page recorded **v0.4.0-beta.16.2** as a "frozen
submission record". That build exists and its hash is below, but nothing in this
repository records whether a form was ever actually submitted for it. Only the
maintainer knows, and it matters: the fund does not publish a way to revise a
submission, so an existing entry would change what to do next.

| Earlier frozen build | |
|---|---|
| Version | v0.4.0-beta.16.2 |
| Installer | `Snapmaker.Studio_0.4.0-beta.16.2_x64-setup.exe` |
| SHA256 | `76106b28e8824875cbbb0ba5969522cecd39bb733bddfc1fbcf8689e00d4853f` |
| Release | <https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.4.0-beta.16.2> |

Do not install that build for testing — use the current one.

## Hardware verification

**beta.24, 2026-08-23 — read-only, 13/13.** Printer discovered, 196 Klipper
objects enumerated, the printer's own 271 × 335 × 281 mm bed used, four loaded
filaments read with colour and sub-type, the fitted nozzle correctly reported as
unknown rather than unsupported, and the project's materials compared both against
toolhead count and against what is loaded. Nothing was started, uploaded or
queued; no temperature, motion, homing, pause, resume, cancel, emergency-stop or
configuration call was made. Record:
[TRUST_STATUS.md](TRUST_STATUS.md) · raw evidence
[internal/hardware-beta24.json](internal/hardware-beta24.json).

**Earlier, 2026-06-24, firmware 1.4.1.6 —** Printer Hub's confirmed actions were
exercised on hardware under supervision: connect, monitor, upload without starting
a print, start, pause, resume and cancel. Emergency stop is code-verified only
(`M112` via `/printer/gcode/script`; the `/printer/emergency_stop` endpoint 404s on
the U1's Moonraker). It has deliberately never been fired, because firing it forces
a Klipper shutdown and firmware restart. Record:
[PRINTER_HUB_VERIFICATION.md](PRINTER_HUB_VERIFICATION.md).

## Known limitations

- The Windows installer is **unsigned**; SmartScreen will warn. Verify the SHA256.
- Emergency stop has never been fired on hardware.
- Studio **does not slice** — it hands a prepared copy to Snapmaker Orca.
- Studio **never takes autonomous control**. Printer Hub actions are local and
  each requires an explicit confirmation; Studio never auto-starts a print.
- Studio is advisory. It does not guarantee a successful print.

## Judge-facing documents

- [innovation-fund/JUDGE_OVERVIEW.md](innovation-fund/JUDGE_OVERVIEW.md) — five
  minutes, from a standing start
- [innovation-fund/JUDGE_WALKTHROUGH.md](innovation-fund/JUDGE_WALKTHROUGH.md) —
  reproduce every claim yourself
- [innovation-fund/DEMO_SCRIPT_90_SECONDS.md](innovation-fund/DEMO_SCRIPT_90_SECONDS.md)
  — the recorded demo, beat by beat
- [media/snapmaker-studio-demo.mp4](media/snapmaker-studio-demo.mp4) — 71 seconds
  of the running application
