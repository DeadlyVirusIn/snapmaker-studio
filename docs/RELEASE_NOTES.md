# Snapmaker Studio v0.4.0-beta.23 — This project, on your printer

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

## Before you slice

Studio now compares what your project needs against the printer it can actually
see: how many materials it uses against how many toolheads your printer reports,
the nozzle the project was made for against the one your printer reports, the
objects against your printer's real bed, and the features a prepared copy relies
on against your firmware's own list.

Where Studio genuinely cannot read something, it says so. Stock U1 firmware does
not report which nozzle is fitted, so that check reads *"Nozzle size — check this
yourself"* and explains what a mismatch would do to your print. It never turns
"couldn't detect" into "your printer can't do it".

## What survived preparing this copy

Every other converter tells you the same word: converted. Studio now lists what
stayed byte-for-byte identical, what it changed and why, what it could not carry
over — and, kept separate on purpose, anything it could not check at all.

Studio only tells you nothing was lost when that check proves it for *your* file.

## Changes Studio made, and the way back

Every file Studio produces is recorded: what was done, what triggered it, each
change with its old value and the reason, and whether the result validated. One
button returns you to your original. Your original was never modified, so going
back simply reopens the untouched file — the copy stays where it is.

## Six colours, four toolheads

That is not one problem but two, and they have different fixes. Studio separates
the colours that share layers — each of which needs a toolhead — from colours that
only appear higher up, which may be handled as planned swaps at the height shown.
When it cannot tell, because painted colour cannot be read without slicing, it
says so instead of guessing in the optimistic direction.

## Smaller things that matter

- A prepared copy is now labelled with the print preset that matches its actual
  layer height. A 0.12 mm project used to come out stamped "0.20 Standard".
- Object placement, colour planning and the printer check now appear on **Check my
  model**, where a beginner actually lands.
- Preparing a copy marks **Preserve creator settings** as recommended, and
  describes both options by what happens to your print rather than by setting name.
- `u1convert selfcheck` runs the whole pipeline and prints a pass/fail table, for
  anyone who wants to see it work without installing the app.

## Removed

**Multi-plate repositioning.** An independent review reproduced a case where it
placed a plate completely off the bed while reporting success. The spacing between
plates is not recorded in the project file, so any move is a guess — the feature
was withdrawn rather than patched. Multi-plate projects are still checked, each
plate on whether its own contents fit a U1 plate, and Studio points you at
Snapmaker Orca's Arrange.

## Fixed

- On a clean install, part of the engine was missing from the package, so the
  local service could not start and the self-check failed. Fixed.
- Two tools in the ecosystem list could never actually be suggested.
- The colour check assumed four toolheads without saying it had not asked your
  printer.
- Studio now limits how much data it will read from a printer, as it already did
  for project files.

## Unchanged

Local-first: no cloud, no account, nothing uploaded. Studio does not slice —
Snapmaker Orca does. Your originals are never modified. Studio never starts a
print on its own, and it gives advisory checks, not a guarantee of print success.

## Install

See [RELEASE_METADATA.md](RELEASE_METADATA.md) for the installer name, size and
SHA256, and [windows-install.md](windows-install.md) for the full instructions.
The installer is not code-signed yet, so Windows SmartScreen will show an unknown
publisher — verify the SHA256 before running it.
