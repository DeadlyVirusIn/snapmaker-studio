# Snapmaker Studio — App Icon Guide

Master: [`app-icon.svg`](app-icon.svg) (dark rounded tile + full Studio Hub mark).
Small sizes use the simplified mark so the icon stays legible in the taskbar.

## Size strategy
| Size | Source | Notes |
|---|---|---|
| 256 / 512 | `app-icon.svg` (full mark) | installer, store, large tiles |
| 128 | `app-icon.svg` | ribbons start to thin — still OK |
| 64 / 48 | **`icon-simple.svg`** on dark tile | ribbons drop; portal + cube only |
| 32 / 16 | **`favicon.svg`** | dark tile + cube/ring; the recognizable minimum |

Rule: **>= 128 px -> full mark; < 128 px -> simplified.** Never ship the full
ribbon scene at 16-32 px (it turns to mud).

## Producing the Windows icon set
1. Render PNGs from the SVGs (e.g. with `resvg`/Inkscape/`sharp`):
   - 512, 256, 128 from `app-icon.svg`
   - 64, 48 from `icon-simple.svg` (composited on a `#0B0F19` rounded tile)
   - 32, 16 from `favicon.svg`
2. Pack into a multi-resolution `icon.ico` (e.g. ImageMagick:
   `magick icon-16.png icon-32.png icon-48.png icon-64.png icon-128.png icon-256.png icon.ico`).
3. Replace `desktop/src-tauri/icons/icon.ico` and add the PNGs Tauri expects
   (`32x32.png`, `128x128.png`, `128x128@2x.png`, `icon.png`); update the `icon`
   array in `desktop/src-tauri/tauri.conf.json`.
4. `tauri icon docs/brand/app-icon.svg` can auto-generate most of the set, but
   **swap the 16/32/48/64 entries** for the simplified renders for legibility.

## Safe area
Keep the mark within the inner ~80% of the tile; the rounded corners (radius
112/512) must not clip ribbons or cube.

## Status
Rasterizing + wiring into the app is a **GA blocker** tracked in
`../RELEASE_READINESS.md`. The SVG masters here are final; only rasterization
remains.
