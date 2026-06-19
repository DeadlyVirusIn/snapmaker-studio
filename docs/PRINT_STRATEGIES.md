# Print Strategies

Snapmaker Studio offers five **intent-based print strategies** for the Snapmaker U1's
multi-color prime/wipe tower. Pick the outcome you want; Studio shows the settings.

> **Studio recommends — Snapmaker Orca slices.** Studio does not slice or print. It reads
> your design, suggests a strategy, and (in Advanced Mode) shows the exact prime/wipe-tower
> settings to apply in Snapmaker Orca, which generates the actual G-code.

## The strategies

| Strategy | Best for | Trade-off |
|---|---|---|
| **Fastest Print** | Single-color / simple / draft prints | A bit more color bleed; less stable on tall jobs |
| **Balanced** (default) | Most multi-color prints | A dependable middle ground |
| **Best Quality** | Crisp color transitions | More filament + time for extra purging |
| **Maximum Reliability** | Tall prints, many colors, long jobs | Largest tower/brim, more waste, least likely to fail |
| **Advanced** | Power users | No automatic overrides — you tune raw values in Orca |

## How Studio recommends

The recommendation uses **real signals from your design only** — color/material count,
source ecosystem, model dimensions, and complexity. It never fabricates print duration,
exact tool-change counts, or purge volumes. When it can't measure something, it says so
("estimated from color count and model complexity").

Rules of thumb Studio applies (grounded in the
[U1 print-profile research](research/U1_PRINT_PROFILE_RESEARCH.md)):

- **Single color** → Fastest (a heavy multi-color tower isn't needed).
- **Tall, many colors, or complex** → Maximum Reliability (tall towers tip over more easily).
- **More than 4 colors** → a warning: the U1 has **4 toolheads**, so some colors share a
  toolhead with extra tool changes.
- Otherwise → Balanced.

## Safety

Every strategy honors the U1's documented limits
([prime-tower collapse guide](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/prime_tower_collapse)):

- The tower speed is **never** auto-raised above the safe 90 mm/s.
- "Skip empty tower layers" (no-sparse-layers) is **never** auto-enabled — it carries an
  explicit collision warning.
- Strategies never touch your geometry, colors, or per-filament data.

These are slicer process settings — they change the sliced result, never the printer
firmware. See [`research/U1_PRINT_PROFILE_RESEARCH.md`](research/U1_PRINT_PROFILE_RESEARCH.md)
for sources, verified-vs-inferred findings, and confidence levels.
