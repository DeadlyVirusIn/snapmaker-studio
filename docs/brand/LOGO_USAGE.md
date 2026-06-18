# Snapmaker Studio — Logo Usage

## Which asset, when
| Context | Asset |
|---|---|
| Dark backgrounds (default) | `logo.svg` (color lockup) |
| Light / single-color / print | `logo-mono.svg` (set color to ink `#0B0F19`) |
| Square mark, dark UI | `icon.svg` |
| Mark on light / photo | `icon-mono.svg` |
| Small UI (< 40 px), tray, list rows | `icon-simple.svg` |
| Browser tab | `favicon.svg` |
| OS app icon | `app-icon.svg` -> rasterized (see `APP_ICON_GUIDE.md`) |
| Social / OG share | `social-preview.svg` (1200x630) |
| README / site banner | `hero.svg` (or `studio-hub-concept.png` for the full art) |

## Spacing rules
- **Clear space:** keep free space >= the portal-ring radius around the mark; for
  the lockup, >= the cap height of "Studio" on all sides.
- **Lockup spacing:** the wordmark starts one mark-width to the right of the mark;
  don't reflow the two wordmark lines.
- **Alignment:** mark optically centered to the wordmark block.

## Minimum sizes
- Color/mono mark: **40 px** min. Below 40 px -> `icon-simple.svg`.
- Simplified mark / favicon: legible to **16 px** (composition: portal ring +
  cube only).
- Lockup: **28 px** min height.

## Backgrounds
- Color logo only on dark (`#0B0F19`-`#05070D`) or imagery dark enough for the
  white wordmark.
- On light or busy backgrounds use `logo-mono.svg` (ink) or place on a dark chip.
- Never the dark-mode white wordmark on light (invisible).

## Don't
- Don't recolor the spectrum, rotate, skew, add shadows/outlines, or box the mark.
- Don't reorder ribbon->portal->cube (it reads as the workflow direction).
- Don't separate the cube from the portal, or the wordmark from the mark in
  official lockups.
- Don't substitute a different typeface for the wordmark.

## Co-branding / attribution
When shown next to Snapmaker official marks, present Snapmaker Studio as an
independent/community project (see the trademark note in `BRAND_GUIDELINES.md`).
