# Snapmaker Studio — Innovation Fund Demo (v0.4.0-beta.15)

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

Audience: a beginner who has never used a Snapmaker U1. Everything runs locally — no
cloud, no account, nothing uploaded. Findings are advisory readiness estimates, not
guarantees of print success.

## The story (one line)
Studio takes a beginner from "I found a model" to "it's printing on my U1" — checking,
preparing, and sending — without them needing to understand a slicer first.

## Full beginner flow (the spine of the demo)

| # | Step | Where | Expected result | Evidence / screenshot |
|---|------|-------|-----------------|-----------------------|
| 1 | Find a model | **Find Models** → click an approved site | Site opens in the locked Studio Model Browser window (no Chrome/Edge) | `screenshots/beta16/model_browser.png` |
| 2 | Understand the file | **Source Check** → choose the downloaded STL/3MF | Detected source slicer + "can read / can't convert yet / next step" | `screenshots/beta16/source_check.png` |
| 3 | Diagnose | **Project Doctor** (or open the file → Workspace) | Readiness verdict (READY/REPAIRABLE/…) + geometry findings, plain language | `screenshots/beta16/project_doctor.png` |
| 4 | Fix / prepare | **Prepare** a U1 profile copy (review in Orca before slicing) | A copy is created; original never modified | `screenshots/beta16/prepare.png` |
| 5 | Open in Orca | **Open in Snapmaker Orca** | Installed Orca launches with the prepared file (one-way handoff) | `screenshots/beta16/orca_handoff.png` |
| 6 | Send to printer | **Printer Hub** → Upload sliced gcode → confirm Start | Gcode uploads; Start asks for confirmation, shows filename | `screenshots/beta16/printer_control.png` |
| 7 | Monitor | **Printer Hub** | Live state, progress, bed + 4 toolhead temps | `screenshots/beta16/printer_monitor.png` |

(Steps 5–7 need an installed Snapmaker Orca and a real U1; if absent, the demo shows
the confirmed-control UI in its offline/guarded state and the Orca detection/launch
path — see PRINTER_HUB_VERIFICATION.md and ORCA_2_3_4_VALIDATION.md.)

## 5-minute version (wow, no hardware needed)
1. **Source Check** a PrusaSlicer or Bambu file → "Studio knows what this is and what's
   safe." (30s)
2. **Project Doctor** on a real model → readiness + geometry risks in plain English. (90s)
3. **Plate Color Remap** on a multicolor 3MF → the 2D preview: "see exactly what colour
   changes and what stays protected; your original is never touched." (90s)
4. **Print Quality Doctor** → pick "fails even with supports" → Add file → evidence from
   the model (overhangs, tip risk). "Advice grounded in YOUR file, not generic." (60s)
5. **Printer Hub** → show monitor + the confirmed control card. "Local, safe, no
   auto-start." (30s)

## 15-minute version
Run the full 7-step flow above end to end, then add:
- **Model Browser**: approved-sites-only, locked, no scraping/login-bypass (trust story).
- **Batch Prepare** + **Project Library** (manage many files).
- **Cost/Pricing/Profit Doctors** (the "should I sell this?" angle).
- Close with the **trust posture**: local-first, unsigned-but-SHA256-verified install,
  user-confirmed printer control, no cloud/account.

## What to emphasize to judges
- Beginner-first: plain language, advisory (never "100% success"), originals safe.
- Differentiation vs Orca/Fluidd: Studio is the *pre-slice intelligence + trust layer*,
  not another slicer or web UI. It explains, prepares, and routes.
- Honesty: it says what it can't do yet (e.g. convert PrusaSlicer settings), which builds
  trust rather than overclaiming.
