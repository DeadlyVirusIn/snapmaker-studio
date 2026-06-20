# Snapmaker Studio — Metrics Sheet

Real, verifiable numbers (no projections, no fabricated traction).

## Product scope
| Metric | Value |
|---|---|
| Intelligence "Doctors" | 7 (Project, Printer, First-Layer, Multi-Material, Cost, Pricing, Profit) |
| Top-level synthesis | 1 (Studio Intelligence Report) |
| Curated community issues (MVP knowledge base) | 6 (out-of-bounds, prime tower, multi-material, first layer, cryptic errors, conversion) |
| Read-only printer endpoints (Moonraker GET) | telemetry, history, file metadata, diagnostics, capabilities, bed mesh |
| Printer-control / write endpoints | 0 (read-only by design) |

## Engineering quality
| Metric | Value |
|---|---|
| Automated tests passing | 166 / 166 |
| Frontend typecheck (tsc) | clean |
| Production build | clean |
| Release candidate | v0.4.0-beta.1 |
| Installer size | 15.27 MB |
| Frozen engine (sidecar) | 13.42 MB |
| App ProductVersion / FileVersion | 0.4.0-beta.1 |
| RC smoke test | endpoints 200, launch OK, sidecar spawns, 0 orphans |

## Time-to-value (demo)
| Metric | Value |
|---|---|
| First answer (Intelligence Report) | ~15 seconds |
| Full reviewer demo (launch to Why Studio) | under 60 seconds |
| Clicks for full demo narrative | 3 |
| Hardware required for demo | 0 (Demo Mode) |
| Model file required for demo | 0 |

## Privacy / trust
| Metric | Value |
|---|---|
| Data sent off-device | 0 (local-first) |
| External network calls in Demo Mode | 0 |
| Estimates labelled as estimates | yes (cost, price, profit, Expected Improvement) |
| Fabricated values | none (unavailable signals skipped, not invented) |

## What is NOT yet measured
- External tester results (form + report template ready in `VALIDATION_KIT.md`;
  tester round pending).
- Field coverage of live-printer features across U1 firmware variants.
