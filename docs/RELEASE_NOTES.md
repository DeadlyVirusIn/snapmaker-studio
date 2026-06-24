# Snapmaker Studio v0.4.0-beta.14 — Printer Hub: monitor, control, send

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

**Watch your Snapmaker U1, control a print safely, and send a sliced file to it —
all locally, no cloud, no account. Pair it with the Studio Model Browser and Project
Doctor for a full local workflow.**

## Printer Hub — now monitor + control

Find your U1 on your network and see it live: print state, progress, bed and 4
toolhead temperatures, history, health, and firmware — read-only, updating
automatically.

New in beta.14, **safe control**:

- **Pause / Resume** a running print (immediate, reversible).
- **Cancel** a print (asks you to confirm first).
- **Upload sliced gcode** to the printer, then **Start this print** — start always
  shows the filename and asks you to confirm.
- **Emergency stop** — a dedicated action that cuts heaters and halts motion.

Safety first: Studio never auto-starts anything. Start, cancel, and emergency-stop
each need an explicit in-app confirmation. If the printer is offline, controls are
off. Start shows the file and a plain warning — *only start a print if the U1 is
clear, loaded, and ready.* Studio uploads sliced gcode only; it does not slice and it
does not control Snapmaker Orca. Details + a manual hardware checklist:
[printer-hub-control.md](printer-hub-control.md).

## Close the loop: Studio → Orca → U1

Prepare a validated U1 copy in Studio (Project Doctor) → **Open in Snapmaker Orca**
and slice there → export the gcode → in Printer Hub, **Upload sliced gcode** and
**Start this print**. Studio prepares and sends; Orca slices; the U1 prints. (Studio
does not slice — it sends gcode you exported.)

## Carried forward

- **Studio Model Browser** — browse approved 3D-model sites in a locked Studio-owned
  browser window; download STL/3MF from the source site, then open them in Studio and
  run Project Doctor. No API keys for beginners. No scraping, mirroring, login/paywall
  bypass, or fake imports.
- Project Doctor, Plate Color Remap, Print Quality Doctor, batch, library, and
  one-click Open in Snapmaker Orca — all unchanged.

## Still to come (honest scope)

Not in beta.14, planned next: a rendered Plate Color Remap 3D preview; evidence
integration for Print Quality Doctor; and broader file-source detection
(PrusaSlicer/Cura/Creality). Printer **control is verified by mocked contract tests**
(no physical U1 in CI) — real-hardware verification is the manual checklist above.

## Security / trust

- Printer Hub is **local network only** — no cloud, no account, no credentials stored.
- Control commands are **user-confirmed relays** to the U1's own Moonraker; the
  backend never starts a job on its own.
- The Model Browser window holds no app capabilities (no IPC to remote pages);
  navigation is locked to the approved-domain allowlist.

## Download (unsigned beta)

Only download from the official GitHub release, and verify the checksum.

```
File:    Snapmaker.Studio_0.4.0-beta.14_x64-setup.exe
Size:    16108521 bytes
SHA256:  44735090d6aea3c7596427b5f37bb9bb346327e91482990405bbbfe4a662119d
```

This is an **unsigned Windows beta** — SmartScreen may show "Unknown publisher."
Verify the SHA256 before installing. Code signing remains planned.

Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.14/docs/windows-install.md).
