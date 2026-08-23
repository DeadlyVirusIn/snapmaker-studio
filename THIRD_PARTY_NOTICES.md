# Third-party notices

Snapmaker Studio is MIT licensed and contains no third-party source code beyond
its declared package dependencies. This file records the other things a project
can owe: **facts learned from other people's documentation**, and the boundary
Studio keeps around licences it cannot mix with.

`docs/innovation-fund/COMPETITOR_MATRIX.md` states the rule Studio operates
under. This file is Studio holding itself to it.

---

## Knowledge credited

### U1 Print Hub — <https://github.com/dlgambill/u1hub> · MIT

Its README documents that the Snapmaker U1 answers Moonraker on **port 80**
through the printer's own nginx, as well as on Klipper's standard 7125. Studio's
printer discovery probes both because of that (`snapstudio_core/moonraker.py`),
which fixed a real class of "printer not found" where a reachable machine looked
offline.

That is a fact about a printer rather than any of the Hub's code — no code or
data from it is used — but it was learned there and is credited here.

### Snapmaker — Klipper, Moonraker and Fluidd forks

<https://github.com/Snapmaker/u1-klipper> · <https://github.com/Snapmaker/u1-moonraker> ·
<https://github.com/Snapmaker/u1-fluidd> (GPL-3.0)

Studio speaks the documented Moonraker HTTP API over the network. It vendors no
code from these projects and does not link against them.

### 3MF Consortium — the 3MF specification

<https://github.com/3MFConsortium/spec_core> (specification text)

Studio's container reader is an independent implementation of the published OPC
package layout. The de-facto layouts that PrusaSlicer and the
BambuStudio/OrcaSlicer family write are read from publicly observable file
structure, not from their source.

---

## Boundary kept

These projects were studied as **behaviour** — the published symptom a rule
addresses, and the file-format schema it operates on. No source code, resources
or profile data from any of them is present in this repository.

| Project | Licence | Why Studio must not copy from it |
|---|---|---|
| Snapmaker Orca, upstream OrcaSlicer, PrusaSlicer, FOrcaSlicer, OrcaSlicer ImageMap, OctoPrint | AGPL-3.0 | Incompatible with MIT distribution |
| Klipper, Moonraker, Fluidd, Mainsail, SnapmakerU1 Extended Firmware | GPL-3.0 | Incompatible with MIT distribution |
| makerworld-to-snapmaker-u1 | MIT shell over PolyForm-Noncommercial-derived internals | The non-commercial terms travel with the derived parts |
| Snapmaker-U1-Config | none declared | No licence means all rights reserved |

Every Snapmaker Orca import rule in `snapstudio_core/orca_import.py` carries a
comment naming the problem it solves, so the reasoning can be audited against the
published symptom rather than taken on trust.

U1 reference profile values in `snapstudio_core/data/` are derived from Snapmaker
Orca's own bundled defaults, exported directly.

---

## Corrections

If you maintain a project named here and something is wrong — the attribution,
the description, or the fact that you are listed at all — open an issue or a pull
request. Registry descriptions live in
`backend/snapstudio_core/data/ecosystem.json` and are a one-object change.
