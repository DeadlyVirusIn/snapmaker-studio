# Snapmaker Studio v0.4.0-beta.18 — Cleaner Novice UX

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

A polish release: less crowded pages, shorter beginner-friendly copy, and the safety /
technical detail moved into expandable notes instead of dominating the screen. No change
to the local-first, no-cloud, no-slicing, no-guarantee principles.

## Cleaner pages

- **Find Models** leads with one line — "Browse approved model sites inside Studio." The
  scrape / locked-window / login policy now lives in a collapsed "How Studio handles
  sites" note instead of a wall of text.
- **Business calculator** feels like a simple form: enter your **spool price** to see cost
  and a suggested price. The essentials (spool price, spool weight, grams, material,
  markup) are up top; electricity, machine wear, labour, fees, and shipping are tucked
  under **Advanced costs**. The long formula/disclaimer paragraphs are gone — one calm
  "rough estimate — not financial advice."

## Business polish (also new)

- **Print hours** field — type the time from Orca when Studio doesn't know it; drives
  electricity, machine wear, and labour. Shows "print time unknown" when it isn't set.
- **Material type** (PLA / PETG / ABS / ASA / TPU) — when grams are estimated from volume
  (no slicer weight, no entered weight), the chosen material's density is applied, and the
  source of the grams is shown. A typed weight always wins.
- Material cost stays exactly `grams × spool price ÷ spool weight` (e.g. 82 g × $24 ÷
  1000 g = $1.97, unit-tested), plus packaging and shipping (charged − cost) in the profit.

## Carried forward

Scale STL export + Compatibility "Prepare U1 copy", First Layer file evidence, Print
Quality evidence, hardware-verified Printer Hub, Source Check, Plate Remap, Model Browser.
Local-first. Studio does not slice; never takes autonomous control; originals are never
modified; estimates are not guarantees.

## Download (unsigned beta)

```
File:    Snapmaker.Studio_0.4.0-beta.18_x64-setup.exe
Size:    16125106 bytes
SHA256:  98f1b0a197e441c6fe0f2ee5e4eed2b4bcf34092d91a6f7dbbfa6b9c06b92aee
```

Unsigned — SmartScreen may show "Unknown publisher." Verify the SHA256 before installing.
Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.18/docs/windows-install.md).
