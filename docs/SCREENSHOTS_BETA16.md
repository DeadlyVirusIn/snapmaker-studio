# Screenshots — beta.16 proof set

> Independent open-source project — not affiliated with or endorsed by Snapmaker.
> All real captures from the live app (v0.4.0-beta.15 build). No placeholders. No private
> paths/IPs in frame.

## Captured (real, in this repo — `docs/screenshots/beta16/`)

| Feature | File | What it proves |
|---------|------|----------------|
| Studio Model Browser | `model_browser.png` | Printables loaded in the locked Studio-owned window |
| Find Models control center | `find_models.png` | Approved-site picker + browser controls |
| Source Check | `source_check.png` | The new file/source detector entry page |
| Print Quality Doctor | `print_quality.png` | Symptom picker + "add your file for evidence" |
| Plate Color Remap | `plate_remap.png` | The remap wizard (2D preview appears once a plate + colours are chosen) |
| Printer Hub | `printer_monitor.png` | The Printer Hub page (connect / monitor / control) |
| Dashboard | `dashboard.png` | App shell + entry points |

## Still requires manual capture (needs a file or hardware — not faked)

These views only appear after the OS file picker or with real hardware, which can't be
automated headlessly. Capture in the installed app:

- **Plate Remap 2D preview, populated** — pick a multicolor 3MF, a plate, and a from/to
  colour → the colour-chip map with from→to + protected accents.
- **Print Quality evidence panel** — pick a symptom, Add your file → "What Studio found
  in your file".
- **Source Check report** — choose a non-U1 / PrusaSlicer file → the can-read /
  cannot-convert / next-step report.
- **Project Doctor result** — open a model → readiness verdict + findings.
- **Open in Snapmaker Orca** — with Orca installed (see ORCA_2_3_4_VALIDATION.md).
- **Printer Hub monitor + control on a real U1** (see PRINTER_HUB_VERIFICATION.md).

Steps for each are in [`JUDGE_DEMO.md`](JUDGE_DEMO.md).
