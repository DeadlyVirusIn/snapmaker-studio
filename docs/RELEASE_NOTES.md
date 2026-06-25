# Snapmaker Studio v0.4.0-beta.17 — Actionable Doctors + Trust Repair

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

This release closes the gap between *diagnosis* and *action*: two Doctors that used to
stop at advice can now create a real file you can open in Snapmaker Orca. Originals are
never modified. Studio does not slice, and never takes autonomous control.

## What's new

- **Scale Doctor can now create a scaled copy.** Pick a recommended scale (or a custom
  one) and **Prepare scaled copy** writes a new file at that size — the original is never
  changed. The filename carries the scale (e.g. `model_scaled_128_U1.3mf`). The success
  panel shows the scaled dimensions, whether it fits the U1, the validation result, and
  buttons to **Open in Snapmaker Orca**, **Copy path**, and **Run Project Doctor**.
  - **STL input is supported now** (geometry is truly scaled — verified by fixture tests
    that the output bounding box equals the input × scale).
  - **3MF input is intentionally blocked** with a clear message: preview the scale here
    and resize in Snapmaker Orca. Verified 3MF scaled export is coming — we don't ship
    unverified scaling.

- **Compatibility Doctor is no longer a dead end.** When a project carries another
  printer's settings, a **Prepare U1 copy** button creates a clean Snapmaker U1 copy
  (using the existing repair path) so Orca opens it with U1-safe settings. Shows the new
  file, Open in Snapmaker Orca, Copy path, and Run Project Doctor. The original is untouched.

- **Print Quality Doctor** continues to show real, file-specific evidence under "What
  Studio found in your file" when a file is loaded, with general checks as a fallback.

- **Honest labels.** The Cost / Pricing / Profit cards now state they use a default
  material price (your Settings filament price is applied on the main Cost estimate and in
  Batch). Full per-card pricing wiring is on the roadmap.

## Limitations (honest)

- Scaled export and scaling guidance are advisory — a readiness estimate, **not a
  print-success guarantee**.
- Uniform scaling only this release; 3MF scaled export, multi-part/multi-plate scaling,
  and per-card Business pricing are roadmap items.
- Windows installer is **unsigned** — verify the SHA256.

## Carried forward

All beta.16.x capabilities: Printer Hub (hardware-verified monitor + user-confirmed
control + send), Source Check, Plate Color Remap, Model Browser, the other Doctors,
Batch, Library, one-click Open in Snapmaker Orca. Local-first — no cloud, no account.

## Download (unsigned beta)

```
File:    Snapmaker.Studio_0.4.0-beta.17_x64-setup.exe
Size:    16122368 bytes
SHA256:  4e29c863a64bbd594b6c62600395cf499e944ebcd14bbf606041fe82e21081c5
```

Unsigned — SmartScreen may show "Unknown publisher." Verify the SHA256 before installing.
Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.17/docs/windows-install.md).
