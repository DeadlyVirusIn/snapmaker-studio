# Snapmaker Studio — Color Palette

> **Source of truth:** the **Brand Identity Asset Pack** —
> [`Brand Identity Snapmaker Studio/`](Brand%20Identity%20Snapmaker%20Studio/)
> (master deck `Gemini_Generated_Image_awl389awl389awl3.png`, section 6
> "Official Color Palette"). Hexes below are transcribed verbatim from that deck.
> Do not introduce colors outside this list.

## Official palette (verbatim from the Asset Pack)

### Rainbow Streams (multi-material flow — 7 colors, left → right)
| Token | Hex | Pack label |
|---|---|---|
| `mm-cyan` | `#00E1FF` | Cyan |
| `mm-magenta` | `#FF00FF` | Magenta |
| `mm-yellow` | `#FFFF00` | Yellow |
| `mm-blue` | `#0000FF` | Blue |
| `mm-green` | `#32CD32` | Green |
| `mm-orange` | `#FF8500` | Orange |
| `mm-purple` | `#8F00FF` | Purple |

### Base
| Token | Hex | Pack label |
|---|---|---|
| `primary-dark` | `#0A101C` | Primary Dark (background / app shell) |
| `accent-white` | `#FFFFFF` | Accent White (wordmark "Snapmaker", outlines) |

### UI chrome (from the Pack's reference HTML / interface mockup)
These power neutral surfaces; the spectrum is for the mark + material story only.
| Token | Hex | Use |
|---|---|---|
| `panel` | `#16192B` | cards / panels |
| `border` | `#334155` | dividers, connectors |
| `text` | `#F2F2F2` | primary text |
| `text-muted` | `#94A3B8` | secondary text / labels |
| `accent` | `#00A6FF` | interactive accent (links, focus) |
| `accent-hover` | `#00E1FF` | hover state |

## Status (maps to product verdicts)
Derived from the official streams — keep meaning, not arbitrary fills.
| State | Hex | Verdict |
|---|---|---|
| ready / success | `#32CD32` | READY / Validated (Green) |
| warn / repairable | `#FFFF00` | REPAIRABLE (Yellow) |
| info / convertible | `#00A6FF` | CONVERTIBLE (Accent) |
| risk / error | `#FF3DF9` | HIGH_RISK (Magenta contrast) |

## Usage rules
- The 7-color spectrum is for the **brand mark and the multi-material story** —
  not general UI fills. UI stays neutral (panel + text); color carries meaning
  (status) only.
- Maintain ≥ 4.5:1 text contrast on `primary-dark`/`panel`.
- Don't introduce spectrum colors outside this list; if a new accent is needed,
  add it to the Asset Pack first, then mirror it here.

## DEPRECATED — earlier "Studio Hub" pastel palette
The previous palette (pink `#FF3DA6`, orange `#FF8A00`, yellow `#FFC400`, green
`#36D399`, blue `#2D9CFF`; bg `#0B0F19`/`#05070D`) is **superseded** by the Asset
Pack. The current `*.svg` files in this folder still carry that pastel family and
near-black backgrounds (`#0A1018`/`#0B0F19`/`#05070D`) — see
[`ASSET_MAPPING.md`](ASSET_MAPPING.md) for the per-file gap list and re-export plan.
