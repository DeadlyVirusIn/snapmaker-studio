# Snapmaker Studio v0.4.0-beta.18.3 — Readiness Truth Fix

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

Trust fixes found by real installed-app testing on a 13-colour / 5-plate project.

## Fixes

- **Project Doctor no longer calls a file "U1-ready / 100" when print-setup risks remain.**
  More colours than the U1's 4 toolheads, or likely-needed supports, now demote the
  headline to "Review before printing" with capped stars and clear at-risk reasons
  (remap to 4 colours, enable supports, arrange plates in Orca).
- **Cost / Pricing / Profit Doctors show the real calculator** (cost, suggested price,
  profit, the grams × price ÷ weight formula) when a model is loaded — no more
  "how to run" placeholder.
- **Compatibility Doctor separates profile from layout.** Success now reads
  "U1 profile copy created" with an explicit caveat that layout isn't verified —
  open in Snapmaker Orca and use **Arrange all plates** before slicing.
- **Scale Doctor 3MF rows are preview-only** — they no longer fake a "copied" action.
  STL keeps a real "Prepare scaled copy". 3MF users get an "Open in Snapmaker Orca to
  resize" path.

Originals are never modified. Studio does not slice. No print-success guarantees.

## Download (unsigned beta)

```
File:    Snapmaker.Studio_0.4.0-beta.18.3_x64-setup.exe
Size:    16128701 bytes
SHA256:  20eca24b7e6c5280680be09899f1cb8caf65a4559b2d8f67cd0a528cf56d0cef
```

Unsigned — SmartScreen may show "Unknown publisher." Verify the SHA256 before installing.
