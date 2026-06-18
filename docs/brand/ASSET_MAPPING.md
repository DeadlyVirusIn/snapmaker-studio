# Asset Mapping & Alignment Audit

> **Source of truth:** the **Brand Identity Asset Pack** —
> [`Brand Identity Snapmaker Studio/`](Brand%20Identity%20Snapmaker%20Studio/).
> Master deck: `Gemini_Generated_Image_awl389awl389awl3.png`.
> This document maps every existing `*.svg` to its Pack reference and records how
> well it currently aligns. **No assets were redesigned in this sprint** — this is
> the audit + alignment plan only.

## The Pack at a glance
| Deck section | Content | Drives |
|---|---|---|
| 1. Hero & Primary Logo | Hub scene + stacked wordmark "Snapmaker / Studio" | `logo.svg`, `hero.svg` |
| 2. Icon Variations Grid | Full color streams · neon glow · single shape · white outline | `icon.svg`, `icon-mono.svg`, `icon-simple.svg` |
| 3. App Icons | Rounded dark tile (color), white/grey tile, desktop mockup | `app-icon.svg` |
| 5. Master Files | icon / wordmark / logo SVG | all SVGs |
| 6. Official Color Palette | 7 streams + Primary Dark `#0A101C` + Accent White | `COLOR_PALETTE.md` |
| 7. Favicon Stress Test | 16→256 px legibility | `favicon.svg`, `icon-simple.svg` |
| 9. Usage Guidelines | Don't distort/stretch/alter; min clear space | `LOGO_USAGE.md` |

## Per-file mapping
| SVG | Maps to (Pack) | Status | Notes |
|---|---|---|---|
| `logo.svg` | §1 Hero & Primary Logo | ⚠ palette mismatch | Layout + Inter wordmark match; stream colors are pastel, not the 7 saturated streams. |
| `logo-mono.svg` | §2 "single color shape" | ✅ aligned | `currentColor`, no palette dependency. |
| `icon.svg` | §2 "full color streams" | ⚠ palette + stream count | ~5 pastel streams; Pack shows 7 saturated streams converging into a brighter hub. |
| `icon-mono.svg` | §2 "white outline" / mono | ✅ aligned | `currentColor`. |
| `icon-simple.svg` | §2 "single color shape" (small) | ⚠ palette mismatch | Reads as the Hub at small size (good); colors pastel. |
| `favicon.svg` | §7 Favicon Stress Test | ⚠ palette + bg | Legible to 16 px (good); bg `#0A1018`/`#0B0F19` vs Pack `#0A101C`. |
| `app-icon.svg` | §3 App Icons (color tile) | ⚠ palette + bg | Rounded dark tile + full mark correct; missing white/grey + monitor variants from §3. |
| `hero.svg` | §1 Hero banner | ⚠ palette mismatch | Composition matches; pastel spectrum + `#05070D` gradient floor. |
| `social-preview.svg` | (OG card, derived from §1) | ⚠ palette mismatch | 1200×630 fine; same pastel spectrum. |

## Audit findings

### 1. Visual differences
- Pack mark: **7 high-saturation streams** converge into a **bright glossy circular
  hub/portal** and exit as a **3D isometric cube**, on a near-black rounded field.
- Current SVGs: ~5 **pastel** streams, softer/flatter hub, lower bloom.

### 2. Missing elements
- Current spectrum lacks pure **Cyan `#00E1FF`**, pure **Blue `#0000FF`**, and
  **Purple `#8F00FF`** as distinct streams (Pack has 7; SVGs have ~5).
- `app-icon.svg` provides only the color tile; Pack §3 also defines a
  **white/grey tile** and a **desktop-monitor mockup** variant — not yet exported.

### 3. Color mismatches
- Spectrum: pastel (`#FF3DA6 #FF8A00 #FFC400 #36D399 #2D9CFF`, plus `#B266FF`) vs
  official (`#00E1FF #FF00FF #FFFF00 #0000FF #32CD32 #FF8500 #8F00FF`).
- Background: SVGs use `#0A1018` / `#0B0F19` / `#05070D`; Pack Primary Dark is
  **`#0A101C`**.

### 4. Icon inconsistencies
- Stream count (5 vs 7), saturation (pastel vs pure), hub bloom/gloss, and portal
  ring definition differ between current icons and the Pack.

### 5. Typography
- ✅ **Inter** matches the Pack (weights 400/600/700). Wordmark lockup "Snapmaker"
  (white) + "Studio" (gradient) matches. Only the gradient's colors differ
  (pastel vs spectrum).

### 6. Polish gaps
- Pack assets show stronger neon bloom, depth/lighting on the hub, glossy rings,
  and a cleaner rounded-square app tile. Current SVGs read flatter and less vivid.

## Alignment plan (future branding sprint — NOT this one)
Re-export each ⚠ SVG against the Pack: swap the pastel spectrum for the 7 official
streams, set background to `#0A101C`, raise hub bloom/gloss, and add the missing
`app-icon` white/grey + monitor variants. Per the directive, **no redesign was
performed here** — this is the recorded gap list for that sprint.
