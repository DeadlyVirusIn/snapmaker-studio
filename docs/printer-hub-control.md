# Printer Hub — control (Phase B) safety + manual verification

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

Studio's Printer Hub talks to the Snapmaker U1's stock Moonraker on the local
network (`U1.local:7125`, LAN-trusted). Phase A is read-only monitoring. Phase B
adds **explicit, user-confirmed control**. No cloud, no account.

## Safety model

- **Nothing auto-runs.** Start, cancel, and emergency-stop each require an explicit
  in-app confirmation before Studio relays the command to the printer.
- **Pause / resume** are reversible and run immediately (no confirmation).
- **Offline blocks everything.** If the printer isn't connected/reachable, no control
  buttons are active.
- **Start shows the filename** and a plain warning: *"Only start a print if the U1 is
  clear, loaded, and ready. Studio sends the command but does not check the bed for
  you."* No success guarantees.
- **Emergency stop** is a dedicated red action: it cuts heaters and halts motion; the
  printer then needs a firmware restart before printing again.
- Studio uploads **sliced gcode only** (`.gcode`/`.g`). It does **not** slice, and it
  does not control Snapmaker Orca.

## Closing the loop (Studio → Orca → U1)

1. Prepare a validated U1 copy in Studio (Project Doctor).
2. **Open in Snapmaker Orca** and slice there; export the gcode.
3. In Printer Hub, **Upload sliced gcode** → Studio offers **Start this print**
   (confirmed). Studio prepares and sends; Orca slices; the U1 prints.

## CI status

There is no physical U1 in CI. Control is covered by **contract tests** that mock
Moonraker (`backend/tests/test_printer_control.py`, 11 tests) and **gating tests**
for the UI safety rules (`desktop/src/lib/printerControl.test.ts`, 8 tests).

## Manual verification checklist (real U1 on the LAN)

- [ ] Printer Hub discovers / connects to the U1 (`U1.local` or IP).
- [ ] Live status, temps, and 4 toolheads render while idle.
- [ ] Controls card is hidden/disabled when the printer is offline.
- [ ] **Upload sliced gcode** uploads a real exported `.gcode` (appears on the printer).
- [ ] **Start** asks for confirmation, shows the filename, and only starts after Confirm.
- [ ] **Pause** pauses immediately; **Resume** resumes.
- [ ] **Cancel** asks for confirmation, then stops the job.
- [ ] **Emergency stop** asks for confirmation, then cuts heaters + halts motion.
- [ ] A disconnected printer surfaces a clear, beginner-friendly error (no stack traces).
- [ ] No private IP/hostnames appear in any shared screenshot.
