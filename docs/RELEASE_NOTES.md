# Snapmaker Studio v0.4.0-beta.15 — Plate preview, evidence, Source Check

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

**Three roadmap features land together: a visual Plate Color Remap preview, evidence-
backed Print Quality advice, and a Source Check that reads what kind of file you have.
All local, read-only, advisory — no cloud, no account, no guarantees.**

## Plate Color Remap — visual preview

The remap wizard now shows a real 2D plate map: every object on the plate appears as a
colour chip filled with its filament colour, the object you're changing shows its
colour going from → to, and painted details and gold/accent colours are flagged as
protected. A legend spells out the source → target swap and which plates stay
untouched. A plate whose colours are painted per-face is no longer a dead end — Studio
still shows the object map and explains why there's no base slot to swap. Your original
file is never modified; export still makes a verified copy. (A full 3D render is future
work; this answers "what changes, what stays" today.)

## Print Quality Doctor — evidence from your file

Pick a symptom, then optionally add your STL/3MF. Studio grounds the advice in *your*
model: it pulls evidence from its own read-only doctors — overhangs and supports-likely,
tip/stability risk, first-layer contact area, bed fit, filament types, colour count —
and shows a "What Studio found in your file" panel with ok/warn/risk badges next to the
general checks. If a symptom has no strong file signal, the general checklist still
applies. Advisory only — no guarantees, no auto-fix, nothing changed.

## Source Check — what file is this, and what's safe next?

Open any STL or 3MF and Studio tells you the source: a bare STL mesh, a generic 3MF, a
Bambu-family 3MF (Snapmaker Orca / Bambu Studio, with a Snapmaker U1 flag), a
PrusaSlicer project, or a Cura project. For each it lists what Studio can read (printer
model, filament colours/types, geometry), what it cannot convert yet (e.g. PrusaSlicer
or Cura print settings), any risks (a non-U1 profile), and the recommended next step for
the U1. Unknown files are reported honestly — Studio never claims a conversion it
doesn't actually do.

## Carried forward

Studio Model Browser (locked Studio-owned window, approved sites only), Printer Hub
(monitor + safe, confirmed control + send sliced gcode), Project Doctor, batch, library,
and one-click Open in Snapmaker Orca. Studio does not slice and does not control Orca.

## Security / trust

Local-first; no cloud, no account. Source Check, Print Quality evidence, and Plate
Remap preview are all read-only — they never modify your files. No "100% print success"
claims anywhere.

## Download (unsigned beta)

Only download from the official GitHub release, and verify the checksum.

```
File:    Snapmaker.Studio_0.4.0-beta.15_x64-setup.exe
Size:    16119500 bytes
SHA256:  991e852c37a03e1eec0730a6b70bc4e8bc1c8ca3218db949ce4f05ff1cab9ebf
```

This is an **unsigned Windows beta** — SmartScreen may show "Unknown publisher."
Verify the SHA256 before installing. Code signing remains planned.

Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.15/docs/windows-install.md).
