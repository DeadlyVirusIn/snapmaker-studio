# Snapmaker Studio v0.4.0-beta.19 — Product Truth Audit Fixes

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

Systemic readiness-truth fixes from an independent multi-model audit (Codex + Claude;
Antigravity returned empty both runs — documented, not relied on).

## Fixes

- **Profile compatibility is no longer shown as full print readiness.** A new shared
  readiness source means a file is only called "ready" when every readiness category passes
  (layout, colours vs toolheads, supports, profile). Otherwise it reads "Review before
  printing" with the specific reasons and next actions.
- **Workspace, Batch, Projects, Source Wizard, Plate Remap, Intelligence Report, Business
  Doctors and Printer Hub** now use honest status language. "U1-ready / ready to slice /
  U1-clean / Safe copy" no longer appear from a profile verdict or structure validation alone
  — a converted copy reads "U1 profile copy saved · open in Orca and review before slicing".
- **Printer Hub** wording now matches its confirmed-control behaviour ("Monitor + confirmed
  controls"). **Business Doctors** show an honest unavailable state instead of a blank.
  Intelligence Report's dimension-only fit is labelled "Size fit (dimensions only)"; the demo
  report carries a prominent "Sample data — not a real analysis" banner.

Originals are never modified. Studio does not slice. No print-success guarantees. Layout/scale
placement remains an advisory heuristic (verify in Orca), not a full port of Orca's PartPlate.

## Download (unsigned beta)

```
File:    Snapmaker.Studio_0.4.0-beta.19_x64-setup.exe
Size:    16134573 bytes
SHA256:  9b19df978da5fc00e52b9b491079ee3434a3dadd498e3c471ae625d2227a68d7
```

Unsigned — verify the SHA256 before installing.
