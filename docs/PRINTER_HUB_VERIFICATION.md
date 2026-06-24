# Printer Hub — verification status (v0.4.0-beta.15)

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

Honest statement of what is verified vs unverified. The U1 runs stock Moonraker/Klipper
on the LAN (confirmed by Snapmaker's own `u1-moonraker` / `u1-klipper` / `u1-fluidd`
repos), so the Printer Hub talks to a standard, documented API.

## What is mocked / what is verified / what is unverified

| Capability | Verified by | Status |
|------------|-------------|--------|
| Discovery (`U1.local:7125`, probe) | `test_moonraker.py` (mocked HTTP) | **Contract-verified, not hardware** |
| Live status / temps / 4 toolheads parsing | `test_moonraker.py` | **Contract-verified** |
| History / health / firmware / diagnostics parse | `test_moonraker.py` | **Contract-verified** |
| Control: pause/resume/cancel/start endpoints | `test_printer_control.py` (mocked Moonraker) | **Contract-verified, not hardware** |
| Upload sliced gcode (multipart) | `test_printer_control.py` | **Contract-verified** |
| Emergency stop endpoint | `test_printer_control.py` | **Contract-verified** |
| UI safety gating (offline blocks; start/cancel/e-stop confirm) | `printerControl.test.ts` (8 tests) | **Verified (pure logic)** |
| **End-to-end on a real U1** | — | **UNVERIFIED — no physical U1 in CI** |

There is **no physical Snapmaker U1 in this build/CI environment**, so no command has
been issued to real hardware. The contract tests assert the correct Moonraker
endpoint/method/payload and graceful failure; they do not prove the U1 accepts them.
We do not claim hardware readiness.

## Manual verification checklist (run on a real U1 on the LAN)

Monitoring:
- [ ] Printer Hub discovers / connects to the U1 (`U1.local` or its IP).
- [ ] Live status, progress, bed + 4 toolhead temps render while idle and while printing.
- [ ] History, health, firmware cards populate (or degrade cleanly if unavailable).
- [ ] A disconnected printer shows a clear, beginner-friendly error (no stack traces).

Control (have filament loaded, bed clear, supervise the machine):
- [ ] Controls are disabled while the printer is offline.
- [ ] **Upload sliced gcode** puts a real exported `.gcode` on the printer.
- [ ] **Start** asks to confirm, shows the filename, starts only after Confirm.
- [ ] **Pause** pauses immediately; **Resume** resumes.
- [ ] **Cancel** asks to confirm, then stops the job.
- [ ] **Emergency stop** asks to confirm, then cuts heaters + halts motion (Klipper then
      needs a firmware restart).
- [ ] No private IP/hostname appears in any shared screenshot.

## Results log (fill in when hardware is available)

| Date | U1 firmware | Item | Pass/Fail | Notes |
|------|-------------|------|-----------|-------|
| _pending_ | _stock / paxx12-extended?_ | _…_ | _…_ | _no U1 available at beta.16 authoring_ |

Note: some users run community **extended firmware** (e.g. paxx12). Firmware-capability
detection reads the Klipper object list, so extra macros/objects degrade gracefully;
verify against both stock and extended firmware if possible.
