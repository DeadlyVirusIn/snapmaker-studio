# Snapmaker Studio — Color Palette

Extracted from the approved "Studio Hub" artwork. Dark-first.

## Surfaces (dark-mode base)
| Token | Hex | Use |
|---|---|---|
| `bg` | `#0B0F19` | primary background / app shell |
| `bg-deep` | `#05070D` | gradient bottom, vignette |
| `surface` | `#121826` | cards / panels |
| `border` | `#3A4252` | dividers, connectors |
| `text` | `#E5E9F0` | primary text |
| `text-muted` | `#9AA4B2` | secondary text / labels |

## Multi-material spectrum (the ribbons)
Use in this order to keep the left->right flow consistent.
| Token | Hex |
|---|---|
| `mm-pink` | `#FF3DA6` |
| `mm-orange` | `#FF8A00` |
| `mm-yellow` | `#FFC400` |
| `mm-green` | `#36D399` |
| `mm-blue` | `#2D9CFF` |

## Portal / transform
| Token | Hex | Use |
|---|---|---|
| `portal-core` | `#FFFFFF` | bright center |
| `portal-glow` | `#6EE7FF` | cyan glow |
| `portal-edge` | `#2D9CFF` | ring edge |
| `cube-top` | `#22D3EE` | finished-print top face |
| `cube-left` | `#FF3DA6` | left face |
| `cube-right` | `#36D399` | right face |

## Gradients
- **Studio wordmark / accent:** `#FF3DA6 -> #FF8A00 -> #36D399 -> #2D9CFF`
  (linear, left->right).
- **Portal core:** radial `#FFFFFF -> #6EE7FF -> transparent #2D9CFF`.
- **App/social background:** linear `#0B0F19 -> #05070D`.

## Status (maps to product verdicts)
| State | Hex | Verdict |
|---|---|---|
| ready / success | `#36D399` | READY / Validated |
| warn / repairable | `#FFC400` | REPAIRABLE |
| info / convertible | `#2D9CFF` | CONVERTIBLE |
| risk / error | `#FF4D4D` | HIGH_RISK |

## Usage rules
- The full spectrum is for the **brand mark and the multi-material story** — not
  general UI fills. UI stays neutral (surfaces + text); color carries meaning
  (status) only.
- Maintain >= 4.5:1 text contrast on `bg`/`surface`.
- Don't introduce spectrum colors outside this list; if a new accent is needed,
  add it here first.

## Tailwind / CSS variable mapping (suggested)
The desktop app's existing tokens (`--background`, `--card`, verdict colors) align
with the above; when wiring branding into the app, set `--background:#0B0F19`,
verdict greens/ambers/blues/reds to the Status hexes.
