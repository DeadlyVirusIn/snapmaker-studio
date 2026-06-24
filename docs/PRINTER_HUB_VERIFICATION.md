# Printer Hub — verification status (v0.4.0-beta.15)

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

Honest statement of what is verified vs unverified. The U1 runs stock Moonraker/Klipper
on the LAN (confirmed by Snapmaker's own `u1-moonraker` / `u1-klipper` / `u1-fluidd`
repos), so the Printer Hub talks to a standard, documented API.

## What is mocked / what is verified / what is unverified

| Capability | Verified by | Status |
|------------|-------------|--------|
| Discovery / connection (Moonraker `:7125`) | **Real U1 on LAN, 2026-06-24** | ✅ **HARDWARE-VERIFIED** |
| Online / printer state (`klippy_state`) | Real U1 (`/server/info`, `/printer/info`) | ✅ **HARDWARE-VERIFIED** (ready/standby) |
| Bed + toolhead temperatures | Real U1 (`/printer/objects/query`) | ✅ **HARDWARE-VERIFIED** (bed 24°, extruder 24°) |
| 4-toolhead presence (mcu e0–e3) | Real U1 (`/printer/objects/list`) | ✅ **HARDWARE-VERIFIED** |
| Bed volume (axis_maximum) | Real U1 (toolhead object) | ✅ **HARDWARE-VERIFIED** (271×335×275 mm) |
| Firmware version | Real U1 (`/printer/info.software_version`) | ✅ **HARDWARE-VERIFIED** (1.4.1.6, extended firmware) |
| History / totals | Real U1 (`/server/history/totals`) | ✅ **HARDWARE-VERIFIED** (16 jobs) |
| Control: pause/resume/cancel/start endpoints | `test_printer_control.py` (mocked Moonraker) | **Contract-verified; hardware test pending safety approval** |
| Upload sliced gcode (multipart) | `test_printer_control.py` | **Contract-verified; hardware test pending** |
| Emergency stop endpoint | `test_printer_control.py` | **Contract-verified; intentionally NOT fired on hardware** |
| UI safety gating (offline blocks; start/cancel/e-stop confirm) | `printerControl.test.ts` (8 tests) | ✅ **Verified (pure logic)** |

**Read-only monitoring is hardware-verified** against a real Snapmaker U1 on the LAN
(2026-06-24): the printer's stock-style Moonraker returned live state, temps, all four
toolheads (mcu e0–e3), bed volume, firmware version (1.4.1.6 — a community **extended
firmware**; the firmware-capability reader walks the Klipper object list, so the extra
macros are handled gracefully), and job history — exactly the data the Printer Hub
parses. Network identifiers (IP, hostname) are redacted from this doc and all
screenshots. **Control was NOT issued to the real printer** in this pass: per the safety
rules, no start / pause / resume / cancel / upload / emergency-stop runs without explicit
operator confirmation that the machine is supervised, the bed is clear, and it is safe.

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
| 2026-06-24 | 1.4.1.6 (extended) | Discovery + connection (Moonraker :7125) | **PASS** | reached on LAN by IP (mDNS `U1.local` did not resolve on this network) |
| 2026-06-24 | 1.4.1.6 (extended) | Online / state | **PASS** | klippy ready, standby |
| 2026-06-24 | 1.4.1.6 (extended) | Bed + toolhead temps | **PASS** | bed 24°, extruder 24° |
| 2026-06-24 | 1.4.1.6 (extended) | 4 toolheads + bed volume | **PASS** | mcu e0–e3; 271×335×275 mm |
| 2026-06-24 | 1.4.1.6 (extended) | History / totals | **PASS** | 16 jobs |
| 2026-06-24 | 1.4.1.6 (extended) | Control (start/pause/cancel/upload/e-stop) | **NOT RUN** | pending explicit safety approval; printer was idle |

Note: some users run community **extended firmware** (e.g. paxx12). Firmware-capability
detection reads the Klipper object list, so extra macros/objects degrade gracefully;
verify against both stock and extended firmware if possible.
