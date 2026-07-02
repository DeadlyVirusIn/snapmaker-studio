# Asset Mapping & Alignment Audit

> **Source of truth:** the **Brand Identity Asset Pack** —
> [`Brand Identity Snapmaker Studio/`](Brand%20Identity%20Snapmaker%20Studio/).
> Master deck: `brand-master-deck.png`.
> This document maps every `*.svg` to its Pack reference and records alignment.
>
> **STATUS: IMPLEMENTATION COMPLETE.** All color assets were re-authored to the
> Pack's 7-stream spectrum on Primary Dark `#0A101C`, with stronger glow/bloom
> and hub definition; the white-tile, grey-tile, and desktop-mockup app-icon
> variants were added. Verified (XML well-formed, 7 official streams present, no
> deprecated pastel hexes) and previewed via headless Chromium. Branding is now
> **frozen** unless a critical issue is found.

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
| `logo.svg` | §1 Hero & Primary Logo | ✅ implemented | 7-stream mark + spectrum "Studio" wordmark (Inter). |
| `logo-mono.svg` | §2 "single color shape" | ✅ aligned | `currentColor`, no palette dependency. |
| `icon.svg` | §2 "full color streams" | ✅ implemented | 7 saturated streams → bright hub → glossy cube; layered bloom. |
| `icon-mono.svg` | §2 "white outline" / mono | ✅ aligned | `currentColor`. |
| `icon-simple.svg` | §2 "single color shape" (small) | ✅ implemented | 3 saturated stream stubs + hub + cube; `#0A101C` well. |
| `favicon.svg` | §7 Favicon Stress Test | ✅ implemented | Primary Dark tile `#0A101C`; saturated stubs; legible to 16 px. |
| `app-icon.svg` | §3 App Icons (color tile) | ✅ implemented | `#0A101C` rounded tile + full 7-stream mark + halo. |
| `app-icon-white.svg` | §3 App Icons (white tile) | ✅ new | White tile + mark (light surfaces / stores). |
| `app-icon-grey.svg` | §3 App Icons (grey tile) | ✅ new | Brushed-metal grey tile + mark. |
| `app-icon-desktop.svg` | §3 App Icons (desktop mockup) | ✅ new | Monitor showing the app + workflow strip. |
| `hero.svg` | §1 Hero banner | ✅ implemented | 7-stream mark, `#0A101C` field, spectrum wordmark + workflow. |
| `social-preview.svg` | (OG card, derived from §1) | ✅ implemented | 1200×630, 7-stream mark, Primary Dark. |

## Audit findings (all RESOLVED in the implementation sprint)
Each finding below was the pre-implementation gap; every item is now fixed in the
assets (see the ✅ table above).

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

## Alignment plan — DONE
Every ⚠ SVG was re-authored against the Pack: pastel spectrum → 7 official streams,
backgrounds → `#0A101C`, hub bloom/gloss raised, and the `app-icon` white/grey +
desktop-mockup variants added. Verification:
- `python` XML parse + palette scan: all 10 assets well-formed, 7 official streams
  present (simplified `icon-simple`/`favicon` carry 3 stream colors by design),
  zero deprecated pastel hexes, `#0A101C` present in every asset.
- Headless Chromium render of each asset + a before/after board (visual check OK).

Branding is **frozen** from here unless a critical issue is found.
