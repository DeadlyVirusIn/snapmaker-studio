# The Phase 1 entry as submitted — historical record

**This is a historical document. Do not treat it as the current description of
Snapmaker Studio.** The current description is
[../INNOVATION_FUND.md](../INNOVATION_FUND.md).

It is kept because it is the text the Technical Committee received, and knowing
exactly what they were told is necessary to judge what, if anything, needs
correcting.

## Facts of the submission

| | |
|---|---|
| Submitted | **24 June 2026, 20:53** (Formspree form on snapmaker.com) |
| Confirmed | 29 June 2026, by community@snapmaker.com |
| Name | Kunal Khurana |
| Project name | Snapmaker Studio |
| Project URL | <https://github.com/DeadlyVirusIn/snapmaker-studio> |
| Category chosen | Slicer / software |
| Public listing | "snapmaker-studio — by Kunal Khurana", one of 41 projects in the running |

## The description as submitted, verbatim

> Most 3D-printing failures are decided before slicing — a mesh that isn't
> watertight, a model that won't fit the bed or tips over, or slicer settings that
> don't map cleanly to the Snapmaker U1. The slicer assumes the file is already
> good. Beginners only find out when a print fails hours later. Nothing tells
> them, in plain language, what will go wrong first.
>
> Snapmaker Studio fills that gap. It's a local-first desktop app — the pre-print
> intelligence layer — that reads the actual geometry of a 3D model and walks it
> through the whole pre-print workflow: understand, validate, prepare, monitor.
>
> A first-time U1 owner opens the Dashboard, taps "Start your first print," and is
> guided step by step: find a model, run Source Check to learn what the file is
> and the safe next step, run Project Doctor to see real-geometry findings in
> plain language, prepare a clean U1-ready copy (the original is never modified),
> open it in Snapmaker Orca to slice, then return to Printer Hub to watch the U1
> live and send the job.
>
> Studio is advisory and honest. It surfaces likely print risks and explains why,
> so the user decides what to fix. It does not slice — Orca does. It never takes
> autonomous control — Printer Hub provides local, user-confirmed actions, and
> Studio never auto-starts a print.
>
> We verified the printer integration on a real Snapmaker U1: live monitoring,
> file upload/send, and the full start/pause/resume/cancel control loop all
> confirmed on hardware.
>
> Everything is local — no cloud, no account, no upload. It's open source and
> free. Studio decides what to fix, Orca slices, and the U1 prints — three
> complementary tools that, together, help beginners catch problems earlier and
> waste less filament.

## Snapmaker's own listing text

> snapmaker-studio — by Kunal Khurana
>
> "Free local pre-print checker for U1. Flags model defects and risky settings up
> front, before you waste filament."

## What has changed since

Nothing in the submitted text became false. A great deal became incomplete.

| Shipped after the entry | Why it matters to the entry |
|---|---|
| Project-to-printer preflight (beta.23) | The entry describes checking a *file*. Studio now compares a file against the machine — materials against toolheads and against what is actually loaded, geometry against the printer's own bed, required features against the firmware's object list. |
| Fidelity audit (beta.23) | The entry says the original is never modified. Studio now also accounts for the copy, element by element, and refuses the phrase "nothing was lost" unless it can prove it. |
| Reversible fix ledger (beta.23) | Every produced file records what changed, why, and the way back. |
| Colour classification beyond four toolheads (beta.23) | Six colours on four toolheads separated into "needs a toolhead" and "can be a swap", with what it cannot classify kept honest. |
| Ecosystem recommender | Studio names the community tool that fits the file — the "openness" half of the fund's criteria. |
| Withdrawn multi-plate maths (beta.23) | A feature removed rather than patched when its arithmetic could not be justified. |
| Installed-build acceptance harness (beta.24) | 21 checks against the published installer, not a dev server. |
| Read-only real-U1 verification (beta.24) | 13 checks against a real machine, which found and fixed a genuine firmware-reading bug. |
| Recorded 52-second demo (beta.24) | The entry had no video. |

The entry's hardware claim is also now understated in a specific way: it described
verifying the *control* loop in June. Since then the *read* path has been verified
too, and it is the read path that the whole product rests on.
