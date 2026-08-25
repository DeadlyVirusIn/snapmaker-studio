# Snapmaker Studio v0.7.2 — a Prusa object's filament survives the crossing

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

A patch release with one defect fixed and one audit that should have caught it.

## Every PrusaSlicer project came out on filament 1

If you assigned an object to filament 3 in PrusaSlicer and asked Studio to prepare
a U1 copy, the copy assigned it filament 1. Every object, every project. The
geometry was byte-identical, nothing was reported removed, and the print would
have come out in the wrong colours.

Prepare now carries what the source says each object prints in. A slot above four
is carried as it is, never renumbered to fit the machine's toolheads — a project
may legitimately reference six colours, and deciding which to merge is a question
for you, with Studio's colour planning, not a silent rewrite. An object with no
assignment of its own takes its volumes' slot when they agree, and its own name
comes across with it.

## The audit could not see it

Fidelity compared per-object assignments only when both files spoke the same
dialect, and a PrusaSlicer source never does. It now reads the assignment from
either dialect and reports one row per object: preserved, changed with
**"slot 3 → slot 1"**, lost, or — for an object whose volumes use different
filaments, which a single-part U1 object cannot represent — not representable,
with the slots named rather than one of them quietly chosen.

## What has not changed

Studio still does not slice — Snapmaker Orca does. It still never starts a print,
never modifies your original file, and never sends anything anywhere.

## Verified against this installer

- Installed-build acceptance: **31/31**, including upgrading in place from v0.7.1
- Real Snapmaker U1, read-only: **26/26**
- `u1convert selfcheck`: **27/27** over 15 documented routes
- `pytest`: **1185 passed, 4 skipped** · `npm run test`: **306 passed**

Verification detail: [docs/TRUST_STATUS.md](TRUST_STATUS.md). Installer name, size
and hash: [docs/RELEASE_METADATA.md](RELEASE_METADATA.md).

## Still true, and stated plainly

Windows only. The installer is not code-signed — verify the SHA256. Purge cannot be
separated from printed filament in Orca's output. The fitted nozzle cannot be read
from the printer. Free storage is not exposed by stock firmware. Painted colour is
read from the project, but whether two painted colours share a printed layer is
decided by the slice. A PrusaSlicer object whose volumes use different filaments
cannot be fully carried into a single-part U1 object, and the audit says so.
Remaining filament is known only where something tracks it.
