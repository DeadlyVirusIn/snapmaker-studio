# Screenshots — beta.18 (real captures)

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

Captured deterministically with a **screenshot harness**: the React frontend served by
Vite, rendered in **headless Edge** (`--headless=new --screenshot`) at 1366×900. No Tauri
native file picker, no backend connection — so **no private data** can appear (printer
shows the default `U1.local` placeholder, disconnected). These prove the cleaned beta.18
page copy and layout.

| Page | File | Proves |
|------|------|--------|
| Dashboard | `dashboard.png` | Launchpad: workflow + "Start your first print" card |
| Find Models | `find_models.png` | One-line "Browse approved model sites inside Studio" (policy collapsed) |
| Source Check | `source_check.png` | Short subtitle, one "Choose a file" action |
| Scale Doctor | `scale_doctor.png` | Concise subtitle + STL/3MF inline note, one CTA |
| First Layer | `first_layer.png` | File-aware entry + symptom picker |
| Print Quality | `print_quality.png` | Symptom picker; file-evidence section |
| Plate Color Remap | `plate_remap.png` | Plate/colour picker |
| Printer Hub | `printer_hub.png` | "Monitor your U1 and send files — every action is confirmed"; controls-off when disconnected |
| Library | `library.png` | "All your models, checked and scored" |
| Batch | `batch.png` | "Add .stl/.3mf files — Studio makes a clean U1 project for each" |
| Settings | `settings.png` | Trimmed read-only hint |
| Help | `help.png` | Concise doc index |

## Harness (screenshot/test support only)

`cd desktop && npm run dev` (Vite), then per route:
`msedge --headless=new --window-size=1366,900 --virtual-time-budget=6000 --screenshot=<f>.png http://localhost:1420<route>`

Frontend-only render (footer shows "Reconnecting…" — no backend by design). Not a product
mode; not shipped in the app. File-loaded Doctor/Business-result states still need a real
file or fixture and are captured manually from the installed app.

## File-loaded states (real backend, bundled samples)

Captured via the harness with the real backend running and a dev-only fallback so headless
Edge can point at it: `?api=PORT:TOKEN` (apiInfo) and `?file=<path>` (dialog). Both are
gated on `import.meta.env.DEV` — **stripped from production builds**, screenshot/test
support only. Files are the repo's bundled samples (`examples/sample_cube.stl`,
`sample_cube_U1.3mf`) — no private data.

| File | Proves |
|------|--------|
| `scale_loaded.png` | 3MF loaded → real recommended-scale ladder (fit/risk), 3MF "preview-only, resize in Orca" constraint inline |
| `scale_success.png` | STL → Preview → Prepare scaled copy flow |
| `compatibility_loaded.png` | U1 3MF → real read-only check ("no known compatibility issues") |
| `source_loaded.png` | Source Check with a file loaded |

## File-loaded set v2 (real backend + synthetic fixture)

| File | Proves |
|------|--------|
| `business_calculator.png` | Workspace with `sample_cube.stl` loaded — real geometry + cost ("~$0.2 in filament, 9.9 g at $20/kg" = grams × price/kg), Design Health |
| `compatibility_issues.png` / `compatibility_success.png` | Synthetic foreign 3MF (`examples/sample_cube_foreign.3mf`) → grouped invalid-setting issues + "Prepare U1 copy" CTA + trimmed read-only banner |

**Foreign fixture:** `examples/sample_cube_foreign.3mf` — the clean U1 sample with a
Bambu-style `printer_settings_id` and out-of-range values (tree_support_wall_count=3,
solid/sparse/wall_filament=0, raft_first_layer_expansion=-1). Synthetic, no private data,
no copyrighted model — only the bundled cube geometry. Triggers 5 invalid + 1 "not U1"
finding so the repair flow can be shown.

**Business assumptions panel** (`business_calculator.png`) and **Print Quality file evidence**
(`print_quality_evidence.png`) are now captured: the Business panel shows the spool inputs,
the grams × price ÷ weight formula, cost breakdown, pricing tiers, profit and the
"rough estimate · not financial advice" line; Print Quality shows "What Studio found in this
file" with the cube's real ~17% overhang evidence (symptom: Poor bridging / overhangs).
