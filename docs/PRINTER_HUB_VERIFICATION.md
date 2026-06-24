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
| Upload sliced gcode (multipart) | **Real U1, 2026-06-24** | ✅ **HARDWARE-VERIFIED** (file created on printer, `print_started: false` — no actuation; then deleted) |
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
| 2026-06-24 | 1.4.1.6 (extended) | Upload sliced gcode (send path) | **PASS** | operator-approved; tiny no-motion gcode uploaded (`print_started:false`), confirmed, deleted |
| 2026-06-24 | 1.4.1.6 (extended) | **Start** | **PASS** | operator-approved; state → printing (dwell-only no-motion gcode) |
| 2026-06-24 | 1.4.1.6 (extended) | **Pause** | **PASS** | state → paused |
| 2026-06-24 | 1.4.1.6 (extended) | **Cancel** | **PASS** | state → cancelled, returned to idle |
| 2026-06-24 | 1.4.1.6 (extended) | **Resume** | **FOUND ISSUE** | endpoint correct, but the U1 raised "System Anomaly 0003 0522" — its firmware resume macro needs a real homed/printing context; not reproducible with a no-motion test print. Recovers (clear popup); verify on a real print |
| 2026-06-24 | 1.4.1.6 (extended) | **Emergency stop** | **BUG FOUND + FIXED** | `POST /printer/emergency_stop` returns **404** on this U1's Moonraker. Fixed in code to use canonical `M112` via `/printer/gcode/script` (confirmed available, HTTP 200). Not fired on hardware (avoids a shutdown/restart cycle) |

### Findings from the real-U1 pass (2026-06-24)
- **E-stop endpoint bug (P0 safety):** the U1's Moonraker build does not expose
  `POST /printer/emergency_stop` (404). Fixed: emergency stop now sends `M112` via
  `/printer/gcode/script` (the canonical Klipper emergency shutdown; endpoint confirmed
  200 on the real U1). Ships in the next build.
- **Resume on the U1** triggers a firmware "System Anomaly" if there is no valid print
  context (no-motion/unhomed test). The app calls the correct endpoint; full resume
  verification needs a real, homed, printing job.
- **mDNS** `U1.local` did not resolve on this network; connect by IP works (the app
  supports manual IP entry).

Note: some users run community **extended firmware** (e.g. paxx12). Firmware-capability
detection reads the Klipper object list, so extra macros/objects degrade gracefully;
verify against both stock and extended firmware if possible.
