# Snapmaker Studio — Demo Video (60–90s)

Launch/teaser cut. One screen-recording of the real app + a closing roadmap
card. Plain, confident VO; no music bed louder than the voice. Target 75s.

## Logline
"3D printing workflows are fragmented. Snapmaker Studio makes any file print —
anywhere."

## Shot list

| Time | On screen | Voiceover | Capture |
|---|---|---|---|
| **0–10s** | A Bambu/Orca file opened in Snapmaker Orca showing the "Customized Preset" / "newer version" warnings (the failure). | "3D printing workflows are fragmented. Your files get trapped between slicers and printers." | Screen-record Orca loading a foreign file with warnings (the before-state). |
| **10–25s** | Open Snapmaker Studio. Drag **Fox Sake.3mf** onto the drop zone. Doctor auto-runs; shows verdict + issues. | "Open Snapmaker Studio. Drop in any file. The Doctor checks it instantly — and tells you exactly what's wrong." | Studio: Dashboard -> drag-drop -> LiveWorkspace Doctor result. |
| **25–45s** | Click **Make U1-ready**. Loading -> green "Saved U1-ready project" with output path + "Validated". | "One click. Studio rebuilds it as a clean Snapmaker U1 project — your geometry and colors preserved, nothing lost." | Studio: convert action -> success state. |
| **45–60s** | Open the converted `Fox Sake_SnapmakerU1.3mf` in Snapmaker Orca. **No warnings.** Slice/print-ready. | "Open it in Snapmaker Orca. Zero warnings. Ready to print." | Screen-record Orca loading the output clean (the after-state). |
| **60–90s** | Slow pan over roadmap cards: Diagnose . Transform . Validate . Manage . Optimize -> "multi-printer, simulation, plugins." End on logo + tagline. | "This is the start. We're building the unified platform for 3D printing workflows — the operating system for multi-material printing." | Title cards from ROADMAP.md pillars + logo. |

## End card
- Official brand assets: `docs/brand/` (mark `logo.svg`, banner `hero.svg`,
  share `social-preview.svg`). Dark background (`#0B0F19`).
- Show the flow once on screen: **Input → Diagnose → Transform → Validate →
  Output** (Validate highlighted — it's always on).
- Tagline: **"The Operating System for Multi-Material 3D Printing."**
- Sub: _One place. Any file. Any printer. Perfect prints._ ·
  "Local-first · Open source · github.com/DeadlyVirusIn/snapmaker-studio"

## Capture notes
- Use real files (Fox Sake.3mf -> Fox Sake_SnapmakerU1.3mf) — the before/after is
  the whole pitch; do not fake it.
- Record at 1440p, light theme for the app (high contrast for screen capture).
- Keep cursor movements deliberate; pause ~1s on the green success state and on
  the warning-free Orca load.
- No narration over the Orca "zero warnings" beat — let it land silently for ~1.5s.

## Final narration (read for ~75s; ~150 wpm)
1. (0–10) "3D printing workflows are fragmented. Your files get trapped between
   slicers and printers."
2. (10–25) "Open Snapmaker Studio. Drop in any file. The Doctor checks it
   instantly — and tells you exactly what's wrong."
3. (25–45) "One click. Studio rebuilds it as a clean Snapmaker U1 project — your
   geometry and colors preserved, nothing lost."
4. (45–60) "Open it in Snapmaker Orca. Zero warnings. Ready to print."
5. (60–90) "This is the start. We're building the unified platform for 3D
   printing workflows — the operating system for multi-material printing."

## Storyboard (frames)
| # | Frame | Duration | Transition |
|---|---|---|---|
| A | Orca with warning dialog over a Bambu file (the pain) | 0:00–0:10 | hard cut |
| B | Studio Dashboard; file dragged onto hero drop zone | 0:10–0:18 | cut on drop |
| C | LiveWorkspace: Doctor result (verdict + issues) | 0:18–0:25 | quick push-in |
| D | Cursor clicks **Make U1-ready**; progress | 0:25–0:35 | cut |
| E | Green "Saved U1-ready project" + path + Validated | 0:35–0:45 | hold 1s |
| F | Snapmaker Orca opens the output — **no warnings** | 0:45–0:60 | silent 1.5s beat |
| G | Roadmap pillar cards animate in | 0:60–0:78 | slow pan |
| H | Logo + tagline end card | 0:78–0:90 | fade |

## Recording guide
- **Tools:** OBS (or built-in recorder) at 1920×1080/60; cursor highlight on.
- **App:** installed `0.3.0-beta.1`, light theme, 1280×800 client area, no
  personal paths visible.
- **Takes:** record each beat separately (B–E in Studio, A+F in Orca) for clean
  edits; do 2–3 takes of the drag and the click.
- **Audio:** VO recorded separately, denoised; soft music bed −18 dB under VO;
  duck to −24 dB during the "zero warnings" beat.
- **Edit:** assemble per storyboard; total 75s target (trim G if over 90s).
- **Export:** 1080p H.264 MP4 + a captioned variant (autoplay-muted social).

## Production checklist
- [ ] Real `Fox Sake.3mf` ready; output deleted beforehand so the save is live.
- [ ] Orca pre-opened twice (before-file and after-file) for clean A/F takes.
- [ ] Brand end card built from `docs/brand/` + tagline.
- [ ] Captions written from the narration block.
- [ ] No personal/identifying info in any frame.
- [ ] Final length 60–90s; "zero warnings" beat lands silent.
