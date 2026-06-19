# Snapmaker Studio — Brand Guidelines

> **Source of truth:** the **Brand Identity Asset Pack** —
> [`Brand Identity Snapmaker Studio/`](Brand%20Identity%20Snapmaker%20Studio/)
> (master deck `Gemini_Generated_Image_awl389awl389awl3.png`). Do not redesign;
> align assets to the Pack. See [`ASSET_MAPPING.md`](ASSET_MAPPING.md) (per-file
> audit), [`COLOR_PALETTE.md`](COLOR_PALETTE.md) (Pack-verbatim palette), and
> [`EXPORT_CHECKLIST.md`](EXPORT_CHECKLIST.md). The earlier hexagon/chevron mark
> and the pastel `studio-hub-concept.png` palette are **deprecated**.

## Primary identity (non-negotiable)
- The **Studio Hub** scene is the **source of truth** and the primary identity:
  **glowing filament ribbons → transform hub/portal → multicolor print cube.**
- The primary mark is **NOT** a dots-only symbol, **NOT** a chevron, and **NOT**
  a bare cube or hexagon. Those were the rejected placeholder; do not use them.
- The **simplified mark** (`icon-simple.svg`, `favicon.svg`) is **only** for small
  sizes (< 40 px / favicon / tray). It keeps ribbon stubs + hub + cube so it still
  reads as the Hub — never substitute a bare cube. Never use the simplified mark
  as the primary logo.

## The mark
Multi-material **color ribbons** flow into a glowing **transform portal** and
emerge as a finished, multicolor **print (isometric cube)**.

It encodes the product in one image:
- **Ribbons (spectrum)** → multi-material input from any ecosystem
- **Portal / lens with a bright core** → diagnose + transform (the engine)
- **Multicolor cube** → a clean, validated, print-ready result
- Left-to-right flow → the mandatory workflow **Input → Diagnose → Transform →
  Validate → Output** (Validate is never dropped — see `../ROADMAP.md`).

## Assets (`docs/brand/`)
| File | Use |
|---|---|
| `logo.svg` | Primary lockup (mark + stacked wordmark), **dark-mode**. |
| `logo-mono.svg` | Monochrome lockup (`currentColor`) for light bg / single-color. |
| `icon.svg` | Full color mark (ribbons + portal + cube), transparent. |
| `icon-mono.svg` | Monochrome mark (`currentColor`). |
| `icon-simple.svg` | **Simplified** mark (portal ring + cube) for small UI. |
| `favicon.svg` | Dark tile + simplified mark, legible on any tab. |
| `app-icon.svg` | Dark rounded tile + full mark (rasterize → `.ico`/`.png`). |
| `social-preview.svg` | 1200×630 OG card. |
| `hero.svg` | README/site banner. |
| `studio-hub-concept.png` | Approved reference artwork (source of truth). |

See `COLOR_PALETTE.md`, `LOGO_USAGE.md`, `APP_ICON_GUIDE.md`, and `README.md`
(brand index: concept, rationale, variations, usage, evolution).

## Typography
- **Inter** (fallback: Segoe UI, Arial, sans-serif).
- Wordmark: "Snapmaker" 700 (white on dark), "Studio" 800 with the spectrum
  gradient.

## Dark-mode standard
The brand is **dark-first** (Primary Dark `#0A101C`). The color logo is for dark
surfaces; on light surfaces use `logo-mono.svg`/`icon-mono.svg` set to ink.

## Clear space & minimum sizes
- Clear space ≥ the portal ring radius on all sides of the mark.
- Full mark min: 40 px. **Below 40 px use `icon-simple.svg`/`favicon.svg`**
  (ribbons drop out by design); legible to 16 px.
- Lockup min height: 28 px.

## Iconography (in-app)
Line icons, 1.75 px stroke, rounded joins (Lucide-style), neutral by default;
spectrum accents only for status (verdict badges) and the brand mark.

## Do / Don't
- ✅ Keep ribbon order left→portal→cube (the workflow reads in that direction).
- ✅ Use `icon-simple` below 40 px; use mono on light/photographic backgrounds.
- ❌ Don't recolor the spectrum arbitrarily, reflect the flow, or drop the portal.
- ❌ Don't place the dark-mode color logo on light backgrounds.

## Trademark note
"Snapmaker" is a Snapmaker trademark. Snapmaker Studio is an **independent
open-source project — not affiliated with or endorsed by Snapmaker**. State that
clearly on every public-facing surface (README, landing, app About, docs). Any
future sponsorship or endorsement must be documented separately before it is
claimed. (Tracked in `../archive/RELEASE_READINESS.md` / `../INNOVATION_FUND.md`.)
