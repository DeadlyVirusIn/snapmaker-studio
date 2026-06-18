# Brand Export Checklist

> **Source of truth:** the **Brand Identity Asset Pack**
> ([`Brand Identity Snapmaker Studio/`](Brand%20Identity%20Snapmaker%20Studio/)).
> Every exported asset must match the Pack's 7-stream spectrum, Primary Dark
> `#0A101C`, Accent White, and Inter type. See [`ASSET_MAPPING.md`](ASSET_MAPPING.md)
> for current per-file gaps. Tick a box only once the export matches the Pack.

## GitHub (repo)
- [ ] `hero.svg` → README banner (aligned to §1, 7-stream spectrum)
- [ ] `social-preview.svg` → 1200×630 PNG set as repo **Social preview** (Settings → General)
- [ ] `favicon.svg` → GitHub Pages favicon (if Pages enabled)
- [ ] Org/repo avatar ← `app-icon.svg` rasterized to 460×460 PNG

## Landing page (`docs/landing/`)
- [ ] `favicon.svg` linked in `<head>`
- [ ] `hero.svg` as the hero visual
- [ ] `social-preview.svg` → `og:image` + `twitter:image`
- [ ] Inter loaded (weights 400/600/700); Primary Dark `#0A101C` background
- [ ] Spectrum usage limited to the mark/material story (neutral UI elsewhere)

## App icon (desktop)
- [ ] `app-icon.svg` → rasterize @ 16/32/48/64/128/256 px
- [ ] Bundle to multi-resolution `.ico` (Windows) — `src-tauri/icons/icon.ico`
- [ ] `.png` set for Tauri `icons/` (32, 128, 128@2x, Square*Logo, StoreLogo)
- [ ] Tile background = Primary Dark `#0A101C`; mark centered with clear space ≥ portal radius
- [ ] Add §3 white/grey tile + monitor-mockup variants (currently missing)

## Windows installer
- [ ] Installer/uninstaller icon ← the `.ico` above
- [ ] Tauri `productName` / window title = "Snapmaker Studio"
- [ ] NSIS/MSI header + sidebar art derived from `hero.svg` (dark, on-brand)
- [ ] Tray/taskbar icon legible at 16 px (use `icon-simple.svg`/`favicon.svg`)
- [ ] Verify icon renders crisp on light AND dark Windows taskbars

## README
- [ ] Top banner = `hero.svg` (already referenced; re-export to spectrum)
- [ ] Status/verdict color chips match `COLOR_PALETTE.md` Status table
- [ ] Brand link points to `docs/brand/README.md` and the Asset Pack
- [ ] No deprecated pastel hexes referenced in copy

## Innovation Fund deck
- [ ] Title/cover uses `logo.svg` lockup on Primary Dark `#0A101C`
- [ ] Master deck `Gemini_Generated_Image_awl389awl389awl3.png` as the brand-identity slide
- [ ] Workflow slide mirrors §8 interface mockup (Input → Diagnose → Transform → Validate → Output)
- [ ] Palette slide = §6 Official Color Palette (7 streams + Primary Dark + Accent White)
- [ ] All screenshots use the in-app neutral UI; spectrum only on the mark/status
- [ ] Inter throughout; no off-brand fonts or pastel spectrum

## Pre-publish gate (all surfaces)
- [ ] Colors validated against [`COLOR_PALETTE.md`](COLOR_PALETTE.md) (Pack-verbatim)
- [ ] No distort / stretch / recolor (Pack §9 "Usage Guidelines")
- [ ] Trademark note present where required (see `BRAND_GUIDELINES.md`)
