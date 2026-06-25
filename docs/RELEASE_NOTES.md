# Snapmaker Studio v0.4.0-beta.17.1 — Business Inputs + Trust Completion

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

Follow-up to beta.17: the business tools now ask for *your* numbers instead of leaning on
defaults, the First Layer Doctor reads your actual file, and the Scale Doctor states its
3MF limit up front. Estimates are rough and depend on your inputs — not financial advice,
not a print-success guarantee.

## What's new

- **Business Doctors ask for real inputs.** Cost / Pricing / Profit now have an editable
  **Material & business assumptions** panel — filament price, electricity rate, printer
  price + life (for wear), labour time + rate, waste/failure %, marketplace fee, and
  markup. Edit any value and the numbers update. It shows the formula
  (material + electricity + machine wear + labour + failure buffer → cost; then fee +
  markup → suggested price) and is saved **locally only** (no cloud, no account).
  - Print time comes from the slicer when you send a file to the printer; otherwise
    time-based costs show as 0 and say so.
  - Spool weight, material type, packaging, and shipping aren't in the estimate yet —
    stated plainly in the panel. **Rough estimate, not financial advice.**

- **First Layer Doctor reads your file.** Open a model and Studio shows **"What Studio
  found in this file"** — bed-contact / footprint / stability findings from the real
  geometry — with general symptom advice as a fallback. If there's no strong file signal,
  it says so honestly.

- **Scale Doctor is clear about 3MF.** A notice appears next to the controls when you open
  a 3MF: *scaled export is available for STL in this beta; for 3MF, preview here and
  resize in Snapmaker Orca.* The "Prepare scaled copy" buttons appear for STL only — no
  misleading action on unsupported formats. (STL scaled export from beta.17 is unchanged.)

## Carried forward

beta.17's Scale Doctor STL export and Compatibility Doctor "Prepare U1 copy", plus all
beta.16.x: hardware-verified Printer Hub, Print Quality file evidence, Source Check, Plate
Remap, Model Browser. Local-first. Studio does not slice; never takes autonomous control;
originals are never modified.

## Limitations (honest)

- Business estimates depend on your inputs and rough assumptions — not financial advice.
- 3MF scaled export, multi-part scaling, and spool/material/packaging/shipping cost inputs
  are roadmap items.
- Windows installer is **unsigned** — verify the SHA256.

## Download (unsigned beta)

```
File:    Snapmaker.Studio_0.4.0-beta.17.1_x64-setup.exe
Size:    16124721 bytes
SHA256:  26bfbc1f0a1b046e6de17277179f7315047adc5fcdb60c6632d6c824a4e92df9
```

Unsigned — SmartScreen may show "Unknown publisher." Verify the SHA256 before installing.
Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.17.1/docs/windows-install.md).
