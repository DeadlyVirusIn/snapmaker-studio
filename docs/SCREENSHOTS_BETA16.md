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

## Submission shot list — still requires manual capture (NOT faked)

Each of these only appears after the OS file picker, or needs the real printer (whose IP
must be redacted), so it can't be captured headlessly. Capture in the installed app, then
redact any IP/hostname/path. Why each is manual:

| Shot | Why it can't be auto-captured |
|------|-------------------------------|
| Dashboard **with the "Start your first print" card** | `dashboard.png` predates beta.16's card — re-capture `/` in the installed app (trivial, no file needed) |
| Plate Remap **populated 2D preview** | needs a multicolor 3MF chosen via the native file dialog |
| Print Quality **evidence panel** | needs a file added via the native dialog |
| Source Check **report** (e.g. a PrusaSlicer file) | needs a file chosen via the native dialog |
| Project Doctor **result** | needs a model opened via the native dialog |
| Open in Snapmaker Orca **handoff** | needs Orca installed (see ORCA_2_3_4_VALIDATION.md) |
| Printer Hub **connected to U1** (live telemetry) | needs the real U1 — and the connected view shows your **real print history (private model/file names)** plus the printer IP. An automated capture was attempted and **discarded for privacy** (reliable redaction of arbitrary history names isn't safe to automate). Capture manually and redact your IP + history filenames. |
| Control **confirmation dialog** (start/cancel) | only renders with a connected printer + an active control; background shows print history → redact |
| Emergency Stop **confirmation dialog** (not fired) | renders the confirm copy; do **not** confirm/fire it; redact the history visible behind the dialog |

Note: the connected Printer Hub and its dialogs were intentionally **not committed** as
screenshots — they exposed the operator's real U1 print history (private names). They are
hardware-verified in [`PRINTER_HUB_VERIFICATION.md`](PRINTER_HUB_VERIFICATION.md); capture
them manually with your own history redacted before sharing.

Steps for each are in [`JUDGE_DEMO.md`](JUDGE_DEMO.md). A 60–90s shot list / voiceover is
in [`DEMO_VIDEO_SCRIPT.md`](DEMO_VIDEO_SCRIPT.md).
