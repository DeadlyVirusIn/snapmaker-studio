# Snapmaker Studio v0.4 — Product Proposal (Novice-First)

**Date:** 2026-06-18 · **Status:** product design only (no implementation) · **Audience:** novice makers

Refines `PLATFORM_EXPANSION.md` into a product spec written for someone who just bought
their first printer. Goal: turn "a tool that fixes files" into **"the app that tells me if
my design will print, and gets it ready in one click."**

## Plain-language glossary (jargon we never show the user)

| Internal term | What the user sees |
|---|---|
| 3MF / project file / STL | **your design** / **print file** |
| printer profile / target | **your printer** |
| filament mapping / arrays / extruder slots | **colors** / **color slots** |
| doctor / diagnose | **Check** ("Will it print?") |
| convert / transform / repair | **Get it ready** |
| validate / validation | **Double-check** / **Ready to print** |
| compatibility score | **Print-Readiness** (★ rating) |
| compatibility matrix | **"Which printers can make this?"** |
| verdict READY/REPAIRABLE/etc. | ✅ Ready · 🛠 Needs a quick fix · ⚠️ Might not print |

---

## The 5 features, in plain words

1. **Design Insights** (Project Intelligence) — "Here's what's in this design."
2. **Print-Readiness Check** (Validation Center) — "Will it print on *my* printer?"
3. **Which printers can make this?** (Compatibility Matrix) — "Your design, on every printer."
4. **Your Printers** (Printer Profiles) — "Tell us what you own; we handle the rest."
5. **Simple Mode** (Beginner Mode) — one guided path, no jargon, on by default.

---

## Screen inventory

| Screen | Purpose | Mode |
|---|---|---|
| **Home** | Add a design; see recent designs | Simple (default) |
| **Add a design** | Drag/drop or browse | Simple |
| **Design Insights** | What's in this design (size, colors, where it's from) | Simple |
| **Print-Readiness Check** | Will it print on my printer? ★ rating + plain fixes | Simple |
| **Which printers can make this?** | Same design across printers | Simple |
| **Get it ready → Done** | One-click prepare + "what now" | Simple |
| **My Designs** | Everything I've worked on (history per design) | Simple |
| **Your Printers** | Pick/add the printers I own | Simple |
| **Settings** | Simple ↔ Advanced toggle | Both |

Advanced Mode = today's Workspace/Doctor/Compare/Batch with the technical labels, for power users.

---

## UX wireframes (beginner language)

### Home (Simple Mode, default)
```
┌────────────────────────────────────────────────────────┐
│  Snapmaker Studio                       My Printer: U1 ▾ │
├────────────────────────────────────────────────────────┤
│                                                          │
│        ⬇  Drop a design here, or  [ Browse… ]            │
│           Works with files from any maker site           │
│                                                          │
│   Recent designs                                         │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐                  │
│   │ Vase    │  │ Bracket │  │ Dragon  │                  │
│   │ ✅ Ready│  │ 🛠 Fix  │  │ ✅ Ready│                  │
│   └─────────┘  └─────────┘  └─────────┘                  │
└────────────────────────────────────────────────────────┘
```
- **See:** a drop zone + recent designs with a status dot.
- **Decide:** add something new, or reopen a recent design.
- **Next:** drop/browse a file → goes to Design Insights.

### Design Insights (Project Intelligence)
```
┌────────────────────────────────────────────────────────┐
│  ← Back            Dragon.print            ✅ Looks good │
├────────────────────────────────────────────────────────┤
│  What's in this design                                   │
│   • Size:        12 × 8 × 15 cm                          │
│   • Colors:      4 colors                                │
│   • Parts:       1 model                                 │
│   • From:        a Bambu design                          │
│   • Detail:      painted areas kept                      │
│                                                          │
│  Print-Readiness for your printer (U1):  ★★★★☆           │
│                                                          │
│        [ Check my printer ]     [ Get it ready ]         │
└────────────────────────────────────────────────────────┘
```
- **See:** what the design is, in human terms, + a readiness rating.
- **Decide:** is this what I expected? do I trust it?
- **Next:** "Get it ready" (one click) or "Check my printer" for detail.

### Print-Readiness Check (Validation Center)
```
┌────────────────────────────────────────────────────────┐
│  ← Back     Will it print on your U1?      ★★★★☆ (4/5)   │
├────────────────────────────────────────────────────────┤
│  ✅ Fits on the print bed                                │
│  ✅ Colors supported (4 of 4)                            │
│  🛠 One setting needs a quick fix  →  we can do this     │
│  ✅ Nothing missing                                      │
│                                                          │
│  "We can fix the one item for you automatically."        │
│                                                          │
│              [ Get it ready ]   [ See other printers ]   │
└────────────────────────────────────────────────────────┘
```
- **See:** a checklist in plain English + a star rating.
- **Decide:** let the app fix the flagged item, or compare printers.
- **Next:** "Get it ready" → Done screen.

### Which printers can make this? (Compatibility Matrix)
```
┌────────────────────────────────────────────────────────┐
│  ← Back        Dragon.print on your printers             │
├────────────────────────────────────────────────────────┤
│   Printer            Will it print?     Colors           │
│   ───────────────────────────────────────────────       │
│   Snapmaker U1   ★   ★★★★☆  Ready          4/4           │
│   Bambu X1C          ★★★★★  Ready          4/4           │
│   Prusa XL           ★★★☆☆  Needs a fix    4/4           │
│                                                          │
│   ★ = your default printer                               │
│                  [ Get it ready for: U1 ▾ ]              │
└────────────────────────────────────────────────────────┘
```
- **See:** the same design rated across the printers they own.
- **Decide:** which printer to make this on.
- **Next:** pick a printer → "Get it ready."

### Get it ready → Done
```
┌────────────────────────────────────────────────────────┐
│                    ✅ Ready to print!                    │
│                                                          │
│   Saved:  Dragon (ready for U1)                          │
│   We kept your original safe and made a print-ready copy.│
│                                                          │
│   What now?                                              │
│   1. Open it in your printer's app                       │
│   2. Press print                                         │
│                                                          │
│        [ Open folder ]      [ Do another ]               │
└────────────────────────────────────────────────────────┘
```
- **See:** confirmation + reassurance (original is safe) + 2 simple next steps.
- **Decide:** done, or do another.
- **Next:** open folder / start over.

### Your Printers (Printer Profiles)
```
┌────────────────────────────────────────────────────────┐
│  Your printers                              [ + Add ]    │
├────────────────────────────────────────────────────────┤
│   ● Snapmaker U1     (default)                           │
│   ○ Bambu X1C                                            │
│   ○ Prusa XL                                             │
│                                                          │
│   Don't see yours?  [ Tell us ]                          │
└────────────────────────────────────────────────────────┘
```
- **See:** the printers they've added; which is default.
- **Decide:** add a printer, switch default.
- **Next:** pick default → every screen tailors to it.

---

## User journey (first-time novice)
1. Opens app → **Home**, asked once: "Which printer do you have?" → picks U1.
2. Drags a design from a maker site download → **Design Insights**: "4 colors, fits, from a Bambu design."
3. Sees **★★★★☆ for your U1** → taps **Get it ready**.
4. App fixes the one flagged item automatically → **Done**: "Ready to print! Original kept safe."
5. Curious → taps **Which printers can make this?** → sees it'd be ★★★★★ on an X1C. (Aspiration + platform feel.)
6. Comes back later → **My Designs** shows the history: added → checked → made ready.

No "3MF," no "profile," no "filament array" anywhere in this path.

---

## Innovation Fund narrative
> **"3D printing is still too hard for newcomers."** Files from one ecosystem don't work on
> another printer, and the error messages are written for experts. Snapmaker Studio v0.4 is the
> **friendly front door**: drop in any design, and in plain language it tells you *will this
> print on my printer?* — then makes it ready in one click. It works across printers (Snapmaker,
> Bambu, Prusa), keeps your originals safe, and never shows you jargon. It turns "I downloaded a
> file I can't use" into "I pressed print." That's how 3D printing reaches the next million makers
> — and it's **local-first and open source**, so it's a platform the community can extend.

Fund-relevant pillars: **accessibility** (novice-first), **interoperability** (cross-printer),
**trust** (originals safe, validation always on), **openness** (local-first, extensible).

---

## Implementation phases (dependency-aware)

- **Phase 1 — "It understands my design"** (no printer dependency)
  - Design Insights (Project Intelligence) + Simple Mode shell + plain-language relabel.
  - Wire the existing history table behind **My Designs**.
  - *Visible value immediately; demoable on day one.*
- **Phase 2 — "It knows my printer"**
  - Your Printers (Printer Profiles framework) + one second printer as proof.
- **Phase 3 — "Will it print on my printer?"**
  - Print-Readiness Check (Validation Center) — printer-aware ★ rating + plain fixes. *Needs Phase 2.*
- **Phase 4 — "On every printer"**
  - Which printers can make this? (Compatibility Matrix). *Needs Phases 2–3.*

---

## Ranking — Innovation Fund impact per engineering week

| Feature | Est. eng weeks | Fund impact | Impact/week | Depends on |
|---|---|---|---|---|
| **Simple Mode + plain-language relabel** | ~1 | High | ★★★★★ | — |
| **Design Insights** | ~1–2 | High | ★★★★★ | — |
| **My Designs + history timeline** | ~0.5 | Med | ★★★★ | — |
| **Print-Readiness Check** | ~2 | High | ★★★★ | Printers |
| **Compatibility Matrix** | ~1 | Very High (demo) | ★★★★ | Printers + Readiness |
| **Your Printers (+1 printer)** | ~3 | Very High | ★★★ | — (foundation) |

**Read:** Simple Mode + Design Insights are the cheapest high-impact wins and need no printer work
— ship them first. Printer Profiles is lower impact-per-week alone, but it's the **foundation** the
two highest-demo features (Readiness Check, Compatibility Matrix) stand on, so it's sequenced early
despite the ratio.

## Recommendation
Build v0.4 in the phase order above. **Phase 1 alone** already reframes the product as a
beginner-friendly platform and is demoable within ~2 weeks. **Phases 2–4** deliver the
"any printer" wow (Compatibility Matrix) that anchors the Innovation Fund pitch. Marketplace
**Discover** stays deferred to v0.5 (legal review, official-API-only) — see `DISCOVER_LOWRISK.md`.

> Product design only — no code. Approval gate before Phase 1 implementation.
