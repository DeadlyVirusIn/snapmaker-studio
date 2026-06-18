# Snapmaker Studio — Brand

Official visual identity: **"Studio Hub."** This directory is the single source
for the brand. **Source of truth:** the **Brand Identity Asset Pack** —
[`Brand Identity Snapmaker Studio/`](Brand%20Identity%20Snapmaker%20Studio/)
(master deck `Gemini_Generated_Image_awl389awl389awl3.png`). The earlier raster
`studio-hub-concept.png` and its pastel palette are **deprecated** in favor of the
Pack — see [`ASSET_MAPPING.md`](ASSET_MAPPING.md) for the per-file alignment audit.

## Concept
Multi-material **color ribbons** flow into a glowing **transform portal** and
emerge as a finished, multicolor **print (cube)**. One image = the whole product:
many materials, from any ecosystem, transformed into one clean, print-ready
result.

## Rationale
- **Differentiated & ownable.** Not another hexagon/cube cliche — the
  ribbons->portal->cube scene is distinct and instantly "multi-material + transform."
- **Encodes the workflow.** Left->right reads as the mandatory product flow
  **Input -> Diagnose -> Transform -> Validate -> Output** (Validate never dropped).
- **Dark-first, modern SaaS.** Matches the app's dark UI and reads as a platform,
  not a utility.
- **Scales by simplification.** Full scene for hero; portal+cube for small sizes.
- Supersedes the earlier placeholder hexagon/chevron mark (**deprecated**).

## Logo variations
| Variation | File |
|---|---|
| Primary lockup (color, dark) | `logo.svg` |
| Monochrome lockup | `logo-mono.svg` |
| Mark (color) | `icon.svg` |
| Mark (mono) | `icon-mono.svg` |
| Simplified mark (small) | `icon-simple.svg` |
| Favicon | `favicon.svg` |
| App icon | `app-icon.svg` |
| Social / OG | `social-preview.svg` |
| README/site banner | `hero.svg` |

## Documents
- `ASSET_MAPPING.md` — **audit**: every SVG → Pack reference + alignment gaps.
- `EXPORT_CHECKLIST.md` — export gates (GitHub, landing, app icon, installer, README, deck).
- `BRAND_GUIDELINES.md` — rules, typography, dark-mode, clear space, do/don't.
- `COLOR_PALETTE.md` — Pack-verbatim palette (7 streams, Primary Dark, Accent White), status colors.
- `LOGO_USAGE.md` — which asset when, spacing, minimum sizes.
- `APP_ICON_GUIDE.md` — size strategy + Windows `.ico` production.

## Usage examples
- **App shell:** `icon-simple.svg` in the sidebar brand slot (currently a Layers
  icon); `bg = #0A101C` (Primary Dark).
- **GitHub repo:** `hero.svg` (or the concept PNG) at the top of README; set
  `social-preview` as the repo's social image.
- **Browser/site:** `favicon.svg`; OG image = `social-preview.svg`.
- **Installer/app icon:** rasterize `app-icon.svg` per `APP_ICON_GUIDE.md`.

## Future brand evolution
- **Vector trace of the concept art.** These SVGs are clean, faithful
  productions of the motif; a designer vector-trace of the 3D-rendered hero
  (lighting/depth) can replace the raster `studio-hub-concept.png` later.
- **Motion.** The portal core can pulse and ribbons flow for loaders / the demo
  end-card.
- **Palette extension.** Add material accents only via `COLOR_PALETTE.md`.
- **Trademark.** Resolve the "Snapmaker" name usage (official blessing vs
  community labeling) before public GA — see `BRAND_GUIDELINES.md`.
