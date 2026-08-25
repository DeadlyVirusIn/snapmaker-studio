# Snapmaker Studio v0.7.1 — what a real brush writes

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

A patch release with two fixes and one correction, all of them found by checking
Studio against something outside itself.

## A genuine painted project could be reported as partly undecodable

v0.7.0 read painting from files that Studio's own encoder had written and slicers
had echoed back. This release went further and painted **inside Snapmaker Orca
2.3.5 and Bambu Studio 02.08.02.61** — their gizmos, their brushes, their filament
palettes — and read what those slicers saved.

That found a defect. A single facet of a large surface, painted with Snapmaker
Orca's round brush, is written as a **35,460-character** attribute; Studio refused
anything over 4,096, a limit chosen before any slicer-authored file had been seen.
Two facets of a real project came back as malformed, losing their filament, area
and height. Studio now reads them: three filament slots across 55,374 painted
patches, in under a tenth of a second.

## "Share the same layers" was more than Studio can prove

Two colours whose heights overlap *can* meet on a printed layer. Whether one
really does is decided when Orca slices, and Studio does not slice. The plan has
not changed — a toolhead is reserved for each such colour, which is the
conservative answer either way — but the wording now matches the evidence:
**"not proven separable — reserve a toolhead each"**.

## Four claims on this project's own pages were false

The README's download button still pointed at v0.6.2. The self-check was described
as a 25-check table and the acceptance harness as 30 checks. The evidence section
credited "the published v0.6.2 installer" directly above v0.7.0's numbers.

The guard that exists to prevent exactly this read one line at a time, so a
sentence that wrapped, or a link outside the Download section, was invisible to
it. It now reads whole blocks — paragraphs, table rows, list items, with the
headings above them — and covers release links anywhere, installer credits,
screenshot paths, combined evidence rows, prose counts and the demo's length. Each
of the four false claims is now a test against the guard itself.

## What has not changed

Studio still does not slice — Snapmaker Orca does. It still never starts a print,
never modifies your original file, and never sends anything anywhere: no cloud, no
account, no telemetry.

## Verified against this installer

- Installed-build acceptance: **31/31**, including upgrading in place from v0.7.0
- Real Snapmaker U1, read-only: **26/26**
- `u1convert selfcheck`: **27/27** over 15 documented routes
- `pytest`: **1153 passed, 3 skipped** · `npm run test`: **306 passed**

Verification detail: [docs/TRUST_STATUS.md](TRUST_STATUS.md). Installer name, size
and hash: [docs/RELEASE_METADATA.md](RELEASE_METADATA.md). What painting Studio
reads, where it stops, and which slicer proved which row:
[docs/PAINTED_COLOUR.md](PAINTED_COLOUR.md).

## Still true, and stated plainly

Windows only. The installer is not code-signed — verify the SHA256. Purge cannot be
separated from printed filament in Orca's output. The fitted nozzle cannot be read
from the printer, and stays unknown. Free storage is not exposed by stock firmware.
Painted colour is read from the project, but whether two painted colours share a
printed layer is decided by the slice, not the file — and that a paint state names
filament *N* has been proven by slicing in PrusaSlicer only. Remaining filament is
known only where something tracks it.
