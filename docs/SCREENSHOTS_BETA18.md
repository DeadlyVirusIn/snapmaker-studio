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
