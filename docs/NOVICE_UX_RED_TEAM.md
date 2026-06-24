# Novice UX Red Team (v0.4.0-beta.15)

> Brutal first-time-U1-owner review. Question each screen: "would a beginner who has
> never sliced understand this?" Severity: P0 blocks/ confuses badly · P1 friction ·
> P2 polish. Effort: S < 1h, M < half day, L > half day.

## Onboarding / first run
| # | Severity | Issue | Why beginners fail | Fix | Effort |
|---|----------|-------|--------------------|-----|--------|
| 1 | P0 | No single "Start here / first print" path on launch | 20+ sidebar items (many "Doctors") overwhelm; a novice doesn't know the order | A Dashboard "Start your first print" card that runs the 7-step flow (Find/Source → Doctor → Prepare → Orca → send) | M |
| 2 | P1 | "Doctor" terminology everywhere (Project/Scale/First Layer/Cost/Pricing/Profit/Multi-Material) | Beginners don't know which Doctor to use when | Group under "Check & Prepare" vs "Business"; one-line "use this when…" on each | M |
| 3 | P1 | Simple vs Advanced mode not obvious at first run | Novice may land in Advanced and see API/filter noise | Default to Simple; a visible toggle with a one-line explanation | S |

## First print / handoff
| # | Sev | Issue | Why | Fix | Effort |
|---|-----|-------|-----|-----|--------|
| 4 | P0 | The slice step is implicit — "Open in Orca" then nothing tells them to slice + export + come back to send | A beginner clicks Open in Orca and is lost in a full slicer | A persistent "next: slice in Orca → export gcode → Printer Hub → Upload" hint after handoff | S |
| 5 | P1 | "gcode" is jargon in the Printer Hub upload button | Novices know "the file Orca made", not "sliced gcode" | Tooltip: "the .gcode file Orca exports after slicing" | S |

## Project Doctor / validation
| # | Sev | Issue | Why | Fix | Effort |
|---|-----|-------|-----|-----|--------|
| 6 | P1 | Verdicts (READY/REPAIRABLE/CONVERTIBLE/HIGH_RISK) are Studio jargon | Beginners don't know what action each implies | Pair each verdict with a verb: "Ready to prepare", "Needs a fix", etc. | S |
| 7 | P2 | Empty state before a file is opened | A blank Doctor page reads as broken | "Open a model to check it" empty state with a button | S |

## Printer Hub
| # | Sev | Issue | Why | Fix | Effort |
|---|-----|-------|-----|-----|--------|
| 8 | P1 | Connection needs hostname/IP knowledge | Novice may not know `U1.local` | "Find my printer" auto-discovery is present — make it the default prominent action; explain `U1.local` | S |
| 9 | P0 (safety) | Emergency stop sits with normal controls | Risk of accidental click; also recovery (firmware restart) not explained | Visually separate e-stop; confirm dialog already exists — add the "needs firmware restart after" note in the confirm | S |
| 10 | P2 | No screenshots/feel of control without a U1 | Judges/users can't see it works | Capture monitor + offline-control states (see SCREENSHOTS_BETA16) | S |

## Plate Color Remap
| # | Sev | Issue | Why | Fix | Effort |
|---|-----|-------|-----|-----|--------|
| 11 | P1 | "filament slot" / "base filament" wording | Beginners think "colour", not "slot" | Lead with colour name, slot in parentheses (already partly done) — apply consistently | S |
| 12 | P2 | Painted-per-face explanation is long | Wall of text on the no-swappable case | Tighten to one sentence + the visual map (the map now exists) | S |

## Source Check
| # | Sev | Issue | Why | Fix | Effort |
|---|-----|-------|-----|-----|--------|
| 13 | P1 | "cannot convert yet" may read as "broken" | Novice may abandon | Reframe as "what to do in Orca instead" — emphasise the next step, not the limitation | S |

## Top fixes for beta.16 (cheapest high-impact)
1. **#1 + #4** — a Dashboard "first print" guided card with the slice-then-send hint (the single biggest beginner win).
2. **#9** — e-stop separation + recovery note (safety + trust).
3. **#6 + #13** — verb-pair verdicts and "next step" framing (clarity, low effort).

These are S/M effort, no architecture change, and directly raise beginner success +
demo quality.
