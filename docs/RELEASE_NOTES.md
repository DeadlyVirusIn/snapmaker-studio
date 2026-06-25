# Snapmaker Studio v0.4.0-beta.18.4 — Layout & Orca-Accurate Scale Fit

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

Two real-usage trust fixes on top of beta.18.3.

## Fixes

- **Real 3MF layout detection.** Studio now reads each placed object's transformed bounding
  box and reports layout readiness — `fail` when an object sits outside the plate or the
  arrangement is wider than the 270 mm bed, `warn` for multi-plate projects it can't fully
  verify, `unknown` when there's no placement data. Project Doctor folds this in, so a
  profile-compatible file is not called ready while layout is unverified or off-plate. Next
  action: open in Snapmaker Orca and **Arrange all plates** before slicing.
- **Orca-accurate Scale Doctor fit.** The size ladder no longer labels a scale "Safe /
  Recommended" from dimensions alone. Snapmaker Orca scales about an object's fixed centre
  and rejects a scale when the placed bbox crosses the plate boundary or height limit, so
  Studio now checks placement too. When it can't verify placement (multi-plate, off-plate),
  the ladder is shown as **size-only** — "Largest fit by size only … verify in Orca" — with
  no false "Recommended". STL keeps a real prepare action; 3MF stays preview-only.

Originals are never modified. Studio does not slice. No print-success guarantees.

## Download (unsigned beta)

```
File:    Snapmaker.Studio_0.4.0-beta.18.4_x64-setup.exe
Size:    16131795 bytes
SHA256:  48bcfe686ae2f1b28fad7265ba3f4cad43a653f1abdface82d9e4170670b8672
```

Unsigned — verify the SHA256 before installing.
